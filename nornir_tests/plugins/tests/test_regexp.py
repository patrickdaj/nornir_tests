import wrapt
from dataclasses import dataclass, field
from typing import Callable, Any, Match, Optional, Union, List
import re

from nornir.core.task import Result

@dataclass
class RegexpRecord:
    regexp: str = ""
    passed: bool = False
    matches: List[str] = field(default_factory=list)
    result_attr: str = "result"
    fail_task: bool = False
    exception: Union[Exception, None] = None

def test_regexp(
    regexp: str = "",
    result_attr: str = "result",
    fail_task: bool = False
):
    """Test decorator using regexp

    Args:
        regexp (str, optional): Regular expression to use for matching.
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).

    """

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs) -> Result:

        test = RegexpRecord(
            regexp=regexp,
            result_attr=result_attr,
            fail_task=fail_task,
        )

        if len(args) > 0:
            task = args[0]
        else:
            task = kwargs["task"]

        result = wrapped(*args, **kwargs)

        try:
            text = getattr(result, test.result_attr, None)

            if not isinstance(text, str):
                text = repr(text)

            test.matches = re.search(test.regexp, text)

            test.passed = True if test.matches else False

            if not test.passed:
                raise Exception(f"no match found for regexp {test.regexp}")

        except Exception as e:
            test.passed = False
            test.exception = e

        if test.fail_task and not test.passed:
            result.failed = True

        if not getattr(result, "tests", None):
            setattr(result, "tests", [])

        result.tests.append(test)

        return result
    return wrapper