import os
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from starlette.websockets import WebSocket

from app import schemas
from app.config import settings
from app.database import get_db
from app.models.group_chat_room import GroupChatRoom
from app.models.user import User
from app.schemas import UserProfile, UpdateUserFieldRequest, ResponseMessage, AvatarUpdate, SettingsURL, UserSettings, \
    CreateGroupChatRequest
from app.services.chat_services import get_chat_messages, create_group_chat_room, get_chat_room_messages
from app.services.settings_services import get_user_profile
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
        avatar_url = f"http://127.0.0.1:8000/{user.filename}"
        avatar_url = avatar_url.replace("\\", "/")
        return avatar_url

    raise HTTPException(status_code=404, detail="Аватар не найден!")


@router.get("/{user_id}/profile", response_model=UserProfile)
def fetch_user_profile(user_id: int, current_user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_profile(user_id, current_user.id, db)


@router.get("/get/chat_message/{chat_id}")
async def get_messages(chat_id: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    get_current_user(token, db)
    messages = get_chat_messages(db, chat_id)
    return messages


@router.post("/api/users/info")
def get_users_info(user_ids: list[int], db: Session = Depends(get_db)):
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    if not users:
        raise HTTPException(status_code=404, detail="Пользователи не найдены")
    return [{"id": user.id, "username": user.username, "filename": user.filename} for user in users]


@router.get("/get/group_chat_message/{group_chat_id}")
async def get_group_chat_messages(group_chat_id: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    get_current_user(token, db)
    group_chat_id = group_chat_id
    messages = get_chat_room_messages(db, group_chat_id)
    return messages


@router.get("/get_chat_rooms")
async def get_chat_rooms(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> list:
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    group_chats = db.query(GroupChatRoom).filter(GroupChatRoom.users.any(id=user.id)).all()

    if not group_chats:
        raise HTTPException(status_code=404, detail="Пользователь не состоит в групповых чатах")

    result = [
        {
            "group_chat_id": group_chat.group_chat_id,
            "group_name": group_chat.group_name,
            "created_at": group_chat.created_at,
            "creator_id": group_chat.creator_id,
        }
        for group_chat in group_chats
    ]

    return result


@router.post("/group_chat/create")
async def create_group_chat(
        request: CreateGroupChatRequest,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> dict:
    user = get_current_user(token, db)

    if not request.user_ids:
        raise HTTPException(status_code=400, detail="Пользователя нема")

    group_chat = create_group_chat_room(db, user.id, request.user_ids, request.group_name)

    return {
        "group_chat_id": group_chat.group_chat_id,
        "group_name": group_chat.group_name,
        "created_at": group_chat.created_at
    }


@router.get("/get/group_chat_message/{group_chat_id}")
async def get_group_chat_messages(
        group_chat_id: str,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> list:
    get_current_user(token, db)

    group_chat = db.query(GroupChatRoom).filter(GroupChatRoom.group_chat_id == group_chat_id).first()
    if not group_chat:
        raise HTTPException(status_code=404, detail="Групповой чат не найден")

    messages = get_chat_room_messages(db, group_chat_id)

    result = [
        {
            "id": message.id,
            "text": message.text,
            "timestamp": message.timestamp.isoformat(),
            "sender": {
                "id": message.sender.id,
                "username": message.sender.username,
                "filename": message.sender.filename
            }
        }
        for message in messages
    ]

    return result
