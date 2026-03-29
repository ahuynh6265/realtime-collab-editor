from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session 
from database import SessionLocal
from models import User 
from schemas import UserCreate, UserLogin, UserResponse 
import auth 



router = APIRouter()

def get_db():
  db =  SessionLocal()
  try: yield db
  finally: db.close()

@router.post("/auth/register", response_model=UserResponse) 
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
  user = db.query(User).filter(user_data.username == User.username).first() 
  if user: 
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username taken")
  user = User(username = user_data.username, password = auth.hash_password(user_data.password))
  db.add(user)
  db.commit()
  db.refresh(user)
  return user 

@router.post("/auth/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)): 
  user = db.query(User).filter(user_data.username == User.username).first()
  if user: 
    if auth.verify_password(user_data.password, user.password):
      token = auth.create_token(user_data.username, user.id)
      return token 
    else: 
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password incorrect.")
    
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or password incorrect.")


@router.get("/auth/me")
def get_username(db: Session = Depends(get_db), token: str = Depends(auth.get_current_user)):
  username = db.query(User).filter(User.username == token["username"]).first() 
  return username.username 