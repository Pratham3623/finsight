import {
  BrainCircuit,
  Building2,
  ChevronDown,
  GitCompare,
  Loader2,
  Send,
  Sparkles,
  TrendingUp,
  WalletCards,
} from "lucide-react";
import { useEffect, useState } from "react";

import {
  analyzeCompany,
  analyzePortfolio,
  compareCompanies,
} from "../api/ai";

import { getCompanyRankings } from "../api/companies";

import type {
  AIAnalysisResponse,
  AIPortfolioAnalysisResponse,
  CompanyRanking,
} from "../types/api";

import "./AIAnalystPage.css";

type AnalystMode =
  | "company"
  | "portfolio"
  | "compare";

const DEFAULT_QUESTIONS = [
  "Analyze the company's financial health.",
  "What are the biggest strengths and weaknesses?",
  "How has profitability changed over time?",
  "Is the company financially efficient?",
];

function formatAnswer(
  answer: string,
): string[] {
  return answer
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
}

export default function AIAnalystPage() {
  const [mode, setMode] =
    useState<AnalystMode>("company");

  const [rankings, setRankings] =
    useState<CompanyRanking[]>([]);

  const [companyId, setCompanyId] =
    useState<number>(184);

  const [compareIds, setCompareIds] =
    useState<number[]>([184, 708]);

  const [question, setQuestion] =
    useState("");

  const [answer, setAnswer] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [loadingCompanies, setLoadingCompanies] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function loadCompanies() {
      try {
        const data =
          await getCompanyRankings(100);

        if (!mounted) {
          return;
        }

        setRankings(data);

        if (data.length > 0) {
          setCompanyId(
            data[0].company_id,
          );

          if (data.length >= 2) {
            setCompareIds([
              data[0].company_id,
              data[1].company_id,
            ]);
          }
        }
      } catch {
        if (mounted) {
          setError(
            "Unable to load companies for the analyst.",
          );
        }
      } finally {
        if (mounted) {
          setLoadingCompanies(false);
        }
      }
    }

    void loadCompanies();

    return () => {
      mounted = false;
    };
  }, []);

  function switchMode(
    nextMode: AnalystMode,
  ) {
    setMode(nextMode);
    setAnswer(null);
    setError(null);
    setQuestion("");
  }

  function toggleCompareCompany(
    id: number,
  ) {
    setCompareIds((current) => {
      if (current.includes(id)) {
        if (current.length <= 2) {
          return current;
        }

        return current.filter(
          (companyIdValue) =>
            companyIdValue !== id,
        );
      }

      if (current.length >= 5) {
        return current;
      }

      return [...current, id];
    });
  }

  async function runAnalysis() {
    const trimmedQuestion =
      question.trim();

    if (!trimmedQuestion) {
      setError(
        "Enter a question for the AI analyst.",
      );
      return;
    }

    if (
      mode === "compare" &&
      compareIds.length < 2
    ) {
      setError(
        "Select at least two companies to compare.",
      );
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setAnswer(null);

      let response:
        | AIAnalysisResponse
        | AIPortfolioAnalysisResponse;

      if (mode === "company") {
        response = await analyzeCompany({
          company_id: companyId,
          question: trimmedQuestion,
        });
      } else if (mode === "portfolio") {
        response = await analyzePortfolio({
          question: trimmedQuestion,
          limit: 10,
        });
      } else {
        const responseComparison =
          await compareCompanies({
            company_ids: compareIds,
            question: trimmedQuestion,
          });

        setAnswer(
          responseComparison.answer,
        );

        return;
      }

      setAnswer(response.answer);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "The AI analyst could not complete the analysis.",
      );
    } finally {
      setLoading(false);
    }
  }

  const selectedCompany =
    rankings.find(
      (company) =>
        company.company_id === companyId,
    );

  return (
    <div className="ai-analyst-page">
      <section className="ai-header">
        <div>
          <div className="ai-eyebrow">
            <Sparkles size={12} />
            INTELLIGENCE
          </div>

          <h1>AI Analyst</h1>

          <p>
            Ask FinSight questions about
            company performance, portfolios,
            and competitive positioning.
          </p>
        </div>

        <div className="ai-header-icon">
          <BrainCircuit size={22} />
        </div>
      </section>

      <section className="ai-mode-tabs">
        <button
          type="button"
          className={
            mode === "company"
              ? "ai-mode-active"
              : ""
          }
          onClick={() =>
            switchMode("company")
          }
        >
          <Building2 size={14} />
          Company
        </button>

        <button
          type="button"
          className={
            mode === "portfolio"
              ? "ai-mode-active"
              : ""
          }
          onClick={() =>
            switchMode("portfolio")
          }
        >
          <WalletCards size={14} />
          Portfolio
        </button>

        <button
          type="button"
          className={
            mode === "compare"
              ? "ai-mode-active"
              : ""
          }
          onClick={() =>
            switchMode("compare")
          }
        >
          <GitCompare size={14} />
          Compare
        </button>
      </section>

      <section className="ai-workspace">
        <div className="ai-query-panel">
          <div className="ai-panel-label">
            ANALYSIS REQUEST
          </div>

          {mode === "company" && (
            <div className="ai-company-selector">
              <label htmlFor="company-select">
                Company
              </label>

              <div className="ai-select-wrapper">
                <select
                  id="company-select"
                  value={companyId}
                  disabled={loadingCompanies}
                  onChange={(event) =>
                    setCompanyId(
                      Number(
                        event.target.value,
                      ),
                    )
                  }
                >
                  {rankings.map(
                    (company) => (
                      <option
                        key={
                          company.company_id
                        }
                        value={
                          company.company_id
                        }
                      >
                        {company.ticker} —{" "}
                        {
                          company.company_name
                        }
                      </option>
                    ),
                  )}
                </select>

                <ChevronDown
                  size={14}
                />
              </div>

              {selectedCompany && (
                <div className="ai-company-context">
                  <span>
                    {
                      selectedCompany.industry_name
                    }
                  </span>

                  <span>
                    ROA{" "}
                    {selectedCompany.avg_roa_pct.toFixed(
                      1,
                    )}
                    %
                  </span>

                  <span>
                    Margin{" "}
                    {selectedCompany.avg_net_profit_margin_pct.toFixed(
                      1,
                    )}
                    %
                  </span>
                </div>
              )}
            </div>
          )}

          {mode === "portfolio" && (
            <div className="ai-mode-description">
              <WalletCards size={16} />

              <div>
                <strong>
                  Portfolio analysis
                </strong>

                <span>
                  Analyze the top tracked
                  companies together.
                </span>
              </div>
            </div>
          )}

          {mode === "compare" && (
            <div className="ai-compare-selector">
              <div className="ai-compare-title">
                <span>
                  Select companies
                </span>

                <small>
                  {compareIds.length}/5
                </small>
              </div>

              <div className="ai-company-list">
                {rankings.map(
                  (company) => {
                    const selected =
                      compareIds.includes(
                        company.company_id,
                      );

                    return (
                      <button
                        key={
                          company.company_id
                        }
                        type="button"
                        className={
                          selected
                            ? "ai-company-option ai-company-option-selected"
                            : "ai-company-option"
                        }
                        onClick={() =>
                          toggleCompareCompany(
                            company.company_id,
                          )
                        }
                      >
                        <span>
                          {company.ticker}
                        </span>

                        <small>
                          {
                            company.company_name
                          }
                        </small>

                        {selected && (
                          <span className="ai-selected-dot" />
                        )}
                      </button>
                    );
                  },
                )}
              </div>
            </div>
          )}

          <div className="ai-question">
            <label htmlFor="ai-question">
              Question
            </label>

            <textarea
              id="ai-question"
              value={question}
              onChange={(event) =>
                setQuestion(
                  event.target.value,
                )
              }
              placeholder={
                mode === "compare"
                  ? "Which company has the stronger financial profile and why?"
                  : mode === "portfolio"
                    ? "What are the strongest and weakest companies in the portfolio?"
                    : "Ask a financial question about this company..."
              }
              rows={7}
              maxLength={4000}
            />

            <div className="ai-question-footer">
              <span>
                {question.length}/4000
              </span>

              <button
                type="button"
                className="ai-run-button"
                disabled={loading}
                onClick={() =>
                  void runAnalysis()
                }
              >
                {loading ? (
                  <>
                    <Loader2
                      size={14}
                      className="ai-spinner"
                    />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Send size={14} />
                    Run analysis
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="ai-suggestions">
            <span>
              Suggested questions
            </span>

            <div>
              {DEFAULT_QUESTIONS.map(
                (suggestion) => (
                  <button
                    type="button"
                    key={suggestion}
                    onClick={() =>
                      setQuestion(
                        suggestion,
                      )
                    }
                  >
                    {suggestion}
                  </button>
                ),
              )}
            </div>
          </div>
        </div>

        <div className="ai-answer-panel">
          <div className="ai-answer-header">
            <div>
              <div className="ai-panel-label">
                ANALYST OUTPUT
              </div>

              <h2>
                {answer
                  ? "Financial analysis"
                  : "Ready for analysis"}
              </h2>
            </div>

            <div className="ai-status">
              <span />
              AI
            </div>
          </div>

          {error && (
            <div className="ai-error">
              <strong>
                Analysis failed
              </strong>

              <span>{error}</span>
            </div>
          )}

          {loading && (
            <div className="ai-loading">
              <div className="ai-loading-icon">
                <BrainCircuit
                  size={24}
                />
              </div>

              <strong>
                FinSight is analyzing the
                financial data...
              </strong>

              <span>
                Reviewing the selected
                context and generating
                an evidence-based response.
              </span>
            </div>
          )}

          {!loading && !answer && !error && (
            <div className="ai-empty">
              <div className="ai-empty-icon">
                <BrainCircuit
                  size={25}
                />
              </div>

              <h3>
                Ask your first question
              </h3>

              <p>
                Select a company or analysis
                mode, enter a question, and
                FinSight will generate an
                analysis using your financial
                data.
              </p>

              <div className="ai-capabilities">
                <div>
                  <TrendingUp size={14} />
                  Financial trends
                </div>

                <div>
                  <BarChartIcon />
                  Profitability
                </div>

                <div>
                  <GitCompare size={14} />
                  Comparisons
                </div>
              </div>
            </div>
          )}

          {!loading && answer && (
            <div className="ai-answer">
              {formatAnswer(answer).map(
                (line, index) => (
                  <p
                    key={`${index}-${line.slice(
                      0,
                      15,
                    )}`}
                  >
                    {line}
                  </p>
                ),
              )}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function BarChartIcon() {
  return (
    <span className="ai-bar-chart-icon">
      <span />
      <span />
      <span />
    </span>
  );
}
