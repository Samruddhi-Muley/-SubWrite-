from app.database import engine, Base
from app.models import User, Article, Like, Follow, Comment

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ All social feature tables created successfully!")
print("   - Likes table")
print("   - Follows table")
print("   - Comments table")