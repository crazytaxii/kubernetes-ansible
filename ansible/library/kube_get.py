#!/usr/bin/env python
#
# Copyright 2019 Caoyingjun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DOCUMENTATION = '''
author: Caoyingjun

'''

import subprocess
import yaml

from kubernetes import client
from kubernetes import config


KUBEADMIN = '/etc/kubernetes/admin.conf'


def get_kube_client():
    config.kube_config.load_kube_config(
        config_file=KUBEADMIN)
    return client.CoreV1Api()


class GetWoker(object):

    def __init__(self, params):
        self.params = params
        self.get_list = self.params.get('get_list')
        self.changed = False

        # Use this to store arguments to pass to exit_json()
        self.result = {}
        self.kube_client = get_kube_client()

    def get_token(self):
        os.environ['KUBECONFIG'] = KUBEADMIN
        cmd = 'kubeadm token list | grep system:bootstrappers'
        tokens = self._run(cmd)
        tokens = tokens.split('\n')

        for tk in tokens:
            if not tk:
                continue
            tk = tk.split()
            if int(tk[1][:-1]) > 0:
                token = tk[0]
                break
        else:
            # if all the token are inactive, recreate it.
            recmd = 'kubeadm token create'
            new_token = self._run(recmd)
            token = new_token[:-1]
            self.changed = True

        self.result['token'] = token

    # Get he apiserver from KUBECONFIG
    def get_kube_apiserver(self):
        with open(KUBEADMIN, 'r') as f:
            kubeconfig = yaml.load(f)

        kube_apiserver = kubeconfig['clusters'][0]['cluster']['server']

        self.result['apiserver'] = kube_apiserver.split('//')[-1]

    def get_token_ca_cert_hash(self):
        cmd = ("openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | "
               "openssl rsa -pubin -outform der 2>/dev/null | "
               "openssl dgst -sha256 -hex | sed 's/^.* //'")
        token_ca_cert_hash = self._run(cmd)

        self.result['token_ca_cert_hash'] = token_ca_cert_hash[:-1]

    def _run(self, cmd):
        proc = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True)
        stdout, _ = proc.communicate()
        return stdout

    @property
    def kube_nodes(self):
        kube_nodes = [node.metadata.name
                      for node in self.kube_client.list_node().items]
        return kube_nodes

    def get_update_nodes(self):
        kube_workers = self.params.get('kube_workers')
        workers_added= list(set(kube_workers) - set(self.kube_nodes))
        self.result['workers_added'] = workers_added

    def run(self):
        self.get_kube_apiserver()
        self.get_update_nodes()
        self.get_token()
        self.get_token_ca_cert_hash()


def main():
    specs = dict(
        kube_workers=dict(type='list', required=True),
        get_list=dict(type='list', required=True),
    )

    module = AnsibleModule(argument_spec=specs, bypass_checks=True)
    params = module.params

    gw = None
    try:
        gw = GetWoker(params)
        gw.run()
        module.exit_json(changed=gw.changed, result=gw.result)
    except Exception as emsg:
        module.fail_json(changed=True, msg=emsg, faild=True)


# import module snippets
from ansible.module_utils.basic import *  # noqa
if __name__ == '__main__':
    main()
