from typing import Optional
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