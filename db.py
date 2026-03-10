import sqlite3
from contextlib import contextmanager
from config import DB_PATH


@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db():
    with _conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS seen_apps (
                app_id TEXT PRIMARY KEY,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS app_details_cache (
                app_id   TEXT PRIMARY KEY,
                data     TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def load_seen_apps() -> set:
    with _conn() as con:
        rows = con.execute("SELECT app_id FROM seen_apps").fetchall()
    return {r[0] for r in rows}


def save_seen_apps(app_ids: set):
    with _conn() as con:
        con.executemany(
            "INSERT OR IGNORE INTO seen_apps (app_id) VALUES (?)",
            [(a,) for a in app_ids],
        )


def clear_seen_apps():
    with _conn() as con:
        con.execute("DELETE FROM seen_apps")


def get_cached_details(app_id: str):
    import json
    with _conn() as con:
        row = con.execute(
            """
            SELECT data FROM app_details_cache
            WHERE app_id = ?
              AND datetime(cached_at, '+12 hours') > datetime('now')
            """,
            (app_id,),
        ).fetchone()
    return json.loads(row[0]) if row else None


def set_cached_details(app_id: str, data: dict):
    import json
    with _conn() as con:
        con.execute(
            "INSERT OR REPLACE INTO app_details_cache (app_id, data) VALUES (?, ?)",
            (app_id, json.dumps(data, ensure_ascii=False)),
        )


def seen_apps_count() -> int:
    with _conn() as con:
        return con.execute("SELECT COUNT(*) FROM seen_apps").fetchone()[0]
