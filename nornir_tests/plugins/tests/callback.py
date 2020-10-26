import wrapt
from dataclasses import dataclass
from typing import Any, List, Callable, Dict

from nornir.core.task import Result
from .test import TestRecord


@dataclass
class CallbackRecord(TestRecord):
    custom: Any = None

    result_keys = ["exception", "custom"]
    repr_keys = ["fail_task"]


def callback(
    callback: Callable[..., Any],
    fail_task: bool = False,
) -> Result:
    """Test decorator using custom callback

    This wrapper can be used to test a task result using a custom callback.  The callback
    has the nornir Result, the Task which includes a host attribute that can be used for
    verifications, and the test record.  To fail the test set test.passed to False and
    populate the CallbackRecord with whatever is desired.

    Args:
        callback (Callable): Callback function
        fail_task (bool, optional): Determines whether test failure results causes setting
            result failure.

    Example:

    .. code-block:: python

        def my_callback(result, test, task):
            if result.result['hostname'] != task.host.hostname:
                test.passed = False
                test.custom = "Hostname did not match inventory"

        results = nr.run(
            wrap_task(napalm_get), getters=['system']
            tests=[
                callback(my_callback, fail_task=True)
            ]
        )

    This would fail the task and thus the host would end up in failed_hosts despite the
    fact that napalm_get had no issues.  It would fail due to the fact that the callback
    was not ok with what was returned.

    This is just another way to deal with validations in Nornir and the primary advantage
    is that it could potentially be chained with another test such as until to wait
    for a particular condition.  It also provides a succinct way to display the logic of
    the validation into results without requiring another task or printing directly.

    """

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[..., Any],
        instance: object,
        args: List[Any],
        kwargs: Dict[str, Any],
    ) -> Result:

        test = CallbackRecord(
            fail_task=fail_task,
        )

        if len(args) > 0:
            task = args[0]
        else:
            task = kwargs["task"]

        result = wrapped(*args, **kwargs)

        try:
            callback(result, test, task)

        except Exception as e:
            test.passed = False
            test.exception = e

        if not getattr(result, "tests", None):
            setattr(result, "tests", [])

        result.tests.append(test)

        if not test.passed and test.fail_task:
            result.failed = True

        return result

    return wrapper
