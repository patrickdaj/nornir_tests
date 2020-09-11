from nornir_tests.plugins.tests import test_until

from nornir_utils.plugins.tasks.data import echo_data

from nornir.core.task import Result

counter = 0

def just_fail(task):
    return Result(host=task.host, failed=True)

def just_pass(task):
    return Result(host=task.host, failed=False)

def generate_exception(task):
    global counter
    if counter < 4:
        counter += 1
        raise Exception("I gonna die")
    return Result(host=task.host, failed=False)

def test_until_passed(nornir):

    results = nornir.run(
        task=echo_data,
        name="whatever",
        z="zzzsuperpassword!dkfj",
        tests=[test_until(delay=1, retries=6)],
    )

    for host, result in results.items():
        assert not result[0].failed
        assert result[0].tests[0].run_time > 0


def test_until_on_failed(nornir):

    results = nornir.run(
        name="whatever",
        task=just_fail,
        tests=[test_until(delay=1, retries=6)],
    )

    for host, result in results.items():
        assert result[0].failed
        assert result[0].tests[0].run_time > 0
        assert not result[0].tests[0].passed


def test_exception_catch(nornir):

    results = nornir.run(
        name='exception',
        task=generate_exception,
        tests=[
            test_until(delay=1, retries=5)
        ]
    )

    for host, result in results.items():
        assert not result[0].failed
        assert result[0].tests[0].run_time > 0

def test_initial_delay(nornir):

    results = nornir.run(
        name='exception',
        task=just_pass,
        tests=[
            test_until(delay=0, retries=0, initial_delay=1)
        ]
    )

    for host, result in results.items():
        assert not result[0].failed
        assert result[0].tests[0].run_time > 1