from app.models.session import Session

from app.models.user_friends import Friendship


def is_friendship_exists(db: Session, requester_id: int, receiver_id: int) -> bool:
    return db.query(Friendship).filter_by(requester_id=requester_id, receiver_id=receiver_id).first() is not None