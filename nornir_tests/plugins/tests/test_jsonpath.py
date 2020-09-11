from dataclasses import dataclass, field
from assertpy import assert_that
from jsonpath_ng import parse
from jsonpath_ng.jsonpath import DatumInContext
from json import loads
from typing import Callable, Any, List

from nornir.core.task import Result

from .test import Test


@dataclass
class test_jsonpath(Test):
    """Test decorator using jsonpath

    This test is based off of the `jsonpath_ng <https://github.com/h2non/jsonpath-ng>`__
        implementation.

    Args:
        path (str, optional): jsonpath path. Defaults to "".
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).
            Defaults to "result".
        assertion (str, optional): Any method of assertpy.assert_that object.  Defaults to 'is_equal'.
        one_of (bool, optional): When found values is > 1, allow one match to pass
            otherwise all returned must match.  Defaults to False.
        host_data (bool, optional): get comparison data from task.host.data, jsonpath will be in equals, contains, or is_in.  Defaults to False.
        fail_task (bool, optional): Determines whether test failure results causes
            setting result failure. Defaults to False.
    """

    assertion: str = "equals"
    value: Any = None
    path: str = ""
    host_data: str = ""
    one_of: bool = False
    result_attr: str = "result"
    matches: List[str] = field(default_factory=list)
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

                    if self.one_of:
                        self.passed = True
                        self.matches.append(match.full_path)
                        break
                except Exception as e:
                    if not self.one_of:
                        raise Exception(e)

                self.matches.append(match.full_path)

            self.passed = True

        except Exception as e:
            self.passed = False
            self.exception = e

        self._add_test(result)

        if not self.passed and self.fail_task:
            result.failed = True

        return result
