"""Unit tests for the time module."""
from datetime import datetime, timedelta, timezone

import pytest

from pytest_prettifier.timestamp import (
    decode_timestamp,
    encode_timestamp,
    tzutc,
)


def test_decode_timestamp():
    """A simple ISO UTC timestamp is decoded into a timezone-naive datetime."""
    result = decode_timestamp("2014-09-11T20:35:00.123456Z")
    assert result == datetime(2014, 9, 11, 20, 35, 0, 123456, tzinfo=tzutc)


def test_decode_timestamp_no_timezone():
    """A string timestamp with no timezone specified is assumed to be UTC."""
    result = decode_timestamp("2014-09-11T10:35:19")
    assert result == datetime(2014, 9, 11, 10, 35, 19, tzinfo=tzutc)


def test_decode_timestamp_to_utc():
    """A string timestamp with a timezone specified is converted."""
    result = decode_timestamp("2014-09-11T10:35:00.123-03:30")
    assert result == datetime(2014, 9, 11, 14, 5, 0, 123000, tzinfo=tzutc)


def test_decode_timestamp_already_a_naive_datetime():
    """A timezone-naive datetime object is assumed to be UTC."""
    result = decode_timestamp(datetime(2014, 9, 11, 1, 2, 3, 456789))
    assert result == datetime(2014, 9, 11, 1, 2, 3, 456789, tzinfo=tzutc)


def test_decode_timestamp_already_a_utc_datetime():
    """A timezone aware UTC datetime object is converted to naive."""
    result = decode_timestamp(datetime(2014, 9, 11, 1, 2, 3, 456789, tzinfo=tzutc))
    assert result == datetime(2014, 9, 11, 1, 2, 3, 456789, tzinfo=tzutc)


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


def test_encode_timestamp():
    """A datetime object is converted to an ISO-formatted timestamp string."""
    result = encode_timestamp(datetime(2014, 9, 11, 1, 2, 3, 456789))
    assert result == "2014-09-11T01:02:03.456789+00:00"


@pytest.mark.parametrize(
    "offset,expected_offset",
    [
        (4, "+04:00"),
        (0, "+00:00"),
        (-4, "-04:00"),
    ],
)
def test_encode_timestamp_with_non_tz_fixed_offset_class_object_as_timezone(offset, expected_offset):
    """When udatetime gets a good but unknown timezeone it's not happy.

    ValueError: Only TZFixedOffset supported.
    """
    result = encode_timestamp(datetime(2014, 9, 11, 1, 2, 3, 456789, tzinfo=timezone(timedelta(hours=offset))))

    assert result == f"2014-09-11T01:02:03.456789{expected_offset}"
