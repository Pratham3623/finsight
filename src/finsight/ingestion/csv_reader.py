from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class IngestionResult:
    dataframe: pd.DataFrame
    source_path: Path
    records_read: int
    columns_read: int


def read_csv(path: Path) -> IngestionResult:
    """Read a CSV file and return ingestion metadata."""

    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Input path is not a file: {path}")

    dataframe = pd.read_csv(path)

    return IngestionResult(
        dataframe=dataframe,
        source_path=path,
        records_read=len(dataframe),
        columns_read=len(dataframe.columns),
    )