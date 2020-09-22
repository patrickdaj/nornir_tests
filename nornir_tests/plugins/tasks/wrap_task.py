import wrapt

from typing import Callable, List, Any, Dict
from nornir.core.task import Result

from nornir_tests.plugins.tests import apply_tests


@wrapt.decorator
def wrap_task(
    wrapped: Callable[..., Any],
    instance: object,
    args: List[Any],
    kwargs: Dict[str, Any],
) -> Result:
    """Wrap task without using @ decorator syntax

    This function return

    Args:
        wrapped (Callable): The task.task function argument

    """
    return apply_tests(wrapped, kwargs.pop("tests", []))(*args, **kwargs)
