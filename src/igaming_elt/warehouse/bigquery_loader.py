from __future__ import annotations

from pyspark.sql import DataFrame

def load_curated_tables_to_bigquery(
    df: DataFrame,
    *,
    project_id: str,
    dataset: str,
    table: str,
    write_mode: str = "overwrite",
) -> None:
    """
    Loads a Spark DataFrame into BigQuery using the Spark BigQuery connector.
    Requires BigQuery connector jars configured via SPARK_EXTRA_PACKAGES and valid
    Google credentials in the environment.
    """
    full_table = f"{project_id}:{dataset}.{table}"

    (
        df.write.format("bigquery")
        .option("table", full_table)
        .option("temporaryGcsBucket", f"{dataset}-tmp")
        .mode(write_mode)
        .save()
    )
