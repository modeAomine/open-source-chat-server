from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas import UserProfile, UpdateUserFieldRequest, ResponseMessage
from app.services.user_services import get_user_by_token, update_user_field
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/user", response_model=UserProfile)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_user_by_token(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


@router.patch("/{username}", response_model=ResponseMessage)
def update_user(username: str, update_data: UpdateUserFieldRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.username != username:
        raise HTTPException(status_code=403, detail={"error": "Unauthorized"})

    updated_user = update_user_field(db, username, update_data.field, update_data.value)
    if not updated_user:
        raise HTTPException(status_code=404, detail={"error": "User not found"})

    return {"message": "Updated successfully"}

