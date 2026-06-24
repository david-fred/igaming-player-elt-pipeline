def load_to_bigquery(df, project_id: str, dataset: str, table: str) -> None:
    # Intentionally left minimal: wire with your preferred Spark BigQuery connector.
    # This keeps the repo runnable/testable without cloud credentials.
    raise NotImplementedError("Configure BigQuery connector to enable warehouse loading.")
