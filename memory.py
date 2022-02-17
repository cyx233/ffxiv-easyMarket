from copy import copy
import os
import json
from pkg_resources import ensure_directory
import requests
import time

from easyMarket.pyxivapi.client import XIVAPIClient


class Memory:
    def __init__(self) -> None:
        dir_path = os.path.abspath(os.path.dirname(__file__))
        self.item_path = os.path.join(dir_path, "item_memory.json")
        self.recipe_path = os.path.join(dir_path, "recipe_memory.json")
        self.price_path = os.path.join(dir_path, "price_memory.json")
        self.post_per_sec = 10
        if os.path.exists(self.item_path):
            with open(self.item_path) as f:
                self.item_memory = json.load(f)
        else:
            self.item_memory = {}

        if os.path.exists(self.recipe_path):
            with open(self.recipe_path) as f:
                self.recipe_memory = json.load(f)
        else:
            self.recipe_memory = {}

        if os.path.exists(self.price_path):
            with open(self.price_path) as f:
                self.price_memory = json.load(f)
        else:
            self.price_memory = {}
        self.client: XIVAPIClient = None

        url = "https://universalis.app/api/marketable"
        r = requests.get(url)
        self.marketable = set(r.json())
        dir_path = os.path.abspath(os.path.dirname(__file__))
        self.file_path = os.path.join(dir_path, "price_memory.json")
        self.server = "豆豆柴"

    async def get_item(self, item_name):
        if item_name in self.item_memory:
            return self.item_memory[item_name]
        time.sleep(1/self.post_per_sec)
        result = await self.client.index_search(
            name=item_name,
            indexes=['Item'],
            columns=['ID', 'Name', 'PriceMid', 'Recipes',
                     'GameContentLinks.GilShopItem'],
            string_algo='match',
            language='zh',
            per_page=1
        )
        if result['Pagination']['ResultsTotal'] > 0:
            if result['Results'][0]['Name'] == item_name:
                data = result['Results'][0]
                if data['GameContentLinks']['GilShopItem'] is None:
                    del data['PriceMid']
                if data['Recipes'] is None:
                    del data['Recipes']
                del data['GameContentLinks']
                del data['Name']
                self.item_memory[item_name] = data
                return data
        return

    async def get_recipe(self, recipe_id):
        if str(recipe_id) in self.recipe_memory:
            return self.recipe_memory[str(recipe_id)]
        time.sleep(1/self.post_per_sec)
        columns = ['AmountIngredient{}'.format(i)for i in range(10)] +\
            ["ItemIngredient{}.Name".format(i)for i in range(10)] +\
            ["ItemIngredient{}.ID".format(i) for i in range(10)] +\
            ["AmountResult"]
        result = await self.client.index_by_id(
            index="Recipe",
            content_id=recipe_id,
            columns=columns,
            language="zh"
        )
        if result is None:
            return
        temp = []
        for i in range(10):
            if result['AmountIngredient{}'.format(i)] > 0:
                temp.append({'amount': result['AmountIngredient{}'.format(
                    i)], 'name': result['ItemIngredient{}'.format(i)]['Name']})
        data = [temp, result["AmountResult"]]
        self.recipe_memory[str(recipe_id)] = data
        return data

    def get_board_price(self, item_id, price_threshold=0.1, time_limit=3600, need=1):
        if str(item_id) in self.price_memory:
            if int(time.time()) - self.price_memory[str(item_id)]['time'] < time_limit:
                return self.price_memory[str(item_id)]['buy'], self.price_memory[str(item_id)]['sale'], self.price_memory[str(item_id)]['sale_per_day']
        assert price_threshold >= 0
        if item_id not in self.marketable:
            return
        url = "https://universalis.app/api/{}/{}".format(self.server, item_id)
        time.sleep(1/self.post_per_sec)
        r = requests.get(url)
        if r.status_code == 200:
            result = r.json()
            if len(result['listings']) == 0:
                return
            best_price = result["listings"][0]['pricePerUnit']
            amount = 0
            money = 0
            for i in result['listings']:
                price = i['pricePerUnit']
                quantity = i['quantity']
                if price <= best_price*(1+price_threshold) or amount < need:
                    money += quantity*price
                    amount += quantity
                    if amount > 99:
                        break
                else:
                    break
            avg_buy = (money*1.05)/amount
            buy_amount = amount

            url = "https://universalis.app/api/history/{}/{}".format(
                self.server, item_id)
            money = 0
            amount = 0
            avg_sale = 0
            for i in result['recentHistory']:
                price = i['pricePerUnit']
                quantity = i['quantity']
                if price <= avg_buy*5:
                    money += quantity*price
                    amount += quantity
                    if amount > 99:
                        break
                else:
                    continue
            if amount > 0:
                avg_sale = (money*0.95)/amount

            if buy_amount > 99:
                self.price_memory[item_id] = {'time': int(
                    time.time()), 'buy': avg_buy, 'sale': avg_sale, 'sale_per_day': sale_per_day}
            return avg_buy, avg_sale, sale_per_day
        else:
            print("Network failed when get price!")

    async def get_item_by_id(self, item_id):
        time.sleep(1/self.post_per_sec)
        data = await self.client.index_by_id(
            index='Item',
            content_id=item_id,
            columns=['ID', 'Name', 'PriceMid', 'Recipes',
                     'GameContentLinks.GilShopItem'],
            language='zh',
        )
        if data is not None:
            item_name = copy(data['Name'])
            if data['GameContentLinks']['GilShopItem'] is None:
                del data['PriceMid']
            if data['Recipes'] is None:
                del data['Recipes']
            del data['GameContentLinks']
            del data['Name']
            self.item_memory[item_name] = data
            return item_name, data
        return

    def save(self):
        with open(self.item_path, "w") as f:
            json.dump(self.item_memory, f, ensure_ascii=False)
        with open(self.recipe_path, "w") as f:
            json.dump(self.recipe_memory, f, ensure_ascii=False)
        with open(self.price_path, "w") as f:
            json.dump(self.price_memory, f, ensure_ascii=False)

    def clear(self):
        self.item_memory = {}
        self.recipe_memory = {}
        self.price_memory = {}
        self.save()


memory_client = Memory()
