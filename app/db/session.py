from sqlalchemy import create_engine
from ..core import app_settings
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(app_settings.DATABASE_URL, echo=app_settings.DEBUG)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
