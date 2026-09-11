"""Financial validation rules per document type."""
from typing import Any, Optional

from app.core.config import settings
from app.core.logging import logger
from app.schemas.extraction import ValidationCheck, ValidationResult


def _num(x: Any) -> Optional[float]:
    """Coerce value to float, handling None, strings, wrapped objects."""
    if x is None:
        return None
    if isinstance(x, dict):
        x = x.get("value")
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip().replace(",", "").replace("$", "").replace("USD", "").strip()
        neg = s.startswith("(") and s.endswith(")")
        s = s.strip("()")
        try:
            v = float(s)
            return -v if neg else v
        except ValueError:
            return None
    return None


def _get(extracted: dict, key: str) -> Any:
    """
    Get raw value from extracted dict, unwrapping {value: ...} wrapper.
    May return a scalar, a per-period dict, or None.
    """
    raw = extracted.get(key)
    if isinstance(raw, dict) and "value" in raw:
        return raw.get("value")
    return raw


def _get_scalar(extracted: dict, key: str) -> Optional[float]:
    """Force a scalar. If value is a per-period dict, returns None."""
    v = _get(extracted, key)
    if isinstance(v, dict):
        return None
    return _num(v)


def _get_period(extracted: dict, key: str, period: str) -> Optional[float]:
    """Get value for a specific period, if value is a per-period dict."""
    v = _get(extracted, key)
    if isinstance(v, dict):
        return _num(v.get(period))
    return _num(v)


def _mk_check(
    name: str,
    formula: str,
    operands: dict[str, Any],
    calculated: Optional[float],
    reported: Optional[float],
) -> ValidationCheck:
    if calculated is None or reported is None:
        return ValidationCheck(
            name=name,
            formula=formula,
            operands=operands,
            calculated_value=calculated,
            reported_value=reported,
            variance=None,
            status="NOT_APPLICABLE",
            message="Required operands missing.",
        )

    variance = round(calculated - reported, 4)
    tolerance = max(settings.VALIDATION_TOLERANCE, abs(reported) * 0.001)
    status = "PASS" if abs(variance) <= tolerance else "FAILED"
    return ValidationCheck(
        name=name,
        formula=formula,
        operands=operands,
        calculated_value=round(calculated, 4),
        reported_value=round(reported, 4),
        variance=variance,
        status=status,
    )


def _finalize(checks: list[ValidationCheck]) -> ValidationResult:
    applicable = [c for c in checks if c.status in ("PASS", "FAILED")]
    if not applicable:
        overall = "NOT_APPLICABLE"
    elif all(c.status == "PASS" for c in applicable):
        overall = "PASS"
    else:
        overall = "FAILED"

    issues = [f"{c.name}: {c.status}" for c in applicable if c.status == "FAILED"]
    return ValidationResult(checks=checks, overall_status=overall, issues=issues)


def _get_periods(extracted: dict) -> list[str]:
    """Return list of periods, or [''] for a single-period doc."""
    periods = extracted.get("periods")
    if isinstance(periods, list) and periods:
        return [str(p) for p in periods]
    return [""]


# ---------- INVOICE ----------

def validate_invoice(extracted: dict) -> ValidationResult:
    checks: list[ValidationCheck] = []

    subtotal = _get_scalar(extracted, "subtotal")
    tax = _get_scalar(extracted, "tax_amount")
    discount = _get_scalar(extracted, "discount") or 0.0
    total = _get_scalar(extracted, "total_amount")

    if subtotal is not None and tax is not None and total is not None:
        calc = subtotal + tax - discount
        checks.append(_mk_check(
            "invoice_total_check",
            "subtotal + tax_amount - discount",
            {"subtotal": subtotal, "tax_amount": tax, "discount": discount},
            calc,
            total,
        ))

    line_items = extracted.get("line_items") or []
    for idx, item in enumerate(line_items, start=1):
        if not isinstance(item, dict):
            continue
        q = _num(item.get("quantity"))
        p = _num(item.get("unit_price"))
        a = _num(item.get("amount"))
        if q is not None and p is not None and a is not None:
            checks.append(_mk_check(
                f"line_item_{idx}_check",
                "quantity * unit_price",
                {"quantity": q, "unit_price": p},
                q * p,
                a,
            ))

    if line_items and subtotal is not None:
        amounts = [_num(it.get("amount")) for it in line_items if isinstance(it, dict)]
        amounts = [a for a in amounts if a is not None]
        if amounts:
            checks.append(_mk_check(
                "line_items_sum_to_subtotal",
                "sum(line_items.amount)",
                {"line_items_total": sum(amounts)},
                sum(amounts),
                subtotal,
            ))

    return _finalize(checks)


# ---------- BALANCE SHEET ----------

