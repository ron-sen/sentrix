from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import String , Text
from app.db.connection import Base

class User(Base):

    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    mail : Mapped[int] = mapped_column(String(100) , nullable= False)
    hashed_password : Mapped[str] = mapped_column(Text , nullable= False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r} , mail={self.mail!r})"