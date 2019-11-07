#!/usr/bin/env python3
import humiocore
import signal
import sys


class HumioClient:
    def __init__(self):
        self.env_config = humiocore.loadenv()
        humiocore.setup_excellent_logging('INFO')

    def _fetch_result(self, query_id):
        client = humiocore.HumioAPI(token=self.env_config['token'], base_url=self.env_config['base_url'])
        query = self.env_config[query_id]
        span = self.env_config[f'{query_id}_span']
        repository = self.env_config[f'{query_id}_repository']

        start = humiocore.utils.parse_ts(f'{span}@s')
        end = humiocore.utils.parse_ts('@s')

        return client.streaming_search(query=query,
                                       repos=[repository],
                                       start=start,
                                       end=end)

    def run_search(self, query_id, callback):
        last_result = None
        current_result = next(self._fetch_result(query_id))
        if len(current_result) != 0 \
                and (last_result is None
                     or current_result != last_result):
            last_result = current_result
            callback(last_result['result'])


if __name__ == '__main__':

    def signal_handler(sig, frame):
        # Cleanup if killed/interrupted:
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    def humio_callback(data):
        print(data)
    humio_client = HumioClient()
    humio_client.run_search('query_last_transfer', humio_callback)
