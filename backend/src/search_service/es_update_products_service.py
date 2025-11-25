import logging

from elasticsearch import Elasticsearch

from src.config import PRODUCTS_ALIAS_NAME
from src.models import ProductModel
from src.search_service.indexer import Indexer

logger = logging.getLogger(__name__)


class ESUpdateProductsService:
    def __init__(self, es: Elasticsearch):
        self.es = es
        self.alias_name = PRODUCTS_ALIAS_NAME

    async def update_products(self):
        try:
            logger.info("Создаём новый индекс...")
            indexer = Indexer(self.es, ProductModel, self.alias_name)

            index_name = await indexer.build_new_cards_index()
            indexer.switch_current_cards_index(index_name)

            logger.info(f"Создан индекс '{index_name}' и alias '{self.alias_name}'")

        except Exception as e:
            logger.error(
                f"Ошибка при обновлении товаров в индексе ElasticSearch: {str(e)}"
            )
            raise
