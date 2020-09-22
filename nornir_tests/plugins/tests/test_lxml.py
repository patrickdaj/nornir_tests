import wrapt
from dataclasses import dataclass, field
import lxml.etree as etree
from jsonpath_ng import parse
from typing import Any, List, Callable, Dict
from assertpy import assert_that

from nornir.core.task import Result
from .test import TestRecord


@dataclass
class XmlPathRecord(TestRecord):
    assertion: str = "is_equal_to"
    matches: List[str] = field(default_factory=list)
    one_of: bool = False
    value: Any = None
    xpath: str = ""
    attrib: str = ""
    text: bool = False
    result_attr: str = "result"
    host_data: str = ""

    result_keys = ["exception", "matches"]
    repr_keys = [
        "fail_task",
        "one_of",
        "value",
        "xpath",
        "attrib",
        "text",
        "result_attr",
        "host_data",
    ]


def test_lxml(
    assertion: str = "is_equal_to",
    value: Any = None,
    xpath: str = "",
    attrib: str = "",
    text: bool = False,
    one_of: bool = False,
    result_attr: str = "result",
    host_data: str = "",
    fail_task: bool = False,
) -> Result:
    """Test decorator using lxml

    This test is based off of the `lxml <https://github.com/h2non/jsonpath-ng>`__ implementation.

    Args:
        xpath (str, optional): xpath locator.
        value (str, optional): value for comparison can be empty but not usual.
        host_data (str, optional): jsonpath to get value from task.host.data.
        one_of (bool, optional): When found values is > 1, allow one match to pass
            otherwise all returned must match.
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).
        text (bool, optional): compare text value ie. <element>text</element>.
        attrib (str, optional): compare attribute value ie. <element @attrib='whatever'>.
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

        test = XmlPathRecord(
            assertion=assertion,
            one_of=one_of,
            value=value,
            xpath=xpath,
            result_attr=result_attr,
            host_data=host_data,
            fail_task=fail_task,
            attrib=attrib,
            text=text,
        )

        if len(args) > 0:
            task = args[0]
        else:
            task = kwargs["task"]

        result = wrapped(*args, **kwargs)

        try:
            attr_data = getattr(result, test.result_attr)

            # test.host_data always preferred
            if test.host_data:
                new_value = parse(test.host_data).find(task.host.data)

                if len(new_value) > 1:
                    raise Exception("host_data can only return one match")

                elif not new_value:
                    raise Exception("host_data not found")

                test.value = new_value[0].value if new_value[0] else test.value

            if isinstance(attr_data, str):
                attr_data = etree.fromstring(attr_data)

            match = attr_data.findall(test.xpath)

            if not match:
                raise Exception(f"no match found from path {test.xpath}")

            for submatch in match:

                try:
                    if test.text:
                        assert_obj = assert_that(submatch.text)
                    elif test.attrib:
                        assert_obj = assert_that(submatch.attrib[test.attrib])
                    else:
                        assert_obj = assert_that(submatch)

                    assert_method = getattr(assert_obj, test.assertion)

                    if test.value:
                        assert_method(test.value)
                    else:
                        assert_method()

                    test.passed = True
                    test.matches.append(attr_data.getroottree().getpath(submatch))

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
