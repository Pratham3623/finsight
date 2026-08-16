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


def main() -> None:
    industries = generate_industries()

    companies = generate_companies(
        count=1_000,
        industries=industries,
        seed=42,
    )

    industries_df = industries_to_dataframe(industries)
    companies_df = companies_to_dataframe(companies)

    reference_path = Path("data/raw/reference")

    write_dataframe_csv(
        industries_df,
        reference_path / "industries.csv",
    )

    write_dataframe_csv(
        companies_df,
        reference_path / "companies.csv",
    )

    print(f"Generated {len(industries_df):,} industries")
    print(f"Generated {len(companies_df):,} companies")
    print(f"Output directory: {reference_path}")


if __name__ == "__main__":
    main()
    
