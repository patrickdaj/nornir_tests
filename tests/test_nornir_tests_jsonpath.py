import json
import os

from nornir_tests.plugins.tests import test_jsonpath

from nornir.core.task import Result

dir_path = os.path.dirname(os.path.realpath(__file__))


def get_json_str(task):
    with open(os.path.join(dir_path, "data/test.json"), "r") as f:
        result = Result(host=task.host, result=f.read())
    return result


def get_json_dict(task):
    with open(os.path.join(dir_path, "data/test.json"), "r") as f:
        result = Result(host=task.host, result=json.load(f))
    return result


def get_list(task):
    return Result(host=task.host, result=[1, 2, 3])


def test_jsonpath_from_str(nornir):

    results = nornir.run(
        task=get_json_str,
        tests=[test_jsonpath(path="books[*].id", value="bk102")],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert not result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert hasattr(result[0].tests[0], "match")


def test_jsonpath_from_dict(nornir):

    results = nornir.run(
        task=get_json_dict,
        tests=[test_jsonpath(path="books[*].id", value="bk102")],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert not result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert hasattr(result[0].tests[0], "match")


def test_jsonpath_from_dict_failure(nornir):

    results = nornir.run(
        task=get_json_dict,
        tests=[test_jsonpath(path="books[*].id", value="bk101", fail_task=True)],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0


def test_jsonpath_invalid_input(nornir):

    results = nornir.run(
        task=get_list,
        tests=[test_jsonpath(path="books[*].id", value="bk101", fail_task=True)],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert result[0].tests[0].msg.find("not parsible as dict") != -1


def test_jsonpath_no_path_match(nornir):

    results = nornir.run(
        task=get_json_dict,
        tests=[
            test_jsonpath(path="books[*].id.invalid", value="bk101", fail_task=True)
        ],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert result[0].tests[0].msg.find("no match found from path") != -1


def test_jsonpath_no_value_match(nornir):

    results = nornir.run(
        task=get_json_dict,
        tests=[test_jsonpath(path="books[*].id", value="invalid")],
    )

    for host, result in results.items():
        assert hasattr(result[0], "tests")
        assert not result[0].failed
        assert str(result[0]) != ""
        assert len(result[0].tests) > 0
        assert result[0].tests[0].msg.find("could not find value") != -1

# TODO -
# add test to validate host_data
# add test to validate one_of
# add test to validate multiple match without one_of