import json
from datetime import datetime
from sqlalchemy import desc
from app.models.chat_message import ChatMessage, MessageStatus
from app.models.chat_notification import ChatNotification
from app.models.chat_room import ChatRoom
from app.models.session import Session

# Удалите глобальный импорт manager
# from app.routes.socket import manager

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


def send_message_and_notify(db: Session, chat_room_id: str, sender_id: str, recipient_id: str, text: str, timestamp: datetime, sender_username: str) -> (ChatMessage, ChatNotification):
    message = send_message(db, chat_room_id, sender_id, recipient_id, text, timestamp)
    notification = notify_sender(db, sender_id, sender_username)
    return message, notification


def send_message(db: Session, chat_room_id: str, sender_id: str, recipient_id: str, text: str, timestamp: datetime) -> ChatMessage:
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

        # Перемещаем импорт manager внутрь функции
        from app.routes.socket import manager

        # Уведомляем отправителя, что сообщение было прочитано
        await manager.send_personal_message(
            json.dumps({
                "type": "message_read",
                "message_id": message.id,
                "status": "READ"
            }),
            message.sender_id
        )
