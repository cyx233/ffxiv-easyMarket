import time
from .memory import memory_client

BIG_NUMBER = 0x3fffffff


class Ingredient:
    def __init__(self, item_name, amount) -> None:
        self.need_amount = amount
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

    async def __get_item_info(self):
        data = await memory_client.get_item(self.item_name)
        if data is None:
            return
        self.item_id = data['ID']
        if self.item_id > 41:
            self.npc_price = data['PriceMid']

        price = memory_client.get_board_price(self.item_id)
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

    async def get_ingredients(self):
        await self.__get_item_info()
        if len(self.recipe_id) == 0:
            return

        for recipe_id in self.recipe_id:
            recipe, result_amount = await memory_client.get_recipe(recipe_id)
            this_recipe = []
            original_price = 0
            direct_price = 0
            best_price = 0
            for i in recipe:
                ingredient_amount = i['amount'] / result_amount
                node = Ingredient(
                    i['name'], ingredient_amount*self.need_amount)
                await node.get_ingredients()
                this_recipe.append(node)

                original_price += node.original_price*ingredient_amount
                direct_price += node.best_buy_price*ingredient_amount
                best_price += node.best_price*ingredient_amount

            self.recipes.append(
                (this_recipe, original_price, direct_price, best_price))

            self.original_price = min(self.original_price, original_price)
            self.direct_price = min(self.direct_price, direct_price)
            self.best_price = min(self.best_price, best_price)
        self.best_price = min(self.best_price, self.best_buy_price)

    def display(self, rank=0):
        if rank == 0:
            print("{:=^50s}".format("查询结果"))
            type_name = "成品"
        elif len(self.recipes) > 0:
            type_name = "半成品"
        else:
            type_name = "素材"
        indent = "\t"*rank
        info = indent + \
            "{}:{}*{}".format(type_name, self.item_name, self.need_amount)
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

        price_info += "{:.2f}/个, 总价{:.2f}".format(
            self.best_price, self.best_price*self.need_amount)
        print(info+price_info)

        for index, recipe in enumerate(self.recipes):
            print(indent+"\t配方{}:".format(index))
            print(
                indent+"\t素材:{:.2f}, 半成品:{:.2f}, 最优线路:{:.2f}".format(recipe[1], recipe[2], recipe[3]))
            for i in recipe[0]:
                i.display(rank+2)

        if rank == 0 and self.board_price < BIG_NUMBER:
            print("{:-^50s}".format("利润核算"))
            print("最优成本:{:.2f}/个".format(self.best_price))
            print("预估售价:{:.2f}/个".format(self.board_sale_price))
            interest = self.board_sale_price-self.best_price
            print("利润:{:.2f}/个".format(interest))
            print("总利润:{:.2f}".format(interest*self.need_amount))
            print("利润率:{:.2%}".format(interest/self.best_price))
            print("{:=^50s}".format("查询结束"))
