
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
from app.models.userauth import User


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


    return  create_user_acc


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







