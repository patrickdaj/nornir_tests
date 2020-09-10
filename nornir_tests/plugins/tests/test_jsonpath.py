from jsonpath_ng import parse
from json import loads
from typing import Callable, Any

from nornir.core.task import Result

from .test import Test


class test_jsonpath(Test):
    """Test decorator using jsonpath

    This test is based off of the `jsonpath_ng <https://github.com/h2non/jsonpath-ng>`__
        implementation.

    Args:
        path (str, optional): jsonpath path. Defaults to "".
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).
            Defaults to "result".
        value (Any, optional): Value to check for in path. Defaults to "".
        one_of (bool, optional): When found values is > 1, allow one match to pass
            otherwise all returned must match.  Defaults to False.
        host_data (str, optional): jsonpath to get value from task.host.data.  Defaults to ""
        fail_task (bool, optional): Determines whether test failure results causes
            setting result failure. Defaults to False.
    """

    def __init__(
        self,
        value: Any = "",
        host_data: str = "",
        path: str = "",
        one_of: bool = False,
        result_attr: str = "result",
        fail_task: bool = False,
    ):
        """Constructor for regexp decorator"""
        self.path = path
        self.host_data = host_data
        self.value = value
        self.one_of = one_of
        self.result_attr = result_attr
        super(test_jsonpath, self).__init__(fail_task)

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
                    raise Exception("host_data can't return multiple results")
                self.value = new_value[0].value if new_value[0].value else self.value

            if isinstance(json_data, str):
                json_data = loads(json_data)

            if not (isinstance(json_data, dict)):
                raise Exception(f"{self.result_attr} not parsible as dict")

            self.match = parse(self.path).find(json_data)

            if not self.match:
                raise Exception(f"no match found from path {self.path}")

            else:
                if len(self.match) > 1:
                    matches = 0
                    for m in self.match:
                        if m.value == self.value and not self.one_of:
                            matches += 1

                        elif self.one_of:
                            self.result = True
                            self.match = m
                            break

                        elif not (m.value != self.value or not self.one_of):
                            raise Exception('no value match on all returned matches')
                    
                    if not self.one_of:
                        self.result = matches == len(self.match)

                else:
                    self.result = self.match[0].value == self.value

            if self.result:
                self.msg = (
                    "jsonpath: {} expanded to {} and value {} found".format(
                        self.path, self.match[0].full_path, self.value
                    )
                )
            else:
                raise Exception(
                    f"could not find value {self.value} at path {self.path}"
                )

        except Exception as e:
            self.result = False
            self.msg = f"jsonpath: {e}"

        if self.fail_task and not self.result:
            result.failed = True

        self._add_test(result)

        return result
