# db.py — PostgreSQL persistence layer (psycopg2)

import logging
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logging.warning("psycopg2 not installed — DB features disabled.")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Connection settings
# ---------------------------------------------------------------------------

DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "postgres"
DB_USER     = "postgres"
DB_PASSWORD = "Almaty2026"


def _connect():
    if not PSYCOPG2_AVAILABLE:
        return None
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
    except Exception as exc:
        logger.error("DB connection failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Schema setup
# ---------------------------------------------------------------------------

DDL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id) ON DELETE CASCADE,
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""

def init_db() -> bool:
    """Create tables if they don't exist. Returns True on success."""
    conn = _connect()
    if conn is None:
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(DDL)
        logger.info("DB schema ready.")
        return True
    except Exception as exc:
        logger.error("init_db failed: %s", exc)
        return False
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_or_create_player(username: str) -> int | None:
    """
    Ensure a player row exists for *username*.
    Returns the player id, or None on error.
    """
    conn = _connect()
    if conn is None:
        return None
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO players (username) VALUES (%s) "
                    "ON CONFLICT (username) DO NOTHING",
                    (username,)
                )
                cur.execute(
                    "SELECT id FROM players WHERE username = %s",
                    (username,)
                )
                row = cur.fetchone()
                return row[0] if row else None
    except Exception as exc:
        logger.error("get_or_create_player failed: %s", exc)
        return None
    finally:
        conn.close()


def save_session(player_id: int, score: int, level_reached: int) -> bool:
    """Insert a completed game session. Returns True on success."""
    conn = _connect()
    if conn is None:
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) "
                    "VALUES (%s, %s, %s)",
                    (player_id, score, level_reached)
                )
        return True
    except Exception as exc:
        logger.error("save_session failed: %s", exc)
        return False
    finally:
        conn.close()


def get_top10() -> list[dict]:
    """
    Return the all-time top-10 scores.
    Each dict has: rank, username, score, level_reached, played_at.
    """
    conn = _connect()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    ROW_NUMBER() OVER (ORDER BY gs.score DESC) AS rank,
                    p.username,
                    gs.score,
                    gs.level_reached,
                    gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT 10
            """)
            return [dict(r) for r in cur.fetchall()]
    except Exception as exc:
        logger.error("get_top10 failed: %s", exc)
        return []
    finally:
        conn.close()


def get_personal_best(player_id: int) -> int:
    """Return the player's all-time best score (0 if none)."""
    conn = _connect()
    if conn is None:
        return 0
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s",
                (player_id,)
            )
            row = cur.fetchone()
            return row[0] if row else 0
    except Exception as exc:
        logger.error("get_personal_best failed: %s", exc)
        return 0
    finally:
        conn.close()