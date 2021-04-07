"""
Simple example for how to run mona_uds_client.py
"""
import time
import logging
from os import environ
from uuid import uuid1
from random import random

from mona_uds_client import MonaUdsClient, MonaSingleMessage

NUM_BATCHES = 40


def actual_run():
    logging.getLogger().setLevel(logging.INFO)
    client = MonaUdsClient("test_mona_user_id")
    logging.getLogger().setLevel(environ.get("LOGLEVEL", logging.INFO))
    logging.info("starting client test")
    start_time = time.time()
    test_batches = [
        [{f"field_{i}": random() for i in range(150)} for _ in range(50)]  # nosec
        for _ in range(NUM_BATCHES)
    ]
    successes = 0
    for ind, batch in enumerate(test_batches):
        messages = [
            MonaSingleMessage(
                contextId=str(uuid1()),
                message=msg,
                arcClass="TEST_CLASS",
                exportTimestamp=1234567890,
            )
            for msg in batch
        ]
        if client.export(messages):
            successes += 1
        else:
            logging.warning(f"failed on index {ind}")

    logging.info(f"sent messges: {successes}/{NUM_BATCHES}")
    logging.info(f"took {time.time() - start_time} sec")


if __name__ == "__main__":
    actual_run()
