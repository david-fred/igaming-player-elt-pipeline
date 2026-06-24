from pyspark.sql import DataFrame, functions as F

def assert_no_nulls(df: DataFrame, cols: list[str]) -> None:
    for c in cols:
        cnt = df.filter(F.col(c).isNull() | F.isnan(F.col(c))).count()
        if cnt != 0:
            raise AssertionError(f"Null/NaN found in column {c}: {cnt}")

def assert_min_rows(df: DataFrame, min_rows: int = 1) -> None:
    n = df.count()
    if n < min_rows:
        raise AssertionError(f"Expected at least {min_rows} rows, got {n}")
