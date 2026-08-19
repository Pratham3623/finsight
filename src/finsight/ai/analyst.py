from __future__ import annotations

import json
import os
from typing import Any

import requests


SYSTEM_PROMPT = """
You are FinSight AI, a financial analytics assistant.

Your job is to explain financial information calculated by
the FinSight analytics platform.

CRITICAL GROUNDING RULES:

1. ONLY use information contained in the supplied FinSight data.
2. NEVER invent, estimate, assume, or hallucinate financial figures.
3. The deterministic_analysis section is authoritative.
4. Any metric_leaders section is authoritative.
5. Any overall_ranking section is authoritative.
6. Any strongest_company section is authoritative.
7. Never recalculate a metric when FinSight has already calculated it.
8. Never replace a deterministic FinSight result with your own calculation.
9. If information is missing or null, say that it is unavailable.
10. If the supplied data cannot answer the exact question, say so directly.
11. Do not answer a different or merely related question just because
    the supplied data happens to contain information about it.

FINANCIAL TERMINOLOGY:

12. "absolute_change" is the raw numerical/currency difference
    between the first and latest value.

13. "percentage_change" is the percentage change between the first
    and latest value.

14. "change_percentage_points" is the difference between two
    percentage-based metrics expressed in percentage points.

15. Never call a percentage change an absolute change.
16. Never call a percentage-point change a percentage change.
17. Preserve the terminology used by FinSight.

TREND RULES:

18. When discussing a trend, use the deterministic trend values
    supplied by FinSight.

19. Do not independently calculate CAGR, percentage changes,
    percentage-point changes, rankings, or scores.

20. If FinSight provides first_value, latest_value, and a calculated
    change, use those supplied values.

COMPARISON RULES:

21. For company comparisons, use the supplied company-level
    comparison data.

22. metric_leaders contains deterministic winners for individual
    metrics. Treat those results as authoritative.

23. overall_ranking contains the deterministic relative ranking.
    Treat it as authoritative.

24. strongest_company contains the deterministic overall leader.
    Treat it as authoritative.

25. NEVER search historical periods yourself to determine which
    company has the highest metric when metric_leaders already
    provides that answer.

26. NEVER substitute a historical quarter for a company-level
    comparison.

27. Clearly distinguish:
    - metric leader
    - trend
    - deterministic classification
    - overall relative ranking
    - your interpretation

28. The overall comparison score is a relative FinSight comparison
    aid, NOT an investment recommendation.

FINANCIAL SAFETY:

29. Do not provide investment advice.
30. Do not tell the user to buy, sell, or hold securities.
31. Do not introduce external financial information.
32. Do not claim facts that are absent from the supplied context.

RESPONSE STYLE:

33. Directly answer the user's exact question.
34. Use concise, professional financial language.
35. Use headings and bullet points when they improve readability.
36. Avoid unnecessary disclaimers.
37. Clearly distinguish factual FinSight results from interpretation.
"""


class FinSightAnalyst:
    """Local LLM-powered financial analysis service using Ollama."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model = model or os.getenv(
            "OLLAMA_MODEL",
            "llama3:latest",
        )

        self.base_url = (
            base_url
            or os.getenv(
                "OLLAMA_BASE_URL",
                "http://host.docker.internal:11434",
            )
        ).rstrip("/")

    def analyze(
        self,
        question: str,
        financial_context: dict[str, Any],
    ) -> str:
        """Generate grounded financial analysis using Ollama."""

        if not question.strip():
            raise ValueError(
                "Question must not be empty."
            )

        if not financial_context:
            raise ValueError(
                "Financial context must not be empty."
            )

        context = json.dumps(
            financial_context,
            indent=2,
            default=str,
        )

        user_prompt = f"""
FINANCIAL DATA SUPPLIED BY FINSIGHT
===================================

{context}

USER QUESTION
=============

{question}

INSTRUCTIONS
============

Answer the user's exact question using ONLY the supplied
FinSight data.

The deterministic FinSight calculations are authoritative.

If this is a company comparison:

1. Use the "companies" section for company-level facts.
2. Use "metric_leaders" for metric-specific winners.
3. Use "overall_ranking" for the relative overall ranking.
4. Use "strongest_company" for the deterministic overall leader.
5. Do NOT inspect historical periods to independently determine
   a winner when the deterministic comparison fields already
   provide the answer.

If this is a trend question:

1. Use "deterministic_analysis".
2. Use the supplied trend values.
3. Do not recalculate them.

When reporting changes:

- absolute_change = raw numerical/currency difference
- percentage_change = percentage change
- change_percentage_points = percentage-point difference

Keep these concepts strictly separate.

If a required value is missing, say it is unavailable.

Do not fabricate a number.

Give a concise, professional answer.
"""

        payload = {
            "model": self.model,
            "prompt": (
                SYSTEM_PROMPT
                + "\n\n"
                + user_prompt
            ),
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,
                "seed": 42,
                "num_ctx": 8192,
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120,
            )
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                f"Could not reach Ollama at {self.base_url}. "
                "Confirm that Ollama is running and reachable "
                "from the API container."
            ) from exc

        except requests.exceptions.Timeout as exc:
            raise RuntimeError(
                f"Ollama request to model '{self.model}' "
                "timed out after 120 seconds."
            ) from exc

        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                f"Ollama request failed: {exc}"
            ) from exc

        if response.status_code != 200:
            raise RuntimeError(
                "Ollama request failed with HTTP "
                f"{response.status_code}: {response.text}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "Ollama returned an invalid JSON response."
            ) from exc

        answer = data.get("response")

        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return answer.strip()
