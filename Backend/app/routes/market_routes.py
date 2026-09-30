
from fastapi import APIRouter , Depends , status 
from sqlalchemy.ext.asyncio import  AsyncSession

from app.db.connection import get_db
from app.security.jwtsecure import get_current_user
from app.services.market_service import MarketService
from app.schemas.market_validation import IndicatorValueResponse , SuitabilityResponse

router = APIRouter(tags=["Market Analysis"])

@router.get(
    "/assets/{asset_id}/indicators",
    response_model= list[IndicatorValueResponse],
    status_code= status.HTTP_200_OK ,
)

async def get_indicators(
    asset_id : int , 
    limit : int = 50 ,
    db : AsyncSession = Depends(get_db) ,
    current_user = Depends(get_current_user),
):
    service = MarketService(db)
    return await service.get_indicator_history(asset_id , limit)

@router.get(
    "/assets/{asset_id}/suitability",
    response_model= list[SuitabilityResponse],
    status_code= status.HTTP_200_OK,
)

async def get_suitability_history(
    asset_id : int , 
    limit : int = 50 , 
    db : AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):

    service = MarketService(db)
    return await service.get_suitability_history(asset_id , limit)

@router.get(
    "/assets/{asset_id}/suitability/latest",
    response_model= SuitabilityResponse , 
    status_code= status.HTTP_200_OK ,
)
async def get_latest_suitability(
    asset_id : int ,
    db : AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    service = MarketService(db)
    return await service.get_latest_suitability(asset_id)