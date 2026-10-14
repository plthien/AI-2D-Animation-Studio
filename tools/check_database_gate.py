from __future__ import annotations

from sqlalchemy import text

from app.db.session import engine


with engine.connect() as connection:
    tables = [
        row[0]
        for row in connection.execute(
            text(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "AND name != 'alembic_version' ORDER BY name"
            )
        )
    ]
    print("TABLE_COUNT", len(tables))
    print("TABLES", ",".join(tables))
    print("FOREIGN_KEYS", connection.exec_driver_sql("PRAGMA foreign_keys").scalar())
    print("JOURNAL_MODE", connection.exec_driver_sql("PRAGMA journal_mode").scalar())
