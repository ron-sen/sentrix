"""
celery task for computing fuzzy suitability scores. reads RSI , PPO , ATR history from indicator_values , runs the fuzzye engine , writes the score + input to suitability_scores , chained to run after compute_indicators  , since it depends on fresh indicator data .

"""


import asyncio
import logging

import pandas as pd
from sqlalchemy import select
from app.celery_app import celery_app
import app.models
from app.db.connection import get_celery_sessionmaker
from app.ml.fuzzy.engine import compute_suitability
from app.models.portfolio_auth import Assets
from app.models.indicator import IndicatorValues , SuitabilityScores
from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)

MIN_HISTORY_ROWS = 30 # matches calibrate quantile bounds minimum


async def run_fuzzy_computation():

    """fetch rsi , ppo , atr history for every active asset , compute suitability , persist."""

    engine , session_factory = get_celery_sessionmaker()

    async with session_factory() as db:
        try :
            result = await db.execute(select(Assets).where(Assets.is_active== True))
            active_assets = result.scalars().all()

            summaries = []

            for asset in active_assets:
                try :
                    stmt = (
                        select(IndicatorValues).where(IndicatorValues.asset_id == asset.asset_id).order_by(IndicatorValues.timestamp.desc()).limit(200) # a bit above min_history_rows for headroom
                    )
                    rows_result = await db.execute(stmt)
                    rows = rows_result.scalars().all()

                    if len(rows) < MIN_HISTORY_ROWS :
                        summaries.append({
                            "asset_id" : asset.asset_id,
                            "error" : f"insufficient history ({len(rows)} , need {MIN_HISTORY_ROWS})",
                        })

                        continue

                    # rows com back newest -fist ; reverse for chronological order
                    rows = list(reversed(rows))

                    rsi_history = pd.Series([float(r.rsi) for r in rows if r.rsi is not None ])
                    ppo_history = pd.Series([float(r.ppo) for r in rows if r.ppo is not None])
                    atr_history = pd.Series([float(r.atr) for r in rows if r.atr is not None])

                    latest = rows[-1]
                    if latest.rsi is None or latest.ppo is None  or latest.atr is None :
                        summaries.append({
                            "asset_id" : asset.asset_id,
                            "error" : "latest row missing rsi/ppo/atr",
                        })
                        continue

                    result_dict = compute_suitability(
                        asset_id= asset.asset_id,
                        rsi_history=rsi_history,
                        ppo_history=ppo_history,
                        atr_history=atr_history,
                        current_rsi=float(latest.rsi),
                        current_ppo = float(latest.ppo),
                        current_atr = float(latest.atr),
                    )

                    payload = {
                        "asset_id" : asset.asset_id,
                        "timestamp" : latest.timestamp ,
                        "suitability_score" : result_dict["suitability_score"],
                        "rsi_input" : float(latest.rsi),
                        "ppo_input" : float(latest.ppo),
                        "atr_input" : float(latest.atr),
                    }

                    stmt = insert(SuitabilityScores).values(**payload)
                    update_dict = {k: v for k ,v in payload.items() if k not in("asset_id" , "timestamp")}
                    stmt = stmt.on_conflict_do_update(
                        index_elements = ["asset_id" ,  "timestamp"] , set_ = update_dict
                    )

                    await db.execute(stmt)

                    summaries.append({"asset_id" : asset.asset_id , "error" : None})

                except Exception as exc:
                    logger.exception(f"Fuzzy computation failed for asset_id = {asset.asset_id}")
                    summaries.append({"asset_id" : asset.asset_id , "error" :str(exc)})
            await db.commit()
            return summaries

        except Exception:
            await db.rollback()
            raise
        finally :
            await db.close()
            await engine.dispose()

@celery_app.task(
    bind = True,
    name = "app.task.compute_suitability" , 
    max_retries = 3,
    default_retry_delay = 30 ,
)
def compute_suitability_task(self):

    """ celery task : compute and persist fuzzy suitability scores for every active"""

    try : 
        logger.info("Fuzzy suitability computation started" , extra = {"task_id": self.request.id})

        summaries = asyncio.run(run_fuzzy_computation())

        failed = [item for item in summaries if item.get("error")]
        succeeded = [item for item in summaries if not item.get("error")]

        result = {
            "status" : "completed_with_errors" if failed else "completed",
            "task_id" : self.request.id ,
            "assets_processed" : len(succeeded),
            "assets_failed" : len(failed),
            "summary" : summaries , 
        }

        logger.info(
            "Fuzzy suitability computation finished",
            extra = {"task_id" : self.request.id , "assets_processed" : len(succeeded) , "asset_failed" : len(failed)},
        )

        return result

    except Exception as exc :
        logger.exception("Fuzzy suitability task failed" , extra = { "task_id" : self.request.id})
        raise self.retry(exc = exc)
