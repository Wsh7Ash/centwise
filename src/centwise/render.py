"""Text and JSON rendering for allocation results."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal

from .currency import Currency, get_currency


@dataclass
class AllocationResult:
    total: Decimal
    parts: list[Decimal]
    currency: Currency
    weights: list[Decimal] = field(default_factory=list)
    label: str = "allocation"

    @property
    def scale(self) -> int:
        return self.currency.scale

    @property
    def total_minor(self) -> int:
        return self.currency.to_minor(self.total)

    @property
    def part_minor(self) -> list[int]:
        return [self.currency.to_minor(part) for part in self.parts]

    @property
    def checksum(self) -> Decimal:
        return sum(self.parts, Decimal(0))

    @property
    def exact(self) -> bool:
        return self.checksum == self.total

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "currency": self.currency.code,
            "scale": self.scale,
            "total": format(self.total, "f"),
            "total_minor": self.total_minor,
            "weights": [format(weight, "f") for weight in self.weights] if self.weights else None,
            "parts": [
                {"index": index, "amount": format(part, "f"), "minor": minor}
                for index, (part, minor) in enumerate(zip(self.parts, self.part_minor), start=1)
            ],
            "sum": format(self.checksum, "f"),
            "exact": self.exact,
        }


def build_result(
    total: Decimal | int | str,
    weights: list[Decimal | int | str],
    currency: str | Currency,
    label: str,
) -> AllocationResult:
    from .allocate import allocate
    from .currency import as_decimal

    code = get_currency(currency)
    parts = allocate(total, weights, code)
    parsed = [as_decimal(weight) for weight in weights]
    return AllocationResult(
        total=code.quantize(as_decimal(total)),
        parts=parts,
        currency=code,
        weights=parsed,
        label=label,
    )


def render_text(result: AllocationResult) -> str:
    width = max(len(str(len(result.parts))), 1)
    out = [
        f"{result.currency} {result.total} {result.label} · {len(result.parts)} part(s) "
        f"· scale {result.scale}",
        "",
    ]
    for index, (part, minor) in enumerate(zip(result.parts, result.part_minor), start=1):
        out.append(f"  {str(index).rjust(width)}  {format(part, 'f').rjust(12)}  ({minor} minor)")
    out.append("")
    status = "exact" if result.exact else "MISMATCH"
    out.append(f"  sum  {format(result.checksum, 'f').rjust(10)}  ({status})")
    return "\n".join(out) + "\n"


def render_json(result: AllocationResult) -> str:
    return json.dumps(result.to_dict(), indent=2) + "\n"


def render_currencies(currencies: dict[str, Currency], as_json: bool = False) -> str:
    if as_json:
        return json.dumps(
            [{"code": item.code, "scale": item.scale} for item in currencies.values()],
            indent=2,
        ) + "\n"
    out = ["code  scale  minor units"]
    for item in currencies.values():
        out.append(f"{item.code}  {item.scale:<5}  {item.minor_units}")
    return "\n".join(out) + "\n"
