from datetime import datetime
from sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

group_chat_users = Table(
    'group_chat_users', Base.metadata,
    Column('group_chat_id', Integer, ForeignKey('group_chat_room.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)


class GroupChatRoom(Base):
    __tablename__ = 'group_chat_room'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_chat_id = Column(String, unique=True, index=True, nullable=False)
    group_name = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", secondary="group_chat_users", back_populates="group_chats")
    messages = relationship("GroupChatMessage", back_populates="group_chat_room")
