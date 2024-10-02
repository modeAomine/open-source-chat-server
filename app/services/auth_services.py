import hashlib
import os

import numpy as np
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.models.user import User, Roles
from app.models.user_settings import UserSettings
from app.schemas import UserCreate, UserLogin
from app.config import settings
from app.utils.matrix import pad_data

pdw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pdw_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pdw_context.verify(plain_password, hashed_password)


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=Roles.USER,
        registration_date=datetime.now(),
        last_active=datetime.now()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    default_settings = UserSettings(
        user_id=db_user.id,
        two_step_verification=False,
        message_deletion_time="1 hour",
        local_password=None,
        blocked_user="",
        phone_visibility="everyone",
        last_seen_visibility="everyone",
        profile_photo_visibility="everyone",
        bio_visibility="everyone",
        message_permissions="everyone",
        call_permission="everyone",
        chat_invitations="everyone"
    )
    db.add(default_settings)
    db.commit()

    return db_user


def authenticate_user(db: Session, user: UserLogin) -> User:
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        return None
    return db_user