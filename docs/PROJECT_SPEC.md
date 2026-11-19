# Project spec

**Name:** centwise
**Category:** open-source-library
**Target user:** a Python developer building billing, invoicing, expense
splitting or revenue-share features who needs a split that sums back to the
total.

**Problem:** dividing money into parts is not ordinary division. `100.00 / 3`
rounded to cents loses a cent, and rounding each share independently makes the
loss depend on part order. Ledger code then has to special-case a remainder, or
it stores a total that does not equal the sum of its rows. Existing answers are
either a one-line `//` that is wrong for negatives and non-decimal currencies, or
a full accounting framework.

**Solution:** a small, dependency-free library that allocates a quantized amount
across weights using largest remainder on integer minor units, with a currency
scale table, a strict `Money` value type, and an invariant-based test suite. A
CLI exposes the same allocation for shell use and for demos.

**Core workflow:**

1. `allocate(total, weights, currency)` or `split(total, n, currency)`.
2. Optionally build `Money` values for arithmetic and formatting.
3. Assert `sum(parts) == total` in your own tests; centwise guarantees it.

## Functional requirements

- Parse amounts from `Decimal`, `int` or `str`; reject `float`, `bool`, `NaN`
  and infinity with explicit errors.
- Quantize to the currency's scale with a named rounding mode, default
  `ROUND_HALF_UP`.
- Allocate by largest remainder in integer minor units; ties break to the
  earliest part; zero weights receive nothing; at least one weight must be
  positive; negative weights are rejected.
- `sum(allocate(T, w)) == quantize(T)` exactly for positive and negative totals.
- Each part differs from its exact proportional share by at most one minor unit.
- `allocate(-T, w) == -allocate(T, w)` element-wise.
- Support 0-, 2- and 3-decimal currencies from a fixed table of at least 25 ISO
  codes; unknown codes are errors.
- `Money` is immutable, quantized on construction, supports same-currency `+`,
  `-`, scalar `*`, unary `-`, `.split()`, `.allocate()`, `.format()` and
  `.to_dict()`; mixing currencies raises.
- CLI: `split`, `allocate --weights`, `currencies`, each with `--json`; exit `0`
  exact, `1` a failed checksum, `2` invalid input.

## Non-functional requirements

- Python 3.12+, standard library only (`decimal` is the only numeric type).
- Deterministic across runs, hash seeds and ambient decimal context.
- No global decimal-context mutation; use a local context for division.
- Public API is exported from the package root and documented in the README.

## Out of scope

Exchange rates, tax jurisdiction rules, amortization schedules, serialization,
database models, multi-currency totals, and locale-specific currency formatting
(symbols, placement, negative styles).

## Success criteria

- A sweep over 8 amounts × 20 part counts plus weighted cases sums exactly in
  every case (the demo records 164/164).
- Tests cover rounding at the half, 0/2/3-decimal currencies, negative totals,
  fractional and zero weights, tie-breaking, float rejection, and CLI exit codes.
- The invoice example produces a total whose three-way split sums to the total,
  printed and asserted at runtime.
