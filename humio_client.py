#!/usr/bin/env python3
import humiocore
import time
import signal
import sys


def _fetch_last_transfer_search(env_config):
    client = humiocore.HumioAPI(**env_config)

    span = env_config['query_span']
    start = humiocore.utils.parse_ts(f'{span}@m')
    end = humiocore.utils.parse_ts('@m')

    return client.streaming_search(query=env_config['query'],
                                   repos=[env_config['repository']],
                                   start=start,
                                   end=end)


def run_search(callback):
    humiocore.setup_excellent_logging('INFO')
    env_config = humiocore.loadenv()

    last_result = None
    while True:
        current_result = next(_fetch_last_transfer_search(env_config))
        if len(current_result) != 0 \
                and (last_result is None
                     or current_result["timestamp"] != last_result["timestamp"]):
            last_result = current_result
            callback(last_result['result'])

        time.sleep(int(env_config['query_interval_seconds']))


if __name__ == '__main__':

    def signal_handler(sig, frame):
        # Cleanup if killed/interrupted:
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    def humio_callback(data):
        print(data)
    run_search(humio_callback)
