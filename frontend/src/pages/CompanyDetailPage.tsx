import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  Building2,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  getCompanyMetrics,
  getCompanySummary,
} from "../api/companies";

import type {
  CompanyMetric,
  CompanySummary,
} from "../types/api";

import "./CompanyDetailPage.css";

function formatCurrency(value: number): string {
  const absolute = Math.abs(value);

  if (absolute >= 1_000_000_000) {
    return `₹${(value / 1_000_000_000).toFixed(2)}B`;
  }

  if (absolute >= 1_000_000) {
    return `₹${(value / 1_000_000).toFixed(1)}M`;
  }

  if (absolute >= 1_000) {
    return `₹${(value / 1_000).toFixed(1)}K`;
  }

  return `₹${value.toFixed(0)}`;
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

function formatDate(value: string): string {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatQuarter(
  metric: CompanyMetric,
): string {
  return `${metric.fiscal_year} Q${metric.fiscal_quarter}`;
}

export default function CompanyDetailPage() {
  const { companyId } = useParams();

  const parsedCompanyId = Number(companyId);

  const [summary, setSummary] =
    useState<CompanySummary | null>(null);

  const [metrics, setMetrics] =
    useState<CompanyMetric[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function loadCompany() {
      if (
        !Number.isInteger(parsedCompanyId) ||
        parsedCompanyId <= 0
      ) {
        setError("Invalid company ID.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const [summaryData, metricsData] =
          await Promise.all([
            getCompanySummary(parsedCompanyId),
            getCompanyMetrics(parsedCompanyId),
          ]);

        if (!mounted) {
          return;
        }

        setSummary(summaryData);
        setMetrics(metricsData);
      } catch (err) {
        if (!mounted) {
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Unable to load company data.",
        );
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void loadCompany();

    return () => {
      mounted = false;
    };
  }, [parsedCompanyId]);

  const chartData = useMemo(() => {
    return metrics.map((metric) => ({
      period: formatQuarter(metric),
      revenue:
        metric.revenue / 1_000_000_000,
      netIncome:
        metric.net_income / 1_000_000_000,
    }));
  }, [metrics]);

  const revenueChange = useMemo(() => {
    if (metrics.length < 2) {
      return null;
    }

    const first = metrics[0].revenue;
    const last =
      metrics[metrics.length - 1].revenue;

    if (first === 0) {
      return null;
    }

    return (
      ((last - first) / Math.abs(first)) *
      100
    );
  }, [metrics]);

  if (loading) {
    return (
      <div className="company-detail-page">
        <div className="company-detail-loading">
          <div className="company-loading-bar" />
          <span>Loading company data...</span>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="company-detail-page">
        <div className="company-detail-error">
          <strong>
            Unable to load company
          </strong>

          <span>
            {error ?? "Company not found."}
          </span>

          <Link
            to="/companies"
            className="company-back-link"
          >
            <ArrowLeft size={14} />
            Back to companies
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="company-detail-page">
      {/* Header */}
      <div className="company-detail-top">
        <Link
          to="/companies"
          className="company-back-link"
        >
          <ArrowLeft size={14} />
          Companies
        </Link>
      </div>

      <section className="company-hero">
        <div className="company-identity">
          <div className="company-logo">
            <Building2 size={20} />
          </div>

          <div className="company-identity-copy">
            <div className="company-meta">
              <span>{summary.ticker}</span>
              <span className="company-meta-dot">
                •
              </span>
              <span>{summary.industry}</span>
            </div>

            <h1>
              {summary.company_name}
            </h1>

            <p>
              Financial performance through{" "}
              {formatDate(
                summary.latest_period,
              )}
            </p>
          </div>
        </div>

        <div className="company-reference">
          <span>COMPANY ID</span>
          <strong>
            #{summary.company_id}
          </strong>
        </div>
      </section>

      {/* KPI cards */}
      <section className="company-kpi-grid">
        <KpiCard
          label="Latest revenue"
          value={formatCurrency(
            summary.latest_revenue,
          )}
          detail={
            revenueChange === null
              ? `${summary.periods_available} periods available`
              : `${revenueChange >= 0 ? "+" : ""}${revenueChange.toFixed(1)}% since first period`
          }
          positive={
            revenueChange === null
              ? undefined
              : revenueChange >= 0
          }
        />

        <KpiCard
          label="Net income"
          value={formatCurrency(
            summary.latest_net_income,
          )}
          detail="Latest reported period"
        />

        <KpiCard
          label="Net profit margin"
          value={formatPercent(
            summary.latest_net_profit_margin_pct,
          )}
          detail="Latest reported period"
        />

        <KpiCard
          label="Return on assets"
          value={formatPercent(
            summary.latest_roa_pct,
          )}
          detail="Latest reported period"
        />
      </section>

      {/* Main analysis area */}
      <section className="company-analysis-grid">
        <div className="company-card company-chart-card">
          <div className="company-card-header">
            <div>
              <h2>
                Revenue & net income
              </h2>

              <p>
                Quarterly financial history
              </p>
            </div>

            <span className="company-card-meta">
              {metrics.length} periods
            </span>
          </div>

          <div className="company-chart">
            {chartData.length === 0 ? (
              <div className="company-empty">
                No financial history
                available.
              </div>
            ) : (
              <ResponsiveContainer
                width="100%"
                height="100%"
              >
                <LineChart
                  data={chartData}
                  margin={{
                    top: 15,
                    right: 12,
                    left: 4,
                    bottom: 4,
                  }}
                >
                  <CartesianGrid
                    vertical={false}
                    stroke="#20252c"
                    strokeDasharray="2 4"
                  />

                  <XAxis
                    dataKey="period"
                    axisLine={false}
                    tickLine={false}
                    tick={{
                      fill: "#69727e",
                      fontSize: 9,
                    }}
                    dy={8}
                  />

                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{
                      fill: "#69727e",
                      fontSize: 9,
                    }}
                    tickFormatter={(value) =>
                      `₹${value}B`
                    }
                    width={48}
                  />

                  <Tooltip
                    contentStyle={{
                      background:
                        "#171a1f",
                      border:
                        "1px solid #303640",
                      borderRadius: 6,
                      color: "#f0f2f5",
                      fontSize: 10,
                    }}
                    formatter={(
                      value,
                      name,
                    ) => [
                      `₹${Number(
                        value,
                      ).toFixed(2)}B`,
                      name === "revenue"
                        ? "Revenue"
                        : "Net income",
                    ]}
                  />

                  <Line
                    type="monotone"
                    dataKey="revenue"
                    stroke="#7896ee"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{
                      r: 4,
                    }}
                  />

                  <Line
                    type="monotone"
                    dataKey="netIncome"
                    stroke="#58b990"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{
                      r: 4,
                    }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="company-chart-legend">
            <span>
              <i className="legend-revenue" />
              Revenue
            </span>

            <span>
              <i className="legend-income" />
              Net income
            </span>
          </div>
        </div>

        <div className="company-card company-health-card">
          <div className="company-card-header">
            <div>
              <h2>
                Financial health
              </h2>

              <p>
                Latest reported metrics
              </p>
            </div>
          </div>

          <HealthMetric
            label="Net profit margin"
            value={
              summary.latest_net_profit_margin_pct
            }
            suffix="%"
          />

          <HealthMetric
            label="Return on assets"
            value={summary.latest_roa_pct}
            suffix="%"
          />

          <HealthMetric
            label="Debt / assets"
            value={
              summary.latest_debt_to_assets_pct
            }
            suffix="%"
            inverse
          />

          <div className="company-period-count">
            <span>
              Available financial periods
            </span>

            <strong>
              {summary.periods_available}
            </strong>
          </div>
        </div>
      </section>

      {/* Financial history */}
      <section className="company-card company-history-card">
        <div className="company-card-header">
          <div>
            <h2>
              Financial history
            </h2>

            <p>
              Detailed quarterly metrics
            </p>
          </div>

          <span className="company-card-meta">
            {metrics.length} observations
          </span>
        </div>

        <div className="company-table-scroll">
          <table className="company-financial-table">
            <thead>
              <tr>
                <th className="period-column">
                  Period
                </th>
                <th>Revenue</th>
                <th>Net income</th>
                <th>Net margin</th>
                <th>
                  Operating margin
                </th>
                <th>ROA</th>
                <th>
                  Debt / assets
                </th>
                <th>
                  Cash flow margin
                </th>
              </tr>
            </thead>

            <tbody>
              {[...metrics]
                .reverse()
                .map((metric) => (
                  <tr
                    key={
                      metric.financial_id
                    }
                  >
                    <td className="period-cell">
                      <strong>
                        {formatQuarter(
                          metric,
                        )}
                      </strong>

                      <span>
                        {formatDate(
                          metric.period_end_date,
                        )}
                      </span>
                    </td>

                    <td>
                      {formatCurrency(
                        metric.revenue,
                      )}
                    </td>

                    <td>
                      {formatCurrency(
                        metric.net_income,
                      )}
                    </td>

                    <td>
                      {formatPercent(
                        metric.net_profit_margin_pct,
                      )}
                    </td>

                    <td>
                      {formatPercent(
                        metric.operating_margin_pct,
                      )}
                    </td>

                    <td className="positive-value">
                      {formatPercent(
                        metric.roa_pct,
                      )}
                    </td>

                    <td>
                      {formatPercent(
                        metric.debt_to_assets_pct,
                      )}
                    </td>

                    <td>
                      {formatPercent(
                        metric.operating_cash_flow_margin_pct,
                      )}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function KpiCard({
  label,
  value,
  detail,
  positive,
}: {
  label: string;
  value: string;
  detail: string;
  positive?: boolean;
}) {
  return (
    <div className="company-kpi-card">
      <span className="company-kpi-label">
        {label}
      </span>

      <strong className="company-kpi-value">
        {value}
      </strong>

      <div className="company-kpi-detail">
        {positive !== undefined && (
          <span
            className={
              positive
                ? "kpi-positive-icon"
                : "kpi-negative-icon"
            }
          >
            {positive ? (
              <TrendingUp size={11} />
            ) : (
              <TrendingDown size={11} />
            )}
          </span>
        )}

        <span
          className={
            positive === true
              ? "kpi-positive-text"
              : positive === false
                ? "kpi-negative-text"
                : ""
          }
        >
          {detail}
        </span>
      </div>
    </div>
  );
}

function HealthMetric({
  label,
  value,
  suffix,
  inverse = false,
}: {
  label: string;
  value: number;
  suffix: string;
  inverse?: boolean;
}) {
  const normalized = Math.max(
    0,
    Math.min(
      100,
      inverse ? 100 - value : value,
    ),
  );

  return (
    <div className="health-metric">
      <div className="health-metric-heading">
        <span>{label}</span>

        <strong>
          {value.toFixed(1)}
          {suffix}
        </strong>
      </div>

      <div className="health-meter">
        <div
          style={{
            width: `${normalized}%`,
          }}
        />
      </div>
    </div>
  );
}
