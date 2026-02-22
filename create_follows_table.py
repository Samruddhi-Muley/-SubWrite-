from app.database import engine, Base
from app.models import User, Article, Like, Follow, Comment

# Create follows table
Base.metadata.create_all(bind=engine)

print("✅ Follows table created successfully!")