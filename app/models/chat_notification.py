from sqlalchemy import Column, Integer, String
from app.database import Base


class ChatNotification(Base):
    __tablename__ = "chat_notification"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String)
    sender_name = Column(String)
