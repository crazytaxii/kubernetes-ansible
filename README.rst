==================
kubernetes-ansible
==================

=======
系统要求
=======
系统：centos7

规则：k8s的node节点到master节点放通6443端口

=======
通用配置
=======

1. 安装部署节点的依赖,执行

   curl https://raw.githubusercontent.com/yingjuncao/kubernetes-ansible/master/tools/setup_env.sh | bash

2. 编辑当前目录的multinode，完成主机组配置，手动开通部署节点到工作节点的免密登陆，并用如下命令测试

   ansible -i multinode all -m ping

=================
kubernetes集群部署
=================

1. 配置工作目录下的multinode,根据实际情况添加主机信息

   vim multinode
   
   [control]
   kube01

   [compute]
   kube02

2. 配置/etc/kubernetes-ansible/globals.yml

   cluster_cidr: "172.30.0.0/16"
   
   service_cidr: "10.254.0.0/16"

3. 安装kubernetes依赖包

   kubernetes-ansible -i multinode bootstrap-servers

4. 进行kubernetes的部署

   kubernetes-ansible -i multinode deploy

=============================
生成kubernetes admin-k8src.sh
=============================

1. 完成k8s的部署之后，需要导入KUBECONFIG到环境变量（类似openstack), 生成admin-k8src.sh

   kubernetes-ansible -i multinode post-deploy

2. 在master节点运行k8s集群命令

   . /root/admin-k8src.sh

   kubectl get node

===========================
kubernetes cluster node扩容
===========================

1. 配置工作目录下的multinode,根据实际情况添加worker node到compute组

   vim multinode
   
   [control]
   kube1

   [compute]
   kube[2:4]
   
3. 安装worker node的依赖包

   kubernetes-ansible -i multinode bootstrap-servers

4. 进行worker node节点的扩容

   kubernetes-ansible -i multinode deploy

===================
kubernetes 清理集群
===================

1. kubernetes清理

   kubernetes-ansible -i multinode destroy  --yes-i-really-really-mean-it

2. 如果环境允许，重启服务器，用来清除flannel.1和cni0的残留信息

   ansible -i multinode all -m shell -a reboot

=============
Ceph 集群部署
=============

1. 配置工作目录下的multinode,根据实际情况添加主机信息到控制组和存储组

   vim multinode

   [control]
   kube01

   [storage]
   kube02

2. 配置/etc/kubernetes-ansible/globals.yml

   enable_ceph: "yes"

3. 为存储节点需要作为osd的盘进行parted标记

   parted $DISK -s -- mklabel gpt mkpart KOLLA_CEPH_OSD_BOOTSTRAP_BS 1 -1

   https://github.com/openstack/kolla-ansible/blob/stable/stein/doc/source/reference/storage/ceph-guide.rst

4. 进行ceph集群的部署

   kubernetes-ansible -i multinode deploy --tag ceph