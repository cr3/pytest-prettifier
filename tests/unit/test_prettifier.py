"""Test."""

import re
from collections.abc import Mapping, Sequence, Set
from datetime import datetime as dt
from datetime import timedelta as td
from unittest.mock import Mock, patch

import pytest
from attrs import make_class

from pytest_prettifier.prettifier import (
    Prettifier,
    PrettifierPlugin,
    attrs_prettifier,
    bytes_prettifier,
    datetime_prettifier,
    dict_prettifier,
    exception_prettifier,
    list_prettifier,
    mock_prettifier,
    object_prettifier,
    pprettify,
    prettify,
    re_prettifier,
    set_prettifier,
    str_prettifier,
    timedelta_prettifier,
    tuple_prettifier,
    type_prettifier,
)


class StubMapping(Mapping):
    """Stub of a mapping."""

    def __getitem__(self, key):
        raise KeyError(key)

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0


class StubSequence(Sequence):
    """Stub of a sequence."""

    def __getitem__(self, index):
        raise IndexError(index)

    def __len__(self):
        return 0


class StubSet(Set):
    """Stub of a set."""

    def __contains__(self, item):
        return False

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0


@pytest.fixture
def prettifier():
    """Prettifier instance that prettifies on a single line."""
    return Prettifier(indent=0, newline="")


@pytest.mark.parametrize(
    "obj, string",
    [
        ([], "[]"),
        ([1], "[1]"),
        (
            [1, 2],
            "\n".join([
                "[",
                "  1, ",
                "  2",
                "]",
            ]),
        ),
        (
            [1, [2, [3]]],
            "\n".join([
                "[",
                "  1, ",
                "  [",
                "    2, ",
                "    [3]",
                "  ]",
                "]",
            ]),
        ),
        ({}, "{}"),
        ({"a": 1}, "{'a': 1}"),
        (
            {"a": 1, "b": 2},
            "\n".join([
                "{",
                "  'a': 1, ",
                "  'b': 2",
                "}",
            ]),
        ),
        (
            [1, {"a": 2, "b": 3}],
            "\n".join([
                "[",
                "  1, ",
                "  {",
                "    'a': 2, ",
                "    'b': 3",
                "  }",
                "]",
            ]),
        ),
        (
            {"a": 1, ("b", "c"): [2, 3]},
            "\n".join([
                "{",
                "  'a': 1, ",
                "  (",
                "    'b', ",
                "    'c'",
                "  ): [",
                "    2, ",
                "    3",
                "  ]",
                "}",
            ]),
        ),
        (make_class("Test", [])(), "Test()"),
        (make_class("Test", ["a"])(1), "Test(a=1)"),
        (make_class("Test", ["a"])({1}), "Test(a=set([1]))"),
        (
            make_class("Test", ["a", "b"])(1, 2),
            "\n".join([
                "Test(",
                "  a=1, ",
                "  b=2",
                ")",
            ]),
        ),
        (
            make_class("Test", ["a"])({1, 2}),
            "\n".join([
                "Test(a=set([",
                "    1, ",
                "    2",
                "  ]))",
            ]),
        ),
    ],
)
def test_prettify(obj, string):
    """Prettifying an object should return a pretty string."""
    assert prettify(obj) == string


@patch("sys.stdout")
def test_pprettify(stdout):
    """Printing a prettified object should write to stdout."""
    pprettify([])
    assert stdout.write.call_args[0][0] == "[]\n"


@pytest.mark.parametrize(
    "types, obj, priority",
    [
        pytest.param(
            object,
            object(),
            0,
            id="0",
        ),
        pytest.param(
            object,
            int(),
            -1,
            id="-1",
        ),
        pytest.param(
            int,
            object(),
            float("-inf"),
            id="-inf",
        ),
    ],
)
def test_prettifier_plugin_priority(types, obj, priority):
    """The priority should be 0, -1 or -inf."""
    plugin = PrettifierPlugin(types, None)
    assert plugin.priority(obj) == priority


@pytest.mark.parametrize(
    "obj, string",
    [
        (make_class("Test", [])(), "Test()"),
        (make_class("Test", ["a"])(1), "Test(a=1)"),
        (make_class("Test", ["a", "b"])(1, ""), "Test(a=1, b='')"),
    ],
)
def test_attrs_prettifier(prettifier, obj, string):
    """Prettifying attrs should return the class and its attributes."""
    assert attrs_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        (b"bytes", "b'bytes'"),
    ],
)
def test_bytes_prettifier(prettifier, obj, string):
    """Prettifying bytes should return it with the `b` prefix."""
    assert bytes_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        (dt(2000, 1, 1), "<2000-01-01T00:00:00.000000+00:00>"),
    ],
)
def test_datetime_prettifier(prettifier, obj, string):
    """Prettifying a datetime should return the encoded timestamp."""
    assert datetime_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        ({}, "{}"),
        ({"a": 1}, "{'a': 1}"),
        ({"a": 1, "b": 2}, "{'a': 1, 'b': 2}"),
        (StubMapping(), "StubMapping({})"),
    ],
)
def test_dict_prettifier(prettifier, obj, string):
    """Prettifying a dict should return comma separated fields in curlies."""
    assert dict_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        (Exception(), "Exception()"),
        (KeyError("key"), "KeyError('key')"),
    ],
)
def test_exception_prettifier(prettifier, obj, string):
    """Prettifying a exception should return its name and arguments."""
    assert exception_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        ([], "[]"),
        ([1], "[1]"),
        ([1, "a"], "[1, 'a']"),
        (StubSequence(), "StubSequence([])"),
    ],
)
def test_list_prettifier(prettifier, obj, string):
    """Prettifying a list should return comma separated fields in squares."""
    assert list_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        (Mock(), "Mock(call_count=0)"),
        (Mock(return_value=0), "Mock(call_count=0, return_value=0)"),
        (Mock(side_effect=KeyError), "Mock(call_count=0, side_effect=KeyError)"),
    ],
)
def test_mock_prettifier(prettifier, obj, string):
    """Prettifying a mock should return its class representation."""
    assert mock_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj",
    [
        1,
        "",
        [],
        {},
    ],
)
def test_object_prettifier(prettifier, obj):
    """Prettifying a object should return its representation."""
    assert object_prettifier.prettify(prettifier, obj) == repr(obj)


@pytest.mark.parametrize(
    "obj, string",
    [
        (re.compile(r"test"), "<test>"),
    ],
)
def test_re_prettifier(prettifier, obj, string):
    """Prettifying a regular expression should return it in brackets."""
    assert re_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        (set(), "set([])"),
        ({1}, "set([1])"),
        ({1, "a"}, "set(['a', 1])"),
        (StubSet(), "StubSet([])"),
    ],
)
def test_set_prettifier(prettifier, obj, string):
    """Prettifying a set should return command separated fields as a set."""
    assert set_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        ("str", "'str'"),
    ],
)
def test_str_prettifier(prettifier, obj, string):
    """Prettifying a str should return it within quotes."""
    assert str_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        (td(seconds=1), "1.0"),
        (td(minutes=1, seconds=1), "61.0"),
    ],
)
def test_timedelta_prettifier(prettifier, obj, string):
    """Prettifying a timedelta should return the total seconds."""
    assert timedelta_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        ((), "()"),
        ((1,), "(1)"),
        ((1, "a"), "(1, 'a')"),
    ],
)
def test_tuple_prettifier(prettifier, obj, string):
    """Prettifying a tuple should return comma separated fields in parens."""
    assert tuple_prettifier.prettify(prettifier, obj) == string


@pytest.mark.parametrize(
    "obj, string",
    [
        (int, "int"),
        (Sequence, "Sequence"),
        (Exception, "Exception"),
        (Prettifier, "pytest_prettifier.prettifier.Prettifier"),
    ],
)
def test_type_prettifier(prettifier, obj, string):
    """Prettifying a type should return its name with module when relevant."""
    assert type_prettifier.prettify(prettifier, obj) == string


def test_prettifier_get_plugin_priority():
    """Getting a plugin should prioritize the most specific type."""
    prettifier = Prettifier(
        registry={
            "pytest_prettifier": {
                "obj": PrettifierPlugin(object, lambda *_: "obj"),
                "str": PrettifierPlugin(str, lambda *_: "str"),
            },
        }
    )
    plugin = prettifier.get_plugin("")
    result = plugin.prettify()
    assert result == "str"


def test_prettifier_get_plugin_no_plugins():
    """Getting a plugin should raise when there are none."""
    prettifier = Prettifier(registry={})
    with pytest.raises(KeyError) as e:
        prettifier.get_plugin([])

    assert "No plugins" in e.value.args[0]


def test_prettifier_get_plugin_no_match():
    """Getting a plugin should raise when there are no matches."""
    prettifier = Prettifier(
        registry={
            "pytest_prettifier": {
                "str": PrettifierPlugin(str, lambda *_: None),
            },
        }
    )
    with pytest.raises(KeyError) as e:
        prettifier.get_plugin([])

    assert "No match" in e.value.args[0]


def test_prettifier_get_plugin_more_than_one():
    """Getting a plugin should raise when there are multiple matches."""
    prettifier = Prettifier(
        registry={
            "pytest_prettifier": {
                "str1": PrettifierPlugin(str, lambda *_: None),
                "str2": PrettifierPlugin(str, lambda *_: None),
            },
        }
    )
    with pytest.raises(KeyError) as e:
        prettifier.get_plugin("")

    assert "More than one" in e.value.args[0]
