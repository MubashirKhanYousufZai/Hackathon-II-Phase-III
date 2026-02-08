from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use SQLite for local development to avoid connection issues
DATABASE_URL = "sqlite:///./todos_local.db"

if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL connection
    engine = create_engine(DATABASE_URL)
else:
    # SQLite connection for fallback/testing
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
