import pytest
import json
import os

from nornir_tests.plugins.tests import test_jsonpath

from nornir.core.task import Result

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_json_str(task):
    with open(os.path.join(dir_path, "data/netjson-config.json"), "r") as f:
        result = Result(host=task.host, result=f.read())
    return result


def get_json_dict(task):
    with open(os.path.join(dir_path, "data/netjson-config.json"), "r") as f:
        result = Result(host=task.host, result=json.load(f))
    return result

def test_nornir_test_jsonpath_contains_passed(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[test_jsonpath(path="$.dns_search", assertion='contains', host_data='$.domain')],
    )

    for result in results.values():
        assert result[0].tests[0].passed

def test_nornir_test_jsonpath_contains_failed(nornir):
    results = nornir.run(
        task=get_json_dict,
        tests=[test_jsonpath(path="$.dns_search", assertion='contains', host_data='$.domain2')],
    )

    for result in results.values():
        assert not result[0].tests[0].passed

