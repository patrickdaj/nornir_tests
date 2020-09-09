import pytest

from nornir_tests.plugins.tests import test_timing

from nornir_utils.plugins.tasks.data import echo_data


@pytest.mark.parametrize("fail_task", [True, False])
def test_failed_argument_values(nornir, fail_task):
    results = nornir.run(
        task=echo_data, x=5, y=10, tests=[test_timing(fail_task=fail_task, min_run_time=60)]
    )

    for host, result in results.items():
        assert hasattr(result[0], "run_time")
        assert hasattr(result[0], "tests")
        assert result[0].failed == fail_task


def test_no_arguments_not_failed(nornir):
    results = nornir.run(task=echo_data, x=5, y=10, tests=[test_timing()])

    for host, result in results.items():
        assert hasattr(result[0], "run_time")
        assert hasattr(result[0], "tests")
        assert result[0].failed == False
