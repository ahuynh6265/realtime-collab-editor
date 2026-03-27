from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
class DocumentUpdate(BaseModel):
  title: str 

class DocumentResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  owner_id: int 
  title: str
  created_at: datetime 
  updated_at: datetime

class DocumentShareCreate(BaseModel):
  username: str

class UserCreate(BaseModel): 
  username: str 
  password: str 

  @field_validator("username")
  @classmethod 
  def check_username(cls, value: str) -> str:
    if len(value) < 1:
      raise ValueError("Username can't be left empty.")
    return value

  @field_validator("password")
  @classmethod 
  def check_password(cls, value: str) -> str:
    if len(value) < 8: 
      raise ValueError("Password must be at least 8 characters.")
    return value

class UserLogin(BaseModel): 
  username: str
  password: str 

class UserResponse(BaseModel): 
  model_config = ConfigDict(from_attributes=True)

  id: int 
  username: str

class AICreate(BaseModel): 
  action: str 
  text: str 

class AIResponse(BaseModel): 
  text: str 

class AIHistoryCreate(BaseModel):
  document_id: int 
  action: str
  text: str 
  ai_response: str 

class AIHistoryResponse(BaseModel): 
  model_config = ConfigDict(from_attributes=True)

  id: int 
  document_id: int
  username: str 
  action: str 
  text: str 
  ai_response: str 
  created_at: datetime 

