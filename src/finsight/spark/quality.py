from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def validate_financial_data(
    dataframe: DataFrame,
) -> dict[str, int]:
    total_records = dataframe.count()

    duplicate_ids = (
        dataframe
        .groupBy("financial_id")
        .count()
        .filter(F.col("count") > 1)
        .count()
    )

    null_company_ids = dataframe.filter(
        F.col("company_id").isNull()
    ).count()

    invalid_revenue = dataframe.filter(
        F.col("revenue") <= 0
    ).count()

    invalid_assets = dataframe.filter(
        F.col("total_assets") <= 0
    ).count()

    invalid_liabilities = dataframe.filter(
        F.col("total_liabilities")
        > F.col("total_assets")
    ).count()

    invalid_debt = dataframe.filter(
        F.col("total_debt")
        > F.col("total_liabilities")
    ).count()

    invalid_quarter = dataframe.filter(
        ~F.col("fiscal_quarter").between(1, 4)
    ).count()

    checks = {
        "records": total_records,
        "duplicate_financial_ids": duplicate_ids,
        "null_company_ids": null_company_ids,
        "invalid_revenue": invalid_revenue,
        "invalid_assets": invalid_assets,
        "liabilities_exceed_assets": invalid_liabilities,
        "debt_exceeds_liabilities": invalid_debt,
        "invalid_fiscal_quarter": invalid_quarter,
    }

    violations = {
        key: value
        for key, value in checks.items()
        if key != "records" and value > 0
    }

    if violations:
        raise ValueError(
            f"Spark financial data validation failed: {violations}"
        )

    return checks