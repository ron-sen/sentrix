
from pathlib import Path

from fastapi import FastAPI , Request
from app.config import settings
from app.routes import  user 

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(user.router)

@app.get("/")
def root() -> dict :
    return {
        "message" : f"{settings.PROJECT_NAME} backend is local ! HELL YEAHHHH... "
    }