from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import AIHistory, Document 
from schemas import AICreate, AIResponse, AIHistoryCreate, AIHistoryResponse
from dotenv import load_dotenv 
import anthropic, os, auth

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
router = APIRouter() 

def get_db():
  db =  SessionLocal() 
  try: yield db
  finally: db.close() 

@router.post("/ai/assist", response_model=AIResponse)
async def create_response(response_data: AICreate, current_user: dict = Depends(auth.get_current_user)): 
  if response_data.action == "rewrite":
    prompt = f"Rewrite the following and return only one version, do not write any headings: {response_data.text}"
  elif response_data.action == "expand":
    prompt = f"Continue writing from where this leaves off, do not rewrite, only return sentences do not write in any headings: {response_data.text}"
  elif response_data.action == "summarize":
    prompt = f"Summarize the following in one concise paragraph. Do not use markdown. Do not add any headings, titles, or formatting. Return plain text only: {response_data.text}"
  elif response_data.action == "brainstorm": 
    prompt = f"Create a bulleted list of topics that are relevant to the text. Do not include any topics that have already been covered.: {response_data.text}"
  else:
    raise HTTPException(status_code=404, detail="Command not found")

  response = client.messages.create(
    model = "claude-haiku-4-5-20251001", 
    max_tokens = 1024, 
    messages = [{"role": "user", "content": prompt}]
  )

  return AIResponse(text=response.content[0].text)

@router.post("/ai/history")
async def save_accepted_response(response_data: AIHistoryCreate, current_user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
  history = AIHistory(document_id = response_data.document_id, username = current_user["username"], action = response_data.action, text = response_data.text, ai_response = response_data.ai_response)
  db.add(history)
  db.commit()
  db.refresh(history)

  return {"status": "saved"}

@router.get("/ai/history/{document_id}", response_model=list[AIHistoryResponse])
def document_history(document_id: int, current_user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
  document = db.query(Document).filter(Document.id == document_id).first() 
  if not document: 
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document ID not found")
  return document.ai_history 