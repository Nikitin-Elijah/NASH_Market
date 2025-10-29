import datetime
from elasticsearch import Elasticsearch, NotFoundError
from src.models import ProductModel


class Indexer:
    def __init__(self, elasticsearch_client: Elasticsearch, products: ProductModel, cards_index_alias: str):
        self.elasticsearch_client = elasticsearch_client
        self.products = products
        self.cards_index_alias = cards_index_alias

    async def build_new_cards_index(self) -> str:
        index_name = "cards-" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.create_empty_cards_index(index_name)

        all_products = await self.products.filter(is_active=True)
        for product in all_products:
            self.put_card_into_index(product, index_name)

        return index_name

    def create_empty_cards_index(self, index_name: str):
        body = {
            "mappings": {
                "properties": {
                    "name": {"type": "text", "analyzer": "russian"},
                    "description": {"type": "text", "analyzer": "russian"},
                    "price": {"type": "scaled_float", "scaling_factor": 100}
                }
            }
        }
        self.elasticsearch_client.indices.create(index=index_name, body=body)

    def put_card_into_index(self, product: ProductModel, index_name: str):
        doc = {
            "name": product.name,
            "description": product.description,
            "price": product.price
        }
        self.elasticsearch_client.index(index=index_name, id=product.id, body=doc)

    def switch_current_cards_index(self, new_index_name: str):
        try:
            old_indices = self.elasticsearch_client.indices.get_alias(name=self.cards_index_alias)
            remove_actions = [
                {"remove": {"index": index_name, "alias": self.cards_index_alias}}
                for index_name in old_indices
            ]
        except NotFoundError:
            remove_actions = []

        actions = remove_actions + [{"add": {"index": new_index_name, "alias": self.cards_index_alias}}]
        self.elasticsearch_client.indices.update_aliases(body={"actions": actions})
