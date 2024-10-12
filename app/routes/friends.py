from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_

from app.models.session import Session

from app.database import get_db
from app.models.user import User
from app.models.user_friends import Friendship, FriendshipStatus
from app.routes.user import get_current_user
from app.schemas import SettingsURL

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/add_friend/{friend_id}")
def add_friend(friend_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    existing_friendship = db.query(Friendship).filter(
        Friendship.requester_id == user.id, Friendship.receiver_id == friend_id
    ).first()

    if existing_friendship:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friend request already sent or confirmed")

    new_friendship = Friendship(
        requester_id=user.id,
        receiver_id=friend_id,
        requester_status=FriendshipStatus.WAITING,
        receiver_status=FriendshipStatus.PENDING
    )
    db.add(new_friendship)
    db.commit()

    return {"message": "Friend request sent"}


@router.post("/confirm_friendship/{friendship_id}")
def confirm_friendship(friendship_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.receiver_id == user.id
    ).first()

    if not friendship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found")

    if friendship.receiver_status == FriendshipStatus.ACCEPTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friendship already confirmed")

    if friendship.receiver_status != FriendshipStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Friendship not pending confirmation")

    friendship.receiver_status = FriendshipStatus.ACCEPTED
    friendship.requester_status = FriendshipStatus.ACCEPTED
    db.commit()

    return {"message": "Friendship confirmed"}


@router.get("/friendships")
def get_all_friendships(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")


    friendships = db.query(Friendship).filter(
        or_(Friendship.requester_id == user.id, Friendship.receiver_id == user.id)
    ).all()

    results = []
    for friendship in friendships:
        if friendship.requester_id == user.id:
            friend = db.query(User).filter(User.id == friendship.receiver_id).first()

            if friendship.requester_status == FriendshipStatus.PENDING:
                friendship_status = 'pending'
            elif friendship.requester_status == FriendshipStatus.WAITING:
                friendship_status = 'waiting'
            elif friendship.requester_status == FriendshipStatus.ACCEPTED:
                friendship_status = 'confirmed'
            elif friendship.requester_status == FriendshipStatus.REJECTED:
                friendship_status = 'rejected'
            elif friendship.requester_status == FriendshipStatus.BLOCKED:
                friendship_status = 'blocked'

        else:
            friend = db.query(User).filter(User.id == friendship.requester_id).first()

            if friendship.receiver_status == FriendshipStatus.PENDING:
                friendship_status = 'pending'
            elif friendship.receiver_status == FriendshipStatus.WAITING:
                friendship_status = 'waiting'
            elif friendship.receiver_status == FriendshipStatus.ACCEPTED:
                friendship_status = 'confirmed'
            elif friendship.receiver_status == FriendshipStatus.REJECTED:
                friendship_status = 'rejected'
            elif friendship.receiver_status == FriendshipStatus.BLOCKED:
                friendship_status = 'blocked'

        results.append({
            "id": friendship.id,
            "friend_id": friend.id,
            "username": friend.username,
            "filename": f"http://127.0.0.1:8000/{friend.filename.replace('\\', '/')}" if friend.filename else None,
            "bio": friend.bio,
            "status": friendship_status,
        })

    return results
