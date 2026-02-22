from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from datetime import datetime
from app.database import Base


class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who is following
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who is being followed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Ensure a user can't follow the same person twice
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='unique_follower_following'),
    )