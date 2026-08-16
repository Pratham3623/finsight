from pathlib import Path

import pandas as pd

from finsight.pipeline.local_etl import run_local_etl


def create_source(path: Path) -> None:
    dataframe = pd.DataFrame(
        {
            "financial_id": [1, 2, 3],
            "company_id": [1, 2, 3],
            "fiscal_year": [2021, 2021, 2021],
            "fiscal_quarter": [1, 2, 3],
            "period_end_date": [
                "2021-03-31",
                "2021-06-30",
                "2021-09-30",
            ],
            "revenue": [100.0, 200.0, 300.0],
            "operating_expenses": [70.0, 140.0, 210.0],
            "net_income": [20.0, 30.0, 40.0],
            "total_assets": [200.0, 300.0, 400.0],
            "total_liabilities": [100.0, 150.0, 200.0],
            "total_debt": [50.0, 75.0, 100.0],
            "operating_cash_flow": [20.0, 30.0, 40.0],
            "investing_cash_flow": [-10.0, -20.0, -30.0],
            "financing_cash_flow": [5.0, 10.0, 15.0],
        }
    )

    dataframe.to_csv(path, index=False)


def test_local_etl_processes_valid_records(tmp_path: Path):
    source = tmp_path / "input.csv"
    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"

    create_source(source)

    result = run_local_etl(
        source,
        processed,
        rejected,
    )

    assert result.quality_report.records_extracted == 3
    assert result.quality_report.records_valid == 3
    assert result.quality_report.records_rejected == 0

    assert processed.exists()
    assert rejected.exists()

    processed_df = pd.read_csv(processed)

    assert len(processed_df) == 3


def test_local_etl_rejects_invalid_records(tmp_path: Path):
    source = tmp_path / "input.csv"
    processed = tmp_path / "processed.csv"
    rejected = tmp_path / "rejected.csv"

    create_source(source)

    dataframe = pd.read_csv(source)
    dataframe.loc[1, "revenue"] = -100
    dataframe.to_csv(source, index=False)

    result = run_local_etl(
        source,
        processed,
        rejected,
    )

    assert result.quality_report.records_extracted == 3
    assert result.quality_report.records_valid == 2
    assert result.quality_report.records_rejected == 1

    rejected_df = pd.read_csv(rejected)

    assert len(rejected_df) == 1
    assert (
        rejected_df.loc[0, "rejection_reason"]
        == "invalid_revenue"
    )