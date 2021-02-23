# Mona UDS Agent

### Mona-UDS-Agent docker image
This docker image runs mona-uds-agent, built on top of FluentD.

##### You should use mona-uds-agent when:
1. You signed up on https://www.monalabs.io/getstarted and have a private endpoint to send your data to Mona
2. Your system runs on a docker orchestration platform such as Kubernetes and you wish to export data directly from it to Mona
3. You want to send your data through Unix Domain Sockets

##### How to run it:
The following environment variables are required:

* **MONA_USER_ID**: the user-id provided to you by Mona (can be found on dashboard.monalabs.io/configurations)

You can use the following YAML formatted file on Kubernetes. 
UDS agents have to be on all nodes from which data needs to be sent, that's why it's required to use DaemonSet.

```
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: mona-uds-agent
spec:
  selector:
    matchLabels:
      app: mona-uds-agent
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  template:
    metadata:
      labels:
        app: mona-uds-agent
    spec:
      initContainers:
        - name: uds-init
          imagePullPolicy: Always
          image: monalabs/mona-agent-uds-init:stable
          command: [ "sh", "./init.sh" ]
          volumeMounts:
            - name: uds-mona-socket
              mountPath: /var/run/mona
      containers:
        - name: mona-uds-agent
          imagePullPolicy: Always
          image: monalabs/mona-uds-agent:stable
          env:
            - name: MONA_USER_ID
              value: '<YOUR_PRIVATE_MONA_USER_ID>'
          resources:
            limits:
              cpu: '2'
              memory: '4G'
          volumeMounts:
            - mountPath: /var/run/mona/
              name: uds-mona-socket
      volumes:
        - name: uds-mona-socket
          hostPath:
            path: /var/run/mona-agent/
```

#### Deployment notes:
* Specifying MONA_USER_ID and using the YAML without any changes will result in the best performance.
  
* Adding SOCKET_UID env var to the DaemonSet YAML allows setting a specific UID in order to use a socket between mona-uds-agent and a container running mona-uds-client (which uses this UID). Default UID: 1000.
* Minimal requirement is 1 CPU, 2GB memory.
