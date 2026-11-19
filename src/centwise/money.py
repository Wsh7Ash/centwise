"""A small immutable money type built on exact allocation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from .allocate import allocate, split
from .currency import Currency, as_decimal, get_currency


@dataclass(frozen=True)
class Money:
    """An amount in one currency, always quantized to that currency's scale."""

    amount: Decimal
    currency: Currency

    def __init__(self, amount: Decimal | int | str, currency: str | Currency = "USD") -> None:
        code = get_currency(currency)
        object.__setattr__(self, "currency", code)
        object.__setattr__(self, "amount", code.quantize(as_decimal(amount)))

    @classmethod
    def zero(cls, currency: str | Currency = "USD") -> "Money":
        return cls(0, currency)

    def _check(self, other: "Money") -> None:
        if not isinstance(other, Money):
            raise TypeError(f"expected Money, got {type(other).__name__}")
        if other.currency != self.currency:
            raise ValueError(f"cannot combine {self.currency} and {other.currency}")

    def __add__(self, other: "Money") -> "Money":
        self._check(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._check(other)
        return Money(self.amount - other.amount, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.amount, self.currency)

    def __mul__(self, factor: Decimal | int | str) -> "Money":
        return Money(self.amount * as_decimal(factor), self.currency)

    __rmul__ = __mul__

    def allocate(self, weights: Sequence[Decimal | int | str]) -> list["Money"]:
        return [
            Money(part, self.currency)
            for part in allocate(self.amount, weights, self.currency)
        ]

    def split(self, parts: int) -> list["Money"]:
        return [Money(part, self.currency) for part in split(self.amount, parts, self.currency)]

    def format(self, grouping: bool = True) -> str:
        spec = "," if grouping else ""
        return f"{self.currency} {self.amount:{spec}.{self.currency.scale}f}"

    def to_dict(self) -> dict[str, object]:
        return {
            "amount": format(self.amount, "f"),
            "currency": self.currency.code,
            "minor": self.currency.to_minor(self.amount),
        }

    def __str__(self) -> str:
        return self.format()
