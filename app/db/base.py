from ..models import User, Base
from .session import engine

# Create the database tables
Base.metadata.create_all(bind=engine)
