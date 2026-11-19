# centwise

**Split money exactly, to the minor unit, with no lost cents.**

`centwise` allocates a `Decimal` amount across weighted parts so the parts always
sum back to the input, using the largest-remainder method and each currency's
real scale (2 for USD, 0 for JPY, 3 for KWD). It is a small library first and a
CLI second.

```text
$ centwise split 100.00 3
USD 100.00 split · 3 part(s) · scale 2

  1         33.34  (3334 minor)
  2         33.33  (3333 minor)
  3         33.33  (3333 minor)

  sum      100.00  (exact)
```

## The problem

`100 / 3` is not payable. Naive rounding gives `33.33 + 33.33 + 33.33 = 99.99`,
which breaks every ledger that asserts a split sums to its total. Rounding each
share independently is worse: the error grows with the number of parts, and the
distribution depends on the order of rounding rather than on the weights.

## What it does

- **`allocate(total, weights, currency)`** — proportional split by
  largest remainder: floors every exact share, then hands out the leftover minor
  units to the largest fractional remainders, ties to the earliest part.
- **`split(total, n, currency)`** — equal split with the same guarantee.
- **Exact minor units** — arithmetic is done on integers of the currency's
  smallest unit, so `0.01` is representable and `Decimal("0.1")` never drifts.
- **Currency scales** — 30 ISO codes with 0, 2 or 3 decimal places.
- **`Money`** — immutable, quantized on construction, with `+`, `-`, `*`,
  `.split()`, `.allocate()` and formatted output; mixing currencies is an error.
- **Strict input** — floats are rejected (they are already inexact), negative
  weights, all-zero weights and non-finite amounts are errors with clear text.
- **CLI and JSON** — `split`, `allocate`, `currencies`, each with `--json` and an
  exactness check on the result.

## Install

```shell
git clone https://github.com/Wsh7Ash/centwise.git
cd centwise
python -m pip install -e .
```

Python 3.12+, no dependencies.

## Usage

```python
from decimal import Decimal
from centwise import Money, allocate, split

split("100.00", 3)
# [Decimal('33.34'), Decimal('33.33'), Decimal('33.33')]

allocate("250.00", [2, 3, 5])
# [Decimal('50.00'), Decimal('75.00'), Decimal('125.00')]

allocate("10.00", ["0.1", "0.2", "0.7"], "EUR")

invoice = Money("199.99", "USD") * Decimal("1.0825")   # tax, rounded once
shares = invoice.split(3)
sum(share.amount for share in shares) == invoice.amount  # True
```

```shell
centwise split 100.00 3
centwise allocate 250.00 --weights 2,3,5
centwise split 1000 3 --currency JPY
centwise split 1.000 3 --currency KWD --json
centwise currencies
```

Exit codes: `0` allocated and exact, `1` a result that does not sum (should not
happen; it is checked), `2` invalid input.

## Guarantees

For any total `T`, weights `w` and currency scale `s`:

1. `sum(allocate(T, w)) == quantize(T)` exactly, in minor units.
2. Every part is within one minor unit of its exact proportional share.
3. `allocate(-T, w) == -allocate(T, w)` element-wise.
4. With equal weights, the largest and smallest parts differ by at most one minor
   unit, and the extra units go to the earliest parts.
5. `allocate` is deterministic: no dependence on dict order, hash seeds or
   rounding mode of the ambient context.

These are the properties the test suite sweeps over multiple amounts, part
counts, weights and currencies.

## API

| Function | Returns | Notes |
|---|---|---|
| `allocate(total, weights, currency="USD", rounding="ROUND_HALF_UP")` | `list[Decimal]` | total is quantized to the currency first |
| `split(total, n, currency="USD")` | `list[Decimal]` | equal weights |
| `get_currency(code)` | `Currency` | case-insensitive, 30 codes |
| `round_amount(amount, currency, rounding)` | `Decimal` | 8 named rounding modes |
| `Money(amount, currency)` | `Money` | float input rejected |

`Money` supports same-currency `+`/`-`, scalar `*`, unary `-`, `.format()`,
`.to_dict()`, `.split()`, `.allocate()`.

## Scope

Not an accounting system: no exchange rates, no tax rules, no journal entries, no
serialization format. Currency scales are a fixed table, not ISO maintenance.
Rounding happens once per operation; `Money` does not carry more precision than
the currency's minor unit.

## Project layout

```text
src/centwise/    currency, allocate, money, render, cli
tests/           46 tests: scales/rounding, allocation invariants, Money, CLI
examples/        an invoice split across three cost centres
scripts/demo.py  CLI runs, a 164-case exactness sweep, and a library example
docs/            architecture, usage, project spec
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md),
[docs/USAGE.md](docs/USAGE.md) and [RESULTS.md](RESULTS.md).

## License

MIT — see [LICENSE](LICENSE).
