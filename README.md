# nornir_tests

`nornir_tests` provides the ability to add one or more tests to a Nornir task.

- Attach verifications or assertions to a task with the entire assertpy library of assertions available
- Fail task on failed tests or just have them for informational purposes
- Get detailed test records for each of the verifications/assertions, printable by print_result

[nornir_tests documentation](https://patrickdaj.github.io/nornir_tests/)

## Potential uses

- Timing a task and making sure it completes within x seconds
- Faling a task if it isn't changed
- Faling a task if text is not in results attribute
- Using jsonpath or xpath to assert a value at a particular path
- Passing a task for an expected exception
- Testing a condition repeatedly until all tests are passing
- Nest multiple tests

## Installation

```shell
pip install nornir-tests
```

## Basic Usage

```python
>> from nornir_tests.plugins.processors import TestsProcessor
>> from nornir_tests.plugins.tests import test_timing, test_until, test_jsonpath
>> from nornir_napalm.plugins.tasks import napalm_get
>>
>> nr = InitNornir()
>> nr.processors.append(TestsProcessor())
>>
>> result = nr.run(
        napalm_get, getters=['facts'],
        tests=[
            test_jsonpath(path='interfaces.eth1.is_enabled', assertion='is_true'),
            test_until(retries=10, delay=30)
        ]
   )
>>
>> print_result(result, vars=['result', 'tests'])
napalm_get**********************************************************************
* vyos ** changed : False ******************************************************
vvvv napalm_get ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
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
'jsonpath: interfaces.eth0.is_up expanded to interfaces.eth0.is_up and value True found - PASSED'
'until: succeeded after 2.0347249507904053 seconds - PASSED'
```

## How it works
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