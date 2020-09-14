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

Tasks
_____

* ** test ** - Run test_regexp, test_jsonpath, or test_xpath or a combination as a task

Processors
__________

* **TestProcessor** - Lightly modified processor to allow for tasks to be decorated at run-time


Common Uses
-----------

* Timing a task and making sure it completes within x seconds
* Faling a task if it isn't changed
* Faling a task if text is not in results attribute
* Using jsonpath or xpath to assert a value at a particular path
* Passing a task for an expected exception
* Testing a condition repeatedly until all tests are passing
* Nest multiple tests

Usage
-----
This is a simple example of using nornir_tests to run a command with an assertion and then 
perform an action and combine assertions to wait for a successful result.  More examples can
be seen in the documentation.

.. code-block:: python

    >>> from nornir_netmiko.tasks import netmiko_send_command
    >>> from nornir_napalm.plugins.tasks import napalm_get
    >>> from nornir_tests.plugins.tests import test_until, test_jsonpath
    >>> from nornir import InitNornir
    >>> from nornir_utils.plugins.functions import print_result
    >>> from nornir_tests.plugins.processors import TestsProcessor
    >>> nr = InitNornir(
    ...         inventory={
    ...             "plugin": "SimpleInventory",
    ...             "options": {
    ...                 "host_file": "data/hosts.yaml",
    ...                 "group_file": "data/groups.yaml",
    ...                 "defaults_file": "data/defaults.yaml",
    ...             },
    ...         },
    ...     )
    >>> nr.processors.append(TestsProcessor())
    >>> vyos = nr.filter(name='vyos')
    >>> print_result(vyos.run(task=netmiko_send_command, command_string='reboot now'))
    netmiko_send_command************************************************************
    * vyos ** changed : False ******************************************************
    vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    ^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    >>> print_result(vyos.run(
    ...         task=napalm_get,
    ...         getters=['interfaces'],
    ...         tests=[
    ...             test_jsonpath(path='interfaces.eth0.is_up', assertion='is_true', fail_task=True),
    ...             test_until(initial_delay=15, retries=10, delay=15, reset_conns=True),
    ...         ]
    ...     ), vars=['tests', 'result'])
    napalm_get**********************************************************************
    * vyos ** changed : False ******************************************************
    vvvv napalm_get ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
    TestList(tests=[test_jsonpath(exception=None, fail_task=True, passed=True, assertion='is_true', 
    value=None, path='interfaces.eth0.is_up', host_data='', one_of=False, result_attr='result', 
    matches=['interfaces.eth0.is_up']), test_until(exception=None, fail_task=False, passed=True, 
    initial_delay=15, retries=10, delay=15, reset_conns=True, t0=1600059187.4073257, 
    t1=1600059228.9614654, run_time=41.554139614105225)])
    { 'interfaces': { 'eth0': { 'description': '',
                                'is_enabled': True,
                                'is_up': True,
                                'last_flapped': -1.0,
                                'mac_address': '08:00:27:e0:28:63',
                                'mtu': -1,
                                'speed': 0},
                    'lo': { 'description': '',
                            'is_enabled': True,
                            'is_up': True,
                            'last_flapped': -1.0,
                            'mac_address': '00:00:00:00:00:00',
                            'mtu': -1,
                            'speed': 0}}}
    ^^^^ END napalm_get ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



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