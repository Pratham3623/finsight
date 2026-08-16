from pathlib import Path

import pandas as pd


SOURCE_PATH = Path("data/raw/financial/financials.csv")
OUTPUT_PATH = Path("data/raw/financial/financials_dirty.csv")


def create_dirty_dataset() -> None:
    """Create a reproducible dataset containing controlled data-quality issues."""

    dataframe = pd.read_csv(SOURCE_PATH)

    # 1. Missing value
    dataframe.loc[10, "revenue"] = None

    # 2. Invalid fiscal quarter
    dataframe.loc[100, "fiscal_quarter"] = 5

    # 3. Negative revenue
    dataframe.loc[200, "revenue"] = -500_000.00

    # 4. Debt exceeds liabilities
    dataframe.loc[300, "total_debt"] = (
        dataframe.loc[300, "total_liabilities"] * 1.5
    )

    # 5. Liabilities exceed assets
    dataframe.loc[400, "total_liabilities"] = (
        dataframe.loc[400, "total_assets"] * 1.5
    )

    # 6. Duplicate financial ID
    dataframe.loc[500, "financial_id"] = dataframe.loc[501, "financial_id"]

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(f"Created dirty dataset: {OUTPUT_PATH}")
    print(f"Records: {len(dataframe):,}")


if __name__ == "__main__":
    create_dirty_dataset()