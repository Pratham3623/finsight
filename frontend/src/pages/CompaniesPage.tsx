import { useEffect, useMemo, useState } from "react";

import {
  ArrowUpRight,
  Building2,
  Search,
  TrendingUp,
} from "lucide-react";

import { Link } from "react-router-dom";

import { getCompanyRankings } from "../api/companies";

import type {
  CompanyRanking,
} from "../types/api";

function formatRevenue(
  value: number,
): string {
  if (
    Math.abs(value) >=
    1_000_000_000
  ) {
    return `₹${(
      value /
      1_000_000_000
    ).toFixed(2)}B`;
  }

  if (
    Math.abs(value) >=
    1_000_000
  ) {
    return `₹${(
      value /
      1_000_000
    ).toFixed(1)}M`;
  }

  return `₹${value.toFixed(0)}`;
}

function formatPercent(
  value: number,
): string {
  return `${value.toFixed(1)}%`;
}

export default function CompaniesPage() {
  const [companies, setCompanies] =
    useState<CompanyRanking[]>(
      [],
    );

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(
      null,
    );

  const [search, setSearch] =
    useState("");

  const [industry, setIndustry] =
    useState("All");

  useEffect(() => {
    let mounted = true;

    async function loadCompanies() {
      try {
        setLoading(true);
        setError(null);

        const data =
          await getCompanyRankings(
            100,
          );

        if (mounted) {
          setCompanies(data);
        }
      } catch (err) {
        if (mounted) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load companies.",
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void loadCompanies();

    return () => {
      mounted = false;
    };
  }, []);

  const industries =
    useMemo(() => {
      return [
        "All",
        ...Array.from(
          new Set(
            companies.map(
              (company) =>
                company.industry_name,
            ),
          ),
        ).sort(),
      ];
    }, [companies]);

  const filteredCompanies =
    useMemo(() => {
      const query =
        search
          .trim()
          .toLowerCase();

      return companies.filter(
        (company) => {
          const matchesSearch =
            !query ||
            company.company_name
              .toLowerCase()
              .includes(query) ||
            company.ticker
              .toLowerCase()
              .includes(query);

          const matchesIndustry =
            industry === "All" ||
            company.industry_name ===
              industry;

          return (
            matchesSearch &&
            matchesIndustry
          );
        },
      );
    }, [
      companies,
      search,
      industry,
    ]);

  return (
    <div className="page-content">
      <section className="page-heading">
        <div>
          <p className="eyebrow">
            RESEARCH
          </p>

          <h1>
            Companies
          </h1>

          <p className="heading-description">
            Explore financial
            performance across
            tracked companies.
          </p>
        </div>

        <div className="companies-summary">
          <Building2 size={15} />

          <span>
            {companies.length}{" "}
            companies tracked
          </span>
        </div>
      </section>

      <section className="companies-toolbar">
        <div className="companies-search">
          <Search size={15} />

          <input
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value,
              )
            }
            placeholder="Search companies or tickers..."
          />
        </div>

        <select
          value={industry}
          onChange={(event) =>
            setIndustry(
              event.target.value,
            )
          }
          className="industry-select"
        >
          {industries.map(
            (item) => (
              <option
                key={item}
                value={item}
              >
                {item}
              </option>
            ),
          )}
        </select>
      </section>

      {error && (
        <div className="dashboard-error">
          <strong>
            Unable to load companies
          </strong>

          <span>
            {error}
          </span>
        </div>
      )}

      <section className="panel companies-panel">
        <div className="companies-table-header">
          <span>
            Company
          </span>

          <span>
            Industry
          </span>

          <span>
            Revenue
          </span>

          <span>
            Net margin
          </span>

          <span>
            ROA
          </span>

          <span>
            Growth
          </span>

          <span />
        </div>

        {loading ? (
          <div className="companies-empty">
            Loading companies...
          </div>
        ) : filteredCompanies.length ===
          0 ? (
          <div className="companies-empty">
            No companies match
            your search.
          </div>
        ) : (
          filteredCompanies.map(
            (
              company,
              index,
            ) => (
              <div
                className="company-table-row"
                key={
                  company.company_id
                }
              >
                <div className="company-table-name">
                  <span className="company-table-rank">
                    {String(
                      index + 1,
                    ).padStart(
                      2,
                      "0",
                    )}
                  </span>

                  <div>
                    <strong>
                      {
                        company.company_name
                      }
                    </strong>

                    <span>
                      {
                        company.ticker
                      }
                    </span>
                  </div>
                </div>

                <span className="table-secondary">
                  {
                    company.industry_name
                  }
                </span>

                <span className="table-number">
                  {formatRevenue(
                    company.avg_revenue,
                  )}
                </span>

                <span className="table-number">
                  {formatPercent(
                    company.avg_net_profit_margin_pct,
                  )}
                </span>

                <span className="table-number table-positive">
                  {formatPercent(
                    company.avg_roa_pct,
                  )}
                </span>

                <span className="table-number">
                  <span className="growth-value">
                    <TrendingUp
                      size={12}
                    />

                    {formatPercent(
                      company.avg_revenue_growth_yoy_pct,
                    )}
                  </span>
                </span>

                <Link
                  className="company-open-button"
                  to={`/companies/${company.company_id}`}
                  title="Open company"
                  aria-label={`Open ${company.company_name}`}
                >
                  <ArrowUpRight
                    size={14}
                  />
                </Link>
              </div>
            ),
          )
        )}
      </section>
    </div>
  );
}
