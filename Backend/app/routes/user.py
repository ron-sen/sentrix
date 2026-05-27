
from fastapi import APIRouter , Depends , HTTPException , Response , status , Request , Cookie
from typing import Annotated
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.schemas.uservalidate import ValidateUser , CreateUser , PersonalProfileValidation  ,  PersonalProfileResponse , PersonalProfileUpdate

from fastapi.security import OAuth2PasswordRequestForm
from app.security.jwtsecure import verify_password , create_access_token , create_refresh_token , get_password_hash , get_current_user

#from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
import jwt

from app.config import Settings
from datetime import timedelta
from app.models.userauth import User , VerificationToken , PersonalProfile
from datetime import datetime

from app.security.mail import send_verification_Email
from app.security.token import secret_token , token_expiry

router = APIRouter()


@router.get("/users")
def get_users(db : Session = Depends(get_db)):
    return db.query(User).all()



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
    user = db.query(User).filter(User.mail == form_data.username).first()

    if not user or not verify_password(form_data.password , user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED ,
            detail="Incorrect mail or password" ,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # JWT

    access_token = create_access_token(data= {"sub": user.mail})
    refresh_token = create_refresh_token(data= {"sub": user.mail})

    # cookies

    response.set_cookie(
        key = "access_token" ,
        value = access_token ,
        httponly = True , 
        samesite = "lax" ,
        secure = True 
    )

    response.set_cookie(
        key = "refresh_token" ,
        value = refresh_token ,
        httponly = True ,
        samesite = "lax" ,
        secure = True 
    )

    return{
        "message" : "Logged in sucessfull",
        "access_token" : access_token ,
        "refresh_token" : refresh_token ,
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
    token_verify.used = True
    db.commit()
    return{
        "message":"Email verified successfully"
    }


@router.post("/perosnal-profile" , status_code=status.HTTP_200_OK)
async def create_personal_user_profile(
    response : Response ,
    profile : PersonalProfileValidation ,
    db : Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    
    exisiting = db.query(PersonalProfile).filter(PersonalProfile.user_id == current_user.id).first()

    if exisiting:
        return exisiting 
    else :
             
        new_profile = PersonalProfile(
        
        user_id = current_user.id ,
        username = profile.username,
        first_name = profile.first_name,
        last_name = profile.last_name,
        date_of_birth = profile.date_of_birth,
        gender = profile.gender,
        bio = profile.bio,
        profile_picture = profile.profile_picture, # it would be url this url will be from frontend img upload , so this field will be from user but from frontend , 
        city = profile.city,
        state = profile.state,
        country = profile.country ,
        phone_number = profile.phone_number

    )
   

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {
        "message" : "Profile created sucessfully"
    }

@router.get("/personal-profile" , status_code=status.HTTP_202_ACCEPTED)
async def getting_personal_profile( 
    response : Response,
    db : Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    
    profile  = db.query(PersonalProfile).filter(PersonalProfile.user_id == current_user.id).first()
    
    if not profile :
        raise HTTPException(
            status_code = 404 , detail = "profile not found"
        )
    return profile


@router.post("/refresh")
async def refresh_token(
    response : Response ,
    refresh_token : str = Cookie(None)
):
    if not refresh_token:
        raise HTTPException(
            status_code=401 , detail= "No refresh token"
        )
    try :
        payload = jwt.decode(refresh_token, Settings.SECRET_KEY , algorithms= [Settings.ALGORITHM])
        email = payload.get("sub")

        if email is None :
            raise HTTPException(status_code=401 , detail= "Invalid refresh token")
    except jwt.InvalidTokenError :
        raise HTTPException(status_code=401 , detail = "Invalid refresh token")
    
    #creating new access token 

    new_access_token = create_access_token(
        data={
            "sub": email
        }
    )

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True , 
        secure = True ,
        samesite= "lax"
    )

    return {
        "message":"Access token refreshed "
    }


@router.post("/signout" , status_code=status.HTTP_200_OK)
async def signout(response : Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {
        "message":"Logged out successfully"
    }


@router.patch("/personal-profile")
async def update_personal_profile(
    profile_update : PersonalProfileUpdate ,
    db : Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    profile  = db.query(PersonalProfile).filter(PersonalProfile.user_id == current_user.id).first()

    update_data = profile_update.model_dump(exclude_unset=True)

    if not profile :
        raise HTTPException(
            status_code= 404 ,  detail = "profile not found"
        )
    else :
        for field , value  in update_data.items():
            setattr(profile , field , value )

            update_profile = PersonalProfileUpdate(

        username = profile.username,
        first_name = profile.first_name,
        last_name = profile.last_name,
        date_of_birth = profile.date_of_birth,
        gender = profile.gender,
        bio = profile.bio,
        profile_picture = profile.profile_picture, # it would be url this url will be from frontend img upload , so this field will be from user but from frontend , 
        city = profile.city,
        state = profile.state,
        country = profile.country ,
        phone_number = profile.phone_number

    )
            
            db.add(update_profile)
            db.commit()
            db.refresh(update_profile)


    return{
        "message": "Profile updated sucessfully "
    }







