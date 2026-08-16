from pathlib import Path

import pandas as pd

from finsight.data_generation.financial_data import FinancialRecord


def financials_to_dataframe(
    records: list[FinancialRecord],
) -> pd.DataFrame:
    """Convert generated financial records into a DataFrame."""
    return pd.DataFrame(
        [
            {
                "financial_id": record.financial_id,
                "company_id": record.company_id,
                "fiscal_year": record.fiscal_year,
                "fiscal_quarter": record.fiscal_quarter,
                "period_end_date": record.period_end_date,
                "revenue": record.revenue,
                "operating_expenses": record.operating_expenses,
                "net_income": record.net_income,
                "total_assets": record.total_assets,
                "total_liabilities": record.total_liabilities,
                "total_debt": record.total_debt,
                "operating_cash_flow": record.operating_cash_flow,
                "investing_cash_flow": record.investing_cash_flow,
                "financing_cash_flow": record.financing_cash_flow,
            }
            for record in records
        ]
    )


def write_financials_csv(
    records: list[FinancialRecord],
    output_path: Path,
) -> None:
    """Write financial records to CSV."""
    dataframe = financials_to_dataframe(records)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        output_path,
        index=False,
    )