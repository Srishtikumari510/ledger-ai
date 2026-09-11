"""LLM-based field and table extraction from document text."""
import json
import re
from typing import Any, Optional

import google.generativeai as genai

from app.core.config import settings
from app.core.logging import logger
from app.services.ocr_service import PageText


_client_configured = False


def _ensure_client() -> None:
    global _client_configured
    if _client_configured:
        return
    if not settings.LLM_API_KEY:
        raise RuntimeError("LLM_API_KEY is not configured.")
    genai.configure(api_key=settings.LLM_API_KEY)
    _client_configured = True


SYSTEM_PROMPTS: dict[str, str] = {
    "invoice": """You are a financial document extraction engine.
Extract ALL invoice fields visible in the text. Return STRICT JSON.

Required keys (use null if absent, DO NOT invent):
- invoice_number, invoice_date, vendor_name, customer_name, currency,
  subtotal, tax_amount, discount, total_amount
- line_items: array of {description, quantity, unit_price, amount}
- any other visible fields (due_date, po_number, addresses, etc.)

Rules:
- Numbers must be plain numeric (no currency symbols, no commas).
- Parentheses like (123) mean negative.
- Each scalar field must include: {"value": <value>, "page_number": <int>, "evidence": "<short quote>"}.
- line_items entries use plain values (not wrapped in {value:...}).
""",
    "balance_sheet": """You are a financial document extraction engine.
Extract ALL Balance Sheet data. Return STRICT JSON.

Required keys (null if absent):
- periods (list of column headers like ["2024","2023"])
- currency, entity_name, statement_date
- total_assets: the reported "Total Assets" value (usually the LAST row in the asset section)
- total_liabilities: the reported "Total Capital and Liabilities" or "Total Liabilities" value
- total_equity: the equity-only subtotal if separately shown, else null
- line_items: array of {label, values: {period: amount}} for EVERY visible row,
  including "Total Capital and Liabilities" and "Total Assets" rows themselves.

IMPORTANT mappings for banks / consolidated statements:
- If only "Total Capital and Liabilities" appears (no separate "Total Liabilities"),
  set total_liabilities = that value AND total_equity = 0.
- If "Total Assets" appears, set total_assets = that value.

Each scalar field: {"value": <v>, "page_number": <int>, "evidence": "<quote>"}.
Numbers plain, parentheses negative, null if missing.
""",
    "profit_and_loss": """You are a financial document extraction engine.
Extract ALL Profit & Loss data. Return STRICT JSON.

Required keys (null if absent):
- periods, currency, entity_name, statement_date
- revenue, cost_of_sales, gross_profit, operating_expenses,
  operating_profit, tax, net_profit
- line_items: array of {label, values: {period: amount}}

Each scalar field: {"value": <v>, "page_number": <int>, "evidence": "<quote>"}.
Numbers plain, parentheses negative, null if missing.
""",
    "cash_flow_statement": """You are a financial document extraction engine.
Extract ALL Cash Flow Statement data. Return STRICT JSON.

Required keys (null if absent):
- periods, currency, entity_name, statement_date
- operating_cash_flow, investing_cash_flow, financing_cash_flow,
  opening_cash, net_change_in_cash, closing_cash
- line_items: array of {label, values: {period: amount}}

Each scalar field: {"value": <v>, "page_number": <int>, "evidence": "<quote>"}.
Numbers plain, parentheses negative, null if missing.
""",
}


def _build_prompt(document_type: str, pages: list[PageText]) -> str:
    system = SYSTEM_PROMPTS.get(document_type, "")
    text_block = "\n\n".join(
        f"[PAGE {p.page_number}]\n{p.text}" for p in pages
    )
    return f"""{system}

--- DOCUMENT TEXT START ---
{text_block}
--- DOCUMENT TEXT END ---

Return ONLY the JSON object. No markdown fences, no commentary.
"""


def _parse_json_safely(raw: str) -> dict[str, Any]:
    """Strip markdown fences and parse."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1:
        cleaned = cleaned[start : end + 1]

    return json.loads(cleaned)


def extract_fields(document_type: str, pages: list[PageText]) -> dict[str, Any]:
    """Call LLM and return parsed extraction dict."""
    _ensure_client()

    prompt = _build_prompt(document_type, pages)
    model_name = settings.LLM_MODEL or "gemini-2.5-flash"

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        raw_text = response.text
    except Exception as e:
        logger.exception("LLM call failed | error=%s", e)
        raise RuntimeError(f"LLM extraction failed: {e}") from e

    try:
        parsed = _parse_json_safely(raw_text)
    except Exception as e:
        logger.exception("Failed to parse LLM JSON | raw=%s", raw_text[:500])
        raise RuntimeError(f"LLM returned non-JSON output: {e}") from e

    logger.info("LLM extraction OK | keys=%s", list(parsed.keys()))
    return parsed