from decimal import Decimal

import pytest

from bankapp.errors import InvalidAmountError
from bankapp.money import fmt, from_cents, parse_amount, to_cents


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("10", "10.00"), ("$1,250.5", "1250.50"), (" 0.005 ", "0.01"), ("99.994", "99.99")],
)
def test_parse_amount(raw, expected):
    assert parse_amount(raw) == Decimal(expected)


@pytest.mark.parametrize("raw", ["", "abc", "-5", "0", "nan", "inf", "1e999999999"])
def test_parse_amount_rejects_bad_input(raw):
    with pytest.raises(InvalidAmountError):
        parse_amount(raw)


def test_cents_round_trip():
    assert from_cents(to_cents(Decimal("0.10") + Decimal("0.20"))) == Decimal("0.30")


def test_fmt():
    assert fmt(Decimal("1234.5")) == "$1,234.50"
    assert fmt(Decimal("-42")) == "-$42.00"
