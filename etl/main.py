import logging
import time
from datetime import datetime, timezone

from constants import ExtractObject
from es_schemas import INDEXES
from extractor import PostgresExtractor
from loader import ElasticsearchLoader
from redis import Redis
from settings import settings
from state import JsonFileStorage, RedisStorage, State
from transformator import Transformator


logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    if settings.USE_REDIS:
        redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        storage = RedisStorage(redis)
    else:
        storage = JsonFileStorage(settings.JSON_STORAGE_FILE)

    state = State(storage)
    loader = ElasticsearchLoader(
        host=settings.ES_HOST, port=settings.ES_PORT, ssl=settings.ES_SSL
    )
    loader.create_indexes(INDEXES)

    while True:
        state.set_state('start_time', datetime.now(timezone.utc).isoformat())

        with PostgresExtractor(settings.PG_DSN) as postgres_extractor:
            for entity_type, source_entities in postgres_extractor.get_updated_entities(
                state
            ):
                if entity_type == ExtractObject.MOVIES:
                    transformator = Transformator(source_movies=source_entities)
                    movies = transformator.get_movies()
                    loader.load_movies(movies)
                elif entity_type == ExtractObject.GENRES:
                    transformator = Transformator(source_genres=source_entities)
                    genres = transformator.get_genres()
                    loader.load_genres(genres)
                elif entity_type == ExtractObject.PEOPLE:
                    transformator = Transformator(source_people=source_entities)
                    people = transformator.get_people()
                    loader.load_people(people)

        logger.info(f'Sleeping {settings.SLEEP_TIME} sec...')
        time.sleep(settings.SLEEP_TIME)
