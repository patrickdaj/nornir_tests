from nornir_napalm.plugins.tasks import napalm_get
from nornir_netmiko.tasks import netmiko_send_command
from nornir_rich.plugins.functions import RichResults
from nornir_tests.plugins.tests import until, jpath
from nornir_tests.plugins.processors import TestsProcessor
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

nr.processors.append(TestsProcessor())

vyos = nr.filter(name="vyos")


# Using @decorator syntax
@jpath(
    path="interfaces_ip.eth0.ipv4",
    assertion="contains_key",
    value="192.168.99.170",
    fail_task=True,
)
def check_interface(task):
    return napalm_get(task, getters=["interfaces_ip"])


result = vyos.run(check_interface, name="Check Interface")

rr.print(result, vars=["result", "tests"])

rr.print(vyos.run(task=netmiko_send_command, command_string="reboot now"))

# Using the TestsProcessor to wrap the task
result = vyos.run(
    task=napalm_get,
    getters=["interfaces"],
    tests=[
        jpath(path="interfaces.eth0.is_up", assertion="is_true", fail_task=True),
        until(initial_delay=15, retries=10, delay=15, reset_conns=True),
    ],
)

rr.print(result, vars=["result", "tests"])
rr.write()
