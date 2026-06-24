from pyspark.sql import SparkSession
from pyspark.sql import Row
import pytest

from igaming_elt.spark_jobs.transforms import (
    to_curated_player_sessions, to_daily_player_metrics, compute_returning_next_day
)
from igaming_elt.quality.checks import assert_no_nulls, assert_min_rows

@pytest.mark.timeout(60)
def test_spark_transforms_and_quality():
    spark = SparkSession.builder.master("local[*]").appName("test").getOrCreate()

    # tiny deterministic dataset
    data = [
        Row(
            event_id="e1", player_id="p1", session_id="s1",
            event_time="2026-01-01T10:00:00Z", game_id="slots_sunburst", platform="web", currency="USD",
            stake_amount=10.0, session_duration_seconds=600, is_deposit=True, deposit_amount=50.0
        ),
        Row(
            event_id="e2", player_id="p1", session_id="s2",
            event_time="2026-01-01T12:00:00Z", game_id="slots_sunburst", platform="web", currency="USD",
            stake_amount=5.0, session_duration_seconds=300, is_deposit=False, deposit_amount=0.0
        ),
        Row(
            event_id="e3", player_id="p1", session_id="s3",
            event_time="2026-01-02T09:00:00Z", game_id="slots_sunburst", platform="web", currency="USD",
            stake_amount=7.5, session_duration_seconds=420, is_deposit=True, deposit_amount=20.0
        ),
    ]
    raw_df = spark.createDataFrame(data)

    curated = to_curated_player_sessions(raw_df)
    assert_min_rows(curated, 1)
    assert_no_nulls(curated, ["player_id", "event_time", "session_id"])

    daily = to_daily_player_metrics(curated)
    assert_min_rows(daily, 1)
    assert_no_nulls(daily, ["player_id", "event_date", "sessions"])

    retention = compute_returning_next_day(daily)
    # On 2026-01-01 p1 returned next day => True
    row = retention.filter(retention.player_id == "p1").orderBy("event_date").collect()[0]
    assert row["event_date"].isoformat() == "2026-01-01"
    assert row["returned_next_day"] == True
