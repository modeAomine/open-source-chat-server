from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.config import settings
from app.models.user import User
from app.schemas import UserProfile


def get_user_by_token(token: str, db: Session) -> UserProfile:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None

        return UserProfile(
            username=user.username,
            password=user.password,
            name=user.name,
            email=user.email,
            filename=user.filename
        )
    except JWTError:
        return None


def update_user_field(db: Session, username: str, field: str, value: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None

    setattr(user, field, value)
    db.commit()
    return user