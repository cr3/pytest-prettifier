pytest-prettifier
=================

`Pytest <http://pytest.org>`_ fixture to prettify test parameters.

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/cr3/pytest-prettifier/blob/master/LICENSE
   :alt: License
.. image:: https://img.shields.io/pypi/v/pytest-prettifier.svg
   :target: https://pypi.python.org/pypi/pytest-prettifier/
   :alt: PyPI
.. image:: https://img.shields.io/github/issues-raw/cr3/pytest-prettifier.svg
   :target: https://github.com/cr3/pytest-prettifier/issues
   :alt: Issues

Requirements
------------

You will need the following prerequisites to use pytest-prettifier:

- Python 3.9, 3.10, 3.11, 3.12, 3.13

Installation
------------

To install pytest-prettifier:

.. code-block:: bash

  $ pip install pytest-prettifier

Usage
-----

You can see the benefits when using test parameters:

.. code-block:: python

  @pytest.mark.parametrize('x', [
      b'a',
  ])
  def test_x(x):
      assert x == b'a'

Without the ``prettifier`` fixture:

.. code-block:: console

  > pytest -s -v
  test_file.py::test_x[a] PASSED

With the ``prettifier`` fixture:

.. code-block:: console

  > pytest -s -v
  test_file.py::test_x[b'a'] PASSED

Here are some of the plugins available by default:

* ``bytes`` output as ``b'bytes'``.
* ``datetime`` output as ``<2000-01-01T00:00:00.000000+00:00>``.
* ``dict`` output as ``{'a': 1}``.
* ``exception`` output as ``KeyError('key')``.
* ``list`` output as ``[1, 'a']``.
* ``mock`` output as ``Mock(call_count=0)``.
* ``object`` output as ``1``, ``""``, ``[]``, ``{}``, etc.
* ``re`` output as ``<test>``.
* ``set`` output as ``set([])``.
* ``str`` output as ``'str'``.
* ``timedelta`` output as ``1.0`` in seconds.
* ``tuple`` output as ``()``.
* ``type`` output as ``int``, ``Exception``, etc.

Extensions
----------

The ``prettifier`` fixture can be extended with custom plugins:

.. code-block:: python

  from pytest_prettifier import PrettifierPlugin

  bool_prettifier = PrettifierPlugin(
      bool,
      lambda p, v, level=0: p.prettify_record("is true" if v else "is false", level),
  )

Then, add it to the ``pyproject.toml`` file of your project:

.. code-block:: text

  [tool.poetry.plugins."pytest_prettifier"]
  bool = "your_project.prettifier:bool_prettifier"

When you use boolean parameters:

.. code-block:: python

  @pytest.mark.parametrize('x', [
      True,
      False,
  ])
  def test_x(x):
      assert isinstance(x, bool)

The parameters will be prettified:

.. code-block:: console

  > pytest -s -v
  test_file.py::test_x[is true] PASSED
  test_file.py::test_x[is false] PASSED


Resources
---------

- `Documentation <https://cr3.github.io/pytest-prettifier/>`_
- `Release Notes <http://github.com/cr3/pytest-prettifier/blob/master/CHANGES.rst>`_
- `Issue Tracker <http://github.com/cr3/pytest-prettifier/issues>`_
- `Source Code <http://github.com/cr3/pytest-prettifier/>`_
- `PyPi <https://pypi.org/project/pytest-prettifier/>`_
