from fastapi import APIRouter, Depends

from app.database import get_db
from app.models.session import Session
from app.schemas import UserSettings
from app.services.settings_services import get_user_settings, update_user_settings

router = APIRouter()


@router.get("/{user_id}")
def fetch_user_settings(user_id: int, db: Session = Depends(get_db)):
    return get_user_settings(user_id, db)


@router.put("/{user_id}")
def modify_user_settings(user_id: int, settings_update: UserSettings, db: Session = Depends(get_db)):
    return update_user_settings(user_id, settings_update, db)