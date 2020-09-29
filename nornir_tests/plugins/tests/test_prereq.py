nr.run(
    wrap_task(napalm_get), getters=['interfaces'],
    tests=[
        test_prereq(host_data='$..ntp_primary', assertion='is_equal_to', value=)
    ])