from pathlib import Path

from pyspark.sql import DataFrame


def write_financial_metrics(
    dataframe: DataFrame,
    output_path: Path,
) -> None:
    (
        dataframe
        .write
        .mode("overwrite")
        .partitionBy("fiscal_year")
        .parquet(str(output_path))
    )


def write_industry_analytics(
    dataframe: DataFrame,
    output_path: Path,
) -> None:
    (
        dataframe
        .write
        .mode("overwrite")
        .parquet(str(output_path))
    )


def write_company_analytics(
    dataframe: DataFrame,
    output_path: Path,
) -> None:
    (
        dataframe
        .write
        .mode("overwrite")
        .parquet(str(output_path))
    )