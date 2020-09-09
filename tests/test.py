from nornir import InitNornir

from nornir_utils.plugins.tasks.data import echo_data
from nornir_utils.plugins.functions import print_result
from nornir_tests.plugins import tests
from nornir_tests.plugins.processors import TestsProcessor

nr = InitNornir()
nr.processors.append(TestsProcessor())

result = nr.run(
    task=echo_data,
    tests=[tests.timing(min_run_time=10), tests.changed(fail=False)],
    x="an x",
    y="a y",
)
print_result(result, vars=["stdout", "test", "result"])


def sub_task(task):
    task.run(
        task=echo_data,
        tests=[tests.timing(min_run_time=10), tests.changed(fail=False)],
        x="an x",
        y="a y",
    )


print_result(nr.run(sub_task, tests=[tests.timing]), vars=["stdout", "test", "result"])
