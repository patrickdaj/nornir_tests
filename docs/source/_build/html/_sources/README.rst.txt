.. image:: https://img.shields.io/badge/docs-passing-green.svg
   :target: https://patrickdaj.github.io/nornir_tests
   :alt: Documentation

.. image:: https://github.com/patrickdaj/nornir_tests/workflows/test_nornir_tests/badge.svg
   :target: https://github.com/patrickdaj/nornir_tests/actions?query=workflow%3Atest_nornir_tests
   :alt: test_nornir_tests

nornir_tests
============

Collection of test/assertion plugins for `nornir <github.com/nornir-automation/nornir/>`_

Installation
------------

.. code::

    pip install nornir_tests

Plugins
-------

Tests
_____

* **test_regexp** - Run assertions on nornir results using assertpy's text assertions
* **test_jsonpath** - Run assertions on nornir results dictionaries using many of assertpy's assertions like "is_in", "is_equal_to" or "contains"
* **test_timing** - Gather timing info from tasks
* **test_wait** - Re-run tasks until assertions pass
* **test_xpath** - Run assertions on nornir results XML using many of assertpy's assertions like "is_in", "is_equal_to" or "contains"


Common Uses
-----------

* Timing a task and making sure it completes within x seconds
* Faling a task if it isn't changed
* Faling a task if text is not in results attribute
* Using jsonpath or xpath to assert a value at a particular path
* Passing a task for an expected exception
* Testing a condition repeatedly until all tests are passing
* Nest multiple tests

Examples
--------

.. toctree::
   :maxdepth: 1

   examples/introduction
   examples/using-test-jsonpath
   examples/using-test-regexp
   examples/using-test-lxml
   examples/using-test-timing
   examples/using-test-until
   examples/all-methods-of-using


How it works
------------

    Each of the tests is actually a decorator or wrapper.  Because of the way nornir works there is
    no way to use normal @ decorator syntax as these need to be applied before function definitions.
    That is possible but not as flexible.  So in order to apply the decorators at runtime, they are
    paired with a special processor that looks for them in task.params.

    Once the task is wrapped, when Nornir calls it the decorator can run code before and after
    execution of the task.  It can then affect the actual result being returned.  For this reason
    it does not really work for anything that doesn't return a result.  So wrapping calls to tasks
    defined in plugins like nornir_napalm or nornir_utils works fine.  Wrapping grouped_task is not
    currently possible but the tasks within the grouped task are.  Nornir run commands that return
    results work fine.

References
----------

The nornir_tests plugin uses other libraries that are pretty critical to know in order to use nornir_tests efficiently.

`jsonpath_ng <https://github.com/h2non/jsonpath-ng>`__ - The github page has a fairly good intro to using jsonpath.

`xpath cheatsheat <https://devhints.io/xpath>`__ - The lxml documentation is great and all but its quite a bit and using something like this cheat sheet is a bit less daunting.

`assertpy <https://github.com/assertpy/assertpy>`__ - This documentation is pretty concise and this module is really the reason I wrote nornir_tests.  Prior to nornir_tests, I was running tasks that executed a bunch of python asserts using tasks.  It didn't permit stacking of assertions or very flexible control of whether or not it should fail a task.