from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import String , Text , INTEGER , ForeignKey , TIMESTAMP , func , Boolean , Date
from app.db.connection import Base
from app.models.portfolio_auth import PortfolioInfo
from datetime import datetime 
from typing import Optional

class User(Base):

    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    mail : Mapped[str] = mapped_column(String(100) , nullable= False)
    hashed_password : Mapped[str] = mapped_column(Text , nullable= False)
    is_verified : Mapped[bool] = mapped_column(Boolean , default=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r} , mail={self.mail!r})"
    
    verification_tokens = relationship("VerificationToken"  , back_populates="user")

    personal_profile = relationship("PersonalProfile" , back_populates="user" )

    portfolios = relationship("PortfolioInfo" , back_populates="user")
   

 # verification table
class VerificationToken(Base):

    __tablename__ = "verification_tokens"

    token_id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id") , nullable= False)
    token : Mapped[str] = mapped_column(Text , nullable=False)
    token_type : Mapped[str] = mapped_column(String(50) , nullable= False)
    used : Mapped[bool] =  mapped_column(Boolean , default=False )
    created_at : Mapped[datetime] = mapped_column(TIMESTAMP , server_default=func.current_timestamp() )
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    
    user = relationship("User" , back_populates="verification_tokens")
    

class PersonalProfile(Base):

    __tablename__ = "personal_profile"

    user_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False , primary_key=True)
    username : Mapped[str] = mapped_column(String(50) , nullable=False ,unique=True  )
    first_name : Mapped[Optional[str]]= mapped_column(String(100))
    last_name : Mapped[Optional[str]] = mapped_column(String(100))
    date_of_birth : Mapped[Optional[Date]] = mapped_column(Date , nullable=False)
    gender : Mapped[Optional[str]] = mapped_column(String(50)) 
    bio : Mapped[Optional[str]] = mapped_column(String)
    profile_picture : Mapped[Optional[str]] = mapped_column(String) 
    city : Mapped[Optional[str]] = mapped_column(String(100))
    state : Mapped[Optional[str]] = mapped_column(String(100))
    country : Mapped[str] = mapped_column(String(100))
    phone_number : Mapped[str] = mapped_column(String(20))
    phone_verified : Mapped[bool] = mapped_column(Boolean , default=False)
    created_at : Mapped[datetime] = mapped_column(TIMESTAMP , server_default=func.current_timestamp())
    updated_at : Mapped[datetime] = mapped_column(TIMESTAMP , server_default=func.current_timestamp() , onupdate=func.current_timestamp())

    user = relationship("User" , back_populates="personal_profile")

