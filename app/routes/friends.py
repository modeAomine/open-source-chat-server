from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.models.session import Session
from sqlalchemy.sql import crud

from app.database import get_db
from app.models.user import User
from app.models.user_friends import Friendship, FriendshipStatus
from app.routes.user import get_current_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/add_friend/{friend_id}")
def add_friend(friend_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    existing_friendship = db.query(Friendship).filter(
        Friendship.user_id == user.id, Friendship.friend_id == friend_id
    ).first()

    if existing_friendship:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friend request already sent or confirmed")

    new_friendship = Friendship(user_id=user.id, friend_id=friend_id, status=FriendshipStatus.PENDING)
    db.add(new_friendship)
    db.commit()

    return {"message": "Friend request sent"}


@router.post("/confirm_friendship/{friendship_id}")
def confirm_friendship(friendship_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    friendship = db.query(Friendship).filter(Friendship.id == friendship_id, Friendship.friend_id == user.id).first()

    if not friendship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found")

    if friendship.status == FriendshipStatus.CONFIRMED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friendship already confirmed")

    friendship.status = FriendshipStatus.CONFIRMED
    db.commit()

    return {"message": "Friendship confirmed"}


@router.get("/friendships")
def get_all_friendships(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    friendships = (
        db.query(Friendship)
        .filter(Friendship.user_id == user.id)
        .join(User, Friendship.friend_id == User.id)
        .add_columns(User.id.label('friend_id'), User.username, User.filename, User.bio)
        .all()
    )

    results = []
    for friendship, friend_id, username, filename, bio in friendships:
        results.append({
            "id": friendship.id,
            "friend_id": friend_id,
            "username": username,
            "filename": filename,
            "bio": bio,
            "status": friendship.status,
        })

    return results


