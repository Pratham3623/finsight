CREATE TABLE IF NOT EXISTS industries (
    industry_id INTEGER PRIMARY KEY,
    industry_name VARCHAR(100) NOT NULL UNIQUE,
    sector VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    industry_id INTEGER NOT NULL,
    industry_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    founded_year INTEGER NOT NULL,

    CONSTRAINT fk_company_industry
        FOREIGN KEY (industry_id)
        REFERENCES industries(industry_id)
);

CREATE TABLE IF NOT EXISTS financials (
    financial_id BIGINT PRIMARY KEY,
    company_id INTEGER NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER NOT NULL,
    period_end_date DATE NOT NULL,

    revenue NUMERIC(18, 2) NOT NULL,
    operating_expenses NUMERIC(18, 2) NOT NULL,
    net_income NUMERIC(18, 2) NOT NULL,

    total_assets NUMERIC(18, 2) NOT NULL,
    total_liabilities NUMERIC(18, 2) NOT NULL,
    total_debt NUMERIC(18, 2) NOT NULL,

    operating_cash_flow NUMERIC(18, 2) NOT NULL,
    investing_cash_flow NUMERIC(18, 2) NOT NULL,
    financing_cash_flow NUMERIC(18, 2) NOT NULL,

    CONSTRAINT fk_financial_company
        FOREIGN KEY (company_id)
        REFERENCES companies(company_id),

    CONSTRAINT chk_financial_quarter
        CHECK (fiscal_quarter BETWEEN 1 AND 4),

    CONSTRAINT chk_liabilities_assets
        CHECK (total_liabilities <= total_assets),

    CONSTRAINT chk_debt_liabilities
        CHECK (total_debt <= total_liabilities),

    CONSTRAINT uq_company_period
        UNIQUE (
            company_id,
            fiscal_year,
            fiscal_quarter
        )
);

CREATE INDEX IF NOT EXISTS idx_financials_company
    ON financials(company_id);

CREATE INDEX IF NOT EXISTS idx_financials_period
    ON financials(period_end_date);

CREATE INDEX IF NOT EXISTS idx_financials_company_period
    ON financials(company_id, period_end_date);

CREATE INDEX IF NOT EXISTS idx_companies_industry
    ON companies(industry_id);