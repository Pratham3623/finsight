from pathlib import Path

from pyspark.sql import DataFrame, SparkSession


def read_parquet_output(
    spark: SparkSession,
    path: Path,
) -> DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Parquet output does not exist: {path}"
        )

    return spark.read.parquet(str(path))


def validate_financial_metrics_output(
    dataframe: DataFrame,
    expected_records: int,
) -> dict[str, int]:
    records = dataframe.count()

    if records != expected_records:
        raise ValueError(
            f"Expected {expected_records:,} financial records, "
            f"found {records:,}"
        )

    required_columns = {
        "financial_id",
        "company_id",
        "fiscal_year",
        "revenue",
        "net_profit_margin_pct",
        "revenue_growth_qoq_pct",
        "revenue_growth_yoy_pct",
    }

    missing = required_columns - set(dataframe.columns)

    if missing:
        raise ValueError(
            f"Missing financial output columns: {sorted(missing)}"
        )

    duplicate_ids = (
        dataframe
        .groupBy("financial_id")
        .count()
        .filter("count > 1")
        .count()
    )

    if duplicate_ids:
        raise ValueError(
            f"Found {duplicate_ids} duplicate financial IDs"
        )

    return {
        "records": records,
        "columns": len(dataframe.columns),
        "duplicate_financial_ids": duplicate_ids,
    }


def validate_industry_output(
    dataframe: DataFrame,
    expected_industries: int,
) -> dict[str, int]:
    records = dataframe.count()

    if records != expected_industries:
        raise ValueError(
            f"Expected {expected_industries} industries, "
            f"found {records}"
        )

    return {
        "records": records,
        "columns": len(dataframe.columns),
    }


def validate_company_output(
    dataframe: DataFrame,
    expected_companies: int,
) -> dict[str, int]:
    records = dataframe.count()

    if records != expected_companies:
        raise ValueError(
            f"Expected {expected_companies:,} companies, "
            f"found {records:,}"
        )

    duplicate_companies = (
        dataframe
        .groupBy("company_id")
        .count()
        .filter("count > 1")
        .count()
    )

    if duplicate_companies:
        raise ValueError(
            f"Found {duplicate_companies} duplicate companies"
        )

    return {
        "records": records,
        "columns": len(dataframe.columns),
        "duplicate_companies": duplicate_companies,
    }