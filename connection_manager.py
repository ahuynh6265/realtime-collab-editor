import json

class ConnectionManager:
  def __init__(self): 
    self.connected_clients = {}

  async def connect(self, websocket, document_id, username):
    await websocket.accept() 
    self.connected_clients.setdefault(document_id, {})
    self.connected_clients[document_id][websocket] = username
  
  def disconnect(self, websocket, document_id):
    del self.connected_clients[document_id][websocket]
  
  async def broadcast(self, websocket, document_id, data):
    for client in self.connected_clients[document_id].keys():
      if client != websocket:
        try: 
          await client.send_text(json.dumps(data))
        except RuntimeError:
          pass
  
  async def broadcast_all(self, document_id, data):
    for client in self.connected_clients[document_id].keys():
      try: 
        await client.send_text(json.dumps(data))
      except RuntimeError:
        pass
  
  async def broadcast_user_only(self, websocket, data):
    try: 
      await websocket.send_text(json.dumps(data))
    except RuntimeError:
      pass