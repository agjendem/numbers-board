#!/usr/bin/env python3
import time
import signal
import sys
from rpi_7segment import Segments
from humio_client import run_search


def run_board(segments):
    def humio_callback(data):
        print(data)
        segments.show(data)

    run_search(humio_callback)


if __name__ == '__main__':
    _segments = Segments(offline=False)

    def signal_handler(sig, frame):
        # Cleanup if killed/interrupted:
        _segments.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    run_board(_segments)
