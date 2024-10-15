import json
from datetime import time, datetime

from fastapi import APIRouter, Depends
from starlette.websockets import WebSocket, WebSocketDisconnect
from app.database import get_db
from app.models.chat_message import MessageStatus
from app.models.group_chat_room import GroupChatRoom
from app.models.session import Session
from app.models.user import User
from app.services.chat_services import create_chat_room, send_message_and_notify, mark_messages_as_read, \
    update_message_status, send_group_message
from app.services.user_services import get_user_by_token

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/users")
async def search_users(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    try:
        while True:
            search_query = await websocket.receive_text()
            results = db.query(User).filter(User.username.ilike(f"%{search_query}%")).all()
            await websocket.send_json([{
                "id": user.id,
                "username": user.username,
                "filename": f"http://127.0.0.1:8000/{user.filename.replace('\\', '/')}" if user.filename else None
            } for user in results])
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({"error": "Произошла ошибка при выполнении поиска."})
    finally:
        await websocket.close()


@router.websocket("/ws/chat/{friend_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        friend_id: str,
        token: str,
        db: Session = Depends(get_db)
):
    user = get_user_by_token(token, db)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    chat_room = create_chat_room(db, str(user.id), friend_id)

    await mark_messages_as_read(db, chat_room.chat_id, str(user.id))

    await manager.connect(websocket, str(user.id))

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "read_messages":
                message_ids = message_data.get("message_ids", [])
                for message_id in message_ids:
                    update_message_status(db, message_id, MessageStatus.READ)

            else:
                text = message_data.get("text", "")
                timestamp = message_data.get("time", datetime.utcnow().isoformat())

                message, notification = send_message_and_notify(
                    db,
                    chat_room.chat_id,
                    sender_id=str(user.id),
                    recipient_id=friend_id,
                    text=text,
                    timestamp=datetime.utcnow(),
                    sender_username=user.username
                )

                payload = json.dumps({
                    "sender_id": str(user.id),
                    "recipient_id": friend_id,
                    "text": message.text,
                    "timestamp": message.timestamp.isoformat()
                })

                await manager.send_personal_message(payload, friend_id)
                await manager.send_personal_message(payload, str(user.id))

    except WebSocketDisconnect:
        manager.disconnect(str(user.id))
        await manager.broadcast(f"Пользователь {user.username} покинул чат")


@router.websocket("/ws/group_chat/{group_chat_id}")
async def group_chat(
    websocket: WebSocket,
    group_chat_id: str,
    token: str,
    db: Session = Depends(get_db)
):
    user = get_user_by_token(token, db)
    if not user:
        await websocket.close(code=4001, reason="Неверный токен")
        return

    group_chat = db.query(GroupChatRoom).filter(GroupChatRoom.group_chat_id == group_chat_id).first()
    if not group_chat:
        await websocket.close(code=404, reason="Групповой чат не найден")
        return

    await manager.connect(websocket, str(user.id))

    try:
        while True:
            data = await websocket.receive_json()

            message_data = data

            if message_data.get("type") == "send_message":
                text = message_data.get("text", "")
                group_chat_id = message_data.get("group_chat_id", "")
                current_timestamp = datetime.utcnow()

                print(f"Received message from user {user.id}: {message_data}")

                try:
                    message = send_group_message(
                        db,
                        group_chat_room_id=group_chat_id,
                        sender_id=str(user.id),
                        text=text,
                        timestamp=current_timestamp
                    )

                    payload = json.dumps(message)

                    await manager.broadcast(payload)
                except Exception as e:
                    print(f"Error while sending group message: {e}")
                    await websocket.close(code=4002, reason="Ошибка при отправке сообщения")
                    break


    except WebSocketDisconnect:
        manager.disconnect(str(user.id))
    except Exception as e:
        if not websocket.client_state.closed:
            await websocket.close(code=4003, reason=str(e))
    finally:
        manager.disconnect(str(user.id))