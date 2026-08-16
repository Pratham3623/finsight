from pathlib import Path

from finsight.spark.analytics import (
    build_company_analytics,
    build_industry_analytics,
)
from finsight.spark.financial_transform import (
    calculate_financial_metrics,
    calculate_growth_metrics,
    enrich_financial_data,
    load_financial_data,
    load_reference_data,
)
from finsight.spark.parquet import (
    write_company_analytics,
    write_financial_metrics,
    write_industry_analytics,
)
from finsight.spark.quality import validate_financial_data
from finsight.spark.session import create_spark_session


FINANCIALS_PATH = "data/processed/financials.csv"
COMPANIES_PATH = "data/raw/reference/companies.csv"
INDUSTRIES_PATH = "data/raw/reference/industries.csv"

OUTPUT_ROOT = Path("data/processed/spark")


def main() -> None:
    print("FinSight Spark Pipeline")
    print("=" * 40)

    spark = create_spark_session()

    try:
        financials = load_financial_data(
            spark,
            FINANCIALS_PATH,
        )

        companies, industries = load_reference_data(
            spark,
            COMPANIES_PATH,
            INDUSTRIES_PATH,
        )

        print(f"Financial records loaded: {financials.count():,}")
        print(f"Companies loaded: {companies.count():,}")
        print(f"Industries loaded: {industries.count():,}")

        dataframe = enrich_financial_data(
            financials,
            companies,
            industries,
        )

        print(
            f"Enriched records: {dataframe.count():,}"
        )

        quality = validate_financial_data(
            dataframe
        )

        print("Spark data quality: PASSED")

        metrics = calculate_financial_metrics(
            dataframe
        )

        metrics = calculate_growth_metrics(
            metrics
        )

        industry_analytics = build_industry_analytics(
            metrics
        )

        company_analytics = build_company_analytics(
            metrics
        )

        print(
            f"Financial metrics: {metrics.count():,}"
        )

        print(
            f"Industry analytics: "
            f"{industry_analytics.count():,}"
        )

        print(
            f"Company analytics: "
            f"{company_analytics.count():,}"
        )

        financial_output = (
            OUTPUT_ROOT / "financial_metrics"
        )

        industry_output = (
            OUTPUT_ROOT / "industry_analytics"
        )

        company_output = (
            OUTPUT_ROOT / "company_analytics"
        )

        write_financial_metrics(
            metrics,
            financial_output,
        )

        write_industry_analytics(
            industry_analytics,
            industry_output,
        )

        write_company_analytics(
            company_analytics,
            company_output,
        )

        print("\nParquet outputs:")
        print(
            f"Financial metrics: {financial_output}"
        )
        print(
            f"Industry analytics: {industry_output}"
        )
        print(
            f"Company analytics: {company_output}"
        )

        print("\nSpark pipeline completed successfully.")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()