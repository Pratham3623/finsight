import { useEffect, useMemo, useState } from "react";
import {
  ChevronDown,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getCompanyRankings } from "../api/companies";
import {
  getHealth,
  getReadiness,
} from "../api/health";
import {
  getIndustryBenchmarks,
} from "../api/industries";

import type {
  CompanyRanking,
  IndustryBenchmark,
} from "../types/api";

function formatCurrency(value: number): string {
  const absolute = Math.abs(value);

  if (absolute >= 1_000_000_000) {
    return `₹${(
      value / 1_000_000_000
    ).toFixed(2)}B`;
  }

  if (absolute >= 1_000_000) {
    return `₹${(
      value / 1_000_000
    ).toFixed(1)}M`;
  }

  if (absolute >= 1_000) {
    return `₹${(
      value / 1_000
    ).toFixed(1)}K`;
  }

  return `₹${value.toFixed(0)}`;
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export default function DashboardPage() {
  const [rankings, setRankings] =
    useState<CompanyRanking[]>([]);

  const [industries, setIndustries] =
    useState<IndustryBenchmark[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [apiHealthy, setApiHealthy] =
    useState(false);

  useEffect(() => {
    let mounted = true;

    async function loadDashboard() {
      setLoading(true);
      setError(null);

      try {
        const [
          rankingData,
          industryData,
          healthData,
          readinessData,
        ] = await Promise.all([
          getCompanyRankings(10),
          getIndustryBenchmarks(),
          getHealth(),
          getReadiness(),
        ]);

        if (!mounted) {
          return;
        }

        setRankings(rankingData);
        setIndustries(industryData);

        setApiHealthy(
          healthData.status ===
            "healthy" &&
            readinessData.status ===
              "ready",
        );
      } catch (err) {
        if (!mounted) {
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load dashboard data.",
        );

        setApiHealthy(false);
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      mounted = false;
    };
  }, []);

  const topCompanies = useMemo(() => {
    return [...rankings]
      .sort(
        (a, b) =>
          a.roa_rank - b.roa_rank,
      )
      .slice(0, 4);
  }, [rankings]);

  const topIndustries = useMemo(() => {
    return [...industries]
      .sort(
        (a, b) =>
          b.avg_roa_pct -
          a.avg_roa_pct,
      )
      .slice(0, 4);
  }, [industries]);

  const aggregateRevenue = useMemo(() => {
    return rankings.reduce(
      (sum, company) =>
        sum + company.avg_revenue,
      0,
    );
  }, [rankings]);

  const averageRoa = useMemo(() => {
    if (rankings.length === 0) {
      return 0;
    }

    return (
      rankings.reduce(
        (sum, company) =>
          sum +
          company.avg_roa_pct,
        0,
      ) / rankings.length
    );
  }, [rankings]);

  const averageMargin = useMemo(() => {
    if (rankings.length === 0) {
      return 0;
    }

    return (
      rankings.reduce(
        (sum, company) =>
          sum +
          company.avg_net_profit_margin_pct,
        0,
      ) / rankings.length
    );
  }, [rankings]);

  const chartData = useMemo(() => {
    return topCompanies.map(
      (company) => ({
        ticker: company.ticker,
        revenue:
          company.avg_revenue /
          1_000_000_000,
      }),
    );
  }, [topCompanies]);

  return (
    <div className="page-content">
      <section className="page-heading">
        <div>
          <p className="eyebrow">
            FINANCIAL OVERVIEW
          </p>

          <h1>
            Good afternoon.
          </h1>

          <p className="heading-description">
            A concise view of your
            financial intelligence
            workspace.
          </p>
        </div>

        <button
          className="period-selector"
          type="button"
        >
          Last 12 months
          <ChevronDown size={14} />
        </button>
      </section>

      {error && (
        <div className="dashboard-error">
          <strong>
            Unable to load live data
          </strong>

          <span>{error}</span>
        </div>
      )}

      <section className="metric-grid">
        <MetricCard
          label="Tracked revenue"
          value={
            loading
              ? "—"
              : formatCurrency(
                  aggregateRevenue,
                )
          }
          description="Top 10 ranked companies"
        />

        <MetricCard
          label="Average net margin"
          value={
            loading
              ? "—"
              : formatPercent(
                  averageMargin,
                )
          }
          description="Across ranked companies"
        />

        <MetricCard
          label="Average return on assets"
          value={
            loading
              ? "—"
              : formatPercent(
                  averageRoa,
                )
          }
          description="Across ranked companies"
        />

        <MetricCard
          label="Companies tracked"
          value={
            loading
              ? "—"
              : rankings.length.toString()
          }
          description="Loaded from analytics API"
        />
      </section>

      <section className="analytics-grid">
        <div className="panel chart-panel">
          <div className="panel-header">
            <div>
              <h2>
                Revenue & profitability
              </h2>

              <p>
                Ranked-company financial
                snapshot
              </p>
            </div>

            <button
              className="panel-action"
              type="button"
            >
              View details
            </button>
          </div>

          {loading ? (
            <div className="chart-state">
              Loading financial data...
            </div>
          ) : topCompanies.length ===
            0 ? (
            <div className="chart-state">
              No financial data available.
            </div>
          ) : (
            <div className="revenue-chart">
              <ResponsiveContainer
                width="100%"
                height="100%"
              >
                <BarChart
                  data={chartData}
                  margin={{
                    top: 20,
                    right: 18,
                    left: 0,
                    bottom: 0,
                  }}
                >
                  <CartesianGrid
                    vertical={false}
                    stroke="#1d2229"
                    strokeDasharray="2 4"
                  />

                  <XAxis
                    dataKey="ticker"
                    axisLine={false}
                    tickLine={false}
                    tick={{
                      fill: "#676f7b",
                      fontSize: 9,
                      fontFamily:
                        "IBM Plex Mono",
                    }}
                    dy={8}
                  />

                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{
                      fill: "#555d68",
                      fontSize: 8,
                      fontFamily:
                        "IBM Plex Mono",
                    }}
                    tickFormatter={(value) =>
                      `₹${value}B`
                    }
                    width={45}
                  />

                  <Tooltip
                    cursor={{
                      fill: "rgba(124, 156, 255, 0.04)",
                    }}
                    contentStyle={{
                      background:
                        "#151920",
                      border:
                        "1px solid #303641",
                      borderRadius: 6,
                      color: "#e8eaed",
                      fontSize: 10,
                    }}
                    formatter={(value) => [
                      `₹${Number(
                        value,
                      ).toFixed(2)}B`,
                      "Revenue",
                    ]}
                  />

                  <Bar
                    dataKey="revenue"
                    fill="#7c9cff"
                    radius={[
                      3,
                      3,
                      0,
                      0,
                    ]}
                    maxBarSize={42}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="chart-legend">
            <span>
              <i className="legend-line primary" />
              Average revenue
            </span>

            <span className="chart-note">
              Top 4 by ROA rank
            </span>
          </div>
        </div>

        <div className="panel quality-panel">
          <div className="panel-header">
            <div>
              <h2>
                Data connection
              </h2>

              <p>
                Live API and database
                status
              </p>
            </div>

            <span
              className={
                apiHealthy
                  ? "healthy-badge"
                  : "warning-badge"
              }
            >
              {loading
                ? "Checking"
                : apiHealthy
                  ? "Healthy"
                  : "Offline"}
            </span>
          </div>

          <div className="quality-score">
            <span className="quality-value">
              {loading
                ? "—"
                : apiHealthy
                  ? "100"
                  : "0"}
            </span>

            <span className="quality-percent">
              %
            </span>
          </div>

          <div className="quality-bar">
            <div
              style={{
                width: `${
                  loading
                    ? 40
                    : apiHealthy
                      ? 100
                      : 0
                }%`,
              }}
            />
          </div>

          <div className="quality-breakdown">
            <QualityRow
              label="API"
              value={
                loading
                  ? "Checking"
                  : apiHealthy
                    ? "Healthy"
                    : "Unavailable"
              }
            />

            <QualityRow
              label="Database"
              value={
                loading
                  ? "Checking"
                  : apiHealthy
                    ? "Ready"
                    : "Unavailable"
              }
            />

            <QualityRow
              label="Rankings"
              value={
                loading
                  ? "Loading"
                  : `${rankings.length} records`
              }
            />

            <QualityRow
              label="Industries"
              value={
                loading
                  ? "Loading"
                  : `${industries.length} records`
              }
            />
          </div>
        </div>
      </section>

      <section className="lower-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h2>
                Top companies
              </h2>

              <p>
                Ranked by return on assets
              </p>
            </div>

            <button
              className="panel-action"
              type="button"
            >
              See all
            </button>
          </div>

          <div className="company-list">
            {loading ? (
              <ListLoading />
            ) : topCompanies.length ===
              0 ? (
              <ListEmpty />
            ) : (
              topCompanies.map(
                (company, index) => (
                  <div
                    className="company-row"
                    key={
                      company.company_id
                    }
                  >
                    <span className="company-rank">
                      {String(
                        index + 1,
                      ).padStart(2, "0")}
                    </span>

                    <div className="company-info">
                      <strong>
                        {company.company_name}
                      </strong>

                      <span>
                        {company.ticker}
                        {" · "}
                        {
                          company.industry_name
                        }
                      </span>
                    </div>

                    <span className="company-metric">
                      {formatPercent(
                        company.avg_roa_pct,
                      )}
                    </span>
                  </div>
                ),
              )
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h2>
                Industry benchmarks
              </h2>

              <p>
                Average return on assets
              </p>
            </div>

            <button
              className="panel-action"
              type="button"
            >
              See all
            </button>
          </div>

          <div className="industry-list">
            {loading ? (
              <ListLoading />
            ) : topIndustries.length ===
              0 ? (
              <ListEmpty />
            ) : (
              topIndustries.map(
                (industry) => (
                  <div
                    className="industry-row"
                    key={
                      industry.industry_id
                    }
                  >
                    <div className="industry-info">
                      <span>
                        {
                          industry.industry_name
                        }
                      </span>

                      <small>
                        {
                          industry.company_count
                        }{" "}
                        companies
                      </small>
                    </div>

                    <strong>
                      {formatPercent(
                        industry.avg_roa_pct,
                      )}
                    </strong>
                  </div>
                ),
              )
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

function MetricCard({
  label,
  value,
  description,
}: {
  label: string;
  value: string;
  description: string;
}) {
  return (
    <div className="metric-card">
      <span className="metric-label">
        {label}
      </span>

      <div className="metric-value">
        {value}
      </div>

      <div className="metric-change-row">
        <span className="metric-description">
          {description}
        </span>
      </div>
    </div>
  );
}

function QualityRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="quality-row">
      <span>{label}</span>

      <strong>{value}</strong>
    </div>
  );
}

function ListLoading() {
  return (
    <div className="list-state">
      Loading live data...
    </div>
  );
}

function ListEmpty() {
  return (
    <div className="list-state">
      No data available.
    </div>
  );
}
