# from typing import List
#
# from fastapi import APIRouter, Depends, Query
# from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketClose
#
# from app.database import get_db
# from app.models.session import Session
# from app.services.chat_services import ChatServices
# from app.services.user_services import get_user_by_token
#
# router = APIRouter()
#
#
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: dict[str, WebSocket] = {}
#
#     async def connect(self, websocket: WebSocket, user_id: str):
#         await websocket.accept()
#         self.active_connections[user_id] = websocket
#
#     def disconnect(self, user_id: str):
#         if user_id in self.active_connections:
#             del self.active_connections[user_id]
#
#     async def broadcast(self, message: str):
#         for connection in self.active_connections.values():
#             await connection.send_text(message)
#
#
# manager = ConnectionManager()
#
#
# @router.websocket("/ws/chat/{receiver_id}")
# async def websocket_endpoint(
#     websocket: WebSocket,
#     receiver_id: str,
#     token: str = Query(...),
#     db: Session = Depends(get_db)
# ):
#     user = get_user_by_token(token, db)
#     if not user:
#         await websocket.close(code=WebSocketClose(4001, "Unauthorized"))
#         return
#
#     chat_services = ChatServices(db)
#     chat_room = chat_services.get_or_create_chat_room(user.id, receiver_id)
#     socket_session = chat_services.create_socket_session(user.id, websocket.client.host)
#
#     await manager.connect(websocket, user.id)
#
#     try:
#         while True:
#             data = await websocket.receive_text()
#
#             message = chat_services.send_message(
#                 chat_room_id=chat_room.chat_id,
#                 sender_id=user.id,  # sender_id теперь берется из авторизованного пользователя
#                 recipient_id=receiver_id,
#                 text=data
#             )
#
#             chat_services.update_last_active(socket_session.session_id)
#             await manager.broadcast(f"{user.username}: {message.text}")
#
#     except WebSocketDisconnect:
#         chat_services.close_socket_session(socket_session.session_id)
#         manager.disconnect(user.id)
#         await manager.broadcast(f"Пользователь {user.username} покинул чат")