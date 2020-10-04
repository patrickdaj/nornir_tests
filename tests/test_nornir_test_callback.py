import json
import os

from nornir_tests.plugins.tasks import wrap_task
from nornir_tests.plugins.tests import callback as t_callback

from nornir.core.task import Result

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_json_dict(task):
    with open(os.path.join(dir_path, "data/netjson-config.json"), "r") as f:
        result = Result(host=task.host, result=json.load(f), changed=False)
    return result


def my_callback(result, test, task):
    if not result.changed:
        test.passed = False


def test_basic_callback(single_host):
    results = single_host.run(
        task=wrap_task(get_json_dict), tests=[t_callback(callback=my_callback)]
    )

    for result in results.values():
        assert not result[0].failed
        assert not result[0].tests[0].passed
