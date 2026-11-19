"""Currencies, their minor-unit scales, and exact conversions to minor units."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

ROUNDING_MODES = {
    "ROUND_UP",
    "ROUND_DOWN",
    "ROUND_CEILING",
    "ROUND_FLOOR",
    "ROUND_HALF_UP",
    "ROUND_HALF_DOWN",
    "ROUND_HALF_EVEN",
    "ROUND_05UP",
}


@dataclass(frozen=True)
class Currency:
    """An ISO 4217 code and the number of decimal places it uses."""

    code: str
    scale: int

    def __post_init__(self) -> None:
        if not self.code or not self.code.isalpha() or len(self.code) != 3:
            raise ValueError(f"invalid currency code {self.code!r}")
        if not 0 <= self.scale <= 4:
            raise ValueError(f"invalid scale {self.scale} for {self.code}")
        object.__setattr__(self, "code", self.code.upper())

    @property
    def minor_units(self) -> int:
        return 10**self.scale

    def quantize(self, amount: Decimal, rounding: str = "ROUND_HALF_UP") -> Decimal:
        return round_amount(amount, self, rounding)

    def to_minor(self, amount: Decimal, rounding: str = "ROUND_HALF_UP") -> int:
        quantized = self.quantize(amount, rounding)
        return int(quantized.scaleb(self.scale))

    def from_minor(self, minor: int) -> Decimal:
        return Decimal(minor).scaleb(-self.scale)

    def __str__(self) -> str:
        return self.code


CURRENCIES: dict[str, Currency] = {
    currency.code: currency
    for currency in (
        Currency("USD", 2),
        Currency("EUR", 2),
        Currency("GBP", 2),
        Currency("CHF", 2),
        Currency("AUD", 2),
        Currency("CAD", 2),
        Currency("NZD", 2),
        Currency("CNY", 2),
        Currency("INR", 2),
        Currency("BRL", 2),
        Currency("MXN", 2),
        Currency("ZAR", 2),
        Currency("SEK", 2),
        Currency("NOK", 2),
        Currency("DKK", 2),
        Currency("PLN", 2),
        Currency("TRY", 2),
        Currency("SGD", 2),
        Currency("HKD", 2),
        Currency("AED", 2),
        Currency("SAR", 2),
        Currency("JPY", 0),
        Currency("KRW", 0),
        Currency("CLP", 0),
        Currency("ISK", 0),
        Currency("VND", 0),
        Currency("KWD", 3),
        Currency("BHD", 3),
        Currency("OMR", 3),
        Currency("TND", 3),
    )
}


def get_currency(value: str | Currency) -> Currency:
    if isinstance(value, Currency):
        return value
    if not isinstance(value, str):
        raise TypeError("currency must be a currency code or Currency")
    code = value.strip().upper()
    try:
        return CURRENCIES[code]
    except KeyError:
        raise ValueError(f"unknown currency {value!r}") from None


def as_decimal(value: Decimal | int | str) -> Decimal:
    """Convert exactly; floats are refused because they are already inexact."""
    if isinstance(value, Decimal):
        result = value
    elif isinstance(value, bool):
        raise TypeError("a boolean is not an amount")
    elif isinstance(value, int):
        result = Decimal(value)
    elif isinstance(value, str):
        try:
            result = Decimal(value.strip())
        except InvalidOperation:
            raise ValueError(f"invalid decimal {value!r}") from None
    elif isinstance(value, float):
        raise TypeError("pass Decimal, int or str; floats are inexact")
    else:
        raise TypeError(f"cannot use {type(value).__name__} as an amount")
    if not result.is_finite():
        raise ValueError("amount must be finite")
    return result


def round_amount(
    amount: Decimal | int | str, currency: str | Currency, rounding: str = "ROUND_HALF_UP"
) -> Decimal:
    if rounding not in ROUNDING_MODES:
        raise ValueError(
            f"unknown rounding mode {rounding!r} (choose from {', '.join(sorted(ROUNDING_MODES))})"
        )
    code = get_currency(currency)
    value = as_decimal(amount)
    return value.quantize(Decimal(1).scaleb(-code.scale), rounding=rounding)
