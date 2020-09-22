import wrapt
from dataclasses import dataclass
from typing import Any, List, Callable, Dict

from nornir.core.task import Result
from .test import TestRecord


@dataclass
class CallbackRecord(TestRecord):
    custom: Any = None

    result_keys = ["exception", "custom"]
    repr_keys = ["fail_task"]


def test_callback(
    callback: Callable[..., Any],
    fail_task: bool = False,
) -> Result:
    """Test decorator using custom callback

    Args:
        callback (Callable): Callback function
        fail_task (bool, optional): Determines whether test failure results causes setting
            result failure.

    """

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[..., Any],
        instance: object,
        args: List[Any],
        kwargs: Dict[str, Any],
    ) -> Result:

        test = CallbackRecord(
            fail_task=fail_task,
        )

        if len(args) > 0:
            task = args[0]
        else:
            task = kwargs["task"]

        result = wrapped(*args, **kwargs)

        try:
            callback(result, test, task)

        except Exception as e:
            test.passed = False
            test.exception = e

        if not getattr(result, "tests", None):
            setattr(result, "tests", [])

        result.tests.append(test)

        if not test.passed and test.fail_task:
            result.failed = True

        return result

    return wrapper
