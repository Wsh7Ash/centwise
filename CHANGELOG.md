# Changelog

## 0.1.0 — 2026-11-19

Initial release.

- `allocate(total, weights, currency)` — largest-remainder allocation in integer
  minor units, exact sum, earliest-part tie-break.
- `split(total, parts, currency)` — equal split with the same guarantee.
- `Currency` / `get_currency` / `CURRENCIES` — 30 ISO codes with 0, 2 or 3 minor
  units, exact `to_minor` / `from_minor` conversions.
- `round_amount` with eight named rounding modes, default `ROUND_HALF_UP`.
- `Money` — immutable, quantized, same-currency arithmetic, `split`,
  `allocate`, `format`, `to_dict`.
- Strict input: floats, booleans, NaN, infinity, negative/all-zero weights and
  unknown currencies are errors with explicit messages.
- CLI: `split`, `allocate --weights`, `currencies`, text and JSON output,
  exactness check, exit codes 0/1/2.
- 46 tests covering invariants across amounts, counts, weights and currencies,
  plus a demo with a 164-case exactness sweep and an invoice example.
