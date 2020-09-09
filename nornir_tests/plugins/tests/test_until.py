from typing import Callable, Any
import time

from nornir.core.task import Result

from .test import Test


class test_until(Test):
    """Test decorator to continue until task result is not failed

    Args:
        initial_delay (int, optional): Initial delay before trying first try.
            Defaults to 0.
        retries (int, optional): Number of retries. Defaults to 0.
        delay (int, optional): Time between retries. Defaults to 0.
        fail_task (bool, optional): . Defaults to False.
    """

    def __init__(
        self,
        initial_delay: int = 0,
        retries: int = 0,
        delay: int = 0,
        fail_task: bool = False,
    ):
        """Constructor for test_until decorator"""
        self.initial_delay = initial_delay
        self.delay = delay
        self.retries = retries
        super(test_until, self).__init__(fail_task)

    def run(self, func: Callable[..., Any], *args: str, **kwargs: str) -> Result:
        """Method decorator to continue until result of task is not failed

        Args:
            func (Callable[..., Any]): Decorated function

        Returns:
            `nornir.core.task.Result`: Result of task after executed and decorated by test_until
        """

        if self.initial_delay:
            time.sleep(self.initial_delay)

        self.t0 = time.time()
        self.result = False

        for i in range(self.retries):
            result = func(*args, **kwargs)

            if not result.failed:
                self.result = True
                break
            else:
                time.sleep(self.delay)

        self.t1 = time.time()

        self.msg = "until: {} after {} seconds".format(
            "succeeded" if self.result else "failed", self.t1 - self.t0
        )

        self._add_test(result)

        return result
