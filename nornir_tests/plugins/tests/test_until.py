import wrapt
from dataclasses import dataclass
from typing import Callable, Any, Union
import time

from nornir.core.task import Result, Task

@dataclass
class UntilRecord:
    passed: bool = False
    t1: float = -1
    t2: float = -1
    run_time: float = -1
    fail_task: bool = False
    exception: Union[Exception, None] = None
    initial_delay: float = 0
    retries: float = 0
    delay: float = 0
    reset_conns: bool = False

def test_until(
    initial_delay: int = 0,
    retries: int = 0,
    delay: int = 0,
    reset_conns: bool = False,
    t0: float = -1,
    t1: float = -1,
    run_time: float = -1,
    fail_task: bool = False
):
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs) -> Result:

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