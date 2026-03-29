from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Document, DocumentShare, User
from schemas import DocumentUpdate, DocumentResponse, DocumentShareCreate
import json, connection_manager, auth
from auth_routes import router as auth_router 
from ai_routes import router as ai_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from limiter import limiter

manager = connection_manager.ConnectionManager()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth_router)
app.include_router(ai_router)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.state.limiter = limiter 
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
  CORSMiddleware, 
  allow_origins=["*"],
  allow_methods=["*"],
  allow_headers=["*"], 
)
try:
  Base.metadata.create_all(bind=engine)
except Exception as e:
  print(f"DB init warning: {e}")

def get_db():
  db = SessionLocal()
  try: yield db
  finally: db.close() 


@app.get("/")
def get_landing(): 
  return FileResponse("static/landing.html")

@app.get("/home")
def get_home():
  return FileResponse("static/home.html")

@app.websocket("/ws/{document_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, document_id: int, username: str, db: Session = Depends(get_db)):
  room = db.query(Document).filter(Document.id == document_id).first() 
  if not room: 
    await websocket.close() 
    return 
  await manager.connect(websocket, document_id, username)
  data = {"type": "update", "content": room.text, "title": room.title, "owner": room.owner_id}
  await manager.broadcast_user_only(websocket, data)

  data = {"type": "notification", "message": f"{username} has joined"}
  await manager.broadcast(websocket, document_id, data)

  data = {"type": "users", "users": list(manager.connected_clients[document_id].values())}
  await manager.broadcast_all(document_id, data)

  print(f"{username} connected to room {document_id} total: {len(manager.connected_clients[document_id])}")

  try:
    while True:
      message = await websocket.receive_text()
      data = json.loads(message)

      if data["type"] == "update": 
        content = data["content"]
        data = {"type": "update", "content": content, "title": room.title}
        await manager.broadcast(websocket, document_id, data)
        room.text = content
        db.commit() 

      elif data["type"] == "typing":
        typing = data["typing"]
        data = {"type": "typing", "typing": typing, "username": username}
        await manager.broadcast(websocket, document_id, data)

  except WebSocketDisconnect: 
    pass
  finally:
    data = {"type": "notification", "message": f"{username} has disconnected"}
    await manager.broadcast(websocket, document_id, data)
    manager.disconnect(websocket, document_id)

    data = {"type": "users", "users": list(manager.connected_clients[document_id].values())}
    await manager.broadcast_all(document_id, data)

@app.patch("/documents/{document_id}") 
async def update_doc_name(document_id: int, document_data: DocumentUpdate, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
  document = db.query(Document).filter(Document.id == document_id).first() 
  if not document: 
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document ID not found")
  document.title = document_data.title
  db.commit()
  db.refresh(document)

  data = {"type": "title", "title": document_data.title}
  await manager.broadcast_all(document_id, data)

  return document 

@app.get("/documents", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
  return db.query(Document).order_by(Document.id).filter(Document.owner_id == current_user["id"]).all() 

@app.get("/editor")
def get_editor(): return FileResponse("static/index.html")

@app.post("/documents")
def create_doc(db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
  new_doc = Document(title="Untitled", text = "", owner_id = current_user["id"])
  db.add(new_doc)
  db.commit() 
  db.refresh(new_doc)

  return new_doc.id

@app.get("/documents/shared", response_model=list[DocumentResponse])
def get_shared(db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)):
  documents = db.query(DocumentShare).filter(DocumentShare.user_id == current_user["id"]).all() 

  shared_docs = []

  for document in documents: 
    shared_docs.append(db.query(Document).filter(Document.id == document.document_id).first())
  
  return shared_docs 


@app.post("/documents/{doc_id}/share")
def share_doc(doc_id: int, doc_data: DocumentShareCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.get_current_user)): 
  username = db.query(User).filter(User.username == doc_data.username).first()
  if not username: 
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Username not found")
  
  if username.id == current_user["id"]:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot share the document with yourself")
  
  document_share = DocumentShare(document_id = doc_id, user_id = username.id)
  try:
    db.add(document_share)
    db.commit()
    db.refresh(document_share)
  except IntegrityError:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"The document has already been shared with {doc_data.username}")
  return {"message": "Document shared successfully."}

@app.get("/auth/login")
def get_login(): return FileResponse("static/login.html")

@app.get("/auth/register")
def get_register(): return FileResponse("static/register.html")
