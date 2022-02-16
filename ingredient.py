import time
from .pyxivapi.client import XIVAPIClient
from .price import price_client
BIG_NUMBER = 0x3fffffff


class Ingredient:
    def __init__(self, item_name, client: XIVAPIClient, memory={}) -> None:
        self.memory = memory

        self.board_price = BIG_NUMBER
        self.board_sale_price = 0
        self.npc_price = BIG_NUMBER

        self.best_buy_price = BIG_NUMBER
        self.best_price = BIG_NUMBER
        self.original_price = BIG_NUMBER
        self.direct_price = BIG_NUMBER
        self.sale_per_day = 0

        self.item_name = item_name
        self.item_id = 0
        self.recipe_id = []
        self.recipes = []
        self.client = client

    async def __get_item_info(self):
        result = await self.client.index_search(
            name=self.item_name,
            indexes=['Item'],
            columns=['ID', 'Name', 'PriceMid', 'Recipes'],
            string_algo='match',
            language='zh',
            per_page=1
        )
        if result['Pagination']['ResultsTotal'] > 0:
            if result['Results'][0]['Name'] == self.item_name:
                data = result['Results'][0]
                self.item_id = data['ID']
                if self.item_id > 41:
                    self.npc_price = data['PriceMid']

                price = price_client.get_board_price(self.item_id)
                if price is not None:
                    self.board_price, self.board_sale_price = price

                if self.npc_price == BIG_NUMBER:
                    self.best_buy_price = min(
                        self.npc_price, self.board_price)
                else:
                    self.best_buy_price = self.board_price

                if data['Recipes'] is not None:
                    for i in data['Recipes']:
                        self.recipe_id.append(i['ID'])
                else:
                    self.original_price = self.best_buy_price
                    self.best_price = self.best_buy_price
                    self.memory[self.item_name] = self

    async def get_ingredients(self, post_per_sec=10):
        time.sleep(1/post_per_sec)
        await self.__get_item_info()
        if len(self.recipe_id) == 0:
            return

        for recipe_id in self.recipe_id:
            columns = ['AmountIngredient{}'.format(i)for i in range(10)] +\
                ["ItemIngredient{}.Name".format(i)for i in range(10)] +\
                ["ItemIngredient{}.ID".format(i)for i in range(10)]
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
            this_recipe = []
            original_price = 0
            direct_price = 0
            best_price = 0
            for i in temp:
                if i['name'] not in self.memory:
                    node = Ingredient(i['name'], self.client, self.memory)
                    await node.get_ingredients(post_per_sec)
                else:
                    node = self.memory[i['name']]
                this_recipe.append(node)

                original_price += node.original_price
                direct_price += node.best_buy_price
                best_price += node.best_price

            self.recipes.append(
                (this_recipe, original_price, direct_price, best_price))

            self.original_price = min(self.original_price, original_price)
            self.direct_price = min(self.direct_price, direct_price)
            self.best_price = min(self.best_price, best_price)
        self.best_price = min(self.best_price, self.best_buy_price)

    def display(self, rank=0):
        if rank == 0:
            type_name = "成品"
        elif len(self.recipes) > 0:
            type_name = "半成品"
        else:
            type_name = "素材"
        indent = "\t"*rank
        info = indent + "{}:{}".format(type_name, self.item_name)
        price_info = ", 最优为"
        if self.best_price == self.npc_price:
            price_info += " npc:"
        elif self.best_price == self.board_price:
            price_info += " 板子:"
        elif self.best_price == self.direct_price:
            price_info += " 半成品:"
        elif self.best_price == self.direct_price:
            price_info += " 原料:"
        else:
            price_info += " 复杂线路:"

        price_info += "{:.2f}".format(self.best_price)
        if rank == 0 and self.board_price < BIG_NUMBER:
            price_info += ", 近期成交{:.2f}".format(self.board_sale_price)
        print(info+price_info)

        for index, recipe in enumerate(self.recipes):
            print(indent+"\t配方{}:".format(index))
            print(
                indent+"\t素材:{:.2f}, 半成品:{:.2f}, 最优线路:{:.2f}".format(recipe[1], recipe[2], recipe[3]))
            for i in recipe[0]:
                i.display(rank+2)
