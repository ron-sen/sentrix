
# utility function to hash password
# for verfying password match the hashed stored
# authenticate and return user

from datetime import datetime , timedelta , timezone
import jwt
from passlib.context import CryptContext
from app.config import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends , HTTPException , status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.models.userauth import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "signin")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")

def get_password_hash(password : str):
    return pwd_context.hash(password)

def verify_password(plain_password : str, hashed_password : str):
    return pwd_context.verify(plain_password , hashed_password)

TOKEN_EXPIRY = 30
REFRESH_TOKEN_EXPIRY = 60 * 24 * 7

def create_access_token(data : dict):
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode , settings.SECRET_KEY , algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_refresh_token(data : dict):
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRY)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode , settings.SECRET_KEY , algorithm=settings.ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme) , db : AsyncSession = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED , 
        detail="Could not validate credentials",
        headers={"www-Authenticate": "Bearer"}
    )
    try :
        paylaod = jwt.decode(token , settings.SECRET_KEY , algorithms=[settings.ALGORITHM])
        email : str = paylaod.get("sub")
        if email is None :
            raise credential_exception
    except jwt.InvalidTokenError:
        raise credential_exception

    result = await db.execute(select(User).where(User.mail == email)) 
    user =result.scalars().first()
    if user is None :
        raise credential_exception
    return user


    



