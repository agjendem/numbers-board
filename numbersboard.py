#!/usr/bin/env python3
import signal
import sys
import time
import getopt
from random import choice
from typing import Dict, Optional
from rpi_7segment import Segments
from ledstrip import LedStrip
from humio_client import HumioClient, QueryConfig
from timeloop import Timeloop
from datetime import timedelta


def update_query_cache(data: str, query: QueryConfig, query_results):
    # Update query results cache with new results for this query:
    current_value = None if query not in query_results else query_results[query]
    if current_value == data:
        print(f'Query {query.get_query_id()} executed and result is still the same: {data}')
    else:
        print(f'Query {query.get_query_id()} executed and result has changed from {current_value} to {data}')
        query_results[query] = data


def execute_query(query: QueryConfig, humio_client: HumioClient, query_results: dict):
    try:
        # Run the query, and pass along the results-object as kwargs,
        # that will further be passed along to the callback once finished
        humio_client.run_search(query, update_query_cache, query_results=query_results)
    except Exception as e:
        # Catch all, to prevent threads slowly dying:
        print(f'Query execution of {query.get_query_id()} failed with error: {e}')


def update_visualizations(segments: Segments, ledstrip: LedStrip, query_results: Dict[QueryConfig, str]):
    random_query: Optional[QueryConfig] = None
    try:
        # Pick a random result, among those we have data for in the cache:
        if len(query_results) > 0:
            random_query: Optional[QueryConfig] = choice(list(query_results.keys()))
            cached_result: str = query_results.get(random_query)

            colors = random_query.get_color().split(',')
            print(f'Rendering ledstrip with colors: {int(colors[0])}, {int(colors[1])}, {int(colors[2])}, {int(colors[3])}')
            if ledstrip is not None:
                ledstrip.color(int(colors[0]), int(colors[1]), int(colors[2]), int(colors[3]))

            # Hack: Right align as there's a bug in the display library for numbers, currently
            print(f'Displaying "{cached_result}" on segments')
            if segments is not None:
                segments.show(f'{cached_result:>7}')
        else:
            print("There is currently no data to display")
            if ledstrip is not None:
                ledstrip.all_white()
            if segments is not None:
                segments.show("No data, booting.")
    except Exception as e:
        # Catch all, to prevent threads slowly dying:
        print(f'Update of visualizations for query {random_query.get_query_id() if random_query is not None else "None"} failed with error: {e}')


def run_board(segments, ledstrip, timeloop, update_frequency):
    humio_client = HumioClient()
    query_results = {}

    # Add all queries defined in ENV as timed jobs:
    for query in humio_client.get_queries():
        print(f'Query with id {query.get_query_id()} registered as background job with interval {query.get_interval()}s')
        timeloop._add_job(execute_query,
                          query=query,
                          humio_client=humio_client,
                          query_results=query_results,
                          interval=timedelta(seconds=query.get_interval()))

    # Add visualization update as a timed job:
    timeloop._add_job(update_visualizations,
                      ledstrip=ledstrip,
                      segments=segments,
                      query_results=query_results,
                      interval=timedelta(seconds=update_frequency))

    timeloop.start()

    # Update displays/strip with info, while waiting for data:
    update_visualizations(segments, ledstrip, query_results)

    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            timeloop.stop()
            break


if __name__ == '__main__':
    tl = Timeloop()

    disable_hardware = False
    update_frequency = 15
    name = sys.argv[0]

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdu:", ["help", "disable-hardware", "update-frequency="])
    except getopt.GetoptError:
        print(f'{name} -d -u 15')
        print(f'{name} --disable-hardware --update-frequency 15')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print(f'{name} -d -u 15')
            print(f'{name} --disable-hardware --update-frequency 15')
            sys.exit()
        elif opt in ('-d', '--disable-hardware'):
            disable_hardware = True
        elif opt in ('-u', '--update-frequency'):
            update_frequency = int(arg)

    if disable_hardware:
        _segments = None
        _ledstrip = None
    else:
        _segments = Segments(offline=False)
        _ledstrip = LedStrip()

    def signal_handler(sig, frame):
        # Cleanup if killed/interrupted:
        if _segments is not None:
            _segments.shutdown()
        tl.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    run_board(_segments, _ledstrip, tl, update_frequency)
