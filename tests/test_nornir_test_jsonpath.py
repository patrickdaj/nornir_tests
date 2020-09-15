import json
import os

from nornir_tests.plugins.tests import test_jsonpath

from nornir.core.task import Result

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_invalid_json(task):
    with open(os.path.join(dir_path, "data/panos_config.xml"), "r") as f:
        result = Result(host=task.host, result=f.read())
    return result


def get_json_str(task):
    with open(os.path.join(dir_path, "data/netjson-config.json"), "r") as f:
        result = Result(host=task.host, result=f.read())
    return result


def get_json_dict(task):
    with open(os.path.join(dir_path, "data/netjson-config.json"), "r") as f:
        result = Result(host=task.host, result=json.load(f))
    return result

@test_jsonpath(path="$.dns_servers", assertion="contains", host_data="$.dns_primary")
def decorated(task):
    return get_json_dict(task)

def test_multi_host_fail_host_test2_decorator(nornir2):
    results = nornir2.run(decorated)

    assert results['test'][0].tests[0].passed
    assert not results['test2'][0].tests[0].passed

    for result in results.values():
        assert len(result[0].tests) == 1

def test_multi_host_fail_host_test2(nornir2):
    results = nornir2.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.dns_servers", assertion="contains", host_data="$.dns_primary"
            )
        ],
    )
    assert results['test'][0].tests[0].passed
    assert not results['test2'][0].tests[0].passed

    for result in results.values():
        assert len(result[0].tests) == 1

def test_contains_passed(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.dns_search", assertion="contains", host_data="$.domain"
            )
        ],
    )

    for result in results.values():
        assert result[0].tests[0].passed


def test_match_len_one(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.type", assertion="is_equal_to", value="DeviceConfiguration"
            )
        ],
    )

    for result in results.values():
        assert result[0].tests[0].passed
        assert len(result[0].tests[0].matches) == 1


def test_contains_failed(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.dns_search", assertion="contains", host_data="$.domain2"
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert str(result[0].tests[0].exception).find("Expected") != -1


def test_found_duplicate_host_data(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.dns_search", assertion="contains", host_data="$..duplicate"
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert (
            str(result[0].tests[0].exception) == "host_data can only return one match"
        )


def test_path_not_found(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(path="$.invalid", assertion="contains", host_data="$.domain")
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert str(result[0].tests[0].exception) == "no match found from path $.invalid"


def test_with_one_of_single_match(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.interfaces..address",
                assertion="is_equal_to",
                value="192.168.1.1",
                one_of=True,
            )
        ],
    )

    for result in results.values():
        assert result[0].tests[0].passed
        assert len(result[0].tests[0].matches) == 1


def test_without_one_of_single_match(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.interfaces..address",
                assertion="is_equal_to",
                value="192.168.1.1",
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert str(result[0].tests[0].exception).find("Expected") != -1


def test_with_one_of_multi_match(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.interfaces..mask",
                assertion="is_equal_to",
                value=24,
                one_of=True,
            )
        ],
    )

    for result in results.values():
        assert result[0].tests[0].passed
        assert len(result[0].tests[0].matches) > 1


def test_without_one_of_multi_match_failed(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.interfaces..mask", assertion="is_equal_to", value="24"
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed


def test_without_one_of_multi_match_passed(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.interfaces..mtu", assertion="is_equal_to", value="1500"
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed


def test_dont_fail_task(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(path="$.dns_servers", assertion="contains", value="8.8.8.8")
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert not result[0].failed


def test_fail_task(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(
                path="$.dns_servers",
                assertion="contains",
                value="8.8.8.8",
                fail_task=True,
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert result[0].failed


def test_string_input(nornir):
    results = nornir.run(
        task=get_json_str,
        tests=[
            test_jsonpath(path="$.interfaces..mtu", assertion="is_equal_to", value=1500)
        ],
    )

    for result in results.values():
        assert result[0].tests[0].passed


def test_invalid_input(nornir):
    results = nornir.run(
        task=get_invalid_json,
        tests=[
            test_jsonpath(
                path="$.interfaces..mtu", assertion="is_equal_to", value="1500"
            )
        ],
    )

    for result in results.values():
        assert not result[0].tests[0].passed
        assert str(result[0].tests[0].exception).find("Expecting value") != -1
