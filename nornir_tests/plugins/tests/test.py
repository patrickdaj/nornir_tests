import pprint
from dataclasses import dataclass
from typing import Any, Union, Dict


@dataclass
class TestRecord:
    passed: bool = False
    fail_task: bool = False
    exception: Union[Exception, None] = None

    result_keys = ["exception"]
    repr_keys = ["fail_task"]

    def result(self) -> Dict[str, Any]:
        return {k: v for k, v in vars(self).items() if v and k in self.result_keys}

    def requirement(self) -> str:
        reqs = {k: v for k, v in vars(self).items() if v and k in self.repr_keys}
        return f"{self.__class__.__name__} - " + pprint.pformat(reqs)
