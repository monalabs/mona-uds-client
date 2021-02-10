# ----------------------------------------------------------------------------
#    Copyright 2021 MonaLabs.io
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
# ----------------------------------------------------------------------------
"""
The main Mona python Unix Domain Sockets client module. Exposes all functions relevant
for client exporting mechanisms.

TODO(nemo): This is an temporary solution until the new mona-py-sdk will be launched
            and be able to support UDS, with a superset of the features offered here.
"""
import socket
import logging
import threading
from os import environ
from typing import List
from dataclasses import dataclass

import msgpack


def _get_boolean_value_for_env_var(env_var, default_value):
    return {"True": True, "true": True, "False": False, "false": False}.get(
        environ.get(env_var), default_value
    )


class MonaExportException(Exception):
    pass


class MonaValidationException(Exception):
    pass


# Designated User ID as supplied by Mona
DEFAULT_MONA_USER_ID = environ.get("MONA_USER_ID", None)

# The following two env vars must be synced with the Mona agent.
DEFAULT_UDS_SERVER_ADDRESS = environ.get(
    "MONA_UDS_SERVER_ADDRESS", "/uds/mona/mona.sock"
)
DEFAULT_UDS_SERVER_REPLICAS = int(environ.get("MONA_UDS_SERVER_REPLICAS", 3))
MONA_AGENT_TAG = environ.get("MONA_AGENT_TAG", "mona.client")

SHOULD_RAISE_EXCEPTIONS = (
    _get_boolean_value_for_env_var("MONA_SHOULD_RAISE_EXCEPTIONS", False),
)
SHOULD_AVOID_LOGGING = _get_boolean_value_for_env_var("MONA_SHOULD_AVOID_LOGGING", True)
MONA_LOGGING_LEVEL = environ.get("MONA_LOGGING_LEVEL", "WARNING")

LOGGER = logging.getLogger("mona-logger")
if SHOULD_AVOID_LOGGING:
    LOGGER.disabled = True
else:
    LOGGER.setLevel(MONA_LOGGING_LEVEL)

# Currently Mutex allows only one export at a time.
# TODO(nemo): Allow multiple concurrent exports if needed.
UDS_SOCKET_MUTEX = threading.Lock()

CURRENT_SERVER_INDEX = 0
SERVER_SELECTOR_MUTEX = threading.Lock()

USER_ID_FIELD_NAME = "userId"
MESSAGES_FIELD_NAME = "messages"


def _raise(error_type, msg):
    if SHOULD_RAISE_EXCEPTIONS:
        raise error_type(msg)


def _select_server(base_address, uds_server_replicas):
    if uds_server_replicas <= 1:
        return base_address
    # Add suffix to the address for the replica number.
    with SERVER_SELECTOR_MUTEX:
        global CURRENT_SERVER_INDEX
        server_address = base_address + str(CURRENT_SERVER_INDEX)
        CURRENT_SERVER_INDEX = (CURRENT_SERVER_INDEX + 1) % uds_server_replicas
        return server_address


@dataclass
class MonaSingleMessage:
    """
    Class for keeping properties for a single Mona Message.

    Attributes:
        contextId (str): (Optional) context ID for the message to be indexed on. If not
            supplied, Mona will assign a uuid for it, but it will be impossible to
            export more data to.
        message (dict): (Required) JSON serializable dict with properties to send about
            the context ID.
        arcClass (str): (Required) context classes are defined in the Mona Config
            and define the schema of the contexts.
        exportTimestamp (int): (Optional) Timestamp in seconds since epoch to set for
            the event of the context Id. If not supplied, current time is used.
    """

    contextId: str
    message: dict
    arcClass: str
    exportTimestamp: int


class MonaUdsClient:
    """
    A Mona UDS thread safe client instance.
    Use export() to send data to Mona through UDS.

    Parameters:
    mona_user_id Designated User ID as supplied by Mona.
    uds_server_address Address on the file system designated for Mona's data transfer.
    """

    def __init__(
        self,
        mona_user_id=DEFAULT_MONA_USER_ID,
        uds_server_address=DEFAULT_UDS_SERVER_ADDRESS,
        uds_server_replicas=DEFAULT_UDS_SERVER_REPLICAS,
    ):
        self._user_id = mona_user_id
        self._uds_server_address = uds_server_address
        self._uds_server_replicas = uds_server_replicas

    def export(self, messages: List[MonaSingleMessage]):
        """
        Sends a batch of messages to Mona's servers, through a separately deployed
        Mona Agent.

        Expects to get an iterable of valid MonaSingleMessages to export.

        May Raise MonaExportException or MonaValidationException if allowed by
        MONA_SHOULD_RAISE_EXCEPTIONS env var.

        Returns bool True if export succeeded or False if failed AND exceptions are
        forbidden.
        """
        try:
            export_data = self._create_rest_api_request_data_msgpack_str(messages)
        except TypeError as err:
            err_msg = f"Mona failed when trying to serialize data: {err}"
            LOGGER.warning(err_msg)
            _raise(MonaValidationException, err_msg)
            return False

        try:
            self._send_data_by_uds(export_data)
        except Exception as err:
            err_msg = f"Mona failed when trying to write data into UDS socket: {err}"
            LOGGER.warning(err_msg)
            _raise(MonaExportException, err_msg)
            return False

        LOGGER.info(f"Exported {len(messages)} items successfully")
        return True

    def _create_rest_api_request_data_msgpack_str(self, messages):
        # The structure of the message is according to the format defined here:
        # https://github.com/fluent/fluentd/blob/master/lib/fluent/plugin/in_unix.rb#L94
        export_data = [
            MONA_AGENT_TAG,
            0,  # Export time 0 tells agent to use current time for internal purposes.
            {
                USER_ID_FIELD_NAME: self._user_id,
                MESSAGES_FIELD_NAME: [message.__dict__ for message in messages],
            },
        ]
        return msgpack.dumps(export_data)

    def _send_data_by_uds(self, export_data):
        uds_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        with UDS_SOCKET_MUTEX:
            uds_socket.connect(
                _select_server(self._uds_server_address, self._uds_server_replicas)
            )
            try:
                uds_socket.sendall(export_data)
            finally:
                uds_socket.close()
