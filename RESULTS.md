# Results

## Environment

- OS: Windows 11 (win32, Git Bash)
- Python: 3.14.3
- Test runner: pytest 9.1.1
- Dependencies: none (standard library only)

## Validation performed

- install: PASS (runs from checkout with `PYTHONPATH=src`)
- build: PASS (`python -m centwise currencies` imports the package and prints the table)
- unit tests: PASS (46/46)
- integration tests: PASS (CLI tests spawn `python -m centwise` as a subprocess)
- lint: N/A (no linter configured; stdlib-only project formatted by hand)
- type check: N/A (no type checker configured; annotations used throughout)
- demo run: PASS (`python scripts/demo.py`, exit 0)
- example run: PASS (`PYTHONPATH=src python examples/invoice.py`)

## Commands executed

```shell
PYTHONPATH=src python -m pytest tests -q
PYTHONPATH=src python scripts/demo.py
PYTHONPATH=src python examples/invoice.py
```

## Observed test result

```text
..............................................                           [100%]
46 passed in 5.96s
```

Coverage: currency lookup and validation, 0/2/3-decimal round trips, all
documented rounding behavior, float/bool/NaN rejection, largest-remainder splits
for 1–11 parts over four amounts, fractional and zero weights, zero and negative
totals, tie-breaking, huge amounts, three- and zero-decimal currencies,
quantization before allocation, invalid weights and part counts, `Money`
arithmetic/formatting/mismatch handling, and every CLI subcommand and error path.

## Demo

`scripts/demo.py` runs the CLI, performs an exactness sweep using the library,
and prints an invoice example. Observed:

```text
$ centwise split 100.00 3
USD 100.00 split · 3 part(s) · scale 2
  1         33.34  (3334 minor)
  2         33.33  (3333 minor)
  3         33.33  (3333 minor)
  sum      100.00  (exact)

$ centwise allocate 250.00 --weights 2,3,5
  1         50.00  (5000 minor)
  2         75.00  (7500 minor)
  3        125.00  (12500 minor)
  sum      250.00  (exact)

$ centwise split 1000 3 --currency JPY   → 334, 333, 333   sum 1000 (exact)
$ centwise split 1.000 3 --currency KWD  → 0.334, 0.333, 0.333 sum 1.000 (exact)

exactness sweep: 164/164 cases exact
```

The library example computes `USD 199.99` subtotal, `USD 16.50` tax at 8.25%
(rounding 16.499175 once), `USD 216.49` total, and a three-way split of
`72.17 + 72.16 + 72.16 = 216.49` (exact).

The invoice example (`examples/invoice.py`) allocates `USD 2,197.48` at 2:5:3:
`439.50 + 1,098.74 + 659.24 = 2,197.48`, asserted at runtime.

Full output: `results/demo.txt`; exit codes and sweep count: `results/gate.txt`.

## Defects found and fixed while building

- The demo's invariant sweep passed float weights (`0.5`), which the library
  correctly rejects as inexact. The sweep now uses `"0.5"` strings, which is also
  the documented usage.
- Initial test expectations for `1.2345 KWD` (1.234 instead of 1.235) and for a
  1:3 split of 10 JPY (2/8 instead of 3/7) were wrong; the library's
  half-up rounding and earliest-part tie-break are the documented behavior, so
  the tests were corrected rather than the code.

## Limitations

- Currency scales are a fixed table of 30 codes, not a live ISO feed.
- Hamilton allocation can exhibit the Alabama paradox when the number of parts
  changes; not meaningful for the invoicing use case.
- No locale formatting, exchange conversion, tax rules or persistence.
- Correctness is established by invariant tests, not by comparison with a
  third-party money library.
