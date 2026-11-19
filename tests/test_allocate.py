from decimal import Decimal

import pytest

from centwise import allocate, split


def total(parts):
    return sum(parts, Decimal(0))


def test_three_way_split_is_exact_and_front_loaded():
    parts = split("100.00", 3)
    assert parts == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]
    assert total(parts) == Decimal("100.00")


def test_every_cent_is_assigned_for_many_divisors():
    for amount in ("0.01", "10.00", "99.99", "1234.56"):
        for count in range(1, 12):
            parts = split(amount, count)
            assert total(parts) == Decimal(amount), (amount, count, parts)
            assert len(parts) == count
            spread = max(parts) - min(parts)
            assert spread <= Decimal("0.01")


def test_weights_use_largest_remainder():
    parts = allocate("10.00", [1, 2, 3])
    assert parts == [Decimal("1.67"), Decimal("3.33"), Decimal("5.00")]
    assert total(parts) == Decimal("10.00")


def test_fractional_weights():
    parts = allocate("10.00", ["0.1", "0.2", "0.7"])
    assert parts == [Decimal("1.00"), Decimal("2.00"), Decimal("7.00")]


def test_zero_weight_gets_nothing():
    parts = allocate("12.00", [1, 0, 1])
    assert parts == [Decimal("6.00"), Decimal("0.00"), Decimal("6.00")]


def test_zero_total():
    assert allocate("0", [1, 2, 3]) == [Decimal("0.00")] * 3


def test_negative_total_mirrors_positive():
    positive = split("100.00", 3)
    negative = split("-100.00", 3)
    assert negative == [-part for part in positive]
    assert total(negative) == Decimal("-100.00")


def test_ties_go_to_the_earliest_part():
    parts = allocate("0.05", [1, 1, 1, 1, 1])
    assert parts[:1] == [Decimal("0.01")]
    assert parts[1:] == [Decimal("0.01")] * 4
    assert allocate("0.03", [1] * 5)[:3] == [Decimal("0.01")] * 3


def test_three_decimal_currency():
    parts = split("1.000", 3, "KWD")
    assert parts == [Decimal("0.334"), Decimal("0.333"), Decimal("0.333")]
    assert total(parts) == Decimal("1.000")


def test_zero_decimal_currency():
    parts = split("1000", 3, "JPY")
    assert parts == [Decimal("334"), Decimal("333"), Decimal("333")]
    assert total(parts) == Decimal("1000")


def test_total_is_quantized_before_allocation():
    parts = split("10.005", 3)
    assert total(parts) == Decimal("10.01")


def test_large_amounts_stay_exact():
    parts = split("999999999999.99", 7)
    assert total(parts) == Decimal("999999999999.99")


def test_weights_win_over_equal_split():
    assert allocate("0.03", [1, 2]) == [Decimal("0.01"), Decimal("0.02")]


@pytest.mark.parametrize(
    "weights,match",
    [
        ([], "at least one weight"),
        ([0, 0], "greater than zero"),
        ([1, -1], "non-negative"),
        ("1,2", "not a string"),
    ],
)
def test_invalid_weights(weights, match):
    with pytest.raises((ValueError, TypeError), match=match):
        allocate("1.00", weights)


@pytest.mark.parametrize("parts", [0, -1])
def test_invalid_part_count(parts):
    with pytest.raises(ValueError, match="at least 1"):
        split("1.00", parts)


def test_part_count_must_be_integer():
    with pytest.raises(TypeError, match="integer"):
        split("1.00", 2.0)
    with pytest.raises(TypeError, match="integer"):
        split("1.00", True)


def test_unknown_currency_and_bad_total():
    with pytest.raises(ValueError, match="unknown currency"):
        split("1.00", 2, "ZZZ")
    with pytest.raises(ValueError, match="invalid decimal"):
        split("one", 2)
    with pytest.raises(TypeError, match="floats"):
        split(1.0, 2)
