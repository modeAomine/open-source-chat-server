from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class ChatRoom(Base):
    __tablename__ = "chat_room"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String)
    sender_id = Column(String)
    recipient_id = Column(String)
    created_at = Column(DateTime, default=func.now())