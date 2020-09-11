from dataclasses import dataclass, field
from assertpy import assert_that
from jsonpath_ng import parse
from jsonpath_ng.jsonpath import DatumInContext
from json import loads
from typing import Callable, Any, List, Union

from nornir.core.task import Result

from .test import Test


@dataclass
class test_jsonpath(Test):
    """Test decorator using jsonpath

    This test is based off of the `jsonpath_ng <https://github.com/h2non/jsonpath-ng>`__
    implementation.  The path and host_data attributes both use the jsonpath syntax
    documented there.  The host_data is a jsonpath starting from the task.host.data
    dictionary.

    The operation is based on the `assertpy <https://github.com/assertpy/assertpy>`__
    implementation.  Any method available to assert_py.assert_that should be usable.
    If the assert_that assertion requires an argument to compare against then that
    should come from either the value argument or the value at the jsonpath match of
    host_data.

    Args:
        path (str, optional): jsonpath path.
        value (str, optional): Data to use for comparison.
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).
        assertion (str, optional): Any method of assertpy.assert_that object.
        one_of (bool, optional): When found values is > 1, allow one match to pass otherwise all returned must match.
        host_data (str, optional): jsonpath starting at task.host.data to use for comparison.
        fail_task (bool, optional): Determines whether test failure results causes setting result failure.

    Examples:
        >>> nr.run(
            task=netmiko_send_command,
            command_string='show ntp',
            name='Check NTP Sync',
            tests=[
                test_jsonpath(
                    path='$..ntp-servers', 
                    operation='is_equal_to', 
                    one_of=True, 
                    value='In Sync', 
                    fail_task=True
                ),
                test_jsonpath(
                    path='$.synced',
                    operation='is_in',
                    host_data='$.ntp_servers'
                    fail_task=True
                )
            ]
        )
        >>>
        >>> test_jsonpath(
                path='$.synced',
                operation='is_in',
                host_data='$.ntp_servers'
                fail_task=True
            )
            @test_jsonpath(
                path='$..ntp-servers',
                operation='is_equal_to',
                one_of=True,
                value='In Sync',
                fail_task=True
            )
        >>> def check_ntp_sync(task):
            return netmiko_send_command(
                task=task,
                command_string='show ntp'
            )
        >>>
        >>> nr.run(check_ntp_sync, name='Check NTP Sync')
        >>>

    """

    assertion: str = "is_equal_to"
    value: Any = None
    path: str = ""
    host_data: str = ""
    one_of: bool = False
    result_attr: str = "result"
    matches: List[str] = field(default_factory=list, repr=False)
    match: List[DatumInContext] = field(default_factory=list, repr=False)

    def run(self, func: Callable[..., Any], task, *args: str, **kwargs: str) -> Result:
        """Method decorator to perform jsonpath parse and find on result of task

        Args:
            func (Callable[..., Any]): Decorated function

        Returns:
            `nornir.core.task.Result`: Result of task after executed and decorated by test_jsonpath
        """
    
        result = func(task, *args, **kwargs)

        try:
            json_data = getattr(result, self.result_attr)

            # self.host_data always preferred
            if self.host_data:
                new_value = parse(self.host_data).find(task.host.data)

                if len(new_value) > 1:
                    raise Exception("host_data can only return one match")

                self.value = new_value[0].value if new_value[0] else self.value

            if isinstance(json_data, str):
                json_data = loads(json_data)

            self.match = parse(self.path).find(json_data)

            if not self.match:
                raise Exception(f"no match found from path {self.path}")

            for match in self.match:
                assert_obj = assert_that(match.value)
                assert_method = getattr(assert_obj, self.assertion)
                try:
                    if self.value:
                        assert_method(self.value)
                    else:
                        assert_method()

                    self.matches.append(str(match.full_path))
                    self.passed = True

                except Exception as e:
                    if not self.one_of or (match == self.match[-1] and not self.passed):
                        raise Exception(e)

        except Exception as e:
            self.passed = False
            self.exception = e

        self._add_test(result)

        if not self.passed and self.fail_task:
            result.failed = True

        return result
