from pathlib import Path

import pandas as pd
import psycopg

from finsight.config.settings import get_database_settings


def get_connection() -> psycopg.Connection:
    settings = get_database_settings()

    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.database,
        user=settings.user,
        password=settings.password,
    )


def load_industries(
    dataframe: pd.DataFrame,
) -> int:
    sql = """
        INSERT INTO industries (
            industry_id,
            industry_name,
            sector
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (industry_id)
        DO UPDATE SET
            industry_name = EXCLUDED.industry_name,
            sector = EXCLUDED.sector;
    """

    rows = [
        (
            int(row.industry_id),
            row.industry_name,
            row.sector,
        )
        for row in dataframe.itertuples(index=False)
    ]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(sql, rows)

    return len(rows)


def load_companies(
    dataframe: pd.DataFrame,
) -> int:
    sql = """
        INSERT INTO companies (
            company_id,
            company_name,
            ticker,
            industry_id,
            industry_name,
            country,
            founded_year
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (company_id)
        DO UPDATE SET
            company_name = EXCLUDED.company_name,
            ticker = EXCLUDED.ticker,
            industry_id = EXCLUDED.industry_id,
            industry_name = EXCLUDED.industry_name,
            country = EXCLUDED.country,
            founded_year = EXCLUDED.founded_year;
    """

    rows = [
        (
            int(row.company_id),
            row.company_name,
            row.ticker,
            int(row.industry_id),
            row.industry_name,
            row.country,
            int(row.founded_year),
        )
        for row in dataframe.itertuples(index=False)
    ]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(sql, rows)

    return len(rows)


def load_financials(
    dataframe: pd.DataFrame,
) -> int:
    sql = """
        INSERT INTO financials (
            financial_id,
            company_id,
            fiscal_year,
            fiscal_quarter,
            period_end_date,
            revenue,
            operating_expenses,
            net_income,
            total_assets,
            total_liabilities,
            total_debt,
            operating_cash_flow,
            investing_cash_flow,
            financing_cash_flow
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        ON CONFLICT (financial_id)
        DO UPDATE SET
            company_id = EXCLUDED.company_id,
            fiscal_year = EXCLUDED.fiscal_year,
            fiscal_quarter = EXCLUDED.fiscal_quarter,
            period_end_date = EXCLUDED.period_end_date,
            revenue = EXCLUDED.revenue,
            operating_expenses = EXCLUDED.operating_expenses,
            net_income = EXCLUDED.net_income,
            total_assets = EXCLUDED.total_assets,
            total_liabilities = EXCLUDED.total_liabilities,
            total_debt = EXCLUDED.total_debt,
            operating_cash_flow = EXCLUDED.operating_cash_flow,
            investing_cash_flow = EXCLUDED.investing_cash_flow,
            financing_cash_flow = EXCLUDED.financing_cash_flow;
    """

    rows = [
        (
            int(row.financial_id),
            int(row.company_id),
            int(row.fiscal_year),
            int(row.fiscal_quarter),
            row.period_end_date,
            float(row.revenue),
            float(row.operating_expenses),
            float(row.net_income),
            float(row.total_assets),
            float(row.total_liabilities),
            float(row.total_debt),
            float(row.operating_cash_flow),
            float(row.investing_cash_flow),
            float(row.financing_cash_flow),
        )
        for row in dataframe.itertuples(index=False)
    ]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(sql, rows)

    return len(rows)


def load_csv_files(
    industries_path: Path,
    companies_path: Path,
    financials_path: Path,
) -> dict[str, int]:
    industries = pd.read_csv(industries_path)
    companies = pd.read_csv(companies_path)
    financials = pd.read_csv(
        financials_path,
        parse_dates=["period_end_date"],
    )

    return {
        "industries": load_industries(industries),
        "companies": load_companies(companies),
        "financials": load_financials(financials),
    }