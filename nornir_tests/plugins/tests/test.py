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

    def as_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in vars(self).items() if v}
