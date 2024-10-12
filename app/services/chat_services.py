from app.models.chat_message import ChatMessage, MessageStatus
from app.models.chat_notification import ChatNotification
from app.models.chat_room import ChatRoom
from app.models.session import Session
from datetime import datetime

from app.models.socket_session import SocketSession


class ChatServices:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_chat_room(self, sender_id: str, recipient_id: str) -> ChatRoom:
        chat_room = (
            self.db.query(ChatRoom)
            .filter(
                ((ChatRoom.sender_id == sender_id) & (ChatRoom.recipient_id == recipient_id)) |
                ((ChatRoom.sender_id == recipient_id) & (ChatRoom.recipient_id == sender_id))
            )
            .first()
        )

        if chat_room:
            return chat_room

        new_chat_room = ChatRoom(
            chat_id=f"{sender_id}_{recipient_id}",
            sender_id=sender_id,
            recipient_id=recipient_id
        )

        self.db.add(new_chat_room)
        self.db.commit()
        self.db.refresh(new_chat_room)
        return new_chat_room

    def send_message(self, chat_room_id: str, sender_id: str, recipient_id: str, text: str) -> ChatMessage:
        new_message = ChatMessage(
            chat_room_id=chat_room_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            text=text,
            timestamp=datetime.utcnow(),
            message_status=MessageStatus.SENT
        )

        self.db.add(new_message)
        self.db.commit()
        self.db.refresh(new_message)
        return new_message

    def create_notification(self, sender_id: str, sender_name: str) -> ChatNotification:
        notification = ChatNotification(
            sender_id=sender_id,
            sender_name=sender_name
        )

        self.db.session.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_chat_message(self, chat_room_id: str) -> list[ChatMessage]:
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.chat_room_id == chat_room_id)
            .order_by(ChatMessage.timestamp.asc())
            .all()
        )
        return messages

    def create_socket_session(self, user_id: str, session_id: str) -> SocketSession:
        new_session = SocketSession(
            user_id=user_id,
            session_id=session_id
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session

    def update_last_active(self, session_id: str):
        session = (
            self.db.query(SocketSession)
            .filter(SocketSession.session_id == session_id)
            .first()
        )
        if session:
            session.last_active_at = datetime.utcnow()
            self.db.commit()

    def close_socket_session(self, session_id: str):
        session = (
            self.db.query(SocketSession)
            .filter(SocketSession.session_id == session_id)
            .first()
        )
        if session:
            self.db.delete(session)
            self.db.commit()