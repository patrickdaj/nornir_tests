from nornir_napalm.plugins.tasks import napalm_get, napalm_ping
from nornir_tests.plugins.tests import test_regexp, test_until, test_timing, test_jsonpath
from nornir_netmiko.plugins import netmiko_send_command, netmiko_send_config
from nornir_rich.plugins.functions import RichResults
from nornir import InitNornir

nr = InitNornir(
    inventory={
        "plugin": "SimpleInventory",
        "options": {
            "host_file": "data/hosts.yaml",
            "group_file": "data/groups.yaml",
            "defaults_file": "data/defaults.yaml",
        },
    },
)

rr = RichResults()

from nornir_tests.plugins.processors import TestsProcessor
nr.processors.append(TestsProcessor())

vyos = nr.filter(name='vyos')

result = vyos.run(
    task=napalm_get,
    getters=['interfaces'],
    tests=[
        test_jsonpath(path='interfaces.eth0.is_up', assertion='is_true'),
    ]
)

rr.print(result)