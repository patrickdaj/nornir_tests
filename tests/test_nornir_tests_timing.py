import pytest

from nornir_tests.plugins.tests import timing as t_timing
from nornir_tests.plugins.tasks import wrap_task

from nornir_utils.plugins.tasks.data import echo_data


@pytest.mark.parametrize("fail_task", [True, False])
def test_failed_argument_values(single_host, fail_task):
    results = single_host.run(
        task=wrap_task(echo_data),
        x=5,
        y=10,
        tests=[t_timing(fail_task=fail_task, min_run_time=60)],
    )

    for host, result in results.items():
        assert len(result[0].tests) > 0
        assert hasattr(result[0].tests[0], "run_time")
        assert result[0].failed == fail_task
        assert result[0].tests[0].t1 > result[0].tests[0].t0


def test_no_arguments_not_failed(single_host):
    results = single_host.run(task=wrap_task(echo_data), x=5, y=10, tests=[t_timing()])

    for host, result in results.items():
        assert hasattr(result[0].tests[0], "run_time")
        assert hasattr(result[0], "tests")
        assert len(result[0].tests) > 0
        assert not result[0].failed
        assert result[0].tests[0].t1 > result[0].tests[0].t0
