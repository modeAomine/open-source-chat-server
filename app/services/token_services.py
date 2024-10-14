import uuid
from datetime import timedelta, datetime
from jose import jwt, JWTError
from app.config import settings
from app.database import get_db
from app.models.session import Session


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())
    })

    access_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return access_token


def create_refresh_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())
    })

    refresh_token = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    return refresh_token


def verify_access_token(token: str) -> dict:
    """
    Верификация JWT access токена. Декодирует токен и проверяет срок действия.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        return payload
    except JWTError:
        return None


def refresh_user_token(refresh_token: str):
    """
    Использует refresh_token для генерации новой пары токенов.
    """
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=settings.ALGORITHM)

        new_access_token = create_access_token(
            data={"sub": payload.get("sub")},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        # new_refresh_token = create_refresh_token(
        #     data={"sub": payload.get("sub")},
        #     expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        # )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except JWTError:
        return None


def revoke_tokens(db: get_db, user_id: int):
    """
    Удаляет все сессии пользователя, аннулируя все активные токены.
    """
    db.query(Session).filter_by(user_id=user_id).delete()
    db.commit()