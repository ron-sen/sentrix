from typing import List

from fastapi import BackgroundTasks , FastAPI
from fastapi_mail import ConnectionConfig , FastMail , MessageSchema , MessageType , NameEmail 
from pydantic import BaseModel , EmailStr
from app.config import settings


class EmailSchema(BaseModel):
    email : List[NameEmail] 

conf = ConnectionConfig(
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_USERNAME = settings.MAIL_USERNAME ,
    MAIL_PASSWORD = settings.MAIL_PASSWORD ,
    MAIL_FROM = settings.MAIL_FROM ,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True , 
    TIMEOUT = 60
)


async def send_verification_Email(email : str , token : str ):

    message = MessageSchema(
        subject="mail-verification",
        recipients = [email] ,
        body = f"<p>Click to verify: http://localhost:8000/verify?token={token}</p>",
        subtype = MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)