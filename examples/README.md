# Examples

`invoice.py` builds an invoice from three line items, applies 8.25% tax once,
and allocates the total across three cost centres weighted 2:5:3. It asserts that
the shares sum to the total and prints both, so running the example is the check.

```shell
PYTHONPATH=src python examples/invoice.py
```

```text
subtotal   USD 2,030.00
tax 8.25%  USD 167.48
total      USD 2,197.48
product      USD 439.50
engineering  USD 1,098.74
operations   USD 659.24
shares sum 2197.48
```

For CLI examples (`split`, `allocate`, `currencies`), see
[`docs/USAGE.md`](../docs/USAGE.md). The demo in `scripts/demo.py` runs those
commands and records the output in `results/`.
