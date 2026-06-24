import asyncio
from dataclasses import asdict
from datetime import timezone
from .config import settings
from .db import init_db, insert_events
from .events import generate_events

async def ingest_synthetic_to_postgres(
    *,
    n_players: int = 50,
    days: int = 7,
    events_per_day_per_player: int = 5,
    seed: int = 42,
    batch_size: int = 500,
) -> int:
    init_db()
    events = generate_events(
        n_players=n_players,
        days=days,
        events_per_day_per_player=events_per_day_per_player,
        seed=seed,
    )

    # convert to dicts for SQLAlchemy
    rows = [asdict(e) for e in events]
    total = 0
    for i in range(0, len(rows), batch_size):
        chunk = rows[i:i+batch_size]
        insert_events(chunk)
        total += len(chunk)

        # yield to event loop
        await asyncio.sleep(0)
    return total

async def main():
    await ingest_synthetic_to_postgres()

if __name__ == "__main__":
    asyncio.run(main())
