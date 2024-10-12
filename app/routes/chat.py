from typing import List

from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.database import get_db
from app.models.session import Session
from app.services.chat_services import ChatServices

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connection: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connection.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connection:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/chat/{sender_id}/{receiver_id}")
async def websocket_endpoint(websocket: WebSocket, sender_id: str, receiver_id: str, db: Session = Depends(get_db)):
    chat_services = ChatServices(db)
    chat_room = chat_services.get_or_create_chat_room(sender_id, receiver_id)
    socket_session = chat_services.create_socket_session(sender_id, websocket.client.host)
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            message = chat_services.send_message(
                chat_room_id=chat_room.chat_id,
                sender_id=sender_id,
                recipient_id=receiver_id,
                text=data
            )

            chat_services.update_last_active(socket_session.session_id)
            await manager.broadcast(f"{sender_id}: {message.text}")

    except WebSocketDisconnect:
        chat_services.close_socket_session(socket_session.session_id)
        manager.disconnect(websocket)
        await manager.broadcast(f"Пользователь {sender_id} покинул чат")