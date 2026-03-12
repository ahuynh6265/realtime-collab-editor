from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Document
import json

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
  data = {"type": "update", "content": room.text}
  await websocket.send_text(json.dumps(data))

  connected_clients[document_id][websocket] = username
  data = {"type": "notification", "message": f"{username} has joined"}
  for client in connected_clients[document_id].keys():
    if client != websocket:
      await client.send_text(json.dumps(data))

  data = {"type": "users", "users": list(connected_clients[document_id].values())}
  for client in connected_clients[document_id].keys():
    await client.send_text(json.dumps(data))

  print(f"{username} connected to room {document_id} total: {len(connected_clients[document_id])}")

  try:
    while True:
      message = await websocket.receive_text()
      data = {"type": "update", "content": message}
      for client in connected_clients[document_id].keys():
        if client != websocket: 
          await client.send_text(json.dumps(data))
      room.text = message
      db.commit() 
  except WebSocketDisconnect: 
    pass
  finally:
    data = {"type": "notification", "message": f"{username} has disconnected"}
    for client in connected_clients[document_id].keys():
      if client != websocket:
        await client.send_text(json.dumps(data))
    
    del connected_clients[document_id][websocket]

    data = {"type": "users", "users": list(connected_clients[document_id].values())}
    for client in connected_clients[document_id].keys():
      await client.send_text(json.dumps(data))