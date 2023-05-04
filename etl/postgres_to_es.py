import logging
import time

from postgres_tools.postgres_exctractor import PostgresExtractor
from elasticsearch_tools.es_loader import ElasticsearchLoader
from utils.states import State, RedisStorage
from config import TIME_INTERVAL_SECONDS, redis_settings
from redis import Redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    repeats = 0
    while True:
        try:
            logger.info(f"Starting data extraction and loading process. Repeats: {repeats}")
            es_loader = ElasticsearchLoader()
            radis_ = Redis(**redis_settings.dict())
            storage = RedisStorage(radis_)
            state = State(storage)

            with PostgresExtractor(state=state) as extractor:
                extractor_funcs = {
                    'genres': extractor.fetch_genres,
                    'persons': extractor.fetch_persons,
                    'movies': extractor.get_all_updated_data,
                }
                for index_name, func_extract in extractor_funcs.items():
                    for chunk in func_extract():
                        logger.info(f"Loading {len(chunk)} records into Elasticsearch, {index_name=}")
                        es_loader.load_data(chunk, index_name)
                        logger.info(f"Loaded {len(chunk)} records into Elasticsearch, {index_name=}")

            logger.info("Data extraction and loading process completed")
        except Exception as e:
            logger.exception(f"An error occurred during data extraction and loading process: {e}")
        finally:
            time.sleep(TIME_INTERVAL_SECONDS)
            repeats += 1


if __name__ == '__main__':
    main()
