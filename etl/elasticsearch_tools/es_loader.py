import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.helpers import BulkIndexError

from config import elasticsearch_settings, CHUNK_SIZE
from utils.backoff import backoff
from elasticsearch_tools.es_index import ES_INDEX
from psycopg2.extras import RealDictCursor

from typing import Iterable, Type


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ElasticsearchLoader:
    es_index = ES_INDEX

    def __init__(self, es_config=elasticsearch_settings,
                 index_name: str = 'movies',
                 batch_size: int = CHUNK_SIZE):
        """
        Initialize the ElasticsearchLoader instance.

        :param es_config: Dictionary containing the Elasticsearch configuration settings.
        :param index_name: Name of the Elasticsearch index to be used.
        :param batch_size: Number of records to be processed in a single batch.
        """

        self.settings = es_config
        self.client = self.get_connect()
        self.index_name = index_name
        self.batch_size = batch_size
        self.create_index()

    @backoff()
    def get_connect(self) -> Elasticsearch:
        client = Elasticsearch(self.settings.get_hosts())
        return client

    def recreate_index(self) -> None:
        """
        Delete the existing Elasticsearch index and create a new one with the same name.
        """

        self.client.indices.delete(index="movies")
        self.create_index()

    def create_index(self) -> bool:
        """
        Create a new Elasticsearch index if it doesn't already exist.

        :return: True if the index is successfully created or already exists, False otherwise.
        """

        if self.client.indices.exists(index=self.index_name):
            return True
        response = self.client.indices.create(index=self.index_name, **self.es_index)
        return response.get('acknowledged', False)

    def process_batch(self, batch: list[RealDictCursor] | list[dict]) -> list[dict]:
        """
        Process a batch of records and prepare them for indexing in Elasticsearch.

        :param batch: List of records to be processed.
        :return: List of prepared records for indexing.
        """

        actions = []
        for row in batch:
            row_converted = dict(row)
            action = {
                "_index": self.index_name,
                "_id": row_converted["id"],
                "_source": row_converted,
            }
            actions.append(action)
        return actions

    def load_data_chunk(self, chunk: list[RealDictCursor] | list[dict]) -> None:
        """
        Load a chunk of records into Elasticsearch.

        :param chunk: List of records to be loaded.
        """

        actions = self.process_batch(chunk)
        try:
            bulk(self.client, actions)
        except BulkIndexError as e:
            logger.exception(e.errors)
        logger.info(f"Loaded {len(actions)} rows to Elasticsearch.")

    def load_data(self, data: Iterable[RealDictCursor] | Iterable[dict]) -> None:
        """
        Load data into Elasticsearch using the specified batch size.

        :param data: Iterable containing the records to be loaded.
        """

        batch = []

        for row in data:
            batch.append(row)
            if len(batch) >= self.batch_size:
                self.load_data_chunk(batch)
                batch = []

        if batch:
            self.load_data_chunk(batch)


if __name__ == '__main__':
    es_loader = ElasticsearchLoader()
