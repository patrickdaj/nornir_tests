import os

from nornir_tests.plugins.tests import regexp as t_regexp
from nornir_tests.plugins.tasks import wrap_task

from nornir.core.task import Result

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_regexp(task):
    with open(os.path.join(dir_path, "data/show-interfaces.text"), "r") as f:
        result = Result(host=task.host, result=f.read())
    return result


def test_single_match(single_host):
    results = single_host.run(
        task=wrap_task(get_regexp),
        tests=[t_regexp(regexp=r"Ethernet1 is up", assertion="is_not_none")],
    )
    assert results["test"][0].tests[0].passed

    for result in results.values():
        assert len(result[0].tests) == 1


def test_multiple_match(single_host):
    results = single_host.run(
        task=wrap_task(get_regexp),
        tests=[t_regexp(regexp=r"Ethernet. is up", assertion="is_not_none")],
    )
    assert results["test"][0].tests[0].passed

    for result in results.values():
        assert len(result[0].tests) == 1
        assert len(result[0].tests[0].matches) == 2


def test_single_match_group(single_host):
    results = single_host.run(
        task=wrap_task(get_regexp),
        tests=[
            t_regexp(
                regexp=r"(.*?) is up",
                assertion="is_equal_to",
                one_of=True,
                value="Ethernet1",
            )
        ],
    )
    assert results["test"][0].tests[0].passed

    for result in results.values():
        assert len(result[0].tests) == 1
        assert len(result[0].tests[0].matches) == 1


def test_too_many_match_groups(single_host):
    results = single_host.run(
        task=wrap_task(get_regexp),
        tests=[
            t_regexp(
                regexp=r"(.*?) is (.*)",
                assertion="is_equal_to",
                one_of=True,
                value="Ethernet1",
            )
        ],
    )
    assert not results["test"][0].tests[0].passed

    for result in results.values():
        assert len(result[0].tests) == 1
        assert len(result[0].tests[0].matches) == 0
