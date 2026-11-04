from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from bankapp.errors import InvalidAmountError

CENT = Decimal("0.01")
ZERO = Decimal("0.00")
MAX_AMOUNT = Decimal("1000000000000")


def to_money(value: Decimal | int | str) -> Decimal:
    """Convert a value to a Decimal rounded to whole cents."""
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        raise InvalidAmountError(f"'{value}' is not a valid amount.") from None
    if not amount.is_finite() or amount.copy_abs() > MAX_AMOUNT:
        raise InvalidAmountError(f"'{value}' is not a valid amount.")
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def parse_amount(raw: str) -> Decimal:
    """Parse user input such as '$1,250.50' into a positive amount."""
    cleaned = raw.strip().replace(",", "").removeprefix("$").strip()
    if not cleaned:
        raise InvalidAmountError("Please enter an amount.")
    amount = to_money(cleaned)
    if amount <= 0:
        raise InvalidAmountError("Amount must be greater than zero.")
    return amount


def to_cents(amount: Decimal) -> int:
    return int(to_money(amount) * 100)


def from_cents(cents: int) -> Decimal:
    return (Decimal(cents) / 100).quantize(CENT)


def fmt(amount: Decimal) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f}"
