from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib.parse

import os

# Database Connection String
# URL encode the password to handle special characters like '@'
password = urllib.parse.quote_plus("Prince@123")
DEFAULT_DATABASE_URL = f"postgresql://postgres:{password}@localhost:5432/library_db"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# Create a SessionLocal class
# Each instance of this class will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
# All models will inherit from this class
Base = declarative_base()

# Dependency to get the database session
def get_db():
    """
    Generator function to get a database session.
    Ensures the session is closed after the request is processed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
