"""
BizForge — Database Layer
SQLAlchemy + SQLite for user storage
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "bizforge.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # null for OAuth users
    avatar_url = Column(String, nullable=True)
    provider = Column(String, default="local")  # local, google, github
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ActivityLog(Base):
    """Tracks every user action: what tool they used, their input, and the AI response."""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null = anonymous
    user_email = Column(String, nullable=True)
    action = Column(String, nullable=False)  # e.g. generate_logo, generate_brand, chat, etc.
    request_data = Column(Text, nullable=True)  # JSON string of the input
    response_data = Column(Text, nullable=True)  # JSON string of the output
    status = Column(String, default="success")  # success / error
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SavedItem(Base):
    """Store user's favorite generations (Logos, Names, Palettes)."""
    __tablename__ = "saved_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_type = Column(String, nullable=False)  # 'logo', 'brand_name', 'palette'
    content = Column(Text, nullable=False)  # JSON string of the item details
    meta_info = Column(Text, nullable=True) # Optional extra info (e.g. prompt used)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency: yields a DB session, closes after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
