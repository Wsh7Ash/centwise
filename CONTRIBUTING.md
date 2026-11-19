# Contributing

Thanks for taking a look at `centwise`.

## Development setup

```shell
git clone https://github.com/Wsh7Ash/centwise.git
cd centwise
python -m pip install -e ".[dev]"
```

No runtime dependencies, and `decimal` is the only numeric type. Do not
introduce floats internally.

## Running checks

```shell
PYTHONPATH=src python -m pytest tests -v
python scripts/demo.py
PYTHONPATH=src python examples/invoice.py
```

CLI tests spawn the module as a subprocess; keep passing `encoding="utf-8"` so
Windows consoles do not produce mojibake.

## Guidelines

- The exactness invariant is non-negotiable: `sum(parts) == quantize(total)`.
  Any change to `allocate` must keep the sweep in `scripts/demo.py` green and add
  a targeted test for the new behavior.
- Money arithmetic happens in integer minor units. If you need more precision,
  say why in the pull request.
- Reject ambiguous input (floats, mixed currencies, unknown codes) instead of
  coercing it.
- Document behavior that callers can observe: rounding mode, tie-break, negative
  totals, and zero weights.
- New currencies need a scale-backed test, not just a table entry.

## Reporting bugs

Include the exact call, the currency, the expected parts and the observed parts,
and state whether the total was negative. A split that does not sum is a
release-blocking bug.
