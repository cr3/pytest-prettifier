"""Common operations for dealing with dates and timestamps.

Here are examples to decode and encode timestamps:

    >>> (decode_timestamp('2000-01-01T00:00:00') ==
    ... parse('2000-01-01T00:00:00+00:00'))
    True
    >>> (encode_timestamp(datetime(2000, 1, 1)) ==
    ... '2000-01-01T00:00:00.000000+00:00')
    True
"""

from datetime import datetime, timedelta

from dateutil.parser import parse
from dateutil.tz import UTC, tz


def decode_timestamp(timestamp):
    """Parse a string or a datetime object to extract a timestamp.

    :raises TypeError: If the timestamp type is invalid.
    :raises ValueError: If the timestamp string is invalid.
    :returns: Datetime object with a tzinfo.
    """
    # If timestamp is not already a datetime, try to parse
    if not isinstance(timestamp, datetime):
        parsed_timestamp = parse(timestamp)
        if parsed_timestamp is None:
            raise ValueError(f"{timestamp!r} is not a valid timestamp")

        timestamp = parsed_timestamp

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=tzutc)

    return timestamp


def encode_timestamp(timestamp):
    """Write a timestamp out as a string.

    datetime expects the tzinfo to be tzoffset even if the given timezone
    does implement the tzinfo abstract class.  Solution is to replace the
    actual timezone with a tzoffset that takes minutes.
    """
    if timestamp.tzinfo is not None and not isinstance(timestamp.tzinfo, tz.tzoffset):
        utcoffset = timestamp.tzinfo.utcoffset(None) // timedelta(seconds=1)
        timestamp = timestamp.replace(tzinfo=tz.tzoffset(None, utcoffset))
    elif timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=tzutc)

    return timestamp.isoformat(timespec="microseconds")


tzutc = UTC
