from decimal import Decimal

import pytest

from centwise import Money
from centwise.currency import get_currency


def test_constructs_and_quantizes():
    assert Money("10", "USD").amount == Decimal("10.00")
    assert Money("1.005", "USD").amount == Decimal("1.01")
    assert Money(7, "JPY").amount == Decimal("7")
    assert Money("1.2345", "KWD").amount == Decimal("1.235")


def test_construction_rejects_floats_and_unknown_currency():
    with pytest.raises(TypeError, match="floats are inexact"):
        Money(1.5, "USD")
    with pytest.raises(ValueError, match="unknown currency"):
        Money("1.00", "ZZZ")


def test_zero_and_equality():
    assert Money.zero("EUR") == Money("0.00", "EUR")
    assert Money("1.00", "EUR") != Money("1.00", "USD")


def test_arithmetic_same_currency():
    a = Money("10.00", "USD")
    b = Money("2.50", "USD")
    assert (a + b).amount == Decimal("12.50")
    assert (a - b).amount == Decimal("7.50")
    assert (-a).amount == Decimal("-10.00")
    assert (a * 3).amount == Decimal("30.00")
    assert (a * Decimal("0.5")).amount == Decimal("5.00")
    assert (2 * b).amount == Decimal("5.00")


def test_arithmetic_rounds_to_the_minor_unit():
    assert (Money("10.00", "USD") * Decimal("0.3333")).amount == Decimal("3.33")


def test_currency_mismatch_is_rejected():
    with pytest.raises(ValueError, match="cannot combine"):
        Money("1.00", "USD") + Money("1.00", "EUR")
    with pytest.raises(ValueError, match="cannot combine"):
        Money("1.00", "USD") - Money("1.00", "EUR")
    with pytest.raises(TypeError, match="expected Money"):
        Money("1.00", "USD") + 1


def test_allocate_and_split_return_money():
    parts = Money("100.00", "USD").split(3)
    assert [part.amount for part in parts] == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]
    assert all(part.currency == get_currency("USD") for part in parts)
    # 10 yen at 1:3 is 2.5 and 7.5; the tie for the leftover yen goes to the
    # earliest part, matching the library's documented tie-break.
    weighted = Money("10.00", "JPY").allocate([1, 3])
    assert [part.amount for part in weighted] == [Decimal("3"), Decimal("7")]


def test_format_grouping():
    assert Money("1234.5", "USD").format() == "USD 1,234.50"
    assert Money("1234.5", "USD").format(grouping=False) == "USD 1234.50"
    assert Money("1000", "JPY").format() == "JPY 1,000"
    assert str(Money("2", "KWD")) == "KWD 2.000"
    assert Money("-0.5", "USD").format() == "USD -0.50"


def test_to_dict():
    assert Money("12.34", "USD").to_dict() == {
        "amount": "12.34",
        "currency": "USD",
        "minor": 1234,
    }
