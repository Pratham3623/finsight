import { useEffect, useMemo, useState } from "react";
import {
  ArrowUpRight,
  Building2,
  Search,
  TrendingUp,
} from "lucide-react";

import { getIndustryBenchmarks } from "../api/industries";

import type {
  IndustryBenchmark,
} from "../types/api";

import "./IndustriesPage.css";

type SortMetric =
  | "roa"
  | "margin"
  | "revenue"
  | "cashflow";

function formatRevenue(value: number): string {
  if (Math.abs(value) >= 1_000_000_000) {
    return `₹${(
      value / 1_000_000_000
    ).toFixed(2)}B`;
  }

  if (Math.abs(value) >= 1_000_000) {
    return `₹${(
      value / 1_000_000
    ).toFixed(1)}M`;
  }

  return `₹${value.toFixed(0)}`;
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export default function IndustriesPage() {
  const [industries, setIndustries] =
    useState<IndustryBenchmark[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [search, setSearch] =
    useState("");

  const [sortMetric, setSortMetric] =
    useState<SortMetric>("roa");

  useEffect(() => {
    let mounted = true;

    async function loadIndustries() {
      try {
        setLoading(true);
        setError(null);

        const data =
          await getIndustryBenchmarks();

        if (mounted) {
          setIndustries(data);
        }
      } catch (err) {
        if (mounted) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load industry benchmarks.",
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void loadIndustries();

    return () => {
      mounted = false;
    };
  }, []);

  const filteredIndustries =
    useMemo(() => {
      const query =
        search.trim().toLowerCase();

      const filtered = industries.filter(
        (industry) =>
          !query ||
          industry.industry_name
            .toLowerCase()
            .includes(query),
      );

      return [...filtered].sort(
        (a, b) => {
          switch (sortMetric) {
            case "margin":
              return (
                b.avg_net_profit_margin_pct -
                a.avg_net_profit_margin_pct
              );

            case "revenue":
              return (
                b.avg_revenue -
                a.avg_revenue
              );

            case "cashflow":
              return (
                b.avg_operating_cash_flow_margin_pct -
                a.avg_operating_cash_flow_margin_pct
              );

            case "roa":
            default:
              return (
                b.avg_roa_pct -
                a.avg_roa_pct
              );
          }
        },
      );
    }, [
      industries,
      search,
      sortMetric,
    ]);

  const totalCompanies =
    industries.reduce(
      (sum, industry) =>
        sum + industry.company_count,
      0,
    );

  const averageRoa =
    industries.length > 0
      ? industries.reduce(
          (sum, industry) =>
            sum + industry.avg_roa_pct,
          0,
        ) / industries.length
      : 0;

  const strongestIndustry =
    industries.length > 0
      ? [...industries].sort(
          (a, b) =>
            b.avg_roa_pct -
            a.avg_roa_pct,
        )[0]
      : null;

  return (
    <div className="industries-page">
      <section className="industries-heading">
        <div>
          <p className="industries-eyebrow">
            RESEARCH
          </p>

          <h1>
            Industry Benchmarks
          </h1>

          <p>
            Compare financial performance
            across the industries tracked
            by FinSight.
          </p>
        </div>

        <div className="industries-heading-icon">
          <Building2 size={20} />
        </div>
      </section>

      <section className="industry-stats">
        <div>
          <span>
            Industries tracked
          </span>

          <strong>
            {industries.length}
          </strong>
        </div>

        <div>
          <span>
            Companies represented
          </span>

          <strong>
            {totalCompanies}
          </strong>
        </div>

        <div>
          <span>
            Average ROA
          </span>

          <strong>
            {formatPercent(
              averageRoa,
            )}
          </strong>
        </div>

        <div>
          <span>
            Highest ROA
          </span>

          <strong>
            {strongestIndustry
              ? formatPercent(
                  strongestIndustry.avg_roa_pct,
                )
              : "—"}
          </strong>

          {strongestIndustry && (
            <small>
              {
                strongestIndustry.industry_name
              }
            </small>
          )}
        </div>
      </section>

      <section className="industries-toolbar">
        <div className="industries-search">
          <Search size={15} />

          <input
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value,
              )
            }
            placeholder="Search industries..."
          />
        </div>

        <div className="industry-sort">
          <button
            type="button"
            className={
              sortMetric === "roa"
                ? "industry-sort-active"
                : ""
            }
            onClick={() =>
              setSortMetric("roa")
            }
          >
            ROA
          </button>

          <button
            type="button"
            className={
              sortMetric === "margin"
                ? "industry-sort-active"
                : ""
            }
            onClick={() =>
              setSortMetric("margin")
            }
          >
            Margin
          </button>

          <button
            type="button"
            className={
              sortMetric === "revenue"
                ? "industry-sort-active"
                : ""
            }
            onClick={() =>
              setSortMetric("revenue")
            }
          >
            Revenue
          </button>

          <button
            type="button"
            className={
              sortMetric === "cashflow"
                ? "industry-sort-active"
                : ""
            }
            onClick={() =>
              setSortMetric("cashflow")
            }
          >
            Cash flow
          </button>
        </div>
      </section>

      {error && (
        <div className="industries-error">
          <strong>
            Unable to load industries
          </strong>

          <span>{error}</span>
        </div>
      )}

      <section className="industries-panel">
        <div className="industries-table-head">
          <span>Rank</span>
          <span>Industry</span>
          <span>Companies</span>
          <span>Revenue</span>
          <span>Net margin</span>
          <span>Operating margin</span>
          <span>ROA</span>
          <span>Debt / assets</span>
          <span>Cash flow</span>
          <span />
        </div>

        {loading ? (
          <div className="industries-empty">
            Loading industry benchmarks...
          </div>
        ) : filteredIndustries.length ===
          0 ? (
          <div className="industries-empty">
            No industries match your
            search.
          </div>
        ) : (
          filteredIndustries.map(
            (industry, index) => (
              <div
                className="industry-row"
                key={industry.industry_id}
              >
                <span className="industry-rank">
                  {String(
                    index + 1,
                  ).padStart(2, "0")}
                </span>

                <div className="industry-name">
                  <strong>
                    {
                      industry.industry_name
                    }
                  </strong>

                  <span>
                    Industry benchmark
                  </span>
                </div>

                <span className="industry-number">
                  {industry.company_count}
                </span>

                <span className="industry-number">
                  {formatRevenue(
                    industry.avg_revenue,
                  )}
                </span>

                <span className="industry-number">
                  {formatPercent(
                    industry.avg_net_profit_margin_pct,
                  )}
                </span>

                <span className="industry-number">
                  {formatPercent(
                    industry.avg_operating_margin_pct,
                  )}
                </span>

                <span className="industry-number industry-positive">
                  {formatPercent(
                    industry.avg_roa_pct,
                  )}
                </span>

                <span className="industry-number">
                  {formatPercent(
                    industry.avg_debt_to_assets_pct,
                  )}
                </span>

                <span className="industry-number industry-positive">
                  <TrendingUp size={11} />
                  {formatPercent(
                    industry.avg_operating_cash_flow_margin_pct,
                  )}
                </span>

                <button
                  type="button"
                  className="industry-open"
                  aria-label={`View ${industry.industry_name}`}
                  title="Industry details"
                >
                  <ArrowUpRight size={14} />
                </button>
              </div>
            ),
          )
        )}
      </section>
    </div>
  );
}
