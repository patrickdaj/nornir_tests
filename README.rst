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
perform an action and combine assertions to wait for a successful result.  The output is from
another plugin that better prints tests but using standard print_result works fine too if it
is included in vars.

.. code-block:: python

    from nornir_napalm.plugins.tasks import napalm_get
    from nornir_netmiko.tasks import netmiko_send_command
    from nornir_rich.plugins.functions import RichResults
    from nornir_tests.plugins.tests import test_until, test_jsonpath
    from nornir_tests.plugins.processors import TestsProcessor
    from nornir import InitNornir

    nr = InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": "data/hosts.yaml",
                "group_file": "data/groups.yaml",
                "defaults_file": "data/defaults.yaml",
            },
        },
    )

    rr = RichResults(record=True)

    nr.processors.append(TestsProcessor())

    vyos = nr.filter(name='vyos')


    # Using @decorator syntax
    @test_jsonpath(
        path='interfaces_ip.eth0.ipv4', 
        assertion='contains_key', 
        value='192.168.99.170', 
        fail_task=True
    )
    def check_interface(task):
        return napalm_get(task, getters=['interfaces_ip'])

    result = vyos.run(check_interface, name='Check Interface')
    rr.print(result)

    rr.print(
        vyos.run(
            task=netmiko_send_command,
            command_string='reboot now'
        )
    )

    # Using the TestsProcessor to wrap the task
    result = vyos.run(
        task=napalm_get,
        getters=['interfaces'],
        tests=[
            test_jsonpath(path='interfaces.eth0.is_up', assertion='is_true', fail_task=True),
            test_until(initial_delay=15, retries=10, delay=15, reset_conns=True),
        ]
    )

    rr.print(result)
    rr.write()


Execution of this using nornir_rich produces the following output:

