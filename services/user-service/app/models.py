from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True,index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True,index=True)
    password_hash=Column(String)
