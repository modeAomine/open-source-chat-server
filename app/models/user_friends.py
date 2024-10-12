from sqlalchemy import Column, Integer, ForeignKey, Enum, func, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum


class FriendshipStatus(PyEnum):
    PENDING = "pending" #рассматривается
    WAITING = "waiting" #ожидание
    ACCEPTED = "accepted" #вы друзья
    REJECTED = "rejected" #отклонили
    BLOCKED = "blocked" #заблокирован


class Friendship(Base):
    __tablename__ = 'friendships'

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey('users.id'), index=True)
    receiver_id = Column(Integer, ForeignKey('users.id'), index=True)
    requester_status = Column(Enum(FriendshipStatus), default=FriendshipStatus.PENDING)
    receiver_status = Column(Enum(FriendshipStatus), default=FriendshipStatus.PENDING)
    created_at = Column(DateTime, default=func.now())

    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_friendships")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_friendships")
