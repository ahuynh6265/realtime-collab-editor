from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone 

class Document(Base):
  __tablename__ = "document"
  id = Column(Integer, primary_key=True, autoincrement=True)
  text = Column(Text, nullable=False)
  title = Column(String, nullable=False)
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

  ai_history = relationship("AIHistory", back_populates="document", cascade="all, delete")

class User(Base):
  __tablename__ = "user" 
  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String, nullable=False, unique=True)
  password = Column(String, nullable=False)

class AIHistory(Base):
  __tablename__ = "ai"
  id = Column(Integer, primary_key=True, autoincrement=True)
  document_id = Column(Integer, ForeignKey("document.id"), nullable=False)
  username = Column(String, nullable=False)
  action = Column(String, nullable=False)
  text = Column(String, nullable=False)
  ai_response = Column(String, nullable=False)
  created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
  
  document = relationship("Document", back_populates="ai_history")