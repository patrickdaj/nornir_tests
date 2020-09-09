from typing import Callable, Any
import re

from nornir.core.task import Result

from .test import Test


class test_regexp(Test):
    """Test decorator using regexp

    Args:
        regexp (str, optional): Regular expression to use for matching. Defaults to "".
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).
            Defaults to "result".
        fail_task (bool, optional): Determines whether test failure results causes
            setting result failure. Defaults to False.
    """

    def __init__(
        self,
        regexp: str = "",
        result_attr: str = "result",
        fail_task: bool = False,
    ):
        """Constructor for regexp decorator"""
        self.regexp = regexp
        self.result_attr = result_attr
        super(test_regexp, self).__init__(fail_task)

    def run(self, func: Callable[..., Any], *args: str, **kwargs: str) -> Result:
        """Method decorator to perform regexp on result of task

        Args:
            func (Callable[..., Any]): Decorated function

        Returns:
            `nornir.core.task.Result`: Result of task after executed and decorated by test_regexp
        """

        result = func(*args, **kwargs)

        try:
            text = getattr(result, self.result_attr, None)

            if not isinstance(text, str):
                text = repr(text)

            self.match = re.search(self.regexp, text)

            self.result = True if self.match else False

            if self.result:
                self.msg = "regexp: {} matched {} in {}".format(
                    self.regexp, self.match.group(0), self.result_attr
                )
            else:
                raise Exception(f"no match found for regex {self.regexp}")

        except Exception as e:
            self.result = False
            self.msg = f"test_regexp: {e}"

        if self.fail_task and not self.result:
            result.failed = True

        self._add_test(result)

        return result
