#!/usr/bin/env python3
"""
Migration script to add result-related columns to the match table.
Run this script to add: result_type, walkover_reason, winner_source
"""

import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

def run_migration():
    """Add missing result columns to match table"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db = SQLAlchemy(app)

    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :db_name
                AND TABLE_NAME = 'match'
                AND COLUMN_NAME IN ('result_type', 'walkover_reason', 'winner_source')
            """), {'db_name': Config.DB_NAME})

            existing_columns = {row[0] for row in result.fetchall()}
            columns_to_add = []

            if 'result_type' not in existing_columns:
                columns_to_add.append("ADD COLUMN `result_type` VARCHAR(20) NULL")
            if 'walkover_reason' not in existing_columns:
                columns_to_add.append("ADD COLUMN `walkover_reason` VARCHAR(30) NULL")
            if 'winner_source' not in existing_columns:
                columns_to_add.append("ADD COLUMN `winner_source` VARCHAR(20) NULL")

            if not columns_to_add:
                print("All columns already exist. Migration not needed.")
                return

            # Add columns
            alter_sql = f"ALTER TABLE `match` {', '.join(columns_to_add)}"
            print(f"Executing: {alter_sql}")
            db.session.execute(text(alter_sql))
            db.session.commit()

            print("Migration completed successfully!")

        except Exception as e:
            print(f"Error running migration: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    run_migration()

