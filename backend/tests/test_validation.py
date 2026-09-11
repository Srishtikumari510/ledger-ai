"""Tests for financial validation rules."""
from app.services import financial_validation_service as fvs


def _wrap(v):
    return {"value": v}


def test_invoice_total_check_pass():
    extracted = {
        "subtotal": _wrap(12500.00),
        "tax_amount": _wrap(625.00),
        "discount": _wrap(0.00),
        "total_amount": _wrap(13125.00),
        "line_items": [],
    }
    result = fvs.run_validations("invoice", extracted)
    names = [c.name for c in result.checks]
    assert "invoice_total_check" in names
    check = next(c for c in result.checks if c.name == "invoice_total_check")
    assert check.status == "PASS"
    assert check.variance == 0.0
    assert result.overall_status == "PASS"


def test_invoice_total_check_fails_on_mismatch():
    extracted = {
        "subtotal": _wrap(100.0),
        "tax_amount": _wrap(10.0),
        "discount": _wrap(0.0),
        "total_amount": _wrap(200.0),
    }
    result = fvs.run_validations("invoice", extracted)
    check = next(c for c in result.checks if c.name == "invoice_total_check")
    assert check.status == "FAILED"
    assert result.overall_status == "FAILED"


def test_invoice_negative_bracket_parsing():
    extracted = {
        "subtotal": _wrap("2,530.00"),
        "tax_amount": _wrap("(253.00)"),   # bracketed = negative
        "discount": _wrap(0.0),
        "total_amount": _wrap("2,277.00"),
    }
    result = fvs.run_validations("invoice", extracted)
    check = next(c for c in result.checks if c.name == "invoice_total_check")
    assert check.status == "PASS"


def test_cash_flow_net_change_pass():
    extracted = {
        "operating_cash_flow": _wrap({"2024": 1000.0}),
        "investing_cash_flow": _wrap({"2024": -300.0}),
        "financing_cash_flow": _wrap({"2024": -200.0}),
        "net_change_in_cash": _wrap({"2024": 500.0}),
        "opening_cash": _wrap({"2024": 100.0}),
        "closing_cash": _wrap({"2024": 600.0}),
        "periods": ["2024"],
    }
    result = fvs.run_validations("cash_flow_statement", extracted)
    names = [c.name for c in result.checks]
    assert any("net_change_in_cash_check" in n for n in names)
    assert any("closing_cash_check" in n for n in names)
    assert result.overall_status == "PASS"


def test_not_applicable_when_fields_missing():
    extracted = {}   # nothing
    result = fvs.run_validations("balance_sheet", extracted)
    assert result.overall_status == "NOT_APPLICABLE"
    assert all(c.status == "NOT_APPLICABLE" for c in result.checks) or result.checks == []