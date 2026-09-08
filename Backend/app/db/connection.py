from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

Base = declarative_base()

def get_engine():
    return create_async_engine(settings.DATABASE_URL, echo=False)

# for celery tasks - initializing at module level ,

def get_celery_sessionmaker():

    """creates a fresh engine + sessionmaker bound to whichever event loop is currently running , must be called inside the async functio that async.io()ivokes for a celery task - never at module import time , since aysncpg connections can't cross event loop boundaries"""

    engine = create_async_engine(settings.DATABASE_URL , echo=False)
    session_factory = async_sessionmaker(
        bind = engine ,
        class_ = AsyncSession,
        autoflush= False ,
        expire_on_commit= False,

    )
    return engine , session_factory

AsyncSessionLocal = None

async def get_db():
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            autoflush=False,
            expire_on_commit=False
        )
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()