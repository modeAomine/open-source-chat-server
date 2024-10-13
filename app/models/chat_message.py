from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum as PyEnum


class MessageStatus(PyEnum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, index=True)
    chat_room_id = Column(String)
    sender_id = Column(String)
    recipient_id = Column(String)
    text = Column(String)
    timestamp = Column(DateTime, default=func.now())
    message_statuses = Column(Enum(MessageStatus), default=MessageStatus.SENT)
    is_deleted = Column(Boolean, default=False)