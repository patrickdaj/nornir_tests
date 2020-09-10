import pytest

from nornir_tests.plugins.tests import test_regexp

from nornir_utils.plugins.tasks.data import echo_data


def test_regexp_not_failed(nornir):
    results = nornir.run(
        task=echo_data,
        z="zzzsuperpassword!dkfj",
        tests=[test_regexp(result_attr="result", regexp=r".*uperpas*word")],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert not result[0].failed
        assert len(result[0].tests) > 0
        assert str(result[0]) != ""


@pytest.mark.parametrize("fail", [True, False])
def test_regexp_failed(nornir, fail):
    results = nornir.run(
        task=echo_data,
        z="zzzsuperpassword!dkfj",
        tests=[
            test_regexp(
                result_attr="result", regexp=r".*upexyzrpas*word", fail_task=fail
            )
        ],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert result[0].failed == fail
        assert len(result[0].tests) > 0
        assert result[0].tests[0].msg.find("no match found for regex") != -1
