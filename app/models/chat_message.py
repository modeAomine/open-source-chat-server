from sqlalchemy import Column, Integer, String, DateTime, Enum, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum
from datetime import datetime


class MessageStatus(PyEnum):
    SENT = "Отправлено"
    DELIVERED = "Доставлено"
    READ = "Прочитано"


message_status = Table(
    'message_status', Base.metadata,
    Column('chat_message_id', Integer, ForeignKey('chat_message.id')),
    Column('status', Enum(MessageStatus))
)


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, index=True)
    chat_room_id = Column(String)
    sender_id = Column(String)
    recipient_id = Column(String)
    text = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_statuses = Column(Enum(MessageStatus), default=MessageStatus.SENT)