def validate_balance_sheet(extracted: dict) -> ValidationResult:
    checks: list[ValidationCheck] = []
    periods = _get_periods(extracted)

    # Per-period scalar equation
    for period in periods:
        total_assets = _get_period(extracted, "total_assets", period)
        total_liabilities = _get_period(extracted, "total_liabilities", period)
        total_equity = _get_period(extracted, "total_equity", period)

        if None not in (total_assets, total_liabilities, total_equity):
            calc = total_liabilities + total_equity
            label = f" [{period}]" if period else ""
            checks.append(_mk_check(
                f"balance_sheet_equation{label}",
                "total_liabilities + total_equity",
                {"total_liabilities": total_liabilities, "total_equity": total_equity},
                calc,
                total_assets,
            ))

    # Per-period line item component reconciliation
    line_items = extracted.get("line_items") or []
    if line_items and periods and periods != [""]:
        for period in periods:
            liab_sum = 0.0
            liab_count = 0
            asset_sum = 0.0
            asset_count = 0
            reported_total_assets = None
            reported_total_liab = None

            for item in line_items:
                if not isinstance(item, dict):
                    continue
                label = (item.get("label") or "").lower()
                vals = item.get("values") or {}
                v = _num(vals.get(period))
                if v is None:
                    continue
                if "total assets" in label or ("total" in label and "assets" in label and "liab" not in label):
                    reported_total_assets = v
                elif "total capital" in label or ("total" in label and "liabilit" in label):
                    reported_total_liab = v

            seen_total = False
            for item in line_items:
                if not isinstance(item, dict):
                    continue
                label = (item.get("label") or "").lower()
                vals = item.get("values") or {}
                v = _num(vals.get(period))
                if v is None:
                    continue
                if "total capital" in label or ("total" in label and "liabilit" in label):
                    seen_total = True
                    continue
                if "total assets" in label or ("total" in label and "assets" in label and "liab" not in label):
                    seen_total = True
                    continue
                if not seen_total:
                    liab_sum += v
                    liab_count += 1
                else:
                    asset_sum += v
                    asset_count += 1

            if liab_count >= 2:
                target = reported_total_liab if reported_total_liab is not None else reported_total_assets
                if target is not None:
                    checks.append(_mk_check(
                        f"bs_liab_components [{period}]",
                        "sum(liability line items)",
                        {"component_sum": round(liab_sum, 4)},
                        liab_sum,
                        target,
                    ))
            if asset_count >= 2 and reported_total_assets is not None:
                checks.append(_mk_check(
                    f"bs_asset_components [{period}]",
                    "sum(asset line items)",
                    {"component_sum": round(asset_sum, 4)},
                    asset_sum,
                    reported_total_assets,
                ))

    return _finalize(checks)


# ---------- P&L ----------

def validate_profit_and_loss(extracted: dict) -> ValidationResult:
    checks: list[ValidationCheck] = []
    periods = _get_periods(extracted)

    for period in periods:
        label = f" [{period}]" if period else ""

        revenue = _get_period(extracted, "revenue", period)
        cogs = _get_period(extracted, "cost_of_sales", period)
        gross = _get_period(extracted, "gross_profit", period)
        op_exp = _get_period(extracted, "operating_expenses", period)
        op_profit = _get_period(extracted, "operating_profit", period)
        tax = _get_period(extracted, "tax", period)
        net = _get_period(extracted, "net_profit", period)

        if None not in (revenue, cogs, gross):
            checks.append(_mk_check(
                f"gross_profit_check{label}",
                "revenue - cost_of_sales",
                {"revenue": revenue, "cost_of_sales": cogs},
                revenue - cogs,
                gross,
            ))

        if None not in (gross, op_exp, op_profit):
            checks.append(_mk_check(
                f"operating_profit_check{label}",
                "gross_profit - operating_expenses",
                {"gross_profit": gross, "operating_expenses": op_exp},
                gross - op_exp,
                op_profit,
            ))

        if None not in (op_profit, tax, net):
            checks.append(_mk_check(
                f"net_profit_check{label}",
                "operating_profit - tax",
                {"operating_profit": op_profit, "tax": tax},
                op_profit - tax,
                net,
            ))

    return _finalize(checks)


# ---------- CASH FLOW ----------

def validate_cash_flow(extracted: dict) -> ValidationResult:
    checks: list[ValidationCheck] = []
    periods = _get_periods(extracted)

    for period in periods:
        label = f" [{period}]" if period else ""

        op = _get_period(extracted, "operating_cash_flow", period)
        inv = _get_period(extracted, "investing_cash_flow", period)
        fin = _get_period(extracted, "financing_cash_flow", period)
        net_change = _get_period(extracted, "net_change_in_cash", period)
        opening = _get_period(extracted, "opening_cash", period)
        closing = _get_period(extracted, "closing_cash", period)

        if None not in (op, inv, fin, net_change):
            checks.append(_mk_check(
                f"net_change_in_cash_check{label}",
                "operating + investing + financing",
                {"operating": op, "investing": inv, "financing": fin},
                op + inv + fin,
                net_change,
            ))

        if None not in (opening, net_change, closing):
            checks.append(_mk_check(
                f"closing_cash_check{label}",
                "opening_cash + net_change_in_cash",
                {"opening_cash": opening, "net_change_in_cash": net_change},
                opening + net_change,
                closing,
            ))

    return _finalize(checks)


VALIDATORS = {
    "invoice": validate_invoice,
    "balance_sheet": validate_balance_sheet,
    "profit_and_loss": validate_profit_and_loss,
    "cash_flow_statement": validate_cash_flow,
}


def run_validations(document_type: str, extracted: dict) -> ValidationResult:
    validator = VALIDATORS.get(document_type)
    if not validator:
        return ValidationResult(checks=[], overall_status="NOT_APPLICABLE", issues=["Unknown type"])
    try:
        return validator(extracted)
    except Exception as e:
        logger.exception("Validation failed | type=%s | error=%s", document_type, e)
        return ValidationResult(checks=[], overall_status="NOT_APPLICABLE", issues=[str(e)])