
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indicator import IndicatorValues , SuitabilityScores
from app.services.exception import AssetNotFound
from app.models.portfolio_auth import Assets


class MarketService :

    def __init__(self , db : AsyncSession):
        self.db = db


    async def _ensure_asset_exists(self , asset_id : int ) -> None :
        result = await self.db.execute(select(Assets).where(Assets.asset_id == asset_id))
        if result.scalars().first() is None :
            raise AssetNotFound()

    async def get_indicator_history(self , asset_id : int , limit : int = 50):
        await self._ensure_asset_exists(asset_id)
        stmt = (
            select(IndicatorValues).where(IndicatorValues.asset_id == asset_id).order_by(IndicatorValues.timestamp.desc()).limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def get_suitability_history(self , asset_id : int  , limit : int = 50):
        await self._ensure_asset_exists(asset_id)
        stmt = (
            select(SuitabilityScores).where(SuitabilityScores.asset_id == asset_id).order_by(SuitabilityScores.timestamp.desc()).limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_latest_suitability(self , asset_id : int ):
        await self._ensure_asset_exists(asset_id)
        stmt = (
            select(SuitabilityScores).where(SuitabilityScores.asset_id == asset_id).order_by(SuitabilityScores.timestamp.desc()).limit(1)
        )
        result  = await self.db.execute(stmt)
        latest = result.scalars().first()
        if latest is None :
            raise AssetNotFound()
        return latest 