from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.main import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, index=True)
    two_step_verification = Column(Boolean, default=False)
    message_deletion_time = Column(String(50), default="1 hour")
    local_password = Column(String(255))
    blocked_user = Column(Text)
    phone_visibility = Column(String(50), default='everyone')
    last_seen_visibility = Column(String(50), default='everyone')
    profile_photo_visibility = Column(String(50), default='everyone')
    bio_visibility = Column(String(50), default='everyone')
    message_permissions = Column(String(50), default='everyone')
    call_permission = Column(String(50), default='everyone')
    chat_invitations = Column(String(50), default='everyone')

    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return (f"UserSettings(user_id={self.user_id}, "
                f"two_step_verification={self.two_step_verification}, "
                f"message_deletion_time={self}")
