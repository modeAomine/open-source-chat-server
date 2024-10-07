import logging

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user_friends import Friendship
from app.models.user_settings import UserSettings
from app.models.user_settings import UserSettings as settings


def get_user_settings(user_id: int, db: Session):
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Настройки не найдены")
    return settings


def update_user_settings(user_id: int, settings_update: settings, db: Session):
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Настройки не найдены")

    for key, value in settings_update.dict(exclude_unset=True).items():
        setattr(settings, key, value)

    db.commit()
    db.refresh(settings)
    return settings


def can_view_settings(field_visibility: str, user_id: int, viewer_id: int, db: Session) -> bool:
    if field_visibility == 'everyone':
        return True
    elif field_visibility == 'contacts':
        friendship = db.query(Friendship).filter(
            ((Friendship.user_id == user_id) & (Friendship.friend_id == viewer_id)) | ((Friendship.user_id == viewer_id) & (Friendship.friend_id == user_id))).first()
        return friendship is not None
    elif field_visibility == 'nobody':
        return False


def is_blocked(user_id: int, viewer_id: int, db: Session) -> bool:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Настройки не найдены")

    blocked_user_ids = settings.blocked_user.split(',') if settings.blocked_user else []
    blocked = str(viewer_id) in blocked_user_ids
    logging.debug(f"Пользователь {viewer_id} заблокирован {user_id}: {blocked}")
    return blocked


def get_user_profile(user_id: int, viewer_id: int, db: Session) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if not settings:
        raise HTTPException(status_code=404, detail="Настройки не найдены")

    if is_blocked(user_id, viewer_id, db):
        logging.warning(f"Пользователь {viewer_id} попытался получить доступ к профилю заблокированного пользователя {user_id}.")
        raise HTTPException(status_code=403, detail="Вы заблокированы этим пользователем.")

    is_friend = db.query(Friendship).filter(
        (Friendship.user_id == user_id) & (Friendship.friend_id == viewer_id) |
        (Friendship.user_id == viewer_id) & (Friendship.friend_id == user_id)
    ).first() is not None

    profile_data = {
        "id": user.id,
        "username": user.username,
        "email": "hidden" if user.email == 'nobody' else user.email,
        "phone": "hidden" if not can_view_settings(settings.phone_visibility, user_id, viewer_id, db) else user.phone,
        "profile_photo": "hidden" if not can_view_settings(settings.profile_photo_visibility, user_id, viewer_id, db) else user.filename,
        "last_seen": "hidden" if not can_view_settings(settings.last_seen_visibility, user_id, viewer_id, db) else user.last_active,
        "bio": "hidden" if not can_view_settings(settings.bio_visibility, user_id, viewer_id, db) else user.bio,
    }

    if settings.phone_visibility == 'nobody':
        profile_data.pop('phone', None)
    elif settings.phone_visibility == 'contacts' and not is_friend:
        profile_data.pop('phone', None)

    if settings.profile_photo_visibility == 'nobody':
        profile_data.pop('profile_photo', None)
    elif settings.profile_photo_visibility == 'contacts' and not is_friend:
        profile_data.pop('profile_photo', None)

    if settings.last_seen_visibility == 'nobody':
        profile_data.pop('last_seen', None)
    elif settings.last_seen_visibility == 'contacts' and not is_friend:
        profile_data.pop('last_seen', None)

    if settings.bio_visibility == 'nobody':
        profile_data.pop('bio', None)
    elif settings.bio_visibility == 'contacts' and not is_friend:
        profile_data.pop('bio', None)

    return profile_data