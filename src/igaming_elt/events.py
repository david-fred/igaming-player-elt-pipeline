from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import random
import uuid

@dataclass(frozen=True)
class PlayerSessionEvent:
    event_id: str
    player_id: str
    session_id: str
    event_time: datetime
    game_id: str
    platform: str
    currency: str
    stake_amount: float          # e.g., dollars
    session_duration_seconds: int
    is_deposit: bool
    deposit_amount: float        # 0 if no deposit

def _rand_amount(rng: random.Random, lo: float, hi: float) -> float:
    return round(rng.uniform(lo, hi), 2)

def generate_events(
    *,
    n_players: int,
    days: int,
    events_per_day_per_player: int,
    seed: int = 42,
    now: datetime | None = None,
) -> list[PlayerSessionEvent]:
    rng = random.Random(seed)
    if now is None:
        now = datetime.now(timezone.utc)

    game_ids = ["slots_sunburst", "blackjack_ace", "roulette_classic"]
    platforms = ["web", "mobile_ios", "mobile_android"]
    currencies = ["USD", "CAD"]

    players = [f"player_{i}" for i in range(n_players)]
    out: list[PlayerSessionEvent] = []

    for d in range(days):
        day_base = now - timedelta(days=d)
        for p in players:
            for _ in range(events_per_day_per_player):
                event_time = day_base.replace(
                    hour=rng.randint(0, 23),
                    minute=rng.randint(0, 59),
                    second=rng.randint(0, 59),
                    microsecond=0,
                )
                stake = _rand_amount(rng, 0.5, 50.0)
                duration = rng.randint(60, 7200)  # 1 min to 2 hours
                is_dep = rng.random() < 0.35
                dep_amt = _rand_amount(rng, 5.0, 200.0) if is_dep else 0.0

                out.append(
                    PlayerSessionEvent(
                        event_id=str(uuid.uuid4()),
                        player_id=p,
                        session_id=str(uuid.uuid4()),
                        event_time=event_time,
                        game_id=rng.choice(game_ids),
                        platform=rng.choice(platforms),
                        currency=rng.choice(currencies),
                        stake_amount=stake,
                        session_duration_seconds=duration,
                        is_deposit=is_dep,
                        deposit_amount=dep_amt,
                    )
                )
    return out
