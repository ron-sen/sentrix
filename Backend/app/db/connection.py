from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
from app.config import settings

Base = declarative_base()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker( autoflush= False , bind = engine)

def get_db():
    db = SessionLocal()
    try :
        yield db
    finally :
        db.close()

        