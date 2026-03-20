import sqlite3
from contextlib import contextmanager
from config import DB_PATH


@contextmanager
def _conn():
    """Yield a SQLite connection and commit changes on success.

    Yields:
        sqlite3.Connection: An open SQLite connection for the application
        database defined by ``DB_PATH``.

    Raises:
        sqlite3.Error: Propagates any database error raised while using the
            yielded connection or committing the transaction.

    Examples:
        >>> with _conn() as connection:
        ...     isinstance(connection, sqlite3.Connection)
        True
    """
    con = sqlite3.connect(DB_PATH)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db():
    """Create the application tables if they do not already exist.

    This function initializes the persistent storage used for tracking seen
    applications and caching fetched Google Play metadata.

    Returns:
        None: This function updates the database schema in place.

    Raises:
        sqlite3.Error: Raised if SQLite cannot create or access the required
            tables.

    Examples:
        >>> init_db()
    """
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
    """Load all previously seen application identifiers from the database.

    Returns:
        set: A set of Google Play application IDs that have already been shown
        to the user.

    Raises:
        sqlite3.Error: Raised if the query against the ``seen_apps`` table
            fails.

    Examples:
        >>> isinstance(load_seen_apps(), set)
        True
    """
    with _conn() as con:
        rows = con.execute("SELECT app_id FROM seen_apps").fetchall()
    return {r[0] for r in rows}


def save_seen_apps(app_ids: set):
    """Persist a collection of application IDs as already seen.

    Args:
        app_ids (set): A set of Google Play application IDs to insert into the
            ``seen_apps`` table. Existing IDs are ignored.

    Returns:
        None: This function saves state in the database and does not return a
        value.

    Raises:
        sqlite3.Error: Raised if SQLite cannot insert the provided IDs.

    Examples:
        >>> save_seen_apps({"com.example.app"})
    """
    with _conn() as con:
        con.executemany(
            "INSERT OR IGNORE INTO seen_apps (app_id) VALUES (?)",
            [(a,) for a in app_ids],
        )


def clear_seen_apps():
    """Remove every stored application ID from the seen history.

    Returns:
        None: This function deletes rows from the ``seen_apps`` table in place.

    Raises:
        sqlite3.Error: Raised if SQLite cannot delete the stored history.

    Examples:
        >>> clear_seen_apps()
    """
    with _conn() as con:
        con.execute("DELETE FROM seen_apps")


def get_cached_details(app_id: str):
    """Return cached Google Play metadata for an application when available.

    Args:
        app_id (str): The Google Play application ID whose cached details
            should be retrieved.

    Returns:
        dict | None: The cached application metadata as a dictionary when an
        unexpired entry exists, otherwise ``None``.

    Raises:
        sqlite3.Error: Raised if SQLite cannot read the cached row.
        json.JSONDecodeError: Raised if the cached payload is present but not
            valid JSON.

    Examples:
        >>> get_cached_details("com.example.app") is None
        True
    """
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
    """Store Google Play metadata for an application in the cache table.

    Args:
        app_id (str): The Google Play application ID used as the cache key.
        data (dict): The serialized application details returned by the scraper
            library.

    Returns:
        None: This function writes the cached payload to the database.

    Raises:
        TypeError: Raised if ``data`` contains values that cannot be serialized
            to JSON.
        sqlite3.Error: Raised if SQLite cannot write the cache entry.

    Examples:
        >>> set_cached_details("com.example.app", {"title": "Example"})
    """
    import json
    with _conn() as con:
        con.execute(
            "INSERT OR REPLACE INTO app_details_cache (app_id, data) VALUES (?, ?)",
            (app_id, json.dumps(data, ensure_ascii=False)),
        )


def seen_apps_count() -> int:
    """Count how many unique application IDs are stored as seen.

    Returns:
        int: The number of rows currently stored in the ``seen_apps`` table.

    Raises:
        sqlite3.Error: Raised if SQLite cannot execute the count query.

    Examples:
        >>> isinstance(seen_apps_count(), int)
        True
    """
    with _conn() as con:
        return con.execute("SELECT COUNT(*) FROM seen_apps").fetchone()[0]
