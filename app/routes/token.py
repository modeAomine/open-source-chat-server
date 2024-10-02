from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
import os
from datetime import timedelta, datetime

from app.models.session import Session
from app.schemas import Token
from app.services.token_services import create_refresh_token, create_access_token
from app.utils.matrix import generate_unitary_matrix

router = APIRouter()


@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        session = db.query(Session).filter(Session.refresh_token == refresh_token).first()
        if not session:
            raise HTTPException(status_code=400, detail="Не валидный токен обновления")

        if session.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Refresh token expired")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        new_access_token = create_access_token(
            data={"sub": str(session.user_id)},
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(session.user_id)},
            expires_delta=refresh_token_expires
        )

        session.refresh_token = new_refresh_token
        session.expires_at = datetime.utcnow() + refresh_token_expires
        db.commit()

        return Token(access_token=new_access_token, refresh_token=new_refresh_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Ошибка генерации refresh_token")
