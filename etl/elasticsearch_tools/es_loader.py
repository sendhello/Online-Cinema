import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.helpers import BulkIndexError

from config import elasticsearch_settings, CHUNK_SIZE
from utils.backoff import backoff
from elasticsearch_tools.es_index import INDEXES
from psycopg2.extras import RealDictCursor

from typing import Iterable, Type


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ElasticsearchLoader:
    indexes = INDEXES

    def __init__(self, es_config=elasticsearch_settings,
                 batch_size: int = CHUNK_SIZE):
        """
        Initialize the ElasticsearchLoader instance.

        :param es_config: Dictionary containing the Elasticsearch configuration settings.
        :param batch_size: Number of records to be processed in a single batch.
        """

        self.settings = es_config
        self.client = self.get_connect()
        self.batch_size = batch_size
        self.recreate_index('movies')

    @backoff()
    def get_connect(self) -> Elasticsearch:
        client = Elasticsearch(self.settings.get_hosts())
        return client

    def recreate_index(self, index_name: str) -> None:
        """
        Delete the existing Elasticsearch index and create a new one with the same name.
        """
        if self.client.indices.exists(index=index_name):
            self.client.indices.delete(index=index_name)
        self.create_index(index_name)

    def create_index(self, index_name: str) -> bool:
        """
        Create a new Elasticsearch index if it doesn't already exist.

        :return: True if the index is successfully created or already exists, False otherwise.
        """
        if self.client.indices.exists(index=index_name):
            return True
        response = self.client.indices.create(index=index_name, **self.indexes[index_name])
        return response.get('acknowledged', False)

    def process_batch(self, batch: list[RealDictCursor] | list[dict], index_name: str) -> list[dict]:
        """
        Process a batch of records and prepare them for indexing in Elasticsearch.

        :param batch: List of records to be processed.
        :param index_name: Name of the Elasticsearch index to be used.
        :return: List of prepared records for indexing.
        """

        actions = []
        for row in batch:
            row_converted = dict(row)
            action = {
                "_index": index_name,
                "_id": row_converted["id"],
                "_source": row_converted,
            }
            actions.append(action)
        return actions

    def load_data_chunk(self, chunk: list[RealDictCursor] | list[dict], index_name: str) -> None:
        """
        Load a chunk of records into Elasticsearch.

        :param chunk: List of records to be loaded.
        :param index_name: Name of the Elasticsearch index to be used.
        """

        actions = self.process_batch(chunk, index_name)
        try:
            bulk(self.client, actions)
        except BulkIndexError as e:
            logger.exception(e.errors)
        logger.info(f"Loaded {len(actions)} rows to Elasticsearch.")

    def load_data(self, data: Iterable[RealDictCursor] | Iterable[dict], index_name: str) -> None:
        """
        Load data into Elasticsearch using the specified batch size.

        :param data: Iterable containing the records to be loaded.
        :param index_name: Name of the Elasticsearch index to be used.
        """

        batch = []

        for row in data:
            batch.append(row)
            if len(batch) >= self.batch_size:
                self.load_data_chunk(batch, index_name)
                batch = []

        if batch:
            self.load_data_chunk(batch, index_name)


if __name__ == '__main__':
    es_loader = ElasticsearchLoader()
