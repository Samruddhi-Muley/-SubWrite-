from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    bio = Column(Text, nullable=True)
    profile_image = Column(String, nullable=True)
    twitter_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_writer = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)  # NEW: Email verification status
    verification_token = Column(String, nullable=True)  # NEW: Email verification token
    reset_token = Column(String, nullable=True)  # NEW: Password reset token
    reset_token_expires = Column(DateTime, nullable=True)  # NEW: Reset token expiry
    created_at = Column(DateTime, default=datetime.utcnow)

    articles = relationship("Article", back_populates="author")