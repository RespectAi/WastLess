# test_db.py
from app.db import engine

if __name__ == "__main__":
    try:
        conn = engine.connect()
        print("✅ Connected to WasteLess DB")
        conn.close()
    except Exception as e:
        print("❌ Connection failed:", e)
