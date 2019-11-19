DOCUMENTATION = '''
author: Caoyingjun

'''

import os
import subprocess

SERVICE_DIR = '/etc/systemd/system'


def _run(cmd):
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return proc.communicate()


def stop_service(service_name):
    stop_cmd = ['systemctl', 'stop', service_name]
    return _run(stop_cmd)


def reload_daemon():
    reload_cmd = ['systemctl', 'daemon-reload']
    return _run(reload_cmd)


def main():
    specs = dict(
        service_name=dict(required=True, type='str'),
    )

    module = AnsibleModule(argument_spec=specs, bypass_checks=True)  # noqa
    params = module.params

    service_name = params.get('service_name')
    service_file = os.path.join(SERVICE_DIR,
                                '.'.join([service_name, 'service']))

    is_remove = False
    error_msg = ''
    if os.path.exists(service_file):
        try:
            is_remove = True
            stop_service(service_name)
            os.remove(service_file)
            reload_daemon()
        except Exception as e:
            error_msg = e

    if not is_remove:
        module.exit_json(changed=False)
    else:
        if not error_msg:
            module.exit_json(changed=True)
        else:
            module.exit_json(failed=True, changed=True, result=error_msg)


# import module snippets
from ansible.module_utils.basic import *  # noqa
if __name__ == '__main__':
    main()
