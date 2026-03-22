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