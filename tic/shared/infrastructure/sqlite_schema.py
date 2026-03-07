"""SQLite schema creation and management."""

import sqlite3
from pathlib import Path


def create_event_store_schema(db_path: Path) -> None:
    """Create the event store schema in a SQLite database.

    Args:
        db_path: Path to the SQLite database file.
    """
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_events_campaign_id
            ON events(campaign_id)
            """
        )
        conn.commit()
    finally:
        conn.close()
