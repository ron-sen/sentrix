
from pydantic import BaseModel , EmailStr , Field , field_validator , ConfigDict  , computed_field
from typing import Annotated , Optional 
from datetime import date 

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


class PersonalProfileValidation(BaseModel):

    username : Annotated[str , Field(..., description= "unique handle" ,min_length=3 , max_length=50)]
    first_name : Annotated[str , Field(..., description="could be repeated" , min_length=0 , max_length=100)]
    last_name : Optional[str] = Field(None , description="could still work" ,
    min_length=0 , max_length=100 )

    date_of_birth : date = Field(..., description="required")

    gender : Optional[str] = Field(None , description="preference dependent")
    bio : Optional[str] = Field(None , description="can be none")
    profile_picture : Optional[str] = Field(None , description="preference  dependent")

    city :  Annotated[str , Field(..., description="could be repeated" , min_length=1 , max_length=100)]
    state :  Annotated[str , Field(..., description="could be repeated" , min_length=1 , max_length=100)]
    country :  Annotated[str , Field(..., description="could be repeated" , min_length=1 , max_length=100)]
    phone_number :  Annotated[str , Field(..., description="unique handle needs to be verified " , min_length=1 , max_length=20)]

    @field_validator("date_of_birth")
    @classmethod
    def valdiate_age(cls , dob : date):
        today = date.today()
        age = today.year - dob.year - ((today.month , today.day) < (dob.month , dob.day))

        if age <= 10 or age >=120 :
            raise ValueError("Age must be greater then 10 and less then 120")
        
        return dob
    


    class PersonalProfileResponse(BaseModel):
        username : str
        first_name : Optional[str]
        last_name : Optional[str]
        date_of_birth : Optional[date]
        age : Optional[str]
        gender : Optional[str]
        bio : Optional[str]
        profile_picture : Optional[str]
        city : Optional[str]
        state : Optional[str]
        country : Optional[str]

        model_config = ConfigDict(from_attributes = True)

        @computed_field
        @property
        def age(self) -> Optional[int]:
            if self.date_of_birth:
                today = date.today()
                return today.year - self.date_of_birth.year - (
                    (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
                )
            return None





