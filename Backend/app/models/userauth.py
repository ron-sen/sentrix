from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import String , Text , INTEGER , ForeignKey , TIMESTAMP , func , Boolean
from app.db.connection import Base
from datetime import datetime

class User(Base):

    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    mail : Mapped[str] = mapped_column(String(100) , nullable= False)
    hashed_password : Mapped[str] = mapped_column(Text , nullable= False)
    is_verified : Mapped[bool] = mapped_column(Boolean , default=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r} , mail={self.mail!r})"
    
    verification_tokens = relationship("VerificationToken"  , back_populates="user")

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
    

