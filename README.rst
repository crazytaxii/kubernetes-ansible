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

1. 安装部署节点的依赖
   yum install -y epel-release
   yum install -y gcc git wget python-setuptools python-devel python-pip vim python-devel libffi-devel openssl-devel

   mkdir -p ~/.pip
   cat << EOF > ~/.pip/pip.conf
   [global]
   trusted-host =  mirrors.aliyun.com
   index-url = http://mirrors.aliyun.com/pypi/simple/
   EOF
   curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py  && python get-pip.py && rm -rf get-pip.py

2. 获取kubernetes-ansible:
    git clone https://github.com/yingjuncao/kubernetes-ansible

3. 拷贝/etc/sdnhub 到部署节点的/etc目录下
    cp -r  kubernetes-ansible/etc/kubernetes-ansible/ /etc/

4. 拷贝ansible/inventory/multinod到工作目录，并配置主机信息，开启部署节点到其他节点的免密
    cp kubernetes-ansible/ansible/inventory/multinode  .

5. 安装kubernetes-ansible
    pip install kubernetes-ansible/

6. 进行部署节点到工作节点的免密测试
    ansible -i multinode all -m ping

7. 安装kubernetes之前，确保所有节点均按照pip, 如果没有安装，则通过如下命令进行安装
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    ansible -i multinode all -m copy -a "src=get-pip.py dest=/root/get-pip.py"
    ansible -i multinode all -m shell -a "python /root/get-pip.py && rm -rf /root/get-pip.py"

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
    enable_kubernetes: "yes"

    cluster_cidr: "172.30.0.0/16"
    service_cidr: "10.254.0.0/16"

3. 安装kubernetes依赖包
    kubernetes-ansible -i multinode bootstrap-servers

4. 进行kubernetes的部署
    kubernetes-ansible -i multinode deploy

============================
生成kubernetes admin-k8src.sh
============================

1. 完成k8s的部署之后，需要导入KUBECONFIG到环境变量（类似openstack), 生成admin-k8src.sh
    kubernetes-ansible -i multinode post-deploy

2. 在master节点运行k8s集群命令
    . /root/admin-k8src.sh

    kubectl get node

=========================
kubernetes cluster node扩容
=========================

1. 配置工作目录下的multinode,根据实际情况添加worker node到compute组
    vim multinode
    [control]
    kube1

    [compute]
    kube[2:3]
    kube4

3. 安装worker node的依赖包
    kubernetes-ansible -i multinode bootstrap-servers

4. 进行worker node节点的扩容
    kubernetes-ansible -i multinode deploy

==================
kubernetes 清理集群
==================

1. kubernetes清理
    kubernetes-ansible -i multinode destroy  --yes-i-really-really-mean-it

2. 如果环境允许，重启服务器，用来清除flannel.1和cni0的残留信息
    ansible -i multinode all -m shell -a reboot

