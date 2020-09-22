import wrapt
from dataclasses import dataclass, field
from assertpy import assert_that
from jsonpath_ng import parse
from json import loads
from typing import Any, List, Callable, Dict

from nornir.core.task import Result
from .test import TestRecord


@dataclass
class JsonPathRecord(TestRecord):
    assertion: str = "is_equal_to"
    matches: List[str] = field(default_factory=list)
    one_of: bool = False
    value: Any = None
    path: str = ""
    result_attr: str = "result"
    host_data: str = ""

    result_keys = ["exception", "matches"]
    repr_keys = [
        "fail_task",
        "host_data",
        "result_attr",
        "path",
        "value",
        "one_of",
        "assertion",
    ]


def test_jsonpath(
    assertion: str = "is_equal_to",
    value: Any = None,
    path: str = "",
    one_of: bool = False,
    result_attr: str = "result",
    host_data: str = "",
    fail_task: bool = False,
) -> Result:
    """Test decorator using jsonpath

    This test is based off of the `jsonpath_ng <https://github.com/h2non/jsonpath-ng>`__
    implementation.  The path and host_data attributes both use the jsonpath syntax
    documented there.  The host_data is a jsonpath starting from the task.host.data
    dictionary.

    The operation is based on the `assertpy <https://github.com/assertpy/assertpy>`__
    implementation.  Any method available to assert_py.assert_that should be usable.
    If the assert_that assertion requires an argument to compare against then that
    should come from either the value argument or the value at the jsonpath match of
    host_data.

    Args:
        path (str, optional): jsonpath path.
        value (str, optional): Data to use for comparison.
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).
        assertion (str, optional): Any method of assertpy.assert_that object.
        one_of (bool, optional): When found values is > 1, allow one match to pass otherwise
            all returned must match.
        host_data (str, optional): jsonpath starting at task.host.data to use for comparison.
        fail_task (bool, optional): Determines whether test failure results causes setting
            result failure.

    """

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[..., Any],
        instance: object,
        args: List[Any],
        kwargs: Dict[str, Any],
    ) -> Result:

        test = JsonPathRecord(
            assertion=assertion,
            one_of=one_of,
            value=value,
            path=path,
            result_attr=result_attr,
            host_data=host_data,
            fail_task=fail_task,
        )

        if len(args) > 0:
            task = args[0]
        else:
            task = kwargs["task"]

        result = wrapped(*args, **kwargs)

        try:
            json_data = getattr(result, test.result_attr)

            # self.host_data always preferred
            if test.host_data:
                new_value = parse(test.host_data).find(task.host.data)

                if len(new_value) > 1:
                    raise Exception("host_data can only return one match")

                test.value = new_value[0].value if new_value[0] else test.value

            if isinstance(json_data, str):
                json_data = loads(json_data)

            match = parse(test.path).find(json_data)

            if not match:
                raise Exception(f"no match found from path {test.path}")

            for submatch in match:
                assert_obj = assert_that(submatch.value)
                assert_method = getattr(assert_obj, test.assertion)
                try:
                    if test.value:
                        assert_method(test.value)
                    else:
                        assert_method()

                    test.matches.append(str(submatch.full_path))
                    test.passed = True

                except Exception as e:
                    if not test.one_of or (submatch == match[-1] and not test.passed):
                        raise Exception(e)

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
