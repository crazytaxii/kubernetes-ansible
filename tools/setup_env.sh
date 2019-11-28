#!/usr/bin/env bash

yum install -y epel-release
yum install -y git gcc python-setuptools python-devel python-pip vim screen python-devel libffi-devel openssl-devel

mkdir -p ~/.pip
cat << EOF > ~/.pip/pip.conf
[global]
trusted-host =  mirrors.aliyun.com
index-url = http://mirrors.aliyun.com/pypi/simple/
EOF

if [[ ! -f "/tmp/get-pip.py"  ]]; then
    curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py  && python /tmp/get-pip.py
fi

if [[ ! -d "kubernetes-ansible" ]]; then
    git clone https://github.com/yingjuncao/kubernetes-ansible
    cp -r kubernetes-ansible/etc/kubernetes-ansible/ /etc/
    cp kubernetes-ansible/ansible/inventory/multinode .
    pip install kubernetes-ansible/
fi