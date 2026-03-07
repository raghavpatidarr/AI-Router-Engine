import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load those secret keys from your .env file
load_dotenv()

# Build the connection URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the Engine (The bridge to Postgres)
engine = create_engine(DATABASE_URL)

# Create a Session (The way we send commands)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The Base class for our future Tables
Base = declarative_base()

# Helper function to get a database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# This tells SQLAlchemy to create all tables defined in models.py
def create_tables():
    Base.metadata.create_all(bind=engine)