from pathlib import Path

import pandas as pd

from finsight.data_generation.financial_data import generate_financials
from finsight.data_generation.output.financial_writer import (
    financials_to_dataframe,
    write_financials_csv,
)
from finsight.data_generation.reference_data import (
    generate_companies,
    generate_industries,
)


def test_financials_to_dataframe():
    industries = generate_industries()
    companies = generate_companies(
        count=5,
        industries=industries,
        seed=42,
    )

    records = generate_financials(
        companies=companies,
        periods=4,
        seed=42,
    )

    dataframe = financials_to_dataframe(records)

    assert len(dataframe) == 20
    assert dataframe["financial_id"].is_unique
    assert dataframe["company_id"].notna().all()


def test_financial_dataframe_columns():
    industries = generate_industries()
    companies = generate_companies(
        count=2,
        industries=industries,
        seed=42,
    )

    records = generate_financials(
        companies=companies,
        periods=2,
        seed=42,
    )

    dataframe = financials_to_dataframe(records)

    assert list(dataframe.columns) == [
        "financial_id",
        "company_id",
        "fiscal_year",
        "fiscal_quarter",
        "period_end_date",
        "revenue",
        "operating_expenses",
        "net_income",
        "total_assets",
        "total_liabilities",
        "total_debt",
        "operating_cash_flow",
        "investing_cash_flow",
        "financing_cash_flow",
    ]


def test_write_financials_csv(tmp_path: Path):
    industries = generate_industries()
    companies = generate_companies(
        count=3,
        industries=industries,
        seed=42,
    )

    records = generate_financials(
        companies=companies,
        periods=4,
        seed=42,
    )

    output_path = tmp_path / "financial" / "financials.csv"

    write_financials_csv(
        records,
        output_path,
    )

    assert output_path.exists()

    loaded = pd.read_csv(output_path)

    assert len(loaded) == 12
    assert loaded["financial_id"].is_unique