import pytest
import xml.etree.ElementTree as ET
import lxml
import os

from nornir_tests.plugins.tests import test_lxml

from nornir.core.task import Result

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_xml_str(task):
    with open(os.path.join(dir_path, "data/test.xml"), "r") as f:
        result = Result(host=task.host, result=f.read())
    return result


def get_xml_etree(task):
    with open(os.path.join(dir_path, "data/test.xml"), "r") as f:
        result = Result(host=task.host, result=ET.fromstring(f.read()))
    return result

def get_xml_lxml(task):
    with open(os.path.join(dir_path, "data/test.xml"), "r") as f:
        result = Result(host=task.host, result=lxml.etree.fromstring(f.read()))
    return result


def get_list(task):
    return Result(host=task.host, result=[1, 2, 3])


def test_lxml_from_str_using_attrib(nornir):

    results = nornir.run(
        task=get_xml_str,
        tests=[test_lxml(xpath=".//book", attrib="id", value="bk101")],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert not result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert hasattr(result[0].tests[0], "match")
        assert result[0].tests[0].result


def test_lxml_from_str_using_text(nornir):

    results = nornir.run(
        task=get_xml_str,
        tests=[test_lxml(xpath=".//book/genre", text=True, value="Computer")],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert not result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert hasattr(result[0].tests[0], "match")
        assert result[0].tests[0].result

@pytest.mark.parametrize('xml_func', [get_xml_etree, get_xml_lxml])
def test_lxml_from_etree(nornir, xml_func):

    results = nornir.run(
        task=xml_func,
        tests=[test_lxml(xpath=".//book/genre", text=True, value="ComputerX")],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert not result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert hasattr(result[0].tests[0], "match")
        assert not result[0].tests[0].result


def test_lxml_from_str_failure(nornir):

    results = nornir.run(
        task=get_xml_str,
        tests=[
            test_lxml(
                xpath=".//book/genre", text=True, value="ComputerX", fail_task=True
            )
        ],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert not result[0].tests[0].result


def test_lxml_invalid_input(nornir):

    results = nornir.run(
        task=get_list,
        tests=[
            test_lxml(
                xpath=".//book/genre", text=True, value="Computer", fail_task=True
            ),
        ],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert not result[0].tests[0].result
        assert result[0].tests[0].msg.find("is not xml or etree") != -1


def test_lxml_no_path_match(nornir):

    results = nornir.run(
        task=get_xml_str,
        tests=[
            test_lxml(
                xpath=".//book/genre/invalid",
                text=True,
                value="Computer",
                fail_task=True,
            )
        ],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert not result[0].tests[0].result
        assert result[0].tests[0].msg.find("no match found from xpath") != -1

@pytest.mark.parametrize('xml_func', [get_xml_etree, get_xml_lxml])
def test_lxml_no_value_match(nornir, xml_func):

    results = nornir.run(
        task=xml_func,
        tests=[
            test_lxml(xpath=".//book/genre", text=True, value="ABC", fail_task=True)
        ],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert not result[0].tests[0].result
        assert result[0].tests[0].msg.find("not found as text") != -1
