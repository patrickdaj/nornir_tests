import pprint
from dataclasses import dataclass
from typing import Callable, List, Any, Union, Dict


def apply_tests(
    task: Callable[..., Any], tests: List[Callable[..., Any]]
) -> Callable[..., Any]:
    """Apply tests (decorators) to task

    Args:
        task (Callable[..., Any]): nornir task
        tests (List[Callable[..., Any]]): test decorators to apply

    Returns:
        Callable[..., Any]: Decorated function
    """
    wrapped = task
    for wrapper in tests:
        wrapped = wrapper(wrapped)

    return wrapped


@dataclass
class TestRecord:
    passed: bool = False
    fail_task: bool = False
    exception: Union[Exception, None] = None

    result_keys = ["exception"]
    repr_keys = ["fail_task"]

    def result(self) -> Dict[str, Any]:
        return {k: v for k, v in vars(self).items() if v and k in self.result_keys}

    def requirement(self) -> str:
        reqs = {k: v for k, v in vars(self).items() if v and k in self.repr_keys}
        return f"{self.__class__.__name__} - " + pprint.pformat(reqs)
