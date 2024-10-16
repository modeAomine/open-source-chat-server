from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str


class Chat(BaseModel):
    sender_a: str
    sender_b: str
    message: str


class FriendCreate(BaseModel):
    user_id: int
    friend_id: int


class FriendResponse(BaseModel):
    id: int
    user_id: int
    friend_id: int

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    id: int
    username: str
    name: Optional[str] = Field(None)
    email: EmailStr
    phone: Optional[str] = Field(None)
    bio: Optional[str] = Field(None)
    filename: Optional[str] = Field(None)


class UpdateUserFieldRequest(BaseModel):
    field: str
    value: str


class ResponseMessage(BaseModel):
    message: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AvatarUpdate(BaseModel):
    filename: Optional[str] = Field(None)


class SettingsURL(BaseModel):
    BASE_URL: str = "http://127.0.0.1:8000"


class UserSettings(BaseModel):
    user_id: int
    two_step_verification: bool = None
    message_deletion_time: str = None
    local_password: str = None
    blocked_user: str = None
    phone_visibility: str = None
    last_seen_visibility: str = None
    profile_photo_visibility: str = None
    bio_visibility: str = None
    message_permissions: str = None
    call_permission: str = None
    chat_invitations: str = None

    class Config:
        orm_model = True


class CreateGroupChatRequest(BaseModel):
    user_ids: List[str]
    group_name: str
