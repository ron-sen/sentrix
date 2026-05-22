
from pydantic import BaseModel , EmailStr , Field , field_validator
from typing import Annotated

class ValidateUser(BaseModel):

    mail : EmailStr
    password: Annotated[str , Field(... , min_length = 8 , max_length= 72)]

    @field_validator("password")
    @classmethod
    def password_validation(cls , v : str) -> str:
        if len(v) < 8 :
            raise ValueError("Must be at least 8 characters long")
        return v 

class CreateUser(BaseModel):
    
    mail : EmailStr
    password: Annotated[str , Field(... , min_length = 8 , max_length= 72)]



