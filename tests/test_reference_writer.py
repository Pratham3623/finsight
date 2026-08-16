from pathlib import Path

from finsight.data_generation.output.reference_writer import (
    companies_to_dataframe,
    industries_to_dataframe,
    write_dataframe_csv,
)
from finsight.data_generation.reference_data import (
    generate_companies,
    generate_industries,
)


def test_industries_to_dataframe():
    industries = generate_industries()

    dataframe = industries_to_dataframe(industries)

    assert len(dataframe) == 20
    assert list(dataframe.columns) == [
        "industry_id",
        "industry_name",
        "sector",
    ]


def test_companies_to_dataframe():
    industries = generate_industries()
    companies = generate_companies(
        count=10,
        industries=industries,
        seed=42,
    )

    dataframe = companies_to_dataframe(companies)

    assert len(dataframe) == 10
    assert dataframe["company_id"].is_unique


def test_write_dataframe_csv(tmp_path: Path):
    industries = generate_industries()

    dataframe = industries_to_dataframe(industries)

    output_path = tmp_path / "reference" / "industries.csv"

    write_dataframe_csv(
        dataframe,
        output_path,
    )

    assert output_path.exists()

    loaded = __import__("pandas").read_csv(output_path)

    assert len(loaded) == 20
    assert list(loaded.columns) == list(dataframe.columns)