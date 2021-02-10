"""
Simple example for how to run mona_uds_client.py
"""
import time
import logging
from os import environ
from uuid import uuid1
from random import random

from mona_uds_client import MonaUdsClient, MonaSingleMessage


def actual_run():
    logging.getLogger().setLevel(logging.INFO)
    client = MonaUdsClient("test_mona_user_id")
    logging.getLogger().setLevel(environ.get("LOGLEVEL", logging.INFO))
    start_time = time.time()
    test_batches = [
        [{f"field_{i}": random() for i in range(150)} for _ in range(50)]  # nosec
        for _ in range(10)
    ]
    for batch in test_batches:
        messages = [
            MonaSingleMessage(
                contextId=str(uuid1()),
                message=msg,
                arcClass="TEST_CLASS",
                exportTimestamp=1234567890,
            )
            for msg in batch
        ]
        client.export(messages)

    logging.info("all messages sent!")
    logging.info(f"took {time.time() - start_time} sec")


if __name__ == "__main__":
    actual_run()
