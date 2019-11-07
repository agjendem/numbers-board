#!/usr/bin/env python3
import humiocore
import time
import signal
import sys


class HumioClient:
    def __init__(self):
        self.env_config = humiocore.loadenv()
        humiocore.setup_excellent_logging('INFO')

    def _fetch_result(self, query, span):
        client = humiocore.HumioAPI(token=self.env_config['token'], base_url=self.env_config['base_url'])

        start = humiocore.utils.parse_ts(f'{span}@s')
        end = humiocore.utils.parse_ts('@s')

        return client.streaming_search(query=query,
                                       repos=[self.env_config['repository']],
                                       start=start,
                                       end=end)

    def run_search(self, query_id, span, interval_seconds, callback):
        last_result = None
        while True:
            current_result = next(self._fetch_result(self.env_config[query_id], span))
            if len(current_result) != 0 \
                    and (last_result is None
                         or current_result != last_result):
                last_result = current_result
                callback(last_result['result'])

            time.sleep(interval_seconds)


if __name__ == '__main__':

    def signal_handler(sig, frame):
        # Cleanup if killed/interrupted:
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    def humio_callback(data):
        print(data)
    humio_client = HumioClient()
    humio_client.run_search('query_last_transfer', '-60m', 10, humio_callback)
