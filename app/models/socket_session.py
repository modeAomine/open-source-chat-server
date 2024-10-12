from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class SocketSession(Base):
    __tablename__ = 'socket_session'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    session_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)