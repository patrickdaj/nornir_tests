import lxml.etree as etree
import xml.etree.ElementTree as ET
from jsonpath_ng import parse
from typing import Callable, Any

from nornir.core.task import Result

from .test import Test


class test_lxml(Test):
    """Test decorator using lxml

    This test is based off of the `lxml <https://github.com/h2non/jsonpath-ng>`__ implementation.

    Args:
        xpath (str, optional): xpath locator. Defaults to "".
        value (str, optional): value for comparison.  Defaults to "".
        host_data (str, optional): jsonpath to get value from task.host.data.  Defaults to ""
        result_attr (str, optional): Attribute to check in results (ie. stdout, result).
            Defaults to "result".
        text (bool, optional): compare text value ie. <element>text</element>. Defaults to False.
        attrib (str, optional): compare attribute value ie. <element @attrib='whatever'>.
            Defaults to "".
        fail_task (bool, optional): Determines whether test failure results causes
            setting result failure. Defaults to False.
    """

    def __init__(
        self,
        text: bool = False,
        host_data: str = "",
        xpath: str = "",
        value: str = "",
        attrib: str = "",
        result_attr: str = "result",
        fail_task: bool = False,
    ):
        """Constructor for regexp decorator"""
        self.xpath = xpath
        self.host_data = host_data
        self.value = value
        self.text = text if text else None
        self.attrib = attrib if attrib else None
        self.result_attr = result_attr
        super(test_lxml, self).__init__(fail_task)

    def run(self, func: Callable[..., Any], *args: str, **kwargs: str) -> Result:
        """Method decorator to perform lxml find and compare on result of task

        Args:
            func (Callable[..., Any]): Decorated function

        Returns:
            `nornir.core.task.Result`: Result of task after executed and decorated by test_jsonpath
        """

        result = func(*args, **kwargs)

        try:
            if not (self.attrib or self.text):
                raise Exception("neither attrib or text were set")

            xml_data = getattr(result, self.result_attr)

            # self.host_data always preferred
            if self.host_data:
                new_value = parse(self.host_data).find(task.host.data)
                self.value = new_value if new_value else self.value

            if isinstance(xml_data, str):
                xml_data = etree.fromstring(xml_data)
            elif isinstance(xml_data, etree._Element):
                pass
            elif isinstance(xml_data, ET.Element):
                pass
            else:
                raise Exception(f"{self.result_attr} is not xml or etree")

            self.match = xml_data.find(self.xpath)

            if self.match == None:
                raise Exception(f"no match found from xpath {self.xpath}")

            else:
                if self.attrib:
                    self.result = self.match.attrib[self.attrib] == self.value

                elif self.text:
                    self.result = self.match.text == self.value

                else:
                    self.result = False

                if self.result:
                    self.msg = "{} found as {} at xpath {}".format(
                        self.value, "text" if self.text else "attrib", self.xpath
                    )

                else:
                    raise Exception(
                        "{} not found as {} at xpath {}".format(
                            self.value, "text" if self.text else "attrib", self.xpath
                        )
                    )

        except Exception as e:
            self.result = False
            self.msg = f"lxml: {e}"

        if self.fail_task and not self.result:
            result.failed = True

        self._add_test(result)

        return result
