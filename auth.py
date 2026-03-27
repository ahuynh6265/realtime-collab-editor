from passlib.hash import pbkdf2_sha256 
from jose import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv 
import os 

load_dotenv() 
SECRET_KEY = os.getenv("SECRET_KEY")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(password):
  hash = pbkdf2_sha256.hash(password)
  return hash 

def verify_password(password, hash_password): 
  return pbkdf2_sha256.verify(password, hash_password)

def create_token(username, id):
  token = jwt.encode({"username": username, "id": id}, SECRET_KEY, algorithm="HS256")
  return token

def get_current_user(token: str = Depends(oauth2_scheme)):
  try: 
    current_user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"]) 
  except:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

  return current_user 