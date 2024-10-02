from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Session(Base):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    access_token = Column(String, index=True)
    refresh_token = Column(String, index=True)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="sessions")