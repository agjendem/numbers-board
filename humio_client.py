from typing import List

import humiocore


class QueryConfig:
    def __init__(self,
                 query_id: str,
                 repository: str,
                 query: str,
                 span: str,
                 interval: int,
                 color: str):
        self.query_id = query_id
        self.repository = repository
        self.query = query
        self.span = span
        self.interval: int = int(interval)
        self.color = color

    def get_query_id(self):
        return self.query_id

    def get_repository(self):
        return self.repository

    def get_query(self):
        return self.query

    def get_span(self):
        return self.span

    def get_interval(self):
        return self.interval

    def get_color(self):
        return self.color

    def __repr__(self) -> str:
        return (
            'QueryConfig('
            f'query_id={self.query_id!r}, '
            f'repository={self.repository!r}, '
            f'query={self.query!r}, '
            f'span={self.span!r}, '
            f'interval={self.interval!r}, '
            f'color={self.color!r}, '
        )


class HumioClient:
    def __init__(self):
        self.env_config = humiocore.loadenv()
        humiocore.setup_excellent_logging('INFO')

    def _fetch_result(self, query: QueryConfig):
        client = humiocore.HumioAPI(token=self.env_config['token'], base_url=self.env_config['base_url'])

        start = humiocore.utils.parse_ts(f'{query.get_span()}@s')
        end = humiocore.utils.parse_ts('@s')

        return client.streaming_search(query=query.get_query(),
                                       repos=[query.get_repository()],
                                       start=start,
                                       end=end)

    def run_search(self, query: QueryConfig, callback, *args, **kwargs):
        last_result = None
        current_result = next(self._fetch_result(query))
        if len(current_result) != 0 \
                and (last_result is None
                     or current_result != last_result):
            last_result = current_result

            # If the query has a column/field named 'result', we pick only that for display:
            if 'result' in last_result:
                callback(last_result['result'], query, *args, **kwargs)
            else:
                callback(last_result, query, *args, **kwargs)

    def get_queries(self) -> List[QueryConfig]:
        queries = []
        for query_id in [key.replace('_repository', '') for key in self.env_config.keys() if key.endswith('_repository')]:
            queries.append(QueryConfig(
                query_id=query_id,
                repository=self.env_config[f'{query_id}_repository'],
                query=self.env_config[query_id],
                span=self.env_config[f'{query_id}_span'],
                interval=self.env_config[f'{query_id}_interval_seconds'],
                color=self.env_config[f'{query_id}_color']
            ))
        return queries
