#!/usr/bin/env python3
import time
import signal
import sys
from rpi_7segment import Segments
from humio_client import HumioClient


def run_board(segments):
    def humio_callback(data):
        print(data)
        segments.show("Siste")
        segments.show(data)

    humio_client = HumioClient()
    queries = ['query_accounts_created', 'query_payments', 'query_number_of_logins', 'query_gold_home']
    while True:
        for query in queries:
            humio_client.run_search(query, humio_callback)
            time.sleep(10)


if __name__ == '__main__':
    _segments = Segments(offline=False)

    def signal_handler(sig, frame):
        # Cleanup if killed/interrupted:
        _segments.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    run_board(_segments)
