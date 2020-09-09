import pytest

from nornir_tests.plugins.tests import test_timing

from nornir_utils.plugins.tasks.data import echo_data


def subtask(task):
    results = task.run(task=echo_data, x=5, y=10, tests=[test_timing()])


def test_task_run(nornir):
    results = nornir.run(subtask)

    for host, result in results.items():
        assert hasattr(result[1], "run_time")
        assert hasattr(result[1], "tests")
        assert result[1].failed == False
