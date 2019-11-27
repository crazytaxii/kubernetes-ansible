#!/usr/bin/env bash

echo nameserver 114.114.114.114 > /etc/resolv.conf
yum install -y epel-release
yum install -y git gcc python-setuptools python-devel python-pip vim screen python-devel libffi-devel openssl-devel

mkdir -p ~/.pip

cat << EOF > ~/.pip/pip.conf
[global]
trusted-host =  mirrors.aliyun.com
index-url = http://mirrors.aliyun.com/pypi/simple/
EOF
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py  && python /tmp/get-pip.py


git clone https://github.com/yingjuncao/kubernetes-ansible
cp -r kubernetes-ansible/etc/kubernetes-ansible/ /etc/
cp kubernetes-ansible/ansible/inventory/multinode .
pip install kubernetes-ansible/