.. raw:: html
    <!DOCTYPE html>
    <head>
    <style>
    .r1 {color: #000000; text-decoration: underline}
    .r2 {color: #000000; font-weight: bold; text-decoration: underline}
    .r3 {color: #000080; font-weight: bold; text-decoration: underline}
    .r4 {color: #000080}
    .r5 {font-weight: bold}
    .r6 {color: #008000}
    .r7 {color: #000080; font-weight: bold}
    .r8 {color: #808000; font-style: italic}
    .r9 {color: #800080; font-style: italic}
    .r10 {color: #00ff00; font-style: italic}
    .r11 {color: #ff0000; font-style: italic}
    body {
        color: #000000;
        background-color: #ffffff;
    }
    </style>
    </head>
    <html>
    <body>
        <code>
            <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span class="r1">Check Interface </span><span class="r2">(</span><span class="r1">hosts: </span><span class="r3">1</span><span class="r2">)</span>
    <span class="r4">* vyos </span>
    ╭─ Check Interface  ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │    result = <span class="r5">{</span>                                                                                                                                    │
    │                 <span class="r6">'interfaces_ip'</span>: <span class="r5">{</span>                                                                                                               │
    │                     <span class="r6">'eth0'</span>: <span class="r5">{</span><span class="r6">'ipv4'</span>: <span class="r5">{</span><span class="r6">'192.168.99.170'</span>: <span class="r5">{</span><span class="r6">'prefix_length'</span>: <span class="r7">24</span><span class="r5">}}}</span>,                                                                 │
    │                     <span class="r6">'lo'</span>: <span class="r5">{</span><span class="r6">'ipv4'</span>: <span class="r5">{</span><span class="r6">'127.0.0.1'</span>: <span class="r5">{</span><span class="r6">'prefix_length'</span>: <span class="r7">8</span><span class="r5">}}</span>, <span class="r6">'ipv6'</span>: <span class="r5">{</span><span class="r6">'::1'</span>: <span class="r5">{</span><span class="r6">'prefix_length'</span>: <span class="r7">128</span><span class="r5">}}}</span>                                 │
    │                 <span class="r5">}</span>                                                                                                                                │
    │             <span class="r5">}</span>                                                                                                                                    │
    │    tests 🟢 test_jsonpath<span class="r5">(</span><span class="r8">exception</span>=<span class="r9">None</span>, <span class="r8">fail_task</span>=<span class="r10">True</span>, <span class="r8">passed</span>=<span class="r10">True</span>, <span class="r8">assertion</span>=<span class="r6">'contains_key'</span>, <span class="r8">value</span>=<span class="r6">'192.168.99.170'</span>,                         │
    │             <span class="r8">path</span>=<span class="r6">'interfaces_ip.eth0.ipv4'</span>, <span class="r8">host_data</span>=<span class="r6">''</span>, <span class="r8">one_of</span>=<span class="r11">False</span>, <span class="r8">result_attr</span>=<span class="r6">'result'</span>, <span class="r8">matches</span>=<span class="r5">[</span><span class="r6">'interfaces_ip.eth0.ipv4'</span><span class="r5">])</span>               │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

    <span class="r1">netmiko_send_command </span><span class="r2">(</span><span class="r1">hosts: </span><span class="r3">1</span><span class="r2">)</span>
    <span class="r4">* vyos </span>
    ✔ netmiko_send_command 

    <span class="r1">napalm_get </span><span class="r2">(</span><span class="r1">hosts: </span><span class="r3">1</span><span class="r2">)</span>
    <span class="r4">* vyos </span>
    ╭─ napalm_get  ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │    result = <span class="r5">{</span>                                                                                                                                    │
    │                 <span class="r6">'interfaces'</span>: <span class="r5">{</span>                                                                                                                  │
    │                     <span class="r6">'eth0'</span>: <span class="r5">{</span>                                                                                                                    │
    │                         <span class="r6">'is_up'</span>: <span class="r10">True</span>,                                                                                                           │
    │                         <span class="r6">'is_enabled'</span>: <span class="r10">True</span>,                                                                                                      │
    │                         <span class="r6">'description'</span>: <span class="r6">''</span>,                                                                                                       │
    │                         <span class="r6">'last_flapped'</span>: <span class="r7">-1.0</span>,                                                                                                    │
    │                         <span class="r6">'mtu'</span>: <span class="r7">-1</span>,                                                                                                               │
    │                         <span class="r6">'speed'</span>: <span class="r7">0</span>,                                                                                                              │
    │                         <span class="r6">'mac_address'</span>: <span class="r6">'08:00:27:e0:28:63'</span>                                                                                       │
    │                     <span class="r5">}</span>,                                                                                                                           │
    │                     <span class="r6">'lo'</span>: <span class="r5">{</span>                                                                                                                      │
    │                         <span class="r6">'is_up'</span>: <span class="r10">True</span>,                                                                                                           │
    │                         <span class="r6">'is_enabled'</span>: <span class="r10">True</span>,                                                                                                      │
    │                         <span class="r6">'description'</span>: <span class="r6">''</span>,                                                                                                       │
    │                         <span class="r6">'last_flapped'</span>: <span class="r7">-1.0</span>,                                                                                                    │
    │                         <span class="r6">'mtu'</span>: <span class="r7">-1</span>,                                                                                                               │
    │                         <span class="r6">'speed'</span>: <span class="r7">0</span>,                                                                                                              │
    │                         <span class="r6">'mac_address'</span>: <span class="r6">'00:00:00:00:00:00'</span>                                                                                       │
    │                     <span class="r5">}</span>                                                                                                                            │
    │                 <span class="r5">}</span>                                                                                                                                │
    │             <span class="r5">}</span>                                                                                                                                    │
    │    tests 🟢 test_jsonpath<span class="r5">(</span><span class="r8">exception</span>=<span class="r9">None</span>, <span class="r8">fail_task</span>=<span class="r10">True</span>, <span class="r8">passed</span>=<span class="r10">True</span>, <span class="r8">assertion</span>=<span class="r6">'is_true'</span>, <span class="r8">value</span>=<span class="r9">None</span>, <span class="r8">path</span>=<span class="r6">'interfaces.eth0.is_up'</span>,            │
    │             <span class="r8">host_data</span>=<span class="r6">''</span>, <span class="r8">one_of</span>=<span class="r11">False</span>, <span class="r8">result_attr</span>=<span class="r6">'result'</span>, <span class="r8">matches</span>=<span class="r5">[</span><span class="r6">'interfaces.eth0.is_up'</span><span class="r5">])</span>                                                 │
    │          🟢 test_until<span class="r5">(</span><span class="r8">exception</span>=<span class="r9">None</span>, <span class="r8">fail_task</span>=<span class="r11">False</span>, <span class="r8">passed</span>=<span class="r10">True</span>, <span class="r8">initial_delay</span>=<span class="r7">15</span>, <span class="r8">retries</span>=<span class="r7">10</span>, <span class="r8">delay</span>=<span class="r7">15</span>, <span class="r8">reset_conns</span>=<span class="r10">True</span>,                   │
    │             <span class="r8">t0</span>=<span class="r7">1600040300.389752</span>, <span class="r8">t1</span>=<span class="r7">1600040357.0873864</span>, <span class="r8">run_time</span>=<span class="r7">56.69763445854187</span><span class="r5">)</span>                                                             │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

    </pre>
        </code>
    </body>
    </html>



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