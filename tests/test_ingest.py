import asyncio
import sqlalchemy as sa
import pytest
from igaming_elt.db import init_db, engine, insert_events
from igaming_elt.events import generate_events
from dataclasses import asdict

@pytest.mark.timeout(60)
def test_insert_events_idempotent():
    init_db()
    events = generate_events(n_players=1, days=1, events_per_day_per_player=2, seed=3)
    rows = [asdict(e) for e in events]
    insert_events(rows)
    insert_events(rows)  # should not duplicate due to PK event_id
    with engine.begin() as conn:
        n = conn.execute(sa.text(f"SELECT COUNT(*) FROM raw_player_session_events")).scalar_one()
    assert n == len(rows)
