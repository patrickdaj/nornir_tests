import pprint

from typing import Callable, List, Any

from nornir.core.task import Result


def apply_tests(
    task: Callable[..., Any], tests: List[Callable[..., Any]]
) -> Callable[..., Any]:
    """Apply tests (decorators) to task

    Args:
        task (Callable[..., Any]): nornir task
        tests (List[Callable[..., Any]]): test decorators to apply

    Returns:
        Callable[..., Any]: Decorated function
    """
    wrapped = task
    for wrapper in tests:
        wrapped = wrapper(wrapped)

    return wrapped


class Test:
    """Test for Nornir task

    This class can be used to decorate nornir tasks and provides the ability to perform
    validations on the result.  It is only usable on tasks that return results such as
    those executed with nornir.run or task.run.  Grouped tasks cannot be decorated but
    the tasks in the grouped tasks function can.
    """

    def __init__(self, fail_task: bool = False):
        """Constructor of Test object

        Args:
            fail_task (bool, optional): Determines whether test failure results causes
                setting result failure. Defaults to False.
        """
        self.fail_task: bool = fail_task

    def run(self, func: Callable[..., Any], *args: str, **kwargs: str) -> Result:
        """run should be implemented in derived classes"""
        raise Exception("Not implemented in base class")

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Call overload

        Args:
            func (Callable[..., Any]): Function to decorate

        Returns:
            Callable[..., Any]: Decorated function
        """

        def inner(*args: str, **kwargs: str) -> Result:
            return self.run(func, *args, **kwargs)

        return inner

    def __str__(self) -> str:
        """To string overload

        Returns:
            str: string representation of Test object
        """
        return "{} - {}".format(self.msg, "PASSED" if self.result else "FAILED")

    def _add_test(self, result: Result) -> None:
        """Add test result to TestList in result

        Args:
            result (`nornir.core.task.Result`): task results object
        """
        if getattr(result, "tests", None):
            result.tests.append(self)
        else:
            result.tests = TestList()
            result.tests.append(self)


class TestList(object):
    """List type container of Test objects"""

    def __init__(self) -> None:
        """Constructor for TestList"""
        self.tests: List[Test] = []

    def __getitem__(self, key: int) -> Test:
        """Index access overload"""
        return self.tests[key]

    def append(self, test: Test) -> None:
        """Append a Test to list

        Args:
            test (Test): Test to append
        """
        self.tests.append(test)

    def __str__(self) -> str:
        """To string overload

        Returns:
            str: string representation of Test object
        """
        string = ""

        for test in self.tests:
            string += pprint.pformat(str(test)) + "\n"

        string.rstrip("\n")

        return string

    def __repr__(self) -> str:
        """Represent overload

        Returns:
            str: string representation of Test object
        """
        return self.__str__()

    def __len__(self) -> int:
        """Length overload

        Returns:
            int: length of test attribute
        """
        return len(self.tests)
