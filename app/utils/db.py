from ..models import Base
from app.db import engine


def create_tables():
    Base.metadata.create_all(bind=engine, checkfirst=True)


def drop_tables():
    Base.metadata.drop_all(bind=engine)
