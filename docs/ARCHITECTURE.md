# Architecture

`centwise` keeps every amount in integer minor units while it computes, and only
converts back to `Decimal` major units at the boundary.

```text
currency.py   Currency(code, scale)
              get_currency / as_decimal / round_amount
              quantize → to_minor (int) → from_minor (Decimal)
allocate.py   allocate(total, weights)   largest remainder on integers
              split(total, n)
money.py      Money(amount, currency)    arithmetic + allocate/split + format
render.py     AllocationResult → text / JSON
cli.py        split / allocate / currencies
```

## Why integers in minor units

`Decimal("0.1")` is exact, but `100 / 3` is not representable at any scale, and
rounding each part independently loses the invariant that the parts sum to the
total. Converting the *total* to an integer number of cents up front makes the
distribution a finite integer problem:

```text
minor_total = 10000          # $100.00
weights     = [1, 1, 1]
exact_i     = 10000 * 1 / 3  # 3333.333...
floor_i     = 3333
remainder   = 10000 - 9999 = 1
```

The remaining cent goes to the part with the largest fractional remainder. With
equal weights all fractions tie, so the tie-break is the part index: the first
part receives it. This makes the result deterministic and stable across runs and
Python versions.

## Largest remainder, precisely

```python
with localcontext() as ctx:
    ctx.prec = 50
    exact = [Decimal(total_minor) * weight / weight_total for weight in weights]
floors = [floor(share) for share in exact]
remainder = total_minor - sum(floors)
fractions = [share - floor for share, floor in zip(exact, floors)]
order = sorted(range(n), key=lambda i: (-fractions[i], i))
for i in order[:remainder]:
    floors[i] += 1
```

`remainder` is always non-negative and strictly smaller than the number of
positive-weight parts (each floor discards less than one unit), so the slice is
well-defined. A wider-than-default precision avoids a truncated `Decimal`
division accidentally producing a fraction slightly below another one; the final
values are integers, so the precision only affects the ordering of the fractions.

Weights may be fractional (`0.1`, `0.2`, `0.7`), because percentages and shares
are usually written that way. They are parsed to `Decimal`, validated as finite
and non-negative, and rejected if the sum is zero.

## Negative totals

The algorithm is defined for positive minor totals. For a negative amount the
library allocates the absolute value and negates every part. This guarantees
`allocate(-T) == -allocate(T)` element-wise, which is the property a refund or a
credit note needs. Allocating a negative number directly with floor semantics
would otherwise hand the leftover unit to a different part.

## Quantization boundary

`Currency.quantize` uses `Decimal.quantize` with the currency's exponent and a
named rounding mode (default `ROUND_HALF_UP`, the usual commercial convention).
`allocate` quantizes the total once before distributing; weights are never
rounded. `Money.__init__` quantizes too, so a `Money` always has exactly `scale`
decimal places and cannot hide sub-cent precision.

`to_minor` quantizes and then multiplies by `10**scale`, returning an `int`;
`from_minor` rescales a `Decimal`. All internal sums are therefore integer sums
and cannot drift.

## Input strictness

- `float` is rejected rather than converted, because `0.1` is already
  `0.1000000000000000055511151231257827...` and the resulting ledger would be
  wrong for reasons the caller cannot see.
- `bool` is rejected explicitly (it is an `int` subclass).
- `NaN` and `Infinity` are rejected before quantization.
- An unknown currency is an error, not a silent fallback to 2 decimals.
- Weight strings are rejected as a whole (`"1,2"`), to catch a CLI-style mistake
  in library use.

## Rendering

`AllocationResult` recomputes the checksum from the parts rather than trusting the
input, so `exact` is a real assertion and the CLI can exit `1` if it ever fails.
`render_text` prints each part with both the major-unit amount and its minor
units, which makes "where did the extra cent go?" visible. JSON includes
`total_minor`, per-part `minor`, `sum` and `exact`.

## Trade-offs

- **Hamilton, not Webster/Sainte-Laguë.** Largest remainder is easy to audit and
  exact; it can exhibit the Alabama paradox if the number of parts changes, which
  is irrelevant for invoicing but worth knowing.
- **Fixed currency table.** No ISO feed; adding a currency is a one-line change.
- **No exchange or tax logic.** Those are policy, not arithmetic, and belong to
  the caller.
