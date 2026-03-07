from database import engine, create_tables
import models  # This is important so SQLAlchemy knows which tables to make!

try:
    print("Connecting to database...")
    # This runs the function you just added to database.py
    create_tables()
    print("✅ SUCCESS: Tables created in PostgreSQL!")
except Exception as e:
    print(f"❌ ERROR: {e}")