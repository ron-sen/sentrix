
import asyncio
import logging  # logging module 

from app.celery_app import celery_app
from app.connectors.orchestrator import MarketOrchestrator
from app.db.connection import CelerySessionLocal

logger = logging.getLogger(__name__) # what is __name__ --> built in variable that holds the current module name ,

async def run_market_ingestion(timeframe: str):

    """
    async function that does the work ,  celery task can't be async directly so we separate the async logic here and call it via asyncio.run() from the task written below

    """

    db = CelerySessionLocal()  # creates a fredh asyncsession with db 

    try :
        # creating opensession and target timeframe 
        # orchestrator will load all active assets and run the available connector per asset 

        orchestrator = MarketOrchestrator(
            db = db,
            timeframe = timeframe , 
        )

        # running full pipline with 120 sec timeout , if it hangs longer then 2 minute (netwrok stall , db lock)and kill it 
        # asyncio.wait_ for raises timeouterror if timeout exceeded

        summaries = await asyncio.wait_for(
            orchestrator.run(),
            timeout = 120 ,
        )

        # commits any pending db writes after orchestrator finishes
        await db.commit()
        return summaries

    except Exception:

        # if anything goes wrong , roll back any partial db writes
        # prevents half baked candles rows from corrupting the hypertable

        await db.rollback()
        raise # re-raise so celery task above can handle retry logic

    finally :
        await db.close() #close the session whather sucess or failure 


@celery_app.task(
    bind = True ,  # give task access to self
    name = "fetch_market_data", # excplicit task name  for beat schedule to references
    max_retries = 3 , # retry up to 3 times before giving up 
    default_retry_delay = 30, # wait 30 sec b/w retries 
)

def fetch_market_data(self , timeframe : str) :

    """
    the actual celery task , this is what beat schedules and worker  executes . must be a regular sync function not async because celery workers are sync  , so we bridge sync into async via asyncio.run

    """

    try : 
        logger.info(
            "Market ingestion started",
            extra={
                "task_id" : self.request.id, # id that celery assigns to this task
                "timeframe" : timeframe ,
            },
        )
        # bridge from sync celery  into async 
        # asyncio.run() creates and event loop , and runs the coroutine 

        summaries = asyncio.run(run_market_ingestion(timeframe))

        #split summaries into succedded and failed 
        # orchestrator adds "errors" key to summary dict when a  connector fails 

        failed = [item for item in summaries if item.get("error")]
        succeeded = [item for item in summaries if not item.get("error")]

        # structred result dict and store it in redis , retrivie it by  task id 

        result = {
            "status" : "completed_with_errors" if failed else "completed",
            "task_id" : self.request.id ,
            "timeframe" : timeframe ,
            "assets_processed" : len(succeeded),
            "assets_failed" : len(failed) ,
            "summary" : summaries ,
        }

        logger.info(
            "Market ingestion finished" ,
            extra = {
                "task_id": self.request.id ,
                "timeframe" : timeframe , 
                "assets_processed" : len(succeeded),
                "assets_failed" : len(failed),
            },
        )

        return result

    except asyncio.TimeoutError as exc :

        # orchestrator ran for more than 120 seconds - something  is stuck 
        # log a warning (not error , since we are retrying)  and retry the task

        logger.warning(
            "Market ingestion timed out" ,
            extra={
                "task_id" : self.request.id ,
                "timeframe" : timeframe , 
            },

        )

        raise self.retry(exc=exc) # self.retry() re-queues the task in redis 

    except Exception as exc :

        # any other unexcepted error  - db down , connector crash etc. 
        # log full traceback and retry 

        logger.exception(
            "Market ingestion failed",
            extra = {
                "task_id" : self.request.id ,
                "timeframe" : timeframe ,
            },
        )

        raise self.retry(exc = exc)