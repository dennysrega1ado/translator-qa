#!/usr/bin/env python3
"""
Script to add execution_description column to translations table
"""
from sqlalchemy import text
from app.database import engine

def add_execution_description_column():
    """
    Add execution_description column to translations table
    """
    print("=" * 60)
    print("Adding execution_description column to translations table")
    print("=" * 60)

    try:
        with engine.connect() as connection:
            # Begin transaction
            trans = connection.begin()

            try:
                # Check if column already exists
                result = connection.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name='translations'
                    AND column_name='execution_description'
                """))

                if result.fetchone():
                    print("\n✓ Column 'execution_description' already exists")
                    trans.commit()
                    return

                # Add the column
                connection.execute(text("""
                    ALTER TABLE translations
                    ADD COLUMN execution_description TEXT
                """))

                print("\n✓ Successfully added execution_description column")

                # Commit transaction
                trans.commit()

                print("\n" + "=" * 60)
                print("SUCCESS: Migration completed!")
                print("=" * 60)

            except Exception as e:
                # Rollback on error
                trans.rollback()
                raise e

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"ERROR: Failed to add column")
        print(f"Error message: {str(e)}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    add_execution_description_column()
