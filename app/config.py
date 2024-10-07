from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    AVATAR_UPLOAD_DIR: str

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), '../.env')


settings = Settings()