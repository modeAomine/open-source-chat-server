from sqlalchemy import Column, Integer, String, DateTime, Enum, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum
from datetime import datetime

from app.models.group_chat_room import group_chat_users
from app.models.user_friends import Friendship


class Roles(PyEnum):
    USER = "Пользователь"
    SUPPORT = "Поддержка"
    ADMIN = "Администратор"


class UserStatus(PyEnum):
    ACTIVE = "Активный"
    INACTIVE = "Неактивный"


user_role = Table(
    'user_role', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role', Enum(Roles))
)

user_status = Table(
    'user_status', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('status', Enum(UserStatus))
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String, unique=True, index=True)
    filename = Column(String)
    profile_background_filename = Column(String)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    bio = Column(String)
    discord = Column(String)
    vk = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    role = Column(Enum(Roles), default=Roles.USER)
    status = Column(Enum(UserStatus), default=UserStatus.INACTIVE)

    sessions = relationship("Session", back_populates="user")
    sent_friendships = relationship("Friendship", foreign_keys=[Friendship.requester_id], back_populates="requester")
    received_friendships = relationship("Friendship", foreign_keys=[Friendship.receiver_id], back_populates="receiver")
    settings = relationship("UserSettings", uselist=False, back_populates="user")
    group_chats = relationship("GroupChatRoom", secondary=group_chat_users, back_populates="users")
    group_chat_messages = relationship("GroupChatMessage", back_populates="sender")

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"
