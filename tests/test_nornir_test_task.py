import json
import os

from nornir_tests.plugins.tests import jpath as t_jsonpath
from nornir_tests.plugins.tasks import wrap_task

from nornir.core.task import Result

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_json_dict(task):
    with open(os.path.join(dir_path, "data/netjson-config.json"), "r") as f:
        result = Result(host=task.host, result=json.load(f))
    return result


def get_json():
    with open(os.path.join(dir_path, "data/netjson-config.json"), "r") as f:
        return json.load(f)


def test_with_function(two_hosts):
    results = two_hosts.run(
        task=wrap_task(get_json_dict),
        tests=[
            t_jsonpath(
                path="$.dns_servers", assertion="contains", host_data="$.dns_primary"
            )
        ],
    )
    assert results["test"][0].tests[0].passed
    assert not results["test2"][0].tests[0].passed

    for result in results.values():
        assert len(result[0].tests) == 1
