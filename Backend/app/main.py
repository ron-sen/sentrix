
from pathlib import Path

from fastapi import FastAPI , Request 
from fastapi.responses import JSONResponse
from app.config import settings
from app.routes import  user  , portfolio_routes
from app.services.exception import AppError

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(user.router)
app.include_router(portfolio_routes.router)

@app.get("/")
def root() -> dict :
    return {
        "message" : f"{settings.PROJECT_NAME} backend is local ! HELL YEAHHHH... "
    }


@app.exception_handler(AppError)
async def app_error_handler(request : Request , exc : AppError):
    return JSONResponse(status_code =exc.status_code ,content = {"detail"  : exc.detail})