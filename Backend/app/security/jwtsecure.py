
# utility function to hash password
# for verfying password match the hashed stored
# authenticate and return user

from datetime import datetime , timedelta , timezone
import jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")

def get_password_hash(password : str):
    return pwd_context.hash(password)

def verify_password(plain_password : str, hashed_password : str):
    return pwd_context.verify(plain_password , hashed_password)

TOKEN_EXPIRY = 30

def create_access_token(data : dict):
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode , settings.SECRET_KEY , algorithm=settings.ALGORITHM)

    return encoded_jwt
