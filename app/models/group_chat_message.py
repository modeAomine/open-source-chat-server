from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum


class GroupChatStatus(PyEnum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"


class GroupChatMessage(Base):
    __tablename__ = "group_chat_message"

    id = Column(Integer, primary_key=True, index=True)
    group_chat_room_id = Column(Integer, ForeignKey("group_chat_room.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    timestamp = Column(DateTime, default=func.now())
    message_status = Column(Enum(GroupChatStatus), default=GroupChatStatus.SENT)
    is_deleted = Column(Boolean, default=False)

    group_chat_room = relationship("GroupChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="group_chat_messages")
