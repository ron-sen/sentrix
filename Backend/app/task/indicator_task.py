
import asyncio
import logging


from sqlalchemy import select

from app.celery_app import celery_app
import app.models 
from app.db.connection import get_celery_sessionmaker
from app.ml.indicators.engine import IndicatorEngine
from app.models.portfolio_auth import Assets

logger = logging.getLogger(__name__)

async def run_indicator_computation(exchange : str , timeframe : str):

    """fetch all active assets and compute+store indicators for each one."""

    engine , session_factory = get_celery_sessionmaker()
    async with session_factory() as db:
        try:
            result = await db.execute(select(Assets).where(Assets.is_active == True))
            active_assets = result.scalars ().all()

            engine_obj = IndicatorEngine(db_session= db)
            summaries = []

            for asset in active_assets:
                try:
                    await engine_obj.process_asset(
                        asset_id=asset.asset_id , exchange=exchange , timeframe= timeframe
                    )
                    summaries.append({ "asset_id" : asset.asset_id , "error" : None})
                except Exception as exc :
                    # one bad asset shouldn't killl the while batch
                    logger.exception(f"Indicator computation failed for asset_id = { asset.asset_id}")
                    summaries.append({"asset_id": asset.asset_id , "error": str(exc)})
            return summaries
        except Exception:
            await db.rollback()
            raise

        finally:
            await db.close()
            await engine.dispose()

@celery_app.task(
    bind = True ,
    name = "app.tasks.compute_indicators",
    max_retries = 3 ,
    default_retry_delay = 30 ,
)
def compute_indicators(self ,exchange : str = "AGGREGATED" , timeframe : str = "1m"):
    """celery tasks: compute and presist all 10 indicators + signals for every a active asset."""

    try:
        logger.info(
            "Indicator computation started",
            extra={"task_id" : self.request.id , "timeframe" : timeframe},
        )

        summaries = asyncio.run(run_indicator_computation(exchange , timeframe))

        failed = [item for item in summaries if item.get("error")]
        succeeded = [item for item in summaries if not item.get("error")]

        result = {
            "status": "completed_with_errors" if failed else "completed",
            "task_id" : self.request.id ,
            "timeframe": timeframe ,
            "assets_processed" : len(succeeded),
            "assets_failed" : len(failed),
            "summary" : summaries,
        }

        logger.info(
            "indicator computation finished",
            extra = {
                "task_id" : self.request.id ,
                "assets_processed" : len(succeeded),
                "assets_failed" : len(failed),
            },
        )

        return result
    except Exception as exc :
        logger.exception("Indicator computation task faile" , extra = {"task_id": self.request.id})
        raise self.retry(exc = exc)

    
    