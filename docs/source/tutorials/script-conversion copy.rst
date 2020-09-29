Why nornir_tests?
=================

In the basic examples below each module is shown individually in more or less common Nornir from
vs how nornir_tests can change/enhance the logic.

Conditional logic
-----------------

.. code-block:: python

    def upgrade_if_bad_ver(task):
        if task.host['version'] == 'bad_version.0.1':
            task.run(netmiko_send_command, command_string='upgrade good_version.1.0')

    nr.run(upgrade_if_bad_ver)

Conditional logic using test_when decorator
-------------------------------------------

.. code-block:: python

    @test_when(host_data='$.version', value='bad_version.0.1')
    def upgrade_if_bad_ver(task):
        task.run(netmiko_send_command, command_string='upgrade good_version.1.0')

    nr.run(upgrade_if_bad_ver)
    
Conditional logic using wrap_task
---------------------------------

.. code-block:: python

    nr.run(
        wrap_task(netmiko_send_command), command_string='upgrade good_version.1.0',
        tests=[test_when(host_data='$.version', value='bad_version.0.1')]
    )

I guess I just get tired of if statements all over the place.  :)

Retry behavior
--------------

.. code-block:: python

    def reboot_device(task):
        task.run(netmiko_send_command, command_string='reboot')

        time.sleep(90)

        for i in range(30):
            time.sleep(30)
            task.host.close_connections()
            task.run(netmiko_send_command, command_string='check device ready')


    nr.run(reboot_device)

Retry behavior using test_until
-------------------------------

.. code-block:: python

    nr.run(netmiko_send_command, command_string='reboot')
    nr.run(
        wrap_task(netmiko_send_command), command_string='check device read',
        tests=[test_wait(initial_delay=90, retries=30, delay=30)]
    )

Looping behavior
----------------

.. code-block:: python

    