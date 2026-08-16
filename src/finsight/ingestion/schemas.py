from dataclasses import dataclass


@dataclass(frozen=True)
class ColumnSchema:
    name: str
    pandas_dtype: str
    required: bool = True


FINANCIAL_SCHEMA = (
    ColumnSchema("financial_id", "int64"),
    ColumnSchema("company_id", "int64"),
    ColumnSchema("fiscal_year", "int64"),
    ColumnSchema("fiscal_quarter", "int64"),
    ColumnSchema("period_end_date", "object"),
    ColumnSchema("revenue", "float64"),
    ColumnSchema("operating_expenses", "float64"),
    ColumnSchema("net_income", "float64"),
    ColumnSchema("total_assets", "float64"),
    ColumnSchema("total_liabilities", "float64"),
    ColumnSchema("total_debt", "float64"),
    ColumnSchema("operating_cash_flow", "float64"),
    ColumnSchema("investing_cash_flow", "float64"),
    ColumnSchema("financing_cash_flow", "float64"),
)