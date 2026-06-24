from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from sqlalchemy import create_engine
from .config import settings
from .spark_jobs.transforms import to_curated_player_sessions, to_daily_player_metrics, compute_returning_next_day
from .quality.checks import assert_no_nulls, assert_min_rows

def main():
    spark = (
        SparkSession.builder
        .appName(settings.app_name)
        .master(settings.spark_local_master)
        .getOrCreate()
    )

    # Read raw from Postgres via JDBC (you can swap for spark.read.format("jdbc") config)
    jdbc_url = settings.database_url
    raw_table = settings.postgres_raw_table

    # Parse user/pwd from SQLAlchemy URL would be brittle; for this starter, recommend explicit JDBC creds later.
    # For local tests, we instead create tiny DataFrames in tests.
    raise NotImplementedError("Wire Spark JDBC credentials or rely on tests for transform validation.")

if __name__ == "__main__":
    main()
