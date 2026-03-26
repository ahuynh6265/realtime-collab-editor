from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
class DocumentUpdate(BaseModel):
  title: str 

class DocumentResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  title: str
  created_at: datetime 
  updated_at: datetime

class UserCreate(BaseModel): 
  username: str = Field(min_length=1)
  password: str 

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