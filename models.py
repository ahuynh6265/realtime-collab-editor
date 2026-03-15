from sqlalchemy import Column, Integer, Text, String
from database import Base

class Document(Base):
  __tablename__ = "document"
  id = Column(Integer, primary_key=True, autoincrement=True)
  text = Column(Text, nullable=False)
  title = Column(String, nullable=False)