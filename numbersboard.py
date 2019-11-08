#!/usr/bin/env python3
import signal
import sys
from rpi_7segment import Segments
from ledstrip import LedStrip
from humio_client import HumioClient


def run_board(segments, ledstrip):
    def humio_callback(data, color):
        c = color.split(',')
        print(data)
        segments.show(data)
        ledstrip.color(c[0], c[1], c[2], c[3])

    humio_client = HumioClient()
    while True:
        humio_client.run_all(humio_callback)


if __name__ == '__main__':
    _segments = Segments(offline=False)
    _ledstrip = LedStrip()
    _ledstrip.all_white()

    def signal_handler(sig, frame):
        # Cleanup if killed/interrupted:
        _segments.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    run_board(_segments, _ledstrip)
