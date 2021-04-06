#!/usr/bin/dumb-init /bin/sh

uid=${SOCKET_UID:-1000}


deluser fluent > /dev/null 2>&1
# (re)add the fluent user with $SOCKET_UID
adduser --disabled-password --uid ${uid} --home /home/fluent fluent > /dev/null 2>&1

# chown data folders
chown -R fluent /home/fluent > /dev/null 2>&1
chown -R fluent /fluentd > /dev/null 2>&1
chown -R fluent /tmp/buffer > /dev/null 2>&1

gosu fluent fluentd -c /fluentd/etc/${FLUENTD_CONF} -p /fluentd/plugins $FLUENTD_OPT "$@"
