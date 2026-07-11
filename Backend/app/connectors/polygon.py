# fetching data 


from app.connectors.base import BaseConnector
from app.config import settings
import httpx
from datetime import datetime , timezone
from typing import Any
import logging

logger = logging.getLogger(__name__)


TIMEFRAME_MAP = {
    "1m" : (1 , "minute"),
    "5m" : (5 , "minute"),
    "15m" : (15 , "minute"),
    "1h" : (1 , "hour"),
    "4h" : (4 , "hour"),
    "1d" : (1 , "day"),
}


class PolygonConnector(BaseConnector):


   
    def __init__(self , db , asset_id , exchange , timeframe , polygon_ticker ):
        super().__init__(db , asset_id , exchange , timeframe)
        self.polygon_ticker = polygon_ticker


    async def fetch( self , start : datetime , end :  datetime) -> Any :

        multiplier , timespan = TIMEFRAME_MAP[self.timeframe]
        start_ms = int(start.timestamp() * 1000)
        end_ms =  int(end.timestamp() *  1000)

        url = (
            f"https://api.polygon.io/v2/aggs/ticker/"
            f"{self.polygon_ticker}/range/"
            f"{multiplier}/{timespan}/"
            f"{start_ms}/{end_ms}"
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url , params={"apiKey": settings.OHLCV})
                response.raise_for_status()
                return response.json()

            
            except httpx.HTTPStatusError as exc :
                logger.error(f"Polygon HTTP error: {exc.response.status_code} for {self.polygon_ticker}")
                raise 
                
            except httpx.RequestError as exc :
                logger.error(f"Polygon network error : {exc}")
                raise 
               

    def normalize(self, raw_data) -> list[dict]:
        
       
        normalized = []

        for item in raw_data["results"]:
           
            normalized.append(
                {
                  "asset_id" : self.asset_id ,
                  "exchange" : self.exchange ,
                  "timeframe" :  self.timeframe ,

                  "candle_time" : datetime.fromtimestamp(item["t"] / 1000, tz=timezone.utc) , 
                  "open_price" : item["o"] ,
                  "close_price" :  item["c"] ,
                  "high_price" : item["h"] ,
                  "low_price" : item["l"] ,
                  "volume" : item["v"] , 
                  "quote_volume" : item.get("vw"), 
                }
            )
        return normalized