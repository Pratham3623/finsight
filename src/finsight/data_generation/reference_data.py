from dataclasses import dataclass
import random


@dataclass(frozen=True)
class Industry:
    industry_id: int
    industry_name: str
    sector: str


@dataclass(frozen=True)
class Company:
    company_id: int
    company_name: str
    ticker: str
    industry_id: int
    industry_name: str
    country: str
    founded_year: int


INDUSTRIES = [
    ("Technology", "Information Technology"),
    ("Financial Services", "Financials"),
    ("Healthcare", "Healthcare"),
    ("Energy", "Energy"),
    ("Consumer Goods", "Consumer Discretionary"),
    ("Industrials", "Industrials"),
    ("Telecommunications", "Communication Services"),
    ("Utilities", "Utilities"),
    ("Real Estate", "Real Estate"),
    ("Materials", "Materials"),
    ("Automotive", "Consumer Discretionary"),
    ("Pharmaceuticals", "Healthcare"),
    ("Semiconductors", "Information Technology"),
    ("Media", "Communication Services"),
    ("Transportation", "Industrials"),
    ("Insurance", "Financials"),
    ("Retail", "Consumer Discretionary"),
    ("Aerospace", "Industrials"),
    ("Chemicals", "Materials"),
    ("Renewable Energy", "Energy"),
]


COUNTRIES = [
    "United States",
    "India",
    "United Kingdom",
    "Germany",
    "Japan",
    "Canada",
    "Australia",
    "Singapore",
]


def generate_industries() -> list[Industry]:
    """Generate the FinSight industry reference dataset."""
    return [
        Industry(
            industry_id=index,
            industry_name=industry_name,
            sector=sector,
        )
        for index, (industry_name, sector) in enumerate(INDUSTRIES, start=1)
    ]


def generate_companies(
    count: int,
    industries: list[Industry],
    seed: int = 42,
) -> list[Company]:
    """Generate deterministic synthetic companies."""
    if count <= 0:
        raise ValueError("Company count must be greater than zero.")

    if not industries:
        raise ValueError("At least one industry is required.")

    rng = random.Random(seed)

    companies: list[Company] = []

    for company_id in range(1, count + 1):
        industry = rng.choice(industries)

        company_name = f"{industry.industry_name} Holdings {company_id:04d}"
        ticker = f"FS{company_id:04d}"

        companies.append(
            Company(
                company_id=company_id,
                company_name=company_name,
                ticker=ticker,
                industry_id=industry.industry_id,
                industry_name=industry.industry_name,
                country=rng.choice(COUNTRIES),
                founded_year=rng.randint(1950, 2020),
            )
        )

    return companies
