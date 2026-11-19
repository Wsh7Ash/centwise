"""Command line entry point for centwise."""

from __future__ import annotations

import argparse
import sys

from .currency import CURRENCIES, get_currency
from .render import build_result, render_currencies, render_json, render_text


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="centwise",
        description="Split money exactly, to the minor unit, with no lost cents.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    split_cmd = sub.add_parser("split", help="split an amount into equal parts")
    split_cmd.add_argument("total")
    split_cmd.add_argument("parts", type=int)
    _common(split_cmd)

    allocate_cmd = sub.add_parser("allocate", help="split an amount by weights")
    allocate_cmd.add_argument("total")
    allocate_cmd.add_argument(
        "--weights", required=True, help="comma-separated weights, e.g. 1,2,3 or 0.5,0.5"
    )
    _common(allocate_cmd)

    currencies = sub.add_parser("currencies", help="list supported currencies and scales")
    currencies.add_argument("--json", action="store_true")
    return parser


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--json", action="store_true")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "currencies":
        sys.stdout.write(render_currencies(CURRENCIES, args.json))
        return 0

    try:
        get_currency(args.currency)
    except (TypeError, ValueError) as exc:
        print(f"centwise: {exc}", file=sys.stderr)
        return 2

    try:
        if args.command == "split":
            if args.parts < 1:
                raise ValueError("parts must be at least 1")
            result = build_result(args.total, [1] * args.parts, args.currency, "split")
        else:
            weights = [part.strip() for part in args.weights.split(",")]
            if not weights or any(not weight for weight in weights):
                raise ValueError("weights must be a comma-separated list of numbers")
            result = build_result(args.total, weights, args.currency, "allocation")
    except (TypeError, ValueError) as exc:
        print(f"centwise: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(render_json(result) if args.json else render_text(result))
    return 0 if result.exact else 1
