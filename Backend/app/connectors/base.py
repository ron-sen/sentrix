
from abc import ABC , abstractmethod
from datetime import datetime , timezone , timedelta
from decimal import Decimal , InvalidOperation
from typing import Any
import logging

from sqlalchemy import select , func 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.portfolio_auth import MarketPriceCandles

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """
    contract every market data provider connector must follow 
    pipline : plan -> fetch -> normalize -> validate -> store

    """

    def __init__(self , db : AsyncSession , asset_id : int , exchange: str , timeframe : str):
        self.db = db
        self.asset_id = asset_id
        self.exchange = exchange
        self.timeframe = timeframe 


    async def plan(self) -> tuple[datetime , datetime]:
        """
        decide what time range to fetch , by checking our own DB for the last candle we already have.
    
        """

        stmt = select(func.max(MarketPriceCandles.candle_time)).where(
            MarketPriceCandles.asset_id == self.asset_id,
            MarketPriceCandles.exchange == self.exchange,
            MarketPriceCandles.timeframe == self.timeframe ,
        )
        result = await self.db.execute(stmt)
        last_candle_time = result.scalar()

        end = datetime.now(timezone.utc)

        if last_candle_time is None :
            start = end - self._default_lookback()
        else : 
            start = last_candle_time

        return start, end 
    
    def _default_lookback(self):
        return timedelta(hours=1)
    
    @abstractmethod
    async def fetch(self , start : datetime , end : datetime ) -> Any :
        """
        call the provider's API and return new response data

        """
    
    @abstractmethod
    def normalize(self , raw_data : Any) -> list[dict]:

        """
        converting providers raw response into a list of dict matching according to our schema

        """

    def validate(self , normalized_rows : list[dict]) -> tuple[list[dict] , list[dict]]:

        """
        sanity check normalized row --> returns ( good rows , bad rows)
        bad rows are quarantined ( logged + skipped) , not stored
        """

        good_rows =[]
        bad_rows = []

        for row in normalized_rows:
            reason = self._check_row(row)
            if reason :
                logger.warning(f"Quarantined candle row: {reason} | row ={row}")
                bad_rows.append({**row , "_quarantine_reason": reason})

            else :
                good_rows.append(row)

        return good_rows , bad_rows
    
    def _check_row(self , row : dict[str , Any]) -> str | None :
        """
        Return the validation failure reason or None when valid
       """
        
        required_fields = (
            "candle_time",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
        )

        for field in required_fields:
            if field not in row or row[field] is None :
                return f"missing required field: {field}"
            
        candle_time = row["candle_time"]

        if not isinstance(candle_time ,datetime):
            return " candle_time must be a datetime"
        
        if candle_time.tzinfo is None or candle_time.utcoffset() is None :
            return "candle_time must be timezone aware"
        
        if candle_time.utcoffset() != timedelta(0):
            return "candltime must be normalized to UTC"
        
        prices : dict[str , Decimal] = {}

        for feild in ("open_price" , "high_price" , "low_price" , "close_price"):
            value = row[feild]

            if isinstance(value , bool):
                return f"{field} must be numeric"
            
            try :
                price = Decimal(str(value))
            except (InvalidOperation , TypeError , ValueError):
                return f"{field} must be numeric"
            
            if not price.is_finite():
                return f"{field} must be finite"
            
            if price <= 0 :
                return f"{field} must be greater than zero"
    
            
            prices[field] = price

        open_price = prices["open_price"]
        high_price = prices["high_price"]
        low_price = prices["low_price"]
        close_price = prices["close_price"]
        

        if high_price < low_price:
            return "high_price cannot be lower than low_price"
        
        if high_price < max( open_price , close_price):
            return "high_price cannot be lower than open_price or close_price"
        
        if low_price > min(open_price , close_price):
            return "low_price cannot be higher than open_price or close_price"
        
        if "volume" in row and row["volume"] is not None :
            try :
                volume = Decimal(str(row["volume"]))
            except (InvalidOperation , TypeError , ValueError):
                return"Volume must be numeric"
            
            if not volume.is_finite():
                return "Volume must be finite"
            if volume < 0 :
                return "volume cannot be negative"
            
        return None
    

    async def store(self , good_rows : list[dict]) -> int : 
        """
        upsert validate row into market_price_candles. same (asset_id , timeframe , candle_time) - > update in place , return number of rows written .

        """

        if not good_rows:
            return 0 
        
        stmt = pg_insert(MarketPriceCandles).values(good_rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                "asset_id" ,
                "exchange",
                "timeframe" , 
                "candle_time"
            ],

            set_ = {
                "open_price" : stmt.excluded.open_price ,
                "high_price" : stmt.excluded.high_price , 
                "low_price" : stmt.excluded.low_price ,
                "close_price" : stmt.excluded.close_price ,
                "volume" : stmt.excluded.volume ,
                "quote_volume" : stmt.excluded.quote_volume,
            },
        )
        await self.db.execute(stmt)
        await self.db.commit()

        logger.info(f"Stored/updated {len(good_rows)}candles for asset_id ={self.asset_id}")
        return len(good_rows)

    
    #* ----------Orchestration----------------------------------

    async def run(self) -> dict :
        """
        run the full pipline : plan -> fetch -> normalize -> validate -> store. returns a summary dict .
        """

        start , end = await self.plan()
        raw_data = await self.fetch(start , end)
        normalized_rows = self.normalize(raw_data)
        good_rows , bad_rows = self.validate(normalized_rows)
        stored_count = await self.store(good_rows)

        summary = {
            "fetched" : len(normalized_rows),
            "stored" : stored_count ,
            "quarantined": len(bad_rows),
        }
        logger.info(f"Connector run complete {summary}")
        return summary