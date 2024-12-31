"""Prettifier for arbitrary Python data structures.

The prettify function can be used to format any object:

    >>> prettify({'a': 1}) == "{'a': 1}"
    True

The Prettifier class can be extended with custom types:

    >>> from attrs import make_class
    >>> Foo = make_class('Foo', ['x'])
    >>> prettifier = Prettifier(registry={
    ...     'pytest_prettifier': {
    ...         'foo': PrettifierPlugin(
    ...           Foo, lambda p, obj, level: p.prettify_record(obj.x, level)),
    ...     },
    ... })
    >>> prettifier.prettify(Foo(0)) == '0'
    True

Note that custom types can be defined in the default registry by specifying
them under the pytest_prettifier group in setup.py entry points.
"""

# This motivation for this module is that the pprint.PrettyPrinter class
# was not meant to be extended for custom types. Even if it was subclassed
# and the _format method was overridden to support these types, it would
# require lots of string manipulation to preserve the indentation level.

import re
from collections import UserDict, UserList, UserString
from collections.abc import Mapping, Sequence, Set
from contextlib import suppress
from datetime import datetime, timedelta
from unittest.mock import Mock

from attrs import asdict, define, field, has

from pytest_prettifier.registry import registry_load
from pytest_prettifier.timestamp import encode_timestamp


def prettify(obj, indent=2, newline="\n", level=0):
    """Return a prettified Python object."""
    prettifier = Prettifier(indent, newline)
    return prettifier.prettify(obj, level)


def pprettify(obj, *args, **kwargs):
    """Print a prettified Python object to stdout."""
    print(prettify(obj, *args, **kwargs))


@define(frozen=True)
class PrettifierPlugin:
    """Plugin for prettifying certain types of value."""

    types = field(converter=lambda t: t if isinstance(t, tuple) else (t,))
    prettify = field(repr=False)

    def priority(self, obj):
        """Priority of an object from 0 (highest) to -inf (lowest)."""
        priorities = []
        for t in self.types:
            with suppress(ValueError):
                priorities.append(
                    -[cls == t for cls in obj.__class__.__mro__].index(True),
                )

        try:
            return max(priorities)
        except ValueError:
            return float("-inf")


attrs_prettifier = PrettifierPlugin(
    None,
    lambda p, obj, level=0: p.prettify_fields(
        f"{obj.__class__.__name__}(",
        ", ",
        ")",
        sorted(
            "{key}={value}".format(
                key=p.prettify_record(key, level + 1).rstrip(),
                value=p.prettify(value, level + 1).lstrip(),
            )
            for key, value in asdict(obj, recurse=False).items()
        ),
        level,
    ),
)


bytes_prettifier = PrettifierPlugin(bytes, lambda p, obj, level=0: p.prettify_record(f"{obj!r}", level))


datetime_prettifier = PrettifierPlugin(
    datetime,
    lambda p, obj, level=0: p.prettify_record(f"<{encode_timestamp(obj)}>", level),
)

dict_prettifier = PrettifierPlugin(
    (dict, Mapping, UserDict),
    lambda p, obj, level=0: p.prettify_fields(
        "{}{{".format(
            "" if isinstance(obj, dict) else f"{obj.__class__.__name__}(",
        ),
        ", ",
        "}}{}".format(
            "" if isinstance(obj, dict) else ")",
        ),
        sorted(
            "{key}: {value}".format(
                key=p.prettify(key, level + 1).rstrip(),
                value=p.prettify(value, level + 1).lstrip(),
            )
            for key, value in obj.items()
        ),
        level,
    ),
)


try:
    _exception_type = BaseException
except NameError:  # pragma: no cover
    _exception_type = Exception

exception_prettifier = PrettifierPlugin(
    _exception_type,
    lambda p, obj, level=0: p.prettify_record(
        (
            obj.__class__.__name__
            if obj.__class__.__module__
            in (
                "builtins",
                "exceptions",
            )
            else "{}.{}".format(
                obj.__class__.__module__,
                obj.__class__.__name__,
            )
        ),
        level,
    ).rstrip()
    + p.prettify(getattr(obj, "args", ()), level).lstrip(),
)


list_prettifier = PrettifierPlugin(
    (list, Sequence, UserList),
    lambda p, obj, level=0: p.prettify_fields(
        "{}[".format(
            "" if isinstance(obj, list) else f"{obj.__class__.__name__}(",
        ),
        ", ",
        "]{}".format(
            "" if isinstance(obj, list) else ")",
        ),
        [p.prettify(item, level + 1) for item in obj],
        level,
    ),
)


