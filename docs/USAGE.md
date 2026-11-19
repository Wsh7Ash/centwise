# Usage

## Splitting a bill

```shell
$ centwise split 100.00 3
USD 100.00 split · 3 part(s) · scale 2

  1         33.34  (3334 minor)
  2         33.33  (3333 minor)
  3         33.33  (3333 minor)

  sum      100.00  (exact)
```

The first part gets the extra cent because equal weights tie on fractional
remainder and the tie-break is the earliest part. Changing the order of the
arguments does not change the guarantee, only which part is first.

## Weighted allocation

```shell
$ centwise allocate 250.00 --weights 2,3,5
USD 250.00 allocation · 3 part(s) · scale 2

  1         50.00  (5000 minor)
  2         75.00  (7500 minor)
  3        125.00  (12500 minor)

  sum      250.00  (exact)
```

Weights can be decimals: `--weights 0.5,0.3,0.2`, and a zero weight is valid and
receives nothing. Negative weights, all-zero weights, an empty entry
(`1,,2`) and non-numeric weights exit `2` with a message on stderr.

## Currency scale

```shell
$ centwise split 1000 3 --currency JPY
JPY 1000 split · 3 part(s) · scale 0

  1           334  (334 minor)
  2           333  (333 minor)
  3           333  (333 minor)

  sum        1000  (exact)
```

`JPY` has no minor unit, so the leftover yen is a whole unit; `KWD` has three
decimals and the leftover is a fils. `centwise currencies` lists all 30 supported
codes, their scales and `10**scale`.

## JSON

```shell
centwise split 100.00 3 --json
```

```json
{
  "label": "split",
  "currency": "USD",
  "scale": 2,
  "total": "100.00",
  "total_minor": 10000,
  "weights": ["1", "1", "1"],
  "parts": [
    {"index": 1, "amount": "33.34", "minor": 3334},
    {"index": 2, "amount": "33.33", "minor": 3333},
    {"index": 3, "amount": "33.33", "minor": 3333}
  ],
  "sum": "100.00",
  "exact": true
}
```

`total_minor`, each `minor` and `sum` are strings/ints, not floats. `weights` is
`null` for `split` invocations.

## Library

```python
from decimal import Decimal
from centwise import Money, allocate, split, get_currency

parts = split("99.99", 7)
assert sum(parts, Decimal(0)) == Decimal("99.99")

shares = allocate("120.00", [1, 1, 2], "EUR")
assert sum(shares, Decimal(0)) == Decimal("120.00")

refund = allocate("-100.00", [1, 1, 1])
assert refund == [-part for part in split("100.00", 3)]

total = Money("199.99", "USD") * Decimal("1.0825")
assert sum((part.amount for part in total.split(3)), Decimal(0)) == total.amount

try:
    Money("1.00", "USD") + Money("1.00", "EUR")
except ValueError as exc:
    print(exc)          # cannot combine USD and EUR
```

Pass `Decimal`, `int` or `str`. Passing a `float` raises `TypeError` on purpose:
by the time a float reaches the library the value is already inexact.

### Rounding

`allocate` and `Money` quantize with `ROUND_HALF_UP`. Use `round_amount` for
another mode:

```python
from centwise import round_amount
round_amount("2.345", "USD")                    # Decimal('2.35')
round_amount("2.345", "USD", "ROUND_DOWN")      # Decimal('2.34')
round_amount("2.5", "JPY", "ROUND_HALF_EVEN")   # Decimal('2')
```

## Ledger pattern

```python
total_minor = get_currency("USD").to_minor(total)
assert sum(part.to_dict()["minor"] for part in shares) == total_minor
```

Because each part is a quantized `Decimal` in the same currency, converting every
part with `to_minor` and summing integers is an exact check. Do that in a test,
not in production code: `centwise` already guarantees it.
