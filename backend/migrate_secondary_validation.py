"""
Database migration script to add secondary_validation column to content_logs table.

Run this script once to update your database schema:
    python migrate_secondary_validation.py
"""
import sqlite3
from pathlib import Path

def migrate_database():
    """Add secondary_validation column to content_logs table."""
    db_path = Path(__file__).parent / "test_language_app.db"

    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(content_logs)")
        columns = [row[1] for row in cursor.fetchall()]

        if "secondary_validation" in columns:
            print("✅ Column 'secondary_validation' already exists. No migration needed.")
            conn.close()
            return

        # Add the new column
        print("🔄 Adding 'secondary_validation' column to content_logs table...")
        cursor.execute("""
            ALTER TABLE content_logs
            ADD COLUMN secondary_validation TEXT
        """)

        conn.commit()
        conn.close()

        print("✅ Migration completed successfully!")
        print("   The secondary_validation column has been added to content_logs table.")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Secondary Validation Migration Script")
    print("=" * 60)
    migrate_database()
