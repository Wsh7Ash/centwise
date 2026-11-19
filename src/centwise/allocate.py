"""Exact allocation of an amount across weighted parts.

The method is largest remainder (Hamilton): every part gets the floor of its
exact proportional share, then the leftover minor units go one each to the parts
with the largest fractional remainders.  The result always sums back to the
input to the cent, and no part is more than one minor unit away from its exact
share.
"""

from __future__ import annotations

from decimal import ROUND_FLOOR, Decimal, localcontext
from typing import Sequence

from .currency import Currency, as_decimal, get_currency


def allocate(
    total: Decimal | int | str,
    weights: Sequence[Decimal | int | str],
    currency: str | Currency = "USD",
    rounding: str = "ROUND_HALF_UP",
) -> list[Decimal]:
    """Split ``total`` proportionally to ``weights``, exactly, in major units."""
    code = get_currency(currency)
    parsed = _parse_weights(weights)
    amount = code.quantize(as_decimal(total), rounding)
    sign = -1 if amount < 0 else 1
    minor_total = abs(code.to_minor(amount))
    parts = _allocate_minor(minor_total, parsed)
    return [sign * code.from_minor(int(part)) for part in parts]


def split(
    total: Decimal | int | str,
    parts: int,
    currency: str | Currency = "USD",
    rounding: str = "ROUND_HALF_UP",
) -> list[Decimal]:
    """Split ``total`` into ``parts`` equal shares, distributing leftover cents."""
    if isinstance(parts, bool) or not isinstance(parts, int):
        raise TypeError("parts must be an integer")
    if parts < 1:
        raise ValueError("parts must be at least 1")
    return allocate(total, [1] * parts, currency, rounding)


def _parse_weights(weights: Sequence[Decimal | int | str]) -> list[Decimal]:
    if isinstance(weights, (str, bytes)):
        raise TypeError("weights must be a sequence of numbers, not a string")
    try:
        values = list(weights)
    except TypeError:
        raise TypeError("weights must be a sequence of numbers") from None
    if not values:
        raise ValueError("at least one weight is required")
    parsed = [as_decimal(value) for value in values]
    if any(value < 0 for value in parsed):
        raise ValueError("weights must be non-negative")
    if sum(parsed) <= 0:
        raise ValueError("at least one weight must be greater than zero")
    return parsed


def _allocate_minor(total_minor: int, weights: list[Decimal]) -> list[Decimal]:
    count = len(weights)
    if total_minor == 0:
        return [Decimal(0)] * count

    with localcontext() as context:
        context.prec = 50
        weight_total = sum(weights)
        exact = [Decimal(total_minor) * weight / weight_total for weight in weights]

    floors = [int(share.to_integral_value(rounding=ROUND_FLOOR)) for share in exact]
    remainder = total_minor - sum(floors)
    fractions = [share - floor for share, floor in zip(exact, floors)]
    order = sorted(range(count), key=lambda index: (-fractions[index], index))
    for index in order[:remainder]:
        floors[index] += 1
    return [Decimal(value) for value in floors]
