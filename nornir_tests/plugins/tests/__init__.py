from typing import Callable, List, Any

from .test_timing import test_timing
from .test_until import test_until
from .test_regexp import test_regexp
from .test_jsonpath import test_jsonpath
from .test_lxml import test_lxml
from .test_callback import test_callback


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


__all__ = [
    "apply_tests",
    "test_regexp",
    "test_timing",
    "test_until",
    "test_jsonpath",
    "test_lxml",
    "test_callback",
]
