import wrapt
from dataclasses import dataclass
from typing import Any, List, Dict, Callable
import time

from nornir.core.task import Result
from .test import TestRecord


@dataclass
class UntilRecord(TestRecord):
    t0: float = -1
    t1: float = -1
    run_time: float = -1
    initial_delay: float = 0
    retries: int = 0
    delay: float = 0
    reset_conns: bool = False

    result_keys = ["exception", "t0", "t1", "run_time"]
    repr_keys = ["fail_task", "initial_delay", "retries", "delay", "reset_conns"]


def until(
    initial_delay: float = 0,
    retries: int = 0,
    delay: float = 0,
    reset_conns: bool = False,
    t0: float = -1,
    t1: float = -1,
    run_time: float = -1,
    fail_task: bool = False,
) -> Result:
    """Test decorator for until
    This decorator allows retrying a task multiple times

    Args:
        initial_delay (float, optional): Time in seconds to wait for first attempt.
        retries (int, optional): Number of times to retry.
        delay (float, optional): Time to wait in between retries in seconds.
        reset_conns (bool, optional): Reset connections in between retries.
        fail_task (bool, optional): Determines whether test failure results causes
            setting result failure.

    """

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[..., Any],
        instance: object,
        args: List[Any],
        kwargs: Dict[str, Any],
    ) -> Result:
        test = UntilRecord(
            initial_delay=initial_delay,
            retries=retries,
            delay=delay,
            reset_conns=reset_conns,
            fail_task=fail_task,
        )

        if len(args) > 0:
            task = args[0]
        else:
            task = kwargs["task"]

        test.t0 = time.time()

        if test.initial_delay:
            time.sleep(test.initial_delay)

        for i in range(test.retries + 1):
            try:
                result = wrapped(*args, **kwargs)
                if not result.failed:
                    test.passed = True
            except Exception as e:
                # pass last exception back to nornir
                if i == test.retries - 1:
                    raise e

            # no need to sleep if this is last iteration
            if test.passed or i == test.retries - 1:
                break

            else:
                if test.reset_conns:
                    task.host.close_connections()
                time.sleep(test.delay)

        test.t1 = time.time()
        test.run_time = test.t1 - test.t0

        if not getattr(result, "tests", None):
            setattr(result, "tests", [])

        result.tests.append(test)

        return result

    return wrapper
