import os

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas import UserProfile, UpdateUserFieldRequest, ResponseMessage, AvatarUpdate
from app.services.user_services import get_user_by_token, update_user_field, save_avatar, update_user_avatar
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/user", response_model=UserProfile)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


@router.patch("/edit_user", response_model=ResponseMessage)
def update_user(update_data: UpdateUserFieldRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        updated_user = update_user_field(
            db, current_user, update_data.field, update_data.value)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=418, detail={"error": f"{update_data.field} already taken"})

    return {"message": "Updated successfully"}


@router.post("/upload_avatar", response_model=AvatarUpdate)
def update_avatar(file: UploadFile = File(...), token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = user.id
    old_avatar_url = user.filename
    new_avatar_url = save_avatar(file, user_id)

    if old_avatar_url and os.path.exists(old_avatar_url):
        os.remove(old_avatar_url)

    user = update_user_avatar(db, user_id, new_avatar_url)

    return {"filename": user.filename}


@router.get("/user/{user_id}/avatar", response_model=str)
def get_user_avatar(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден!")

    if user.filename:
        avatar_url = f"/{settings.AVATAR_UPLOAD_DIR}/{user_id}/{user.filename}"
        return avatar_url

    raise HTTPException(status_code=404, detail="Аватар не найден!")