mock_prettifier = PrettifierPlugin(
    Mock,
    lambda p, obj, level=0: p.prettify_fields(
        f"{obj.__class__.__name__}(",
        ", ",
        ")",
        [
            "{key}={value}".format(
                key=p.prettify_record(key, level + 1).rstrip(),
                value=p.prettify(value, level + 1).lstrip(),
            )
            for key, value in [
                (
                    "call_count",
                    obj.call_count,
                ),
                (
                    "return_value",
                    None if isinstance(obj.return_value, Mock) else obj.return_value,
                ),
                (
                    "side_effect",
                    obj.side_effect,
                ),
            ]
            if value is not None
        ],
        level,
    ),
)


object_prettifier = PrettifierPlugin(
    object,
    lambda p, obj, level=0: (
        attrs_prettifier.prettify(p, obj, level) if has(obj) else p.prettify_record(repr(obj), level)
    ),
)


re_prettifier = PrettifierPlugin(
    type(re.compile(r"")),
    lambda p, obj, level=0: p.prettify_record(f"<{obj.pattern}>", level),
)


set_prettifier = PrettifierPlugin(
    (set, Set),
    lambda p, obj, level=0: p.prettify_fields(
        f"{obj.__class__.__name__}([",
        ", ",
        "])",
        sorted(p.prettify(item, level + 1) for item in obj),
        level,
    ),
)


str_prettifier = PrettifierPlugin((str, UserString), lambda p, obj, level=0: p.prettify_record(f"{obj!r}", level))


timedelta_prettifier = PrettifierPlugin(
    timedelta,
    lambda p, obj, level=0: p.prettify_record(repr(obj.total_seconds()), level),
)


tuple_prettifier = PrettifierPlugin(
    tuple,
    lambda p, obj, level=0: p.prettify_fields("(", ", ", ")", [p.prettify(item, level + 1) for item in obj], level),
)


type_prettifier = PrettifierPlugin(
    type,
    lambda p, obj, level=0: p.prettify_record(
        (
            obj.__name__
            if obj.__module__
            in (
                "__builtin__",
                "_abcoll",
                "builtins",
                "collections.abc",
                "exceptions",
            )
            else f"{obj.__module__}.{obj.__name__}"
        ),
        level,
    ),
)


@define(frozen=True)
class Prettifier:
    """Make a readable version of a value, using plugins."""

    indent = field(default=2)
    newline = field(default="\n")
    registry = field(factory=lambda: registry_load("pytest_prettifier"))

    def prettify(self, obj, level=0):
        """Prettify an object using the plugins from the registry."""
        plugin = self.get_plugin(obj)
        return plugin.prettify(self, obj, level).rstrip()

    def prettify_fields(self, start, separator, end, fields, level=0):
        """Prettify fields with a start, end, and separators in between.

        The prettified fields are returned on multiple lines if there
        are more than 1 and one a single line if there are less.
        """
        if len(fields) > 1:

            def sep(index):
                return separator if index < len(fields) - 1 else ""

            parts = (
                [
                    self.prettify_record(start, level),
                ]
                + [self.prettify_record(field.strip() + sep(index), level + 1) for index, field in enumerate(fields)]
                + [
                    self.prettify_record(end, level).rstrip(),
                ]
            )
        else:
            parts = (
                [
                    start,
                ]
                + [
                    fields[0].strip() if fields else "",
                ]
                + [
                    end,
                ]
            )

        return "".join(parts)

    def prettify_record(self, obj, level=0):
        """Prettify a record.

        The prettified record is prefixed with indentation and suffixed
        with a newline.
        """
        return "{indent}{obj}{newline}".format(
            indent=" " * self.indent * level,
            newline=self.newline,
            obj=obj,
        )

    def get_plugin(self, obj):
        """Read plugins from pytest_prettifier entrypoint."""
        prettifiers = self.registry.get("pytest_prettifier", {})

        plugins = {p: p.priority(obj) for p in prettifiers.values()}
        if not plugins:
            raise KeyError("No plugins found")

        priority = max(plugins.values())
        if priority == float("-inf"):
            raise KeyError(f"No matching plugin found for {obj!r}")

        plugins = [k for k, v in plugins.items() if v == priority]
        if len(plugins) > 1:
            raise KeyError(f"More than one plugin found for {obj!r}: {plugins!r}")

        return plugins[0]
