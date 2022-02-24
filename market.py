# ItemKind.ID = 7 其他
# ItemUICategory.ID = 57 家具
# ItemUICategory.ID = 58 魔晶石
import json

from easyMarket.pyxivapi.client import XIVAPIClient
from .ingredient import Ingredient
from .memory import memory_client


class MarketClient:
    def __init__(self, post_per_sec=10, api_key=None, server="豆豆柴"):
        with open('ItemUI_id2name.json',encoding="utf-8") as f:
            self.category_id2name = json.load(f)
            self.category_name2id = list(self.category_id2name.values())
        self.client = XIVAPIClient(api_key=api_key)
        memory_client.client = self.client
        memory_client.post_per_sec = post_per_sec

    async def get_recipe_route(self, item_name, amount=1):
        root = Ingredient(item_name, amount)
        await root.get_ingredients()
        root.update_price()
        return root

    async def get_recipe_route_by_id(self, item_id, amount=1):
        item_name, _ = await memory_client.get_item_by_id(item_id)
        return await self.get_recipe_route(item_name, amount)

    async def close(self):
        memory_client.save()
        await self.client.session.close()
