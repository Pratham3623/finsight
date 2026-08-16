from pathlib import Path

from finsight.pipeline.local_etl import run_local_etl


def main() -> None:
    source_path = Path(
        "data/raw/financial/financials_dirty.csv"
    )

    processed_path = Path(
        "data/processed/financials.csv"
    )

    rejected_path = Path(
        "data/rejected/financials.csv"
    )

    print("FinSight Local ETL Pipeline")
    print("=" * 40)

    result = run_local_etl(
        source_path=source_path,
        processed_path=processed_path,
        rejected_path=rejected_path,
    )

    report = result.quality_report

    print(f"Records extracted: {report.records_extracted:,}")
    print(f"Records processed: {report.records_valid:,}")
    print(f"Records rejected:  {report.records_rejected:,}")
    print()
    print(f"Completeness:    {report.completeness_score:.2f}%")
    print(f"Validity:        {report.validity_score:.2f}%")
    print(f"Uniqueness:      {report.uniqueness_score:.2f}%")
    print(f"Consistency:     {report.consistency_score:.2f}%")
    print(f"Overall quality: {report.overall_quality_score:.2f}%")
    print()
    print(f"Processed: {result.processed_path}")
    print(f"Rejected:  {result.rejected_path}")
    print()
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()