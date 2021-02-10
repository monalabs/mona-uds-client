# Mona's Unix Domain Socket client code

This repository contains all Mona python client for UDS code. The main package
is under the dir "client", and is published to PyPi as "mona-uds-client".

The Mona UDS client requires a Mona Agent deployed locally in order to run. Other
packages contain required information about how to install the Mona Agent in 
different environments and are published separately.

With any issues please email itai@monalabs.io.

# Example use:

Example code can be found in client/mona_uds_client_test.py.

In a nutshell, after installing the PyPi package:
$ pip install mona_uds_client

This is the common use:

```
from mona_uds_client.mona_uds_client import MonaUdsClient, MonaSingleMessage

# Use User ID as supplied by Mona team here.
client = MonaUdsClient("test_user")

# Use relevant context ID as defined in Mona configuration.
context_class = "MY_CONTEXT"

# Export a batch of two messages to Mona.
message1 = {"x": 1, "s": "some_str", "l": ["a"], "o": {"k": ["v1", "v2"]}
message2 = {"x": 2, "s": "another_str", "l": ["b"], "o": {"k": ["v3", "v4"]}

# Actual export
client.export(
    [
        MonaSingleMessage(
            contextId="context_id1",
            message=message1,
            arcClass=context_class,
        ),  # No export timestamp means use current time
        MonaSingleMessage(
            contextId="context_id2",
            message=message2,
            arcClass=context_class,
            exportTimestamp=1234567890
        ),
    ]
)
```

## Uploading new version to PyPI
The main reference to follow to do that is on:
https://packaging.python.org/tutorials/packaging-projects/

### Prerequisites:
1. Register on PyPI with your mona email: https://pypi.org/
2. Ask itai@monalabs.io or nemo@monalabs.io to add you as collaborator
3. If not installed, install twine: $ python3 -m pip install --user --upgrade twine
4. If not installed, install build tools: $ python3 -m pip install --user --upgrade setuptools wheel

### Actual upload:
1. Change version number under setup.py
2. If a new dependency is required, add it under setup.py under "install_requires"
3. Build new version: 
```
$ python3 setup.py sdist bdist_wheel
```
4. Upload new version (can change '*' to actual version):
```
$ python -m twine upload dist/*
```