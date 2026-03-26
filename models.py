from sqlalchemy import Column, Integer, Text, String, DateTime
from database import Base
from datetime import datetime, timezone 

class Document(Base):
  __tablename__ = "document"
  id = Column(Integer, primary_key=True, autoincrement=True)
  text = Column(Text, nullable=False)
  title = Column(String, nullable=False)
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class User(Base):
  __tablename__ = "user" 
  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String, nullable=False, unique=True)
  password = Column(String, nullable=False)

class AIHistory(Base):
  __tablename__ = "ai"
  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String, nullable=False)
  action = Column(String, nullable=False)
  text = Column(String, nullable=False)
  ai_response = Column(String, nullable=False)
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  