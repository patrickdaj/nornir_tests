from typing import Callable, Any
import sys
import time

from nornir.core.task import Result

from .test import Test


class test_timing(Test):
    """Test decorator for timing

    Args:
        fail_task (bool, optional): Determines whether test failure results causes
            setting result failure. Defaults to False.
        min_run_time (int, optional): Required minimum runtime. Defaults to 0.
        max_run_time (int, optional): Required maximum runtime. Defaults to sys.maxsize.
    """

    def __init__(
        self,
        fail_task: bool = False,
        min_run_time: int = 0,
        max_run_time: int = sys.maxsize,
    ):
        """Constructor for timing decorator"""

        self.min_run_time = min_run_time
        self.max_run_time = max_run_time
        super(test_timing, self).__init__(fail_task)

    def run(self, func: Callable[..., Any], *args: str, **kwargs: str) -> Result:
        """Method decorator to perform timing on result of task

        Args:
            func (Callable[..., Any]): Decorated function

        Returns:
            `nornir.core.task.Result`: Result of task after executed and decorated by test_timing
        """
        self.t0 = time.time()
        result = func(*args, **kwargs)
        self.t1 = time.time()

        result.run_time = self.t1 - self.t0

        self.result = (
            result.run_time > self.min_run_time and result.run_time < self.max_run_time
        )

        self.msg = (
            f"timing: {self.min_run_time} < {result.run_time} < {self.max_run_time}",
        )

        if self.fail_task and not self.result:
            result.failed = True

        self._add_test(result)

        return result
