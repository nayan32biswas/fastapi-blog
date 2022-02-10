from typing import Optional, List

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
    WebSocket,
    WebSocketDisconnect,
)

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def get_ws_token(websocket: WebSocket, token: Optional[str] = Query(None)):
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return token


@router.websocket("/ws/{client_id}/")
async def websocket_endpoint(
    websocket: WebSocket, client_id: int, token: str = Depends(get_ws_token)
):
    print(f"token: {token}")
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


"""
var ws = new WebSocket("ws://localhost:8000/ws/3/?token=this-is-a-jwt-token");
ws.onmessage = function(event) { console.log(event.data) };
function sendMessage(message) { ws.send(message); }
"""
