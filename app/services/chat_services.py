import json
import uuid
from datetime import datetime
from typing import List
from uuid import UUID

from app.models.chat_message import ChatMessage, MessageStatus
from app.models.chat_notification import ChatNotification
from app.models.chat_room import ChatRoom
from app.models.group_chat_room import GroupChatRoom
from app.models.group_chat_message import GroupChatMessage, GroupChatStatus
from app.models.session import Session
from app.models.user import User


def create_chat_room(db: Session, sender_id: str, recipient_id: str) -> ChatRoom:
    sender_id = str(sender_id)
    recipient_id = str(recipient_id)

    user_ids = sorted([sender_id, recipient_id])
    chat_room_id = f"{user_ids[0]}_{user_ids[1]}"

    chat_room = db.query(ChatRoom).filter(ChatRoom.chat_id == chat_room_id).first()

    if chat_room:
        return chat_room

    new_chat_room = ChatRoom(chat_id=chat_room_id, sender_id=sender_id, recipient_id=recipient_id)
    db.add(new_chat_room)
    db.commit()
    db.refresh(new_chat_room)
    return new_chat_room


def send_message_and_notify(db: Session, chat_room_id: str, sender_id: str, recipient_id: str, text: str,
                            timestamp: datetime, sender_username: str) -> (ChatMessage, ChatNotification):
    message = send_message(db, chat_room_id, sender_id, recipient_id, text, timestamp)
    notification = notify_sender(db, sender_id, sender_username)
    return message, notification


def send_message(db: Session, chat_room_id: str, sender_id: str, recipient_id: str, text: str,
                 timestamp: datetime) -> ChatMessage:
    new_message = ChatMessage(
        chat_room_id=chat_room_id,
        sender_id=sender_id,
        recipient_id=recipient_id,
        text=text,
        timestamp=timestamp,
        message_statuses=MessageStatus.SENT
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def get_chat_messages(db: Session, chat_room_id: str, offset: int = 0, limit: int = 100) -> list[ChatMessage]:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_room_id == chat_room_id)
        .order_by(ChatMessage.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return messages


def get_chat_notifications(db: Session, user_id: str) -> list[ChatNotification]:
    notifications = db.query(ChatNotification).filter(ChatNotification.sender_id == user_id).all()
    return notifications


def update_message_status(db: Session, message_id: int, status: MessageStatus) -> ChatMessage:
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if message:
        message.message_statuses = status
        db.commit()
        db.refresh(message)
        return message
    return None


def notify_sender(db: Session, sender_id: str, sender_name: str) -> ChatNotification:
    notification = ChatNotification(sender_id=sender_id, sender_name=sender_name)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


async def mark_messages_as_read(db: Session, chat_room_id: str, recipient_id: str) -> None:
    """ Обновляем статус всех сообщений как "READ" для данного получателя """
    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_room_id == chat_room_id,
        ChatMessage.recipient_id == recipient_id,
        ChatMessage.message_statuses != MessageStatus.READ
    ).all()

    for message in messages:
        message.message_statuses = MessageStatus.READ
        db.commit()
        db.refresh(message)

        from app.routes.socket import manager

        await manager.send_personal_message(
            json.dumps({
                "type": "message_read",
                "message_id": message.id,
                "status": "READ"
            }),
            message.sender_id
        )


""" 
Функциии для гурпового чата: 
"""


def create_group_chat_room(db: Session, creator_id: str, user_ids: List[str], group_name: str) -> GroupChatRoom:
    creator_id = str(creator_id)
    user_ids = [str(user_id) for user_id in user_ids]

    new_group_chat = GroupChatRoom(
        group_chat_id=f"{group_name}",
        group_name=group_name,
        creator_id=creator_id,
        created_at=datetime.now()
    )

    db.add(new_group_chat)
    db.commit()
    db.refresh(new_group_chat)

    creator_user = db.query(User).filter(User.id == creator_id).first()
    if creator_user:
        new_group_chat.users.append(creator_user)

    for user_id in user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            new_group_chat.users.append(user)

    db.commit()
    return new_group_chat


def add_user_to_group_chat(db: Session, group_chat_room_id: str, user_id: str) -> GroupChatRoom:
    group_chat = db.query(GroupChatRoom).filter(GroupChatRoom.group_chat_id == group_chat_room_id).first()

    if group_chat:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user not in group_chat.users:
            group_chat.users.append(user)
            db.commit()

    return group_chat


def send_group_message(db: Session, group_chat_room_id: str, sender_id: str, text: str, timestamp: datetime) -> dict:
    new_message = GroupChatMessage(
        group_chat_room_id=group_chat_room_id,
        sender_id=sender_id,
        text=text,
        timestamp=timestamp,
        message_status=GroupChatStatus.SENT
    )
    try:
        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        sender = db.query(User).filter(User.id == sender_id).first()

        avatar_url = f"http://127.0.0.1:8000/{sender.filename}".replace("\\", "/") if sender.filename else 'https://via.placeholder.com/50'

        return {
            "id": new_message.id,
            "text": new_message.text,
            "timestamp": new_message.timestamp.isoformat(),
            "sender": {
                "id": sender.id,
                "username": sender.username,
                "filename": avatar_url
            }
        }

    except Exception as e:
        db.rollback()
        print(f"Error saving message to the database: {e}")
        raise e


def get_chat_room_messages(db: Session, group_chat_room_id: str, offset: int = 0, limit: int = 100) -> List[dict]:
    messages = (
        db.query(GroupChatMessage, User.username, User.filename)
        .join(User, GroupChatMessage.sender_id == User.id)
        .filter(GroupChatMessage.group_chat_room_id == group_chat_room_id)
        .order_by(GroupChatMessage.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    result = [
        {
            "id": message.id,
            "text": message.text,
            "timestamp": message.timestamp.isoformat(),
            "sender": {
                "id": message.sender_id,
                "username": username,
                "filename": f"http://127.0.0.1:8000/{filename}".replace("\\", "/") if filename else 'https://via.placeholder.com/50'
            }
        }
        for message, username, filename in messages
    ]

    return result
