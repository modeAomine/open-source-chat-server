from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, registry
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

mapper_registry = registry()
Base = mapper_registry.generate_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()