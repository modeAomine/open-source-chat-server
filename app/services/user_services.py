import os
import uuid

from fastapi import UploadFile, HTTPException
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
                id=user.id,
                username=user.username,
                name=user.name,
                phone=user.phone,
                bio=user.bio,
                email=user.email,
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


def save_avatar(file: UploadFile, user_id: int) -> str:
    try:
        print("Получаем файл:", file.filename)
        file_ext = file.filename.split('.')[-1]
        random_filename = f"{uuid.uuid4()}.{file_ext}"
        user_dir = os.path.join(settings.AVATAR_UPLOAD_DIR, str(user_id))
        file_path = os.path.join(user_dir, random_filename)

        os.makedirs(user_dir, exist_ok=True)
        print("Сохраняем файл по пути:", file_path)

        with open(file_path, 'wb') as buffer:
            buffer.write(file.file.read())
        print("Файл успешно сохранен.")

        return file_path
    except Exception as e:
        print("Ошибка:", e)
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {e}")


def update_user_avatar(db: Session, user_id: int, avatar_url: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"Пользователь не найден!")

    user.filename = avatar_url
    db.commit()
    db.refresh(user)
    return user