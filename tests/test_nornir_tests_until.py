from nornir_tests.plugins.tests import test_until

from nornir_utils.plugins.tasks.data import echo_data

from nornir.core.task import Result


def just_fail(task):
    return Result(host=task.host, failed=True)


def test_until_passed(nornir):

    results = nornir.run(
        task=echo_data,
        name="whatever",
        z="zzzsuperpassword!dkfj",
        tests=[test_until(delay=1, retries=6)],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert not result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert result[0].tests[0].t1 > result[0].tests[0].t0


def test_until_on_failed(nornir):

    results = nornir.run(
        name="whatever",
        task=just_fail,
        tests=[test_until(delay=1, retries=6)],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert result[0].failed
        assert len(result[0].tests) > 0
        assert result[0].tests[0].t1 > result[0].tests[0].t0
