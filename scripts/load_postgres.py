from pathlib import Path

from finsight.database.loader import load_csv_files


def main() -> None:
    counts = load_csv_files(
        industries_path=Path("data/raw/reference/industries.csv"),
        companies_path=Path("data/raw/reference/companies.csv"),
        financials_path=Path("data/processed/financials.csv"),
    )

    print("PostgreSQL load completed")
    print(f"Industries:  {counts['industries']:,}")
    print(f"Companies:   {counts['companies']:,}")
    print(f"Financials:  {counts['financials']:,}")


if __name__ == "__main__":
    main()