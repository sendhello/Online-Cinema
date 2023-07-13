import logging

from elastic_transport import NodeConfig, Transport
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from schemas import Genre, Index, Movie, Person
from utils import backoff


logger = logging.getLogger(__name__)


class ElasticsearchLoader:
    def __init__(self, host: str, port: str, ssl: bool):
        self.client: Elasticsearch = self.__get_connect(host, port, ssl)

    @backoff()
    def __ping(self, node_config) -> None:
        """Проверка соединения с ES

        Пробует соединиться с ES, если не получается - бросает исключение,
        которое перехватывается backoff
        """
        transport = Transport([node_config])
        node = transport.node_pool.get()
        node.perform_request('GET', '/')

    @backoff()
    def __get_connect(self, host: str, port: str, ssl: bool) -> Elasticsearch:
        protocol = 'https' if ssl else 'http'

        node_config = NodeConfig(protocol, host, int(port))
        client = Elasticsearch([node_config])
        self.__ping(node_config)

        return client

    @backoff()
    def __bulk(self, actions):
        bulk(self.client, actions)

    @staticmethod
    def __create_action(model: Movie | Genre | Person, index_name: str) -> dict:
        """Генерация action для отправки bulk запроса в Elasticsearch."""
        index = Index(
            _index=index_name,
            _id=model.id,
            _source=model.dict(),
        )
        return index.dict(by_alias=True)

    @backoff()
    def create_index(self, index_name: str, index: dict) -> None:
        """Создание нового индекса в Elasticsearch если его еще не существует."""

        if self.client.indices.exists(index=index_name):
            return None

        self.client.indices.create(index=index_name, **index)
        logger.info(f'Index {index_name} created')

    @backoff()
    def create_indexes(self, indexes: dict[str, dict]) -> None:
        """Create news indexes in Elasticsearch."""

        for index_name, index in indexes.items():
            print(f"Creating {index_name}...")
            self.create_index(index_name, index)

    def load_movies(self, movies: list[Movie]):
        actions = [self.__create_action(movie, 'movies') for movie in movies]
        self.__bulk(actions)
        logger.info(f"Sent {len(movies)} movies to index")

    def load_genres(self, genres: list[Genre]):
        actions = [self.__create_action(genre, 'genres') for genre in genres]
        self.__bulk(actions)
        logger.info(f"Sent {len(genres)} genres to index")

    def load_people(self, people: list[Person]):
        actions = [self.__create_action(person, 'persons') for person in people]
        self.__bulk(actions)
        logger.info(f"Sent {len(people)} persons to index")
