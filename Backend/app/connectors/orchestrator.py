


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , or_
from app.models.portfolio_auth import Assets
from app.connectors.binance import BinanceConnector
from app.connectors.polygon import PolygonConnector
import logging


logger = logging.getLogger(__name__)

class MarketOrchestrator :
    def __init__(self , db: AsyncSession , timeframe : str) :
        self.db = db
        self.timeframe = timeframe
    
    async def run(self) -> list[dict]:

        # load enabled assets 
        stmt = select(Assets).where(
            Assets.is_active == True ,
            or_(
                Assets.binance_symbol != None,
                Assets.polygon_ticker != None ,
            )

        )
        result = await self.db.execute(stmt)
        assets = result.scalars().all()


        summaries = []

        for asset in assets : 

            try :
                if asset.binance_symbol is not None :
                    connector = BinanceConnector(
                        db = self.db ,
                        asset_id= asset.asset_id,
                        exchange= "AGGREGATED" ,
                        timeframe= self.timeframe , 
                        binance_symbol= asset.binance_symbol,
                    )
                else : 
                    connector = PolygonConnector(
                         db = self.db ,
                        asset_id= asset.asset_id,
                        exchange= "AGGREGATED" ,
                        timeframe= self.timeframe , 
                        polygon_ticker= asset.polygon_ticker,
                    )
                summary = await connector.run()
                summaries.append(summary)
            
            except Exception as e :
                logger.error(f"Failed to run connector for asset {asset.symbol}: {e}")
                summaries.append(
                    {
                        "asset": asset.symbol,
                        "error": str(e),
                        "fetched": 0,
                        "stored": 0,
                        "quarantined": 0, 
                    }
                )

                continue


        return summaries

        

