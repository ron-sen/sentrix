
from typing import Generic , TypeVar

from pydantic import BaseModel , Field 
from pydantic.generics import GenericModel
from sqlalchemy.orm import Session
from sqlalchemy.sql import select 

from app.db.connection import get_db

T = TypeVar("T" , bound = get_db)

class PaginationInput(BaseModel):

    pass