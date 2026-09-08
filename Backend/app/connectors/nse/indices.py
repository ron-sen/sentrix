
import yfinance as yf
from app.connectors.base import BaseConnector
from datetime import datetime , timezone 
from typing import Any

import logging
from app.connectors.nse.client import is_market_open
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models.nse import NSEPriceCandles



logger = logging.getLogger(__name__)


TIMEFRAME_MAP = {
    "1m" : "1m" ,
    "5m" : "5m",
    "15m" : "15m",
    "1h" : "1h" ,
    "1d" : '1d',
}

class NiftyConnector(BaseConnector):

    def __init__(self, db, instrument_id ,exchange, timeframe , yf_symbol):
        super().__init__(db, instrument_id , exchange, timeframe)

        self.yf_symbol = yf_symbol


    async def fetch(self, start : datetime, end : datetime) -> Any :

        #* market hrs guard - nse only trades 9 : 15 AM to 3:30 PM IST weekdays

        if not is_market_open():
            logger.info(f"NSE market is closed , skipping fetch for {self.yf_symbol}")
            return None  # normalize will handle none gracefully

        interval = TIMEFRAME_MAP[self.timeframe]

        #* yfinance is sync - run in same thread no httpx needed 
        #* start/end as strings in YYYY-MM-DD formate

        data = yf.download(
            self.yf_symbol ,
            start=start.strftime("%Y-%m-%d"), 
            end=end.strftime("%Y-%m-%d"),
            interval = interval , 
            progress = False , # supress download pogress bar in logs 
        )

        logger.info(f"Fetched {len(data)} rows for {self.yf_symbol}")
        return data


    def normalize(self, raw_data) -> list[dict] :


        #* handling market closed case 
        if raw_data is None or raw_data.empty :
            return []
        
        normalized = []

        for timestamp , row in raw_data.iterrows():

            #* timeframe is pandas timestamp with IST timezone ( +5 : 30)
            #* converts to UTC for storage

            candle_time = timestamp.to_pydatetime().astimezone(timezone.utc)

            normalized.append({
                "instrument_id": self.asset_id,
                "exchange":    self.exchange,
                "timeframe":   self.timeframe,
                "candle_time": candle_time,
                "open_price":  float(row["Open"].iloc[0]),
                "high_price":  float(row["High"].iloc[0]),
                "low_price":   float(row["Low"].iloc[0]),
                "close_price": float(row["Close"].iloc[0]),

                "volume": float(row["Volume"].iloc[0]) if row["Volume"].iloc[0] else None,
                
                "quote_volume": None,  # yfinance doesn't provide quote volume for indices
            })

        return normalized

    async def store(self, good_rows: list[dict]) -> int:
        if not good_rows:
            return 0

  

        stmt = pg_insert(NSEPriceCandles).values(good_rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["instrument_id", "exchange", "timeframe", "candle_time"],
            set_={
                "open_price":  stmt.excluded.open_price,
                "high_price":  stmt.excluded.high_price,
                "low_price":   stmt.excluded.low_price,
                "close_price": stmt.excluded.close_price,
                "volume":      stmt.excluded.volume,
            },
        )
        await self.db.execute(stmt)
        await self.db.commit()

        logger.info(f"Stored {len(good_rows)} NSE candles for instrument_id={self.asset_id}")
        return len(good_rows)


