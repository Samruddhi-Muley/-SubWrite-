from app.database import engine, Base
from app.models import User, Article, Like

# Create likes table
Base.metadata.create_all(bind=engine)

print("✅ Likes table created successfully!")