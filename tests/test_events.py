from igaming_elt.events import generate_events

def test_generate_events_shape():
    events = generate_events(n_players=2, days=1, events_per_day_per_player=3, seed=1)
    assert len(events) == 2 * 1 * 3
    e = events[0]
    assert e.player_id.startswith("player_")
    assert e.session_duration_seconds >= 60
