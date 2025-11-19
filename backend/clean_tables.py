"""
Script to clean (truncate) specific tables in the PostgreSQL database.
This script removes all data from the following tables:
- prompts
- translations
- manual_scores

The tables are truncated in the correct order to respect foreign key constraints.
"""

import sys
from sqlalchemy import text
from app.database import engine
from app.config import get_settings


def clean_tables():
    """
    Truncate the prompts, translations, and manual_scores tables.
    Tables are truncated in order to respect foreign key constraints.
    """

    settings = get_settings()

    print("=" * 60)
    print("DATABASE TABLE CLEANER")
    print("=" * 60)
    print(f"\nDatabase: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    print("\nTables to be cleaned (all data will be deleted):")
    print("  - manual_scores")
    print("  - translations")
    print("  - prompts")
    print("\n" + "=" * 60)

    # Ask for confirmation
    response = input("\nAre you sure you want to delete all data from these tables? (yes/no): ")

    if response.lower() != 'yes':
        print("\nOperation cancelled.")
        return

    print("\nCleaning tables...")

    try:
        with engine.connect() as connection:
            # Begin transaction
            trans = connection.begin()

            try:
                # Truncate tables in order (respecting foreign key constraints)
                # Manual scores first (depends on translations and users)
                connection.execute(text("TRUNCATE TABLE manual_scores CASCADE"))
                print("  ✓ Cleaned manual_scores")

                # Translations second (depends on prompts)
                connection.execute(text("TRUNCATE TABLE translations CASCADE"))
                print("  ✓ Cleaned translations")

                # Prompts last
                connection.execute(text("TRUNCATE TABLE prompts CASCADE"))
                print("  ✓ Cleaned prompts")

                # Commit transaction
                trans.commit()

                print("\n" + "=" * 60)
                print("SUCCESS: All tables have been cleaned!")
                print("=" * 60)

            except Exception as e:
                # Rollback on error
                trans.rollback()
                raise e

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"ERROR: Failed to clean tables")
        print(f"Error message: {str(e)}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    clean_tables()
