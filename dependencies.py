from fastapi import HTTPException, status
from models import Document

def document_lookup(document_id, db, user_id):
  document = db.query(Document).filter(Document.id == document_id).first()
  if not document: 
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Document ID not found") 
  
  if document.owner_id != user_id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action on this document.")
  
  return document