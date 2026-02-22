import sqlite3

# Connect to database
conn = sqlite3.connect('subwrite.db')
cursor = conn.cursor()

# Add tags column
try:
    cursor.execute("ALTER TABLE articles ADD COLUMN tags TEXT")
    print("✅ Added 'tags' column to articles table")
except sqlite3.OperationalError as e:
    print(f"⚠️ tags column: {e}")

# Commit changes
conn.commit()
conn.close()

print("\n✅ Database migration complete!")