#!/usr/bin/env python3
"""Run centwise over realistic allocations and verify the exactness invariant."""

from __future__ import annotations

import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:  # pragma: no cover
    pass

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
sys.path.insert(0, str(ROOT / "src"))

from centwise import Money, allocate, split  # noqa: E402


def run_cli(args: list[str]) -> tuple[int, str]:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        [sys.executable, "-m", "centwise", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    return proc.returncode, (proc.stdout + proc.stderr).rstrip()


def invariant_sweep() -> tuple[int, int]:
    amounts = ["0.01", "0.05", "1.00", "10.00", "99.99", "1234.56", "999999999999.99", "-100.00"]
    cases = 0
    failures = 0
    for amount in amounts:
        for count in range(1, 21):
            parts = split(amount, count)
            cases += 1
            expected = Decimal(amount).quantize(Decimal("0.01"))
            if sum(parts, Decimal(0)) != expected or max(parts) - min(parts) > Decimal("0.01"):
                failures += 1
    for weights in ([1, 2, 3], ["0.5", "0.5"], [1, 0, 2], [7, 11, 13, 17]):
        parts = allocate("250.00", weights)
        cases += 1
        if sum(parts, Decimal(0)) != Decimal("250.00"):
            failures += 1
    return cases, failures


def main() -> int:
    RESULTS.mkdir(exist_ok=True)
    sections: list[str] = []
    gates: list[str] = []
    failures = 0

    steps = [
        ("split 100.00 by 3", ["split", "100.00", "3"]),
        ("allocate 250.00 at 2:3:5", ["allocate", "250.00", "--weights", "2,3,5"]),
        ("split 1000 JPY by 3", ["split", "1000", "3", "--currency", "JPY"]),
        ("split 1.000 KWD by 3", ["split", "1.000", "3", "--currency", "KWD"]),
        ("split 100.00 by 3 as JSON", ["split", "100.00", "3", "--json"]),
    ]
    for title, args in steps:
        code, output = run_cli(args)
        sections.append(f"$ centwise {' '.join(args)}\n{output}\n[exit code: {code}]")
        gates.append(f"{title}: exit code {code}")
        if code != 0:
            failures += 1

    cases, bad = invariant_sweep()
    gates.append(f"exactness sweep: {cases - bad}/{cases} cases exact")
    if bad:
        failures += 1

    invoice = Money("120.00", "USD") + Money("79.99", "USD")
    tax = invoice * Decimal("0.0825")
    shares = (invoice + tax).split(3)
    lines = [
        "library example",
        f"  subtotal        {invoice.format()}",
        f"  tax at 8.25%    {tax.format()}",
        f"  total           {(invoice + tax).format()}",
        f"  three-way split {', '.join(share.format() for share in shares)}",
        f"  shares sum      {sum((share.amount for share in shares), Decimal(0))} "
        f"({'exact' if sum((share.amount for share in shares), Decimal(0)) == (invoice + tax).amount else 'MISMATCH'})",
    ]
    sections.append("\n".join(lines))

    separator = "\n\n" + ("-" * 78) + "\n\n"
    text = separator.join(sections) + "\n"
    (RESULTS / "demo.txt").write_text(text, encoding="utf-8")
    (RESULTS / "gate.txt").write_text("\n".join(gates) + "\n", encoding="utf-8")
    print(text)
    print("\n".join(gates))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
