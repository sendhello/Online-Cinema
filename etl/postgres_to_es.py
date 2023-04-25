import logging
import time

from postgres_tools.postgres_exctractor import PostgresExtractor
from elasticsearch_tools.es_loader import ElasticsearchLoader
from utils.states import State, JsonFileStorage
from config import TIME_INTERVAL_SECONDS


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    repeats = 0
    while True:
        try:
            logger.info(f"Starting data extraction and loading process. Repeats: {repeats}")
            es_loader = ElasticsearchLoader()
            storage = JsonFileStorage("state.json")
            state = State(storage)

            with PostgresExtractor(state=state) as extractor:
                for chunk in extractor.get_all_updated_data():
                    logger.info(f"Loading {len(chunk)} records into Elasticsearch")
                    es_loader.load_data(chunk)
                    logger.info(f"Loaded {len(chunk)} records into Elasticsearch")
            logger.info("Data extraction and loading process completed")
        except Exception as e:
            logger.exception(f"An error occurred during data extraction and loading process: {e}")
        finally:
            time.sleep(TIME_INTERVAL_SECONDS)
            repeats += 1


if __name__ == '__main__':
    main()
