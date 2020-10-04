import wrapt

from typing import Optional, Callable, List, Any, Dict
from nornir.core.task import Result


def apply_tests(
    task: Callable[..., Any], tests: List[Callable[..., Any]]
) -> Callable[..., Any]:
    """Apply tests (decorators) to task

    This is strictly used for wrapping a nornir task in all tests defined.  It
    has no other use than applying the tests and is used only by wrap_task.

    Args:
        task (Callable[..., Any]): nornir task
        tests (List[Callable[..., Any]]): test decorators to apply

    Returns:
        Callable[..., Any]: Decorated function
    """
    apply_last: Optional[Callable[..., Any]] = None
    wrapped = task

    for wrapper in tests:

        # always apply until last
        if wrapper.__module__.endswith("until") and tests[-1] != wrapper:
            apply_last = wrapper
            continue

        wrapped = wrapper(wrapped)

    if apply_last:
        wrapped = apply_last(wrapped)

    return wrapped


@wrapt.decorator
def wrap_task(
    wrapped: Callable[..., Any],
    instance: object,
    args: List[Any],
    kwargs: Dict[str, Any],
) -> Result:
    """Wrap task without using @ decorator syntax

    wrap_task wraps the task function of a nornir.run or task.run with all
    the decorators/wrappers in the tests array.

    This function return

    Args:
        wrapped (Callable): The task.task function argument

    """
    return apply_tests(wrapped, kwargs.pop("tests", []))(*args, **kwargs)
