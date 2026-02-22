from app.database import engine, Base
from app.models import User, Article

# This will add the new columns to existing tables
Base.metadata.create_all(bind=engine)

print("✅ Database updated successfully!")
print("New columns added: bio, profile_image, twitter_url, github_url, website_url")