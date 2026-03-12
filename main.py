from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Document


connected_clients = {}

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

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
def get_static(): return FileResponse("static/index.html")

@app.websocket("/ws/{document_id}/{username}")
async def websocket_endpoint(websocket: WebSocket, document_id: int, username: str, db: Session = Depends(get_db)):
  await websocket.accept() 

  room = db.query(Document).filter(Document.id == document_id).first() 
  connected_clients.setdefault(document_id, {})
  if not room: 
    room = Document(text = "")
    db.add(room)
    db.commit() 
  await websocket.send_text(room.text)

  connected_clients[document_id][websocket] = username
  print(f"{username} connected to room {document_id} total: {len(connected_clients[document_id])}")

  try:
    while True:
      message = await websocket.receive_text()
      for client in connected_clients[document_id].keys():
        if client != websocket: 
          await client.send_text(message)
      room.text = message
      db.commit() 
  except WebSocketDisconnect: 
    pass
  finally:
    del connected_clients[document_id][websocket]