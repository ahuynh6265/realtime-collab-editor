from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import AIHistory 
from schemas import AICreate, AIResponse 
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
async def create_response(response_data: AICreate, current_user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)): 
  if response_data.action == "rewrite":
    prompt = f"Rewrite the following and return only one version, do not write any headings: {response_data.text}"
  elif response_data.action == "expand":
    prompt = f"Continue writing from where this leaves off, do not rewrite, only return sentences do not write in any headings: {response_data.text}"
  elif response_data.action == "summarize":
    prompt = f"Summarize the following in one concise paragraph. Do not use markdown. Do not add any headings, titles, or formatting. Return plain text only: {response_data.text}"
  elif response_data.action == "brainstorm": 
    prompt = f"Create a bulleted list of topics that relevant to the text. Do not include any topics that have already been covered.: {response_data.text}"

  response = client.messages.create(
    model = "claude-haiku-4-5-20251001", 
    max_tokens = 1024, 
    messages = [{"role": "user", "content": prompt}]
  )

  #add history check frontend  
  history = AIHistory(username = current_user["username"], action = response_data.action, text = response_data.text, ai_response = response.content[0].text)
  db.add(history)
  db.commit()
  db.refresh(history)

  return AIResponse(text=response.content[0].text)