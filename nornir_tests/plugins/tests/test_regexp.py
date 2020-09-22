import wrapt
from dataclasses import dataclass, field
from typing import Union, Optional, Match, Any, TypeVar, Callable, Dict, List
import re

from nornir.core.task import Result

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class RegexpRecord:
    regexp: str = ""
    passed: bool = False
    matches: Optional[Match[Any]] = field(default=None)
    result_attr: str = "result"
    one_of: bool = False
    value: Any = None
    host_data: str = ""
    fail_task: bool = False
    exception: Union[Exception, None] = None


def test_regexp(
    regexp: str = "",
    result_attr: str = "result",
    assertion: str = "is_not_none",
    value: Any = None,
    path: str = "",
    one_of: bool = False,
    host_data: str = "",
    fail_task: bool = False,
) -> Result:
    """Test decorator using regexp

    Args:
        regexp (str, optional): Regular expression to use for matching.
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).
        value (str, optional): Data to use for comparison.
        assertion (str, optional): Any method of assertpy.assert_that object.
        one_of (bool, optional): When found values is > 1, allow one match to pass otherwise
            all returned must match.
        host_data (str, optional): jsonpath starting at task.host.data to use for comparison.

    """

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[..., Any],
        instance: object,
        args: List[Any],
        kwargs: Dict[str, Any],
    ) -> Result:

        test = RegexpRecord(
            regexp=regexp,
            result_attr=result_attr,
            fail_task=fail_task,
        )

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
