import sqlite3

# Connect to database
conn = sqlite3.connect('subwrite.db')
cursor = conn.cursor()

# Add new columns
try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
    print("✅ Added 'is_verified' column")
except sqlite3.OperationalError as e:
    print(f"⚠️ is_verified column: {e}")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN verification_token TEXT")
    print("✅ Added 'verification_token' column")
except sqlite3.OperationalError as e:
    print(f"⚠️ verification_token column: {e}")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    print("✅ Added 'reset_token' column")
except sqlite3.OperationalError as e:
    print(f"⚠️ reset_token column: {e}")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires TEXT")
    print("✅ Added 'reset_token_expires' column")
except sqlite3.OperationalError as e:
    print(f"⚠️ reset_token_expires column: {e}")

# Commit changes
conn.commit()
conn.close()

print("\n✅ Database migration complete!")