from typing import List

from nornir.core.inventory import Host
from nornir.core.task import AggregatedResult, MultiResult, Task

from nornir_tests.plugins.tests import apply_tests


class TestsProcessor:
    """This processor adds additional functionality to wrap tasks with test decorators.

    This was required due to the fact that decorators can't be easily applied to the tasks
    in Nornir.  Multiple decorations can be applied to a task but it is only usable on
    tasks that return a result such as nr.run tasks or task.run tasks.  Tests cannot be
    applied to grouped task calls but they can be present inside them.
    """

    def task_started(self, task: Task) -> None:
        """
        Nothing was added to this method.
        """
        if "tests" in task.params:
            task.task = apply_tests(task.task, task.params["tests"])
            del task.params["tests"]

    def task_completed(self, task: Task, result: AggregatedResult) -> None:
        """
        Nothing was added to this method.
        """
        pass

    def task_instance_started(self, task: Task, host: Host) -> None:
        """
        This method is overriden to apply decorators in task.params['tests'] to
        task.task.
        """
        if "tests" in task.params:
            task.task = apply_tests(task.task, task.params["tests"])
            del task.params["tests"]

    def task_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        """
        Nothing was added to this method.
        """
        pass

    def subtask_instance_started(self, task: Task, host: Host) -> None:
        """
        This method is overriden to apply decorators in task.params['tests'] to
        task.task.
        """
        if "tests" in task.params:
            task.task = apply_tests(task.task, task.params["tests"])
            del task.params["tests"]

    def subtask_instance_completed(
        self, task: Task, host: Host, result: MultiResult
    ) -> None:
        """
        Nothing was added to this method.
        """
        pass
