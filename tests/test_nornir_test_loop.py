import os

from nornir_tests.plugins.tasks import wrap_task
from nornir_tests.plugins.tests import loop as t_loop
from nornir_utils.plugins.tasks.data import echo_data

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_basic_loop(single_host):
    results = single_host.run(
        task=wrap_task(echo_data), tests=[t_loop(placeholder="x", values=[1, 2, 3])]
    )

    for result in results.values():
        assert len(result.result) == 3
        assert not result.failed
