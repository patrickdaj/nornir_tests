from dataclasses import dataclass, field
import lxml.etree as etree
from jsonpath_ng import parse
from typing import Callable, Any, List
from assertpy import assert_that

from nornir.core.task import Result

from .test import Test

@dataclass
class test_lxml(Test):
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
        fail_task (bool, optional): Determines whether test failure results causes setting result failure.
    """
    text: bool = False
    host_data: str = ""
    xpath: str = ""
    one_of: bool = False
    value: str = ""
    attrib: str = ""
    result_attr: str = "result"
    assertion: str = "is_equal_to"
    matches: List[str] = field(default_factory=list)
    match: List[Any] = field(default_factory=list, repr=False)

    def run(self, func: Callable[..., Any], task, *args: str, **kwargs: str) -> Result:
        """Method decorator to perform lxml find and compare on result of task

        Args:
            func (Callable[..., Any]): Decorated function

        Returns:
            `nornir.core.task.Result`: Result of task after executed and decorated by test_jsonpath
        """

        result = func(task, *args, **kwargs)
        try:
            attr_data = getattr(result, self.result_attr)

            # self.host_data always preferred
            if self.host_data:
                new_value = parse(self.host_data).find(task.host.data)

                if len(new_value) > 1:
                    raise Exception("host_data can only return one match")

                elif not new_value:
                    raise Exception("host_data not found")

                self.value = new_value[0].value if new_value[0] else self.value


            if isinstance(attr_data, str):
                attr_data = etree.fromstring(attr_data)
                
            self.match = attr_data.findall(self.xpath)

            if not self.match:
                raise Exception(f"no match found from path {self.xpath}")

            for match in self.match:

                try:
                    if self.text:
                        assert_obj = assert_that(match.text)
                    elif self.attrib:
                        assert_obj = assert_that(match.attrib[self.attrib])
                    else:
                        assert_obj = assert_that(match)

                    assert_method = getattr(assert_obj, self.assertion)
                    
                    if self.value:
                        assert_method(self.value)
                    else:
                        assert_method()

                    self.passed = True
                    self.matches.append(attr_data.getroottree().getpath(match))

                except Exception as e:
                    if not self.one_of or (match == self.match[-1] and not self.passed):
                        raise Exception(e)


        except Exception as e:
            self.passed = False
            self.exception = e

        self._add_test(result)

        if not self.passed and self.fail_task:
            result.failed = True

        return result
