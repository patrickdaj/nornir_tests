import os

from nornir import InitNornir
from nornir.core.filter import F
from nornir.core.state import GlobalState

from nornir_tests.plugins.processors import TestsProcessor

import pytest


global_data = GlobalState(dry_run=True)


@pytest.fixture(scope="session", autouse=True)
def nornir(request):
    """Initializes nornir"""
    dir_path = os.path.dirname(os.path.realpath(__file__))

    nornir = InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": "{}/inventory_data/hosts.yaml".format(dir_path),
                "group_file": "{}/inventory_data/groups.yaml".format(dir_path),
                "defaults_file": "{}/inventory_data/defaults.yaml".format(dir_path),
            },
        },
        dry_run=True,
    )

    nornir.data = global_data
    nornir.processors.append(TestsProcessor())

    return nornir


@pytest.fixture(scope="session", autouse=True)
def single_host(nornir):
    return nornir.filter(name="test")


@pytest.fixture(scope="session", autouse=True)
def two_hosts(nornir):
    return nornir.filter(F(groups__contains="two_hosts"))


@pytest.fixture(scope="function", autouse=True)
def reset_data():
    global_data.dry_run = True
    global_data.reset_failed_hosts()
