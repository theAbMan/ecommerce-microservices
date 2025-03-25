from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .database import SessionLocal
from .models import User
from pydantic import BaseModel
from jose import jwt, JWTError
import datetime
import os

router = APIRouter()

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    username:str
    email:str
    password:str

class UserLogin(BaseModel):
    username:str
    password:str

@router.post("/signup")
def signup(user: UserCreate,db:Session=Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message":"User Created successfully"}


@router.post("/login")
def login(user:UserLogin,db:Session=Depends(get_db)):
    db_user = db.query(User).filter(User.username==user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    
    token = jwt.encode({"sub":db_user.username,"exp":datetime.datetime.utcnow()+datetime.timedelta(hours=1)},SECRET_KEY,algorithm=ALGORITHM)

    return {"access_token":token,"token_type":"bearer"}


@router.get("/verify-token")
def verify_token(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Token")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"username":payload.get("sub")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")