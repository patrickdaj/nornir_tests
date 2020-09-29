import json
import os

from nornir_tests.plugins.tasks import wrap_task
from nornir_tests.plugins.tests import test_loop as t_loop
from nornir_utils.plugins.tasks.data import echo_data

from nornir.core.task import Result

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_json_dict(task):
    with open(os.path.join(dir_path, "data/netjson-config.json"), "r") as f:
        result = Result(host=task.host, result=json.load(f), changed=False)
    return result


def my_callback(result, test, task):
    if not result.changed:
        test.passed = False


def test_basic_loop(single_host):
    results = single_host.run(
        task=wrap_task(echo_data),
        tests=[
            t_loop(placeholder='x', values=[1, 2, 3])
        ]
    )

    for result in results.values():
        assert len(result.result) == 3
        assert not result.failed
