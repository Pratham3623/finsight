from pathlib import Path

import pandas as pd

from finsight.data_generation.reference_data import (
    Company,
    Industry,
)


def industries_to_dataframe(
    industries: list[Industry],
) -> pd.DataFrame:
    """Convert generated industries into a DataFrame."""
    return pd.DataFrame(
        [
            {
                "industry_id": industry.industry_id,
                "industry_name": industry.industry_name,
                "sector": industry.sector,
            }
            for industry in industries
        ]
    )


def companies_to_dataframe(
    companies: list[Company],
) -> pd.DataFrame:
    """Convert generated companies into a DataFrame."""
    return pd.DataFrame(
        [
            {
                "company_id": company.company_id,
                "company_name": company.company_name,
                "ticker": company.ticker,
                "industry_id": company.industry_id,
                "industry_name": company.industry_name,
                "country": company.country,
                "founded_year": company.founded_year,
            }
            for company in companies
        ]
    )


def write_dataframe_csv(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """Write a DataFrame to CSV, creating parent directories."""
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        output_path,
        index=False,
    )