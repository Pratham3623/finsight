import { useEffect, useMemo, useState } from "react";
import {
  ArrowUpRight,
  BarChart3,
  Search,
  TrendingUp,
} from "lucide-react";
import { Link } from "react-router-dom";

import { getCompanyRankings } from "../api/companies";

import type {
  CompanyRanking,
} from "../types/api";

import "./RankingsPage.css";

type RankingMetric =
  | "roa"
  | "revenue"
  | "margin"
  | "growth";

function formatRevenue(
  value: number,
): string {
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

function formatPercent(
  value: number,
): string {
  return `${value.toFixed(1)}%`;
}

export default function RankingsPage() {
  const [rankings, setRankings] =
    useState<CompanyRanking[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [search, setSearch] =
    useState("");

  const [metric, setMetric] =
    useState<RankingMetric>("roa");

  useEffect(() => {
    let mounted = true;

    async function loadRankings() {
      try {
        setLoading(true);
        setError(null);

        const data =
          await getCompanyRankings(100);

        if (mounted) {
          setRankings(data);
        }
      } catch (err) {
        if (mounted) {
          setError(
            err instanceof Error
              ? err.message
              : "Unable to load rankings.",
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void loadRankings();

    return () => {
      mounted = false;
    };
  }, []);

  const filteredRankings =
    useMemo(() => {
      const query =
        search.trim().toLowerCase();

      const filtered = rankings.filter(
        (company) =>
          !query ||
          company.company_name
            .toLowerCase()
            .includes(query) ||
          company.ticker
            .toLowerCase()
            .includes(query) ||
          company.industry_name
            .toLowerCase()
            .includes(query),
      );

      return [...filtered].sort(
        (a, b) => {
          switch (metric) {
            case "revenue":
              return (
                b.avg_revenue -
                a.avg_revenue
              );

            case "margin":
              return (
                b.avg_net_profit_margin_pct -
                a.avg_net_profit_margin_pct
              );

            case "growth":
              return (
                b.avg_revenue_growth_yoy_pct -
                a.avg_revenue_growth_yoy_pct
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
      rankings,
      search,
      metric,
    ]);

  const averageRoa =
    rankings.length > 0
      ? rankings.reduce(
          (sum, company) =>
            sum + company.avg_roa_pct,
          0,
        ) / rankings.length
      : 0;

  const averageMargin =
    rankings.length > 0
      ? rankings.reduce(
          (sum, company) =>
            sum +
            company.avg_net_profit_margin_pct,
          0,
        ) / rankings.length
      : 0;

  const averageGrowth =
    rankings.length > 0
      ? rankings.reduce(
          (sum, company) =>
            sum +
            company.avg_revenue_growth_yoy_pct,
          0,
        ) / rankings.length
      : 0;

  return (
    <div className="rankings-page">
      <section className="rankings-heading">
        <div>
          <p className="rankings-eyebrow">
            RESEARCH
          </p>

          <h1>Company Rankings</h1>

          <p>
            Compare tracked companies
            across key financial
            performance indicators.
          </p>
        </div>

        <div className="rankings-heading-icon">
          <BarChart3 size={20} />
        </div>
      </section>

      <section className="ranking-stats">
        <div>
          <span>Companies ranked</span>
          <strong>{rankings.length}</strong>
        </div>

        <div>
          <span>Average ROA</span>
          <strong>
            {formatPercent(averageRoa)}
          </strong>
        </div>

        <div>
          <span>Average net margin</span>
          <strong>
            {formatPercent(
              averageMargin,
            )}
          </strong>
        </div>

        <div>
          <span>Average revenue growth</span>
          <strong>
            {formatPercent(
              averageGrowth,
            )}
          </strong>
        </div>
      </section>

      <section className="rankings-toolbar">
        <div className="rankings-search">
          <Search size={15} />

          <input
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value,
              )
            }
            placeholder="Search companies, tickers or industries..."
          />
        </div>

        <div className="ranking-switcher">
          <button
            type="button"
            className={
              metric === "roa"
                ? "ranking-switch-active"
                : ""
            }
            onClick={() =>
              setMetric("roa")
            }
          >
            ROA
          </button>

          <button
            type="button"
            className={
              metric === "revenue"
                ? "ranking-switch-active"
                : ""
            }
            onClick={() =>
              setMetric("revenue")
            }
          >
            Revenue
          </button>

          <button
            type="button"
            className={
              metric === "margin"
                ? "ranking-switch-active"
                : ""
            }
            onClick={() =>
              setMetric("margin")
            }
          >
            Margin
          </button>

          <button
            type="button"
            className={
              metric === "growth"
                ? "ranking-switch-active"
                : ""
            }
            onClick={() =>
              setMetric("growth")
            }
          >
            Growth
          </button>
        </div>
      </section>

      {error && (
        <div className="rankings-error">
          <strong>
            Unable to load rankings
          </strong>

          <span>{error}</span>
        </div>
      )}

      <section className="rankings-panel">
        <div className="rankings-table-head">
          <span>Rank</span>
          <span>Company</span>
          <span>Industry</span>
          <span>Revenue</span>
          <span>Net margin</span>
          <span>ROA</span>
          <span>Growth</span>
          <span />
        </div>

        {loading ? (
          <div className="rankings-empty">
            Loading rankings...
          </div>
        ) : filteredRankings.length ===
          0 ? (
          <div className="rankings-empty">
            No companies match your
            search.
          </div>
        ) : (
          filteredRankings.map(
            (company, index) => (
              <div
                className="ranking-row"
                key={
                  company.company_id
                }
              >
                <div className="ranking-position">
                  {String(
                    index + 1,
                  ).padStart(2, "0")}
                </div>

                <div className="ranking-company">
                  <strong>
                    {company.company_name}
                  </strong>

                  <span>
                    {company.ticker}
                  </span>
                </div>

                <div className="ranking-industry">
                  {company.industry_name}
                </div>

                <div className="ranking-value">
                  {formatRevenue(
                    company.avg_revenue,
                  )}
                </div>

                <div className="ranking-value">
                  {formatPercent(
                    company.avg_net_profit_margin_pct,
                  )}
                </div>

                <div className="ranking-value ranking-positive">
                  {formatPercent(
                    company.avg_roa_pct,
                  )}
                </div>

                <div className="ranking-growth">
                  <TrendingUp size={11} />

                  {formatPercent(
                    company.avg_revenue_growth_yoy_pct,
                  )}
                </div>

                <Link
                  to={`/companies/${company.company_id}`}
                  className="ranking-open"
                  aria-label={`Open ${company.company_name}`}
                >
                  <ArrowUpRight size={14} />
                </Link>
              </div>
            ),
          )
        )}
      </section>
    </div>
  );
}
