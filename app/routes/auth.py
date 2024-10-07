from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.routes.user import get_current_user
from app.schemas import UserCreate, UserLogin, Token
from app.services.auth_services import create_user, authenticate_user
from app.services.token_services import create_access_token, create_refresh_token
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.models.session import Session
from app.utils.matrix import generate_unitary_matrix

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    create_user(db, user)
    return {"message": "User registered successfully."}


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    data = {"sub": db_user.username}

    access_token = create_access_token(
        data=data,
        expires_delta=access_token_expires
    )

    refresh_token = create_refresh_token(
        data=data,
        expires_delta=refresh_token_expires
    )

    db_session = Session(
        user_id=db_user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + refresh_token_expires
    )
    db.add(db_session)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        db.query(Session).filter(Session.user_id == current_user.id).delete()
        db.commit()
        return {"message": "Вы успешно вышли"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка выхода")
