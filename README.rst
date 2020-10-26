.. image:: https://img.shields.io/badge/docs-passing-green.svg
   :target: https://patrickdaj.github.io/nornir_tests
   :alt: Documentation

.. image:: https://github.com/patrickdaj/nornir_tests/workflows/test_nornir_tests/badge.svg
   :target: https://github.com/patrickdaj/nornir_tests/actions?query=workflow%3Atest_nornir_tests
   :alt: test_nornir_tests

nornir_tests
============

Collection of test/assertion plugins for `nornir <github.com/nornir-automation/nornir/>`_

The point of nornir_tests is to provide a bit more flexibility in how the data that is sent back from
a task run is validated.  When using a task like napalm_get or netmiko_send_command, the results
come back in a variety of forms and typically code needs to be written to validate and/or act upon it.  
One issue with this methodology is that you can't easily impact the result passed/failed attribute.  
nornir_tests is meant to validate the result data and make sure the returned result is correct and not 
just that it came back.  It also adds some utility methods that pair well with the tests.  It utilizes 
a few different libraries to hopefully make things a bit easier to test.

Installation
------------

.. code::

    pip install nornir_tests

Plugins
-------

Tests
_____

* **regexp** - Run assertions on nornir results using assertpy's assertions
* **jpath** - Run assertions on nornir results dictionaries using many of assertpy's assertions
* **timing** - Gather timing info from tasks
* **wait** - Re-run tasks until assertions pass
* **xpath** - Run assertions on nornir results XML using many of assertpy's assertions
* **callback** - Run a custom callback to handle results
* **shorten** - (Not implemented) Shorten the data in result using jpath/xpath/regexp
* **when** - (Not implemented) Conditionally skip tasks based on jpath/xpath/regexp
* **loop** - (Work in progress) Repeat task using a list of values

Tasks
_____

* **wrap_task** - Wrap a nornir task with tests without having to use @ decorator syntax


Common Uses
-----------

* Validating returned results and modifying Result object based on test parameters
* Only running a task on a subset of inventory depending on a pre-test
* Timing a task and making sure it completes within a certain amount of time
* Asserting particular values exist at a path using regexp, jsonpath or xpath
* Passing a task for an expected exception
* Testing a condition repeatedly until all tests are passing, like a reboot, or job completing
* Nest multiple tests
* Reduce the result in some fashion

One thing to address is that all of these things can be done with Nornir and Python without
this module except.  In most cases the hope is that the code involved will look cleaner and
be much shorter with nornir_tests.  There are certainly some neat things that nornir_tests can
do that would require some trickier/uglier code to accomplish without it.  The real goal is to
obtain a clean way to test nornir results but there are a few random methods that have been
implemented that are more of nice to haves such as shorten and loop.

What does it do exactly?
------------------------

Integrate validations into running of a task.  This allows the validation to impact whether or
not the task failed.  Validations can be chained together.  Supports jsonpath, xpath, and regexp
validations.  The default assertion performed is 'is_equal_to' from the assertpy library but
most will work within reason.

.. code-block:: python

    @jpath(path='$..state', value='active', fail_task=True)
    @jpath(path='$..peer.connection', value='up', fail_task=True)
    def get_ha_info(task):
        return netmiko_send_command(task, command_string='show ha info', use_textfsm=True)

    nr.run(get_ha_info)

Retry a task until a condition is met.

.. code-block:: python

    @xpath(path='.//neighbor/entry[@name="router1"].connected', assertion='is_true')
    @wait(retries=10, delay=5)
    def get_ospf_neighbors(task):
        return netmiko_send_command(task, command_string='show ip ospf nei', use_textfsm=True)

    nr.run(get_ospf_neighbors)

Conditionally run a task on a particular nornir inventory.

.. code-block:: python

    @when(results=results, failed=True)
    @when(results=results, path='$.version', value='10.0')
    def run_when_failed_and_version_10(task):
        return netmiko_send_command(task, command_string='echo failures')
    
    results = nr.run(netmiko_send_command, command_string='show system info', use_textfsm=True)
    nr.run(run_when_failed_and_version_10)

Time tasks and optionally fail them if criteria are not met.

.. code-block:: python

    @timing(max_run_time=10, fail_task=True)
    def check_status(task):
        return netmiko_send_command(task, command_string='check status')

    nr.run(check_status)

Alternative to @ decorator syntax
---------------------------------

All the previous examples used @ decorator syntax but that is not the most flexible way of
using nornir_tests.  There are requirements that go along with using decorator syntax in that
the function must return a result and therefore the way it is called in the function may not
be ideal.

The alternative and probably easier method is to wrap the task directly:

.. code-block:: python

    vyos.run(
        wrap_task(napalm_get), getters=['interfaces'],
        tests=[
            jpath(path='interfaces.eth0.is_up', assertion='is_true', fail_task=True),
            until(initial_delay=15, retries=10, delay=15, reset_conns=True)
        ]
    )

Viewing test results
--------------------

The test results can be seen using the standard print_result in nornir_utils but an extended
version of print_result is also included in this module to better print test records.

For more details, see the `documentation <https://patrickdaj.github.io/nornir_tests/html/index.html>`__

References
----------

The nornir_tests plugin uses other libraries that are pretty critical to know in order to use nornir_tests efficiently.

`jsonpath_ng <https://github.com/h2non/jsonpath-ng>`__ - The github page has a fairly good intro to using jsonpath.

`xpath cheatsheat <https://devhints.io/xpath>`__ - The lxml documentation is great and all but its quite a bit and using something like this cheat sheet is a bit less daunting.

`assertpy <https://github.com/assertpy/assertpy>`__ - This documentation is pretty concise and this module is really the reason I wrote nornir_tests.  Prior to nornir_tests, I was running tasks that executed a bunch of python asserts using tasks.  It didn't permit stacking of assertions or very flexible control of whether or not it should fail a task.