from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi import Request

from celery_tasks.tasks import process_message_task

import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: int):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send(self, message: str, client_id: int):
        ws = self.active_connections.get(client_id)
        if ws:
            await ws.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Envío inmediato del eco o feedback al usuario
            await manager.send(json.dumps({
                "type": "user",
                "message": data
            }), client_id)
            # Lanzar tarea asíncrona a Celery, pasándole client_id
            process_message_task.delay(data, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.post("/webhook/task-complete")
async def task_complete(payload: dict):
    """
    Endpoint que consume el webhook de Celery cuando termina la tarea.
    Esperamos un JSON con { "client_id": <int>, "response": <str> }
    """
    client_id = payload["client_id"]
    bot_response = payload["response"]
    # Reenvío al cliente
    await manager.send(json.dumps({
        "type": "bot",
        "message": bot_response
    }), client_id)
    return {"status": "ok"}