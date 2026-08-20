import json
import os
from typing import Any

import requests


SYSTEM_PROMPT = """
You are FinSight Analyst, a financial analysis assistant inside
the FinSight financial intelligence platform.

Your job is to interpret ONLY the financial data supplied by
FinSight and answer the user's question accurately.

CORE RULES:

1. Use only the supplied FinSight financial context.
2. Never invent financial data.
3. Never introduce external financial information.
4. If a required value is missing, say it is unavailable.
5. Deterministic FinSight calculations are authoritative.
6. Do not independently recalculate deterministic comparison
   or trend results.
7. Clearly distinguish facts from interpretation.

COMPARISONS:

8. Use the "companies" section for company-level facts.
9. Use "metric_leaders" for metric-specific winners.
10. Use "overall_ranking" for relative overall ranking.
11. Use "strongest_company" for the deterministic overall leader.
12. Never substitute a historical period for a company-level
    comparison.
13. Do not independently determine a comparison winner when
    deterministic comparison fields already provide the answer.

TRENDS:

14. Use "deterministic_analysis".
15. Use the supplied trend values.
16. Do not independently recalculate deterministic trend values.

CHANGES:

17. absolute_change means the raw numerical difference.
18. percentage_change means percentage change.
19. change_percentage_points means percentage-point difference.
20. Keep these concepts strictly separate.

FINANCIAL SAFETY:

21. Do not provide investment advice.
22. Do not tell the user to buy, sell, or hold securities.
23. Do not claim facts absent from the supplied context.

RESPONSE STYLE:

24. Directly answer the user's exact question.
25. Use concise, professional financial language.
26. Use headings and bullet points when useful.
27. Avoid unnecessary disclaimers.
28. Clearly distinguish factual FinSight results from interpretation.
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
   a winner when deterministic comparison fields already provide
   the answer.

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
                "num_predict": 500,
            },
        }

        session = requests.Session()

        # Never use system proxy variables for the local Ollama
        # connection.
        session.trust_env = False

        ollama_url = (
            f"{self.base_url}/api/generate"
        )

        print(
            "========== FINSIGHT OLLAMA REQUEST =========="
        )
        print(
            f"PID: {os.getpid()}"
        )
        print(
            f"MODEL: {self.model}"
        )
        print(
            f"BASE URL: {self.base_url}"
        )
        print(
            f"OLLAMA URL: {ollama_url}"
        )
        print(
            f"CONTEXT LENGTH: {len(context)}"
        )
        print(
            f"PROMPT LENGTH: "
            f"{len(SYSTEM_PROMPT) + len(user_prompt)}"
        )
        print(
            f"TRUST ENV: {session.trust_env}"
        )
        print(
            "=============================================="
        )

        try:
            response = session.post(
                ollama_url,
                json=payload,
                timeout=(10, 300),
            )

        except requests.exceptions.ConnectionError as exc:

            print(
                "========== OLLAMA CONNECTION ERROR =========="
            )
            print(
                f"TYPE: {type(exc).__name__}"
            )
            print(
                f"ERROR: {exc}"
            )
            print(
                f"ARGS: {exc.args}"
            )

            if exc.__cause__:
                print(
                    f"CAUSE: {repr(exc.__cause__)}"
                )

            if exc.__context__:
                print(
                    f"CONTEXT: {repr(exc.__context__)}"
                )

            print(
                "=============================================="
            )

            raise RuntimeError(
                "Could not reach Ollama at "
                f"{self.base_url}. "
                f"Underlying connection error: {exc!r}"
            ) from exc

        except requests.exceptions.Timeout as exc:

            print(
                "========== OLLAMA TIMEOUT ERROR ============="
            )
            print(
                f"TYPE: {type(exc).__name__}"
            )
            print(
                f"ERROR: {exc}"
            )
            print(
                "=============================================="
            )

            raise RuntimeError(
                f"Ollama request to model "
                f"'{self.model}' timed out after "
                "300 seconds."
            ) from exc

        except requests.exceptions.RequestException as exc:

            print(
                "========== OLLAMA REQUEST ERROR ============"
            )
            print(
                f"TYPE: {type(exc).__name__}"
            )
            print(
                f"ERROR: {exc}"
            )
            print(
                f"ARGS: {exc.args}"
            )
            print(
                "=============================================="
            )

            raise RuntimeError(
                f"Ollama request failed: {exc!r}"
            ) from exc

        print(
            "========== OLLAMA RESPONSE ================="
        )
        print(
            f"STATUS: {response.status_code}"
        )
        print(
            f"RESPONSE LENGTH: {len(response.text)}"
        )
        print(
            f"RESPONSE PREVIEW: {response.text[:1000]}"
        )
        print(
            "=============================================="
        )

        if response.status_code != 200:
            raise RuntimeError(
                "Ollama request failed with HTTP "
                f"{response.status_code}: "
                f"{response.text}"
            )

        try:
            data = response.json()

        except ValueError as exc:

            raise RuntimeError(
                "Ollama returned an invalid JSON response."
            ) from exc

        answer = data.get("response")

        if not isinstance(answer, str):
            raise RuntimeError(
                "Ollama returned an invalid response."
            )

        answer = answer.strip()

        if not answer:
            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return answer
