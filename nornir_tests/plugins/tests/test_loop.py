import wrapt
from dataclasses import dataclass, field
from typing import Any, List, Dict, Callable

from nornir.core.task import Result, MultiResult
from .test import TestRecord


@dataclass
class LoopRecord(TestRecord):
    values: List[Any] = field(default_factory=list)
    placeholder: Any = None
    reset_conns: bool = False

    result_keys = ["exception", "processed"]
    repr_keys = ["values", "reset_conns"]


def test_loop(
    values: List[Any],
    placeholder: Any,
    reset_conns: bool = False,
) -> Result:
    @wrapt.decorator
    def wrapper(
        wrapped: Callable[..., Any],
        instance: object,
        args: List[Any],
        kwargs: Dict[str, Any],
    ) -> Result:

        test = LoopRecord(
            values=values,
            placeholder=placeholder,
            reset_conns=reset_conns,
        )

        if len(args) > 0:
            task = args[0]
        else:
            task = kwargs["task"]

        result = MultiResult(name=f"{task.name} - test_loop")

        for value in values:
            kwargs.update({placeholder: value})
            result.append(wrapped(*args, **kwargs))

            if result[-1].failed:
                result.failed = True

            if result[-1].changed:
                result.changed = True

            if test.reset_conns:
                task.host.close_connections()

        return result

    return wrapper
