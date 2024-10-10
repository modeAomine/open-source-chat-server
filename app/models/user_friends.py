from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum


class FriendshipStatus(PyEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    BLOCKED = "blocked"


class Friendship(Base):
    __tablename__ = 'friendships'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    friend_id = Column(Integer, ForeignKey('users.id'), index=True)
    status = Column(Enum(FriendshipStatus), default=FriendshipStatus.PENDING)

    user = relationship("User", foreign_keys=[user_id], back_populates="friendships")
    friend = relationship("User", foreign_keys=[friend_id])