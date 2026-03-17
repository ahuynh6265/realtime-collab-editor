from pydantic import BaseModel, ConfigDict

class DocumentUpdate(BaseModel):
  title: str 

class DocumentResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True, populate_by_name=True)

  id: int
  title: str