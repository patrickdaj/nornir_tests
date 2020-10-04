import pytest

from nornir_tests.plugins.tests import regexp as t_regexp
from nornir_tests.plugins.tasks import wrap_task

from nornir_utils.plugins.tasks.data import echo_data


def t_regexp_not_failed(single_host):
    results = single_host.run(
        task=wrap_task(echo_data),
        z="zzzsuperpassword!dkfj",
        tests=[t_regexp(result_attr="result", regexp=r".*uperpas*word")],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert not result[0].failed
        assert len(result[0].tests) > 0
        assert str(result[0]) != ""


@pytest.mark.parametrize("fail", [True, False])
def t_regexp_failed(single_host, fail):
    results = single_host.run(
        task=wrap_task(echo_data),
        z="zzzsuperpassword!dkfj",
        tests=[
            t_regexp(result_attr="result", regexp=r".*upexyzrpas*word", fail_task=fail)
        ],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert result[0].failed == fail
        assert len(result[0].tests) > 0
        assert str(result[0].tests[0].exception).find("no match found for regex") != -1
