Nornir with Tests
=================

The following is a fairly simple nornir script to upgrade an HA pair of PanOS firewalls.  The first
section shows how it is written with standard Nornir and the second how it would be written with
the addition of nornir_tests.

.. code-block:: python

    from nornir import InitNornir

    nr = InitNornir()

    fw1 = nr.filter(name='fw1')
    fw2 = nr.filter(name='fw2')
    fws = nr.filter(F(groups_in=='fws' & groups_in='testbed1')

    @test_
    def check_pending_changes(task):
        r = task.run(netmiko_send_command, command_string='show pending-changes')

        if r.result