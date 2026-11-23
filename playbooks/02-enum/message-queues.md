# Message queue enumeration

## Recognise the services
sudo nmap -Pn -sV -p 1883,8883,5671,5672,61616,8161,15672 <TargetIP>
sudo nmap -Pn -p 1883 --script mqtt-subscribe <TargetIP>
sudo nmap -Pn -p 5672 --script amqp-info <TargetIP>
- [ ] 1883 and 8883 MQTT, 5672 and 5671 AMQP, 61616 ActiveMQ OpenWire, 8161 ActiveMQ web, 15672 RabbitMQ management
- [ ] amqp-info gives product, version, platform, mechanisms and capabilities before any credential is tried
- [ ] mqtt-subscribe listens for five seconds by default; topics and payloads reviewed for data and the $SYS broker version
- [ ] Exact product and version through searchsploit and the vendor advisories, then :Pb public-exploits only when the conditions match

## MQTT access
Anonymous, then with every credential found:
mosquitto_sub -h <TargetIP> -p 1883 -t '#' -v -W 5
mosquitto_sub -h <TargetIP> -p 1883 -u '<Username>' -P '<Password>' -t '#' -v -W 5
mosquitto_sub -h <TargetIP> -p 1883 -t '$SYS/#' -v -W 5
TLS on 8883, with THE-CA changed to the CA certificate path:
mosquitto_sub -h <TargetIP> -p 8883 --cafile THE-CA -t '#' -v -W 5
- [ ] Anonymous subscription works: retained messages and live payloads can hold credentials, commands and internal names
- [ ] Not authorised for one topic does not rule out another: compare # with $SYS/# and the ACL found later
- [ ] The CA verified; --insecure is not a substitute for understanding why certificate verification failed
- [ ] Subscribe only: no publish, retained-message removal or clear operation from this checklist

## RabbitMQ and AMQP access
Try guest/guest once, then the credentials found:
curl -sS -u guest:guest http://<TargetIP>:15672/api/whoami
curl -sS -u '<Username>:<Password>' http://<TargetIP>:15672/api/whoami
curl -sS -u '<Username>:<Password>' http://<TargetIP>:15672/api/overview
- [ ] RabbitMQ refuses remote guest/guest by default, so its refusal is not proof that guest was changed or that AMQP is closed
- [ ] overview gives the RabbitMQ and Erlang versions, listeners and management details for version triage
With management access, export the definitions read-only:
curl -sS -u '<Username>:<Password>' http://<TargetIP>:15672/api/definitions -o rabbitmq-definitions.json
- [ ] rabbitmq-definitions.json treated as a credential artifact: password hashes, users, permissions, vhosts, queues, exchanges and bindings
- [ ] A 403 here can mean missing management tags; do not publish or consume through the HTTP API just to prove queue access

## ActiveMQ access
Anonymous first, then admin/admin once and every credential found:
curl -sS -i http://<TargetIP>:8161/admin/
curl -sS -u admin:admin http://<TargetIP>:8161/admin/
curl -sS -u '<Username>:<Password>' http://<TargetIP>:8161/admin/
- [ ] The web console shows broker names, queues, topics and connections; read only, with nothing sent or deleted
- [ ] OpenWire on 61616 and the web console have separate configuration: web access alone does not prove broker permissions
- [ ] The version in the broker-start line in data/activemq.log checked against the same exact release

## Mosquitto artifacts
On the broker host, including files loaded through include_dir:
sudo grep -nE '^(listener|allow_anonymous|listener_allow_anonymous|password_file|acl_file|psk_file|persistence|persistence_location|persistence_file|include_dir|log_dest)' /etc/mosquitto/mosquitto.conf /etc/mosquitto/conf.d/*.conf 2>/dev/null
sudo ls -la /etc/mosquitto /var/lib/mosquitto
- [ ] Files named by password_file, acl_file and psk_file read for password hashes, topic permissions and pre-shared keys
- [ ] persistence_location and persistence_file locate mosquitto.db: preserve it for offline review of retained and queued data
- [ ] Version 1.6 and earlier could allow anonymous remote access by default; current versions do not unless no listener is configured, and then only locally

## RabbitMQ artifacts
On a Debian or Ubuntu broker host:
sudo grep -nE 'default_user|default_pass|loopback_users|auth_mechanisms|definitions|listeners|ssl_options|management' /etc/rabbitmq/rabbitmq.conf /etc/rabbitmq/advanced.config 2>/dev/null
- [ ] default_user and default_pass, remote guest access through loopback_users, authentication backends and TLS settings recorded
- [ ] definitions.local.path leads to the JSON artifact; advanced.config can hold settings absent from rabbitmq.conf
- [ ] Password hashes and secrets in definitions and config files kept as sensitive loot, not pasted into notes meant for sharing

## ActiveMQ artifacts
On the broker host, with its install folder as ACTIVEMQ-HOME:
grep -nE 'transportConnector|authenticationUser|authorizationEntry|networkConnector|userName|password|anonymousAccessAllowed' ACTIVEMQ-HOME/conf/activemq.xml
cat ACTIVEMQ-HOME/conf/jetty-realm.properties ACTIVEMQ-HOME/conf/users.properties ACTIVEMQ-HOME/conf/groups.properties ACTIVEMQ-HOME/conf/credentials.properties ACTIVEMQ-HOME/conf/login.config 2>/dev/null
- [ ] Transport connectors, anonymous access, users, groups, queue and topic permissions, and broker-to-broker credentials reviewed
- [ ] jetty-realm.properties covers the web console; users.properties and groups.properties cover JAAS broker authentication
- [ ] data/activemq.log and the broker's data directory preserved for offline artifact review
