import lxml
import os

from nornir_tests.plugins.tests import xpath as t_lxml
from nornir_tests.plugins.tasks import wrap_task

from nornir.core.task import Result

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_non_xml_str(task):
    return Result(host=task.host, result="kdfjkd^%%%##  ")


def get_xml_str(task):
    with open(os.path.join(dir_path, "data/panos_config.xml"), "r") as f:
        result = Result(host=task.host, result=f.read())
    return result


def get_xml_etree(task):
    with open(os.path.join(dir_path, "data/panos_config.xml"), "r") as f:
        result = Result(host=task.host, result=lxml.etree.fromstring(f.read()))
    return result


def get_list(task):
    return Result(host=task.host, result=[1, 2, 3])


def test_is_equal_passed_and_len_one(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath='.//monitor-profile/entry[@name="default"]/interval',
                assertion="is_equal_to",
                text=True,
                value="3",
            )
        ],
    )

    for result in results.values():
        assert result[0].tests[0].passed
        assert len(result[0].tests[0].matches) == 1


def test_is_equal_passed_attribute(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath=".//system/match-list/entry",
                assertion="is_equal_to",
                value="System_Log_Forwarding",
                attrib="name",
                one_of=True,
            )
        ],
    )

    for result in results.values():
        assert result[0].tests[0].passed
        assert len(result[0].tests[0].matches) == 1


def test_contains_failed(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath='.//monitor-profile/entry[@name="default"]/interval',
                assertion="is_equal_to",
                text=True,
                value="4",
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert str(result[0].tests[0].exception).find("Expected") != -1


def test_found_no_host_data(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath='.//monitor-profile/entry[@name="default"]/interval',
                assertion="is_equal_to",
                text=True,
                host_data="$.invalid",
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert str(result[0].tests[0].exception) == "host_data not found"


def test_found_duplicate_host_data(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath='.//monitor-profile/entry[@name="default"]/interval',
                assertion="is_equal_to",
                text=True,
                host_data="$..duplicate",
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert (
            str(result[0].tests[0].exception) == "host_data can only return one match"
        )


def test_path_not_found(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath=".//invalid/invalid", assertion="contains", host_data="$.domain"
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert (
            str(result[0].tests[0].exception)
            == "no match found from path .//invalid/invalid"
        )


def test_with_one_of_single_match(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath=".//ike-crypto-profiles/entry[@name='default']/encryption/member",
                assertion="is_equal_to",
                value="aes-128-cbc",
                one_of=True,
                text=True,
            )
        ],
    )

    for result in results.values():
        assert result[0].tests[0].passed
        assert len(result[0].tests[0].matches) == 1


def test_without_one_of_single_match(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath=".//entry/encryption/member",
                assertion="is_equal_to",
                value="aes-128-cbc",
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert str(result[0].tests[0].exception).find("Expected") != -1


def test_with_one_of_multi_match(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath=".//wildfire-action",
                assertion="is_equal_to",
                value="reset-both",
                text=True,
                one_of=True,
            )
        ],
    )

    for result in results.values():
        assert result[0].tests[0].passed
        assert len(result[0].tests[0].matches) > 1


def test_without_one_of_multi_match_failed(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath=".//wildfire-action", assertion="is_equal_to", value="reset-both"
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed


def test_without_one_of_multi_match_passed(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[t_lxml(xpath="alarm-rate", assertion="is_equal_to", value="10000")],
    )

    for result in results.values():
        assert not result[0].tests[0].passed


def test_dont_fail_task(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[t_lxml(xpath="alarm-rate", assertion="is_equal_to", value="-1")],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert not result[0].failed


def test_fail_task(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_etree),
        tests=[
            t_lxml(
                xpath="alarm-rate", assertion="is_equal_to", value="-1", fail_task=True
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert result[0].failed


def test_string_input(single_host):
    results = single_host.run(
        task=wrap_task(get_xml_str),
        tests=[
            t_lxml(
                xpath=".//minimum-length",
                assertion="is_equal_to",
                value="12",
                text=True,
            )
        ],
    )

    for result in results.values():
        assert result[0].tests[0].passed


def test_invalid_input(single_host):
    results = single_host.run(
        task=wrap_task(get_non_xml_str),
        tests=[t_lxml(xpath=".//whatever", assertion="is_equal_to", value="1500")],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert str(result[0].tests[0].exception).find("Start tag expected") != -1
