from dataclasses import dataclass
from typing import Callable, Any
import time

from nornir.core.task import Result

from .test import Test

@dataclass
class test_until(Test):
    """Test decorator to continue until task result is not failed

    Args:
        initial_delay (int, optional): Initial delay before trying first try.
            Defaults to 0.
        retries (int, optional): Number of retries. Defaults to 0.
        delay (int, optional): Time between retries. Defaults to 0.
        reset_conns (bool, optional): Reset connections between retries.
            Defaults to False.
        fail_task (bool, optional): . Defaults to False.
    """
    initial_delay: int = 0
    retries: int = 0
    delay: int = 0
    reset_conns: bool = False
    t0: int = -1
    t1: int = -1
    run_time: int = -1

    def run(self, func: Callable[..., Any], task, *args: str, **kwargs: str) -> Result:
        """Method decorator to continue until result of task is not failed

        Args:
            func (Callable[..., Any]): Decorated function

        Returns:
            `nornir.core.task.Result`: Result of task after executed and decorated by test_until
        """

        self.t0 = time.time()

        if self.initial_delay:
            time.sleep(self.initial_delay)

        for i in range(self.retries + 1):
            try:
                result = func(task, *args, **kwargs)
                if not result.failed:
                    self.passed = True
            except Exception as e:
                # pass last exception back to nornir
                if i == self.retries - 1:
                    raise e

            # no need to sleep if this is last iteration
            if self.passed or i == self.retries - 1:
                break
            
            else:
                if self.reset_conns:
                    task.host.close_connections()
                time.sleep(self.delay)

        self.t1 = time.time()

        self.run_time = self.t1 - self.t0

        self._add_test(result)

        return result
