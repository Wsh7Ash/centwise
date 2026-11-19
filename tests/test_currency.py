from decimal import Decimal

import pytest

from centwise.currency import (
    CURRENCIES,
    Currency,
    as_decimal,
    get_currency,
    round_amount,
)


def test_lookup_is_case_insensitive():
    assert get_currency("usd") is CURRENCIES["USD"]
    assert get_currency(" Kwd ") is CURRENCIES["KWD"]
    assert get_currency(CURRENCIES["JPY"]).scale == 0


def test_unknown_currency():
    with pytest.raises(ValueError, match="unknown currency"):
        get_currency("XXX")


def test_currency_validation():
    assert Currency("usd", 2).code == "USD"
    with pytest.raises(ValueError, match="invalid currency code"):
        Currency("US", 2)
    with pytest.raises(ValueError, match="invalid currency code"):
        Currency("US1", 2)
    with pytest.raises(ValueError, match="invalid scale"):
        Currency("USD", 5)


def test_minor_unit_round_trip():
    usd = get_currency("USD")
    assert usd.minor_units == 100
    assert usd.to_minor(Decimal("12.34")) == 1234
    assert usd.from_minor(1234) == Decimal("12.34")
    kwd = get_currency("KWD")
    assert kwd.to_minor(Decimal("1.234")) == 1234
    assert kwd.from_minor(1234) == Decimal("1.234")
    jpy = get_currency("JPY")
    assert jpy.to_minor(Decimal("1000")) == 1000
    assert jpy.from_minor(1000) == Decimal("1000")


def test_to_minor_rounds_half_up_by_default():
    assert get_currency("USD").to_minor(Decimal("1.005")) == 101
    assert get_currency("USD").to_minor(Decimal("1.004")) == 100


def test_round_amount_modes():
    assert round_amount("2.345", "USD") == Decimal("2.35")
    assert round_amount("2.345", "USD", "ROUND_DOWN") == Decimal("2.34")
    assert round_amount("2.5", "JPY") == Decimal("3")
    assert round_amount("-2.5", "JPY", "ROUND_HALF_UP") == Decimal("-3")
    with pytest.raises(ValueError, match="unknown rounding mode"):
        round_amount("1", "USD", "ROUND_SIDEWAYS")


def test_as_decimal_rejects_floats_and_non_finite():
    with pytest.raises(TypeError, match="floats are inexact"):
        as_decimal(1.1)
    with pytest.raises(ValueError, match="finite"):
        as_decimal(Decimal("NaN"))
    with pytest.raises(ValueError, match="invalid decimal"):
        as_decimal("twelve")
    with pytest.raises(TypeError, match="boolean"):
        as_decimal(True)
    with pytest.raises(TypeError, match="cannot use"):
        as_decimal([1])


def test_all_registered_scales_match_known_minor_units():
    assert len(CURRENCIES) >= 25
    assert CURRENCIES["JPY"].scale == 0
    assert CURRENCIES["USD"].scale == 2
    assert CURRENCIES["KWD"].scale == 3
    assert all(0 <= item.scale <= 3 for item in CURRENCIES.values())
