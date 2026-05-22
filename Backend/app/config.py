import os
from pathlib import Path
from  dotenv import load_dotenv
load_dotenv()
class Settings:

    PROJECT_NAME : str = "Sentrix"

    SECRET_KEY : str = os.getenv("SECRET_KEY" , "temporary_low_security_key")
    ALGORITHM : str = os.getenv("ALGORITHM" , "HS256")
    DATABASE_URL : str = os.getenv("DATABASE_URL")


settings = Settings()