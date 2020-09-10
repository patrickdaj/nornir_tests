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
        value (Any, optional): Value to check for in path. Defaults to ""
        host_data (str, optional): jsonpath to get value from task.host.data.  Defaults to ""
        fail_task (bool, optional): Determines whether test failure results causes
            setting result failure. Defaults to False.
    """

    def __init__(
        self,
        value: Any = "",
        host_data: str = "",
        path: str = "",
        result_attr: str = "result",
        fail_task: bool = False,
    ):
        """Constructor for regexp decorator"""
        self.path = path
        self.host_data = host_data
        self.value = value
        self.result_attr = result_attr
        super(test_jsonpath, self).__init__(fail_task)

    def run(self, func: Callable[..., Any], *args: str, **kwargs: str) -> Result:
        """Method decorator to perform jsonpath parse and find on result of task

        Args:
            func (Callable[..., Any]): Decorated function

        Returns:
            `nornir.core.task.Result`: Result of task after executed and decorated by test_jsonpath
        """

        result = func(*args, **kwargs)

        try:
            json_data = getattr(result, self.result_attr)

            # self.host_data always preferred
            if self.host_data:
                new_value = parse(self.host_data).find(task.host.data)
                self.value = new_value if new_value else self.value

            if isinstance(json_data, str):
                json_data = loads(json_data)

            if not (isinstance(json_data, dict)):
                raise Exception(f"{self.result_attr} not parsible as dict")

            self.match = parse(self.path).find(json_data)

            if not self.match:
                raise Exception(f"no match found from path {self.path}")

            else:
                if isinstance(self.value, list):
                    # TODO
                    pass

                elif len(self.match) > 1:
                    # TODO
                    pass

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
