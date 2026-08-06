
from app.tasks import  fetch_market_data
from fastapi import APIRouter , Response , Request , status , Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.connection import get_db

router = APIRouter(tags=["tasks"])


@router.post(
    "/fetch-market-candles" ,
    status_code= status.HTTP_202_ACCEPTED,
)
async def fetch_market_candles(timeframe : str):

    task = fetch_market_data.delay(timeframe)
    
    return {
        "task_id" : task.id , 
        "status" : "Market ingestion queued" ,
        "timeframe" : timeframe , 
    }
