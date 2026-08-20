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

    with pytest.raises(
        FileNotFoundError,
        match="Input file does not exist",
    ):
        read_csv(source)


def test_read_csv_directory(tmp_path: Path):
    with pytest.raises(
        ValueError,
        match="Input path is not a file",
    ):
        read_csv(tmp_path)


def test_read_csv_empty_file(tmp_path: Path):
    source = tmp_path / "empty.csv"
    source.touch()

    with pytest.raises(pd.errors.EmptyDataError):
        read_csv(source)


def test_read_csv_header_only_file(tmp_path: Path):
    source = tmp_path / "header_only.csv"

    source.write_text(
        "company_id,revenue\n",
        encoding="utf-8",
    )

    result = read_csv(source)

    assert result.records_read == 0
    assert result.columns_read == 2
    assert list(result.dataframe.columns) == [
        "company_id",
        "revenue",
    ]


def test_read_csv_preserves_missing_values(
    tmp_path: Path,
):
    source = tmp_path / "missing_values.csv"

    source.write_text(
        "company_id,revenue\n"
        "1,100\n"
        "2,\n"
        "3,300\n",
        encoding="utf-8",
    )

    result = read_csv(source)

    assert result.records_read == 3
    assert result.columns_read == 2
    assert pd.isna(
        result.dataframe.loc[1, "revenue"]
    )


def test_read_csv_handles_utf8_text(
    tmp_path: Path,
):
    source = tmp_path / "utf8.csv"

    source.write_text(
        "company_id,company_name\n"
        "1,Café Industries\n"
        "2,東京 Holdings\n",
        encoding="utf-8",
    )

    result = read_csv(source)

    assert result.records_read == 2
    assert (
        result.dataframe.loc[0, "company_name"]
        == "Café Industries"
    )
    assert (
        result.dataframe.loc[1, "company_name"]
        == "東京 Holdings"
    )


def test_read_csv_malformed_csv_is_rejected(
    tmp_path: Path,
):
    source = tmp_path / "malformed.csv"

    source.write_text(
        "company_id,revenue\n"
        "1,100\n"
        '2,"broken\n'
        "3,300\n",
        encoding="utf-8",
    )

    with pytest.raises(
        pd.errors.ParserError,
    ):
        read_csv(source)


def test_read_csv_path_is_file(
    tmp_path: Path,
):
    source = tmp_path / "financials.csv"

    source.write_text(
        "company_id,revenue\n"
        "1,100\n",
        encoding="utf-8",
    )

    result = read_csv(source)

    assert result.source_path.is_file()
