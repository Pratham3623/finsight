from pathlib import Path

from finsight.spark.output_validation import (
    read_parquet_output,
    validate_company_output,
    validate_financial_metrics_output,
    validate_industry_output,
)
from finsight.spark.session import create_spark_session


OUTPUT_ROOT = Path("data/processed/spark")


def main() -> None:
    print("FinSight Spark Output Validation")
    print("=" * 40)

    spark = create_spark_session()

    try:
        financials = read_parquet_output(
            spark,
            OUTPUT_ROOT / "financial_metrics",
        )

        industries = read_parquet_output(
            spark,
            OUTPUT_ROOT / "industry_analytics",
        )

        companies = read_parquet_output(
            spark,
            OUTPUT_ROOT / "company_analytics",
        )

        financial_report = (
            validate_financial_metrics_output(
                financials,
                expected_records=19_993,
            )
        )

        industry_report = validate_industry_output(
            industries,
            expected_industries=20,
        )

        company_report = validate_company_output(
            companies,
            expected_companies=1_000,
        )

        print(
            f"Financial records: "
            f"{financial_report['records']:,}"
        )

        print(
            f"Financial columns: "
            f"{financial_report['columns']}"
        )

        print(
            f"Industry records: "
            f"{industry_report['records']}"
        )

        print(
            f"Company records: "
            f"{company_report['records']:,}"
        )

        print("\nParquet validation: PASSED")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()