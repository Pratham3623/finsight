from pathlib import Path

from finsight.data_generation.financial_data import generate_financials
from finsight.data_generation.output.financial_writer import (
    write_financials_csv,
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

    records = generate_financials(
        companies=companies,
        start_year=2021,
        periods=20,
        seed=42,
    )

    output_path = Path("data/raw/financial/financials.csv")

    write_financials_csv(
        records,
        output_path,
    )

    print(f"Generated {len(records):,} financial records")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()