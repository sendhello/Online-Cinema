import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Generator, Optional

from config import postgres_settings, CHUNK_SIZE
from utils.states import State, JsonFileStorage
from utils.backoff import backoff
from postgres_tools.sql_query_load import (
    get_updated_ids_query, get_films_by_related_ids_query, get_film_data_query
)


class PostgresExtractor:
    def __init__(self, state: State, chunk_size: int = CHUNK_SIZE, connection_params: Optional[dict] = None):
        self.connection_params = postgres_settings.dict() if connection_params is None else connection_params

        self.state = state
        self.chunk_size = chunk_size
        self.conn = None

        self.tables_names = ("film_work", "person", "genre")
        self.related_tables_names = ("person", "genre")

    @backoff()
    def __enter__(self):
        """
        Enter the context manager, establish the connection to the PostgreSQL database.

        :return: The PostgresExtractor instance.
        """
        self.conn = psycopg2.connect(**self.connection_params, cursor_factory=RealDictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager, close the connection to the PostgreSQL database.
        """
        if self.conn is not None:
            self.conn.close()

    @backoff()
    def fetch_updated_data(self, table_name: str) -> Generator[list[str], None, None]:
        """
        Fetch updated records' IDs from the given table_name.

        :param table_name: Name of the table to fetch updated records from.
        :return: A generator yielding lists of updated record IDs.
        """
        last_updated_at = self.state.get_state(f'{table_name}_last_updated_at') or '1970-01-01 00:00:00'
        query = get_updated_ids_query(table_name, last_updated_at, self.chunk_size)

        with self.conn.cursor() as cursor:
            cursor.execute(query)
            while True:
                data = cursor.fetchmany(self.chunk_size)
                if not data:
                    break

                formatted_dt = data[-1]['updated_at'].strftime('%Y-%m-%d %H:%M:%S.%f %z')
                data = [row['id'] for row in data]
                yield data
                self.state.set_state(f'{table_name}_last_updated_at', formatted_dt)

    def fetch_related_film_works(self, table_name: str, related_ids: list[str]) -> Generator[list[str], None, None]:
        """
        Fetch related film_works' IDs based on the given table_name and related_ids.

        :param table_name: Name of the related table (genre or person).
        :param related_ids: List of related record IDs.
        :return: A generator yielding lists of related film_work IDs.
        """
        query = get_films_by_related_ids_query(table_name, related_ids, limit=self.chunk_size)
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            while True:
                data = cursor.fetchmany(self.chunk_size)
                if not data:
                    break
                data = [row['id'] for row in data]
                yield data

    def fetch_film_work_details(self, film_work_ids: list[str]) -> Generator[list[str], None, None]:
        """
        Fetch details of film_work records based on the given film_work_ids.

        :param film_work_ids: List of film_work IDs.
        :return: A generator yielding lists of film_work details.
        """
        query = get_film_data_query(film_work_ids, limit=self.chunk_size)
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            while True:
                data = cursor.fetchmany(self.chunk_size)
                if not data:
                    break
                yield data

    def get_related_data(self, table_name: str, relates_ids: list[str]) -> list[str]:
        """
        Get a list of related film_work IDs based on the given table_name and relates_ids.

        :param table_name: Name of the related table (genre or person).
        :param relates_ids: List of related record IDs.
        :return: A list of related film_work IDs.
        """
        related_film_work_ids = set()
        related_film_works = self.fetch_related_film_works(table_name, relates_ids)
        for data_related_chunk in related_film_works:
            for film_work in data_related_chunk:
                related_film_work_ids.add(film_work)
        return list(related_film_work_ids)

    @backoff()
    def get_all_updated_data(self) -> Generator[list[str], None, None]:
        """
        Fetch all updated data from the tables film_work, person, and genre.

        :return: A generator yielding lists of updated records.
        """
        for table_name in self.tables_names:
            for data_updated_chunk in self.fetch_updated_data(table_name):
                if table_name in self.related_tables_names:
                    related_film_work_ids = self.get_related_data(table_name, data_updated_chunk)
                    film_work_details = self.fetch_film_work_details(related_film_work_ids)
                    for film_work_data_chunk in film_work_details:
                        yield film_work_data_chunk
                else:
                    yield from self.fetch_film_work_details(data_updated_chunk)


def main():
    from etl.elasticsearch_tools.es_loader import ElasticsearchLoader
    es_loader = ElasticsearchLoader()
    storage = JsonFileStorage("state.json")
    state = State(storage)

    with PostgresExtractor(state, postgres_settings.dict()) as extractor:
        for chunk in extractor.get_all_updated_data():
            es_loader.load_data(chunk)


if __name__ == '__main__':
    main()
