from pathlib import Path

import pandas as pd
import pytest

from finsight.ingestion.csv_reader import read_csv


def test_read_csv(tmp_path: Path):
    source = tmp_path / "financials.csv"

    dataframe = pd.DataFrame(
        {
            "company_id": [1, 2],
            "revenue": [100.0, 200.0],
        }
    )

    dataframe.to_csv(source, index=False)

    result = read_csv(source)

    assert result.source_path == source
    assert result.records_read == 2
    assert result.columns_read == 2
    assert list(result.dataframe.columns) == [
        "company_id",
        "revenue",
    ]


def test_read_csv_missing_file(tmp_path: Path):
    source = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        read_csv(source)


def test_read_csv_directory(tmp_path: Path):
    with pytest.raises(ValueError):
        read_csv(tmp_path)