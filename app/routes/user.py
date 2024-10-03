from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas import UserProfile, UpdateUserFieldRequest, ResponseMessage
from app.services.user_services import get_user_by_token, update_user_field
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
    # мб лучше проверять на фронте????
    if update_data.field == 'username' and current_user.username == update_data.value:
        raise HTTPException(status_code=418, detail={"error": "Username == New_username"})

    try:
        updated_user = update_user_field(
            db, current_user, update_data.field, update_data.value)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=418, detail={"error": f"{update_data.field} already taken"})

    return {"message": "Updated successfully"}
