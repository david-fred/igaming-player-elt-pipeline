import sqlalchemy as sa
from sqlalchemy import text
from .config import settings

engine = sa.create_engine(settings.database_url, pool_pre_ping=True)

RAW_TABLE_DDL = f"""
CREATE TABLE IF NOT EXISTS {settings.postgres_raw_table} (
  event_id TEXT PRIMARY KEY,
  player_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  event_time TIMESTAMPTZ NOT NULL,
  game_id TEXT NOT NULL,
  platform TEXT NOT NULL,
  currency TEXT NOT NULL,
  stake_amount DOUBLE PRECISION NOT NULL,
  session_duration_seconds INTEGER NOT NULL,
  is_deposit BOOLEAN NOT NULL,
  deposit_amount DOUBLE PRECISION NOT NULL
);
"""

def init_db() -> None:
    with engine.begin() as conn:
        conn.execute(text(RAW_TABLE_DDL))

def insert_events(events: list[dict]) -> None:
    if not events:
        return
    cols = list(events[0].keys())
    col_csv = ", ".join(cols)
    placeholders = ", ".join([f":{c}" for c in cols])

    sql = text(f"""
      INSERT INTO {settings.postgres_raw_table} ({col_csv})
      VALUES ({placeholders})
      ON CONFLICT (event_id) DO NOTHING
    """)

    with engine.begin() as conn:
        conn.execute(sql, events)
