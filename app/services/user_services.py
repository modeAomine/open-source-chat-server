from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.config import settings
from app.models.user import User
from app.schemas import UserProfile


def get_user_by_token(token: str, db: Session, return_pedic=False) -> UserProfile:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None

        if return_pedic:
            return UserProfile(
                username=user.username,
                name=user.name,
                phone=user.phone,
                email=user.email,
                filename=user.filename
            )

        return user
    except JWTError:
        return None


def update_user_field(db: Session, current_user: User, field: str, value: str):

    if field == 'password':
        pass
        print('ПОМЕНЯЛ ПАРОЛЬЧИК ТИПА')
    else:
        setattr(current_user, field, value)

    db.commit()
    return current_user

