import wrapt
from dataclasses import dataclass
from typing import Union, Callable, Dict, List, Any
import sys
import time

from nornir.core.task import Result


@dataclass
class TimingRecord:
    passed: bool = False
    t0: float = -1
    t1: float = -1
    run_time: float = -1
    fail_task: bool = False
    exception: Union[Exception, None] = None
    min_run_time: int = 0
    max_run_time: int = 0


def test_timing(
    min_run_time: int = 0,
    max_run_time: int = sys.maxsize,
    t0: float = -1,
    t1: float = -1,
    run_time: float = -1,
    fail_task: bool = False,
) -> Result:
    """Test decorator for timing

    Args:
        fail_task (bool, optional): Determines whether test failure results causes
            setting result failure. Defaults to False.
        min_run_time (int, optional): Required minimum runtime. Defaults to 0.
        max_run_time (int, optional): Required maximum runtime. Defaults to sys.maxsize.
    """

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[..., Any],
        instance: object,
        args: List[Any],
        kwargs: Dict[str, Any],
    ) -> Result:

        test = TimingRecord(
            fail_task=fail_task, min_run_time=min_run_time, max_run_time=max_run_time
        )

        test.t0 = time.time()
        result = wrapped(*args, **kwargs)
        test.t1 = time.time()

        result.run_time = test.t1 - test.t0

        test.passed = (
            result.run_time > test.min_run_time and result.run_time < test.max_run_time
        )

        if test.fail_task and not test.passed:
            result.failed = True

        if not getattr(result, "tests", None):
            setattr(result, "tests", [])

        result.tests.append(test)

        return result

    return wrapper
