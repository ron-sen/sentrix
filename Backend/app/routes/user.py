
from fastapi import APIRouter , Depends , HTTPException , Response , status , Request , Cookie
from typing import Annotated
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.schemas.uservalidate import ValidateUser , CreateUser

from fastapi.security import OAuth2PasswordRequestForm
from app.security.jwtsecure import verify_password , create_access_token , get_password_hash

#from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from jose import jwt , JWTError

from app.config import Settings
from datetime import timedelta
from app.models.userauth import User , VerificationToken
from datetime import datetime

from app.security.mail import send_verification_Email
from app.security.token import secret_token , token_expiry

router = APIRouter()


@router.get("/users")
def get_users(db : Session = Depends(get_db)):
    return db.query(User).all



@router.post("/signup" , status_code=status.HTTP_201_CREATED)
async def create_user_acc(user : CreateUser  , db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.mail == user.mail).first()

    if existing_user :
        raise HTTPException(status_code=409 , detail = "User already registered")
    else:
        new_user = User(

            mail = user.mail ,
            hashed_password  = get_password_hash(user.password)       
             
     )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token =  secret_token()
    expiry = token_expiry()

    verification_token = VerificationToken(
        user_id = new_user.id ,
        token = token ,
        token_type = "email verification",
        expires_at = expiry
    )
    db.add(verification_token)
    db.commit()
    await send_verification_Email(user.mail, token)


    return  {
        "message": "User registered sucessfully ! "
    }


@router.post("/signin" , status_code=status.HTTP_202_ACCEPTED)
async def signin_for_access_token(
    response : Response ,
    form_data : Annotated[OAuth2PasswordRequestForm , Depends()],
    db : Session = Depends(get_db)
):
    user = db.query(User).filter(User.mail == form_data.password).first()

    if not user or not verify_password(form_data.password , user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED ,
            detail="Incorrect mail or password" ,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # JWT

    access_token = create_access_token(data= {"sub": user.mail})

    # cookies

    response.set_cookie(
        key = "access_token" ,
        value = access_token ,
        httponly = True , 
        samesite = "lax" ,
        secure = True 
    )

    return{
        "message" : "Logged in sucessfull",
        "access_token" : access_token ,
        "token_type" : "bearer"
    }


@router.get("/verify" , status_code=status.HTTP_200_OK)
async def verify_email(token : str , response : Response , db : Session = Depends(get_db)):

    token_verify = db.query(VerificationToken).filter(VerificationToken.token == token).first()

    if not token_verify :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    if token_verify.used == True:
        raise HTTPException(status_code=400, detail="Token already used")

    if token_verify.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")
    
    user = db.query(User).filter(User.id == token_verify.user_id).first()

    user.is_verified = True 
    db.commit()
    return{
        "message":"Email verified successfully"
    }

    


