from app.models.session import Session

from app.models.user_friends import Friendship


def is_friendship_exists(db: Session, user_id: int, friend_id: int) -> bool:
    return db.query(Friendship).filter_by(user_id=user_id, friend_id=friend_id).first() is not None