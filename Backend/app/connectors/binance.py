
from app.connectors.base import BaseConnector
from app.config import settings
import httpx
from datetime import datetime , timezone 
from typing import Any
import logging


logger = logging.getLogger(__name__)

BINANCE_URL = "https://api.binance.com/api/v3/klines"

class BinanceConnector(BaseConnector):


    def __init__(self, db, asset_id, exchange, timeframe , binance_symbol):
        super().__init__(db, asset_id, exchange, timeframe )
        self.binance_symbol = binance_symbol



    async def fetch(self , start : datetime , end : datetime) -> Any :

        start_ms = int(start.timestamp() * 1000)
        end_ms = int(end.timestamp() * 1000)

        params = {
            "symbol": self.binance_symbol ,
            "interval": self.timeframe,
            "startTime": start_ms,
            "endTime": end_ms,
            "limit": 1000,
        }

        async with httpx.AsyncClient(timeout=10.0) as client : 
            try :
                response = await client.get(BINANCE_URL , params=params)
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as exc :
                logger.error(
                    f"Binance HTTP error: {exc.response.status_code} "
                    f"for {self.binance_symbol}"
                )
                raise

            except httpx.RequestError as exc :
                logger.error(f"Binance network error : {exc}")
                raise 


    def normalize(self, raw_data) -> list[dict] :
        
       
        normalized = []

        for item in raw_data :

                       normalized.append(
                {
                    "asset_id": self.asset_id,
                    "exchange": self.exchange,
                    "timeframe": self.timeframe,

                    "candle_time": datetime.fromtimestamp(
                        item[0] / 1000,
                        tz=timezone.utc,
                    ),

                    "open_price": item[1],
                    "high_price": item[2],
                    "low_price": item[3],
                    "close_price": item[4],

                    "volume": item[5],
                    "quote_volume": item[7],
                }
            )

        return normalized

            
    
            



             
