"""Unit tests for the time module."""

from datetime import datetime, timedelta, timezone

import pytest
from dateutil import tz

from pytest_prettifier.timestamp import (
    decode_timestamp,
    encode_timestamp,
    tzutc,
)


def test_decode_timestamp():
    """A simple ISO UTC timestamp is decoded into a timezone-naive datetime."""
    result = decode_timestamp("2000-01-01T00:00:00.000000Z")
    assert result == datetime(2000, 1, 1, tzinfo=tzutc)


def test_decode_timestamp_no_timezone():
    """A string timestamp with no timezone specified is assumed to be UTC."""
    result = decode_timestamp("2000-01-01T00:00:00")
    assert result == datetime(2000, 1, 1, tzinfo=tzutc)


def test_decode_timestamp_to_utc():
    """A string timestamp with a timezone specified is converted."""
    result = decode_timestamp("2000-01-01T00:00:00.000-01:00")
    assert result == datetime(2000, 1, 1, 1, tzinfo=tzutc)


def test_decode_timestamp_already_a_naive_datetime():
    """A timezone-naive datetime object is assumed to be UTC."""
    result = decode_timestamp(datetime(2000, 1, 1))
    assert result == datetime(2000, 1, 1, tzinfo=tzutc)


def test_decode_timestamp_already_a_utc_datetime():
    """A timezone aware UTC datetime object is converted to naive."""
    result = decode_timestamp(datetime(2000, 1, 1, tzinfo=tzutc))
    assert result == datetime(2000, 1, 1, tzinfo=tzutc)


@pytest.mark.parametrize(
    "timestamp",
    [
        None,
        1,
    ],
)
def test_decode_timestamp_invalid_type(timestamp):
    """Raise TypeError on invalid timestamp type."""
    with pytest.raises(TypeError):
        decode_timestamp(timestamp)


def test_decode_timestamp_invalid_string():
    """Raise a ValueErorr on invalid timestamp string."""
    with pytest.raises(ValueError):
        decode_timestamp("test")


def test_encode_timestamp_without_tzinfo():
    """A datetime without tzinfo should default to UTC."""
    result = encode_timestamp(datetime(2000, 1, 1))

    assert result == "2000-01-01T00:00:00.000000+00:00"


def test_encode_timestamp_with_tzinfo_as_timezone():
    """A datetime with tzinfo as should convert it to a tzoffset."""
    result = encode_timestamp(datetime(2000, 1, 1, tzinfo=timezone(timedelta(hours=1))))
    assert result == "2000-01-01T00:00:00.000000+01:00"


def test_encode_timestamp_with_tzinfo_as_tzoffset():
    """A datetime with a tzinfo as tzoffset should leave it as is."""
    result = encode_timestamp(datetime(2000, 1, 1, tzinfo=tz.tzoffset(None, 60 * 60)))
    assert result == "2000-01-01T00:00:00.000000+01:00"
