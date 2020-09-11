from dataclasses import dataclass, field
from typing import Callable, Any, List
import re

from nornir.core.task import Result

from .test import Test


class test_regexp(Test):
    """Test decorator using regexp

    Args:
        regexp (str, optional): Regular expression to use for matching.
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).

    """
    regexp: str = ''
    result_attr: str = "result"
    matches: re.Match = field(repr=False)

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

            self.matches = re.search(self.regexp, text)

            self.passed = True if self.matches else False

            if not self.passed:
                raise Exception(f"no match found for regexp {self.regexp}")
          
        except Exception as e:
            self.result = False
            self.exception = e

        if self.fail_task and not self.result:
            result.failed = True

        self._add_test(result)

        return result
