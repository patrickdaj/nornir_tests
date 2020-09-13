from dataclasses import dataclass, field
from typing import Callable, Any, Match, Optional, Union
import re

from nornir.core.task import Result

from .test import Test


@dataclass
class test_regexp(Test):
    """Test decorator using regexp

    Args:
        regexp (str, optional): Regular expression to use for matching.
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).

    """

    matches: Union[Optional[Match[Any]], None] = field(default=None, repr=False)
    regexp: str = ""
    result_attr: str = "result"

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
