from __future__ import annotations

import os

from pyspark.sql import SparkSession

from .config import settings
from .spark_jobs.transforms import (
    to_curated_player_sessions,
    to_daily_player_metrics,
    compute_returning_next_day,
)
from .quality.checks import assert_no_nulls, assert_min_rows
from .warehouse.bigquery_loader import load_curated_tables_to_bigquery


def main():
    # Spark BigQuery connector needs extra jars (set via env or hardcode if you prefer).
    spark = (
        SparkSession.builder
        .appName(settings.app_name)
        .master(settings.spark_local_master)
        .config("spark.sql.session.timeZone", "UTC")
        # IMPORTANT: You must provide creds externally (ADC) via env, or use GOOGLE_APPLICATION_CREDENTIALS.
        .getOrCreate()
    )

    raw_query = f"""
      (SELECT
         event_id, player_id, session_id, event_time,
         game_id, platform, currency,
         stake_amount, session_duration_seconds,
         is_deposit, deposit_amount
       FROM {settings.postgres_raw_table}
      ) AS raw_events
    """

    # Parse PostgreSQL URL parts from SQLAlchemy-style URL.
    # DATABASE_URL example:
    # postgresql+psycopg://igaming:igaming@localhost:5432/igaming
    # We'll use env variables for Spark JDBC instead (simpler + robust).
    pg_host = os.getenv("PG_HOST", "localhost")
    pg_port = int(os.getenv("PG_PORT", "5432"))
    pg_db = os.getenv("PG_DB", "igaming")
    pg_user = os.getenv("PG_USER", "igaming")
    pg_password = os.getenv("PG_PASSWORD", "igaming")

    jdbc_url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_db}"

    raw_df = (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", raw_query)
        .option("user", pg_user)
        .option("password", pg_password)
        .option("driver", "org.postgresql.Driver")
        .load()
    )

    curated = to_curated_player_sessions(raw_df)
    assert_min_rows(curated, 1)
    assert_no_nulls(curated, ["player_id", "event_time", "session_id"])

    daily = to_daily_player_metrics(curated)
    assert_min_rows(daily, 1)
    assert_no_nulls(daily, ["player_id", "event_date", "sessions"])

    retention = compute_returning_next_day(daily)

    # If warehouse creds aren’t configured, fail fast with a clear message
    if not settings.bq_project_id or not settings.bq_dataset:
        raise RuntimeError("Set BQ_PROJECT_ID and BQ_DATASET in your environment to load to BigQuery.")

    # BigQuery load (requires connector jars + a writable temporary GCS bucket)
    load_curated_tables_to_bigquery(
        curated,
        project_id=settings.bq_project_id,
        dataset=settings.bq_dataset,
        table="curated_player_sessions",
        write_mode="overwrite",
    )
    load_curated_tables_to_bigquery(
        daily,
        project_id=settings.bq_project_id,
        dataset=settings.bq_dataset,
        table="agg_player_daily_metrics",
        write_mode="overwrite",
    )
    load_curated_tables_to_bigquery(
        retention,
        project_id=settings.bq_project_id,
        dataset=settings.bq_dataset,
        table="cohort_retention_flags",
        write_mode="overwrite",
    )

    spark.stop()


if __name__ == "__main__":
    main()
