from pyspark.sql import DataFrame, functions as F

def to_curated_player_sessions(raw_df: DataFrame) -> DataFrame:
    # Clean + type-safe columns
    return (
        raw_df
        .select(
            "event_id",
            "player_id",
            "session_id",
            F.to_timestamp("event_time").alias("event_time"),
            F.col("game_id").alias("game_id"),
            F.col("platform").alias("platform"),
            F.col("currency").alias("currency"),
            F.col("stake_amount").cast("double").alias("stake_amount"),
            F.col("session_duration_seconds").cast("int").alias("session_duration_seconds"),
            F.col("is_deposit").cast("boolean").alias("is_deposit"),
            F.col("deposit_amount").cast("double").alias("deposit_amount"),
        )
        .filter(F.col("event_time").isNotNull())
    )

def to_daily_player_metrics(curated_df: DataFrame) -> DataFrame:
    return (
        curated_df
        .withColumn("event_date", F.to_date("event_time"))
        .groupBy("player_id", "event_date")
        .agg(
            F.countDistinct("session_id").alias("sessions"),
            F.sum("session_duration_seconds").alias("total_session_seconds"),
            F.avg("stake_amount").alias("avg_stake_amount"),
            F.sum(F.when(F.col("is_deposit"), F.col("deposit_amount")).otherwise(F.lit(0.0))).alias("deposit_amount_total"),
        )
        .withColumn("total_session_minutes", (F.col("total_session_seconds") / 60.0))
        .drop("total_session_seconds")
    )

def compute_returning_next_day(daily_df: DataFrame) -> DataFrame:
    # Simple retention flag: did user have any activity next day?
    df1 = daily_df.alias("d1")
    df2 = daily_df.alias("d2")
    return (
        df1.join(
            df2,
            (df1["player_id"] == df2["player_id"]) &
            (F.date_add(df1["event_date"], 1) == df2["event_date"]),
            how="left"
        )
        .select(
            df1["player_id"],
            df1["event_date"],
            df1["sessions"],
            df1["total_session_minutes"],
            df1["avg_stake_amount"],
            df1["deposit_amount_total"],
            F.when(df2["player_id"].isNotNull(), F.lit(True)).otherwise(F.lit(False)).alias("returned_next_day"),
        )
    )
