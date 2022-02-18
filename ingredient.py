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
        self.recipes = []

    async def __get_item_info(self):
        data = await memory_client.get_item(self.item_name)
        if data is None:
            return []
        self.item_id = data['ID']
        if "PriceMid" in data:
            self.npc_price = data['PriceMid']

        all_recipes = []
        if 'Recipes' in data:
            for i in data['Recipes']:
                all_recipes.append(i['ID'])
        return all_recipes

    async def get_ingredients(self):
        all_recipes = await self.__get_item_info()
        if len(all_recipes) == 0:
            return
        for recipe_id in all_recipes:
            recipe, result_amount = await memory_client.get_recipe(recipe_id)
            this_recipe = []
            for i in recipe:
                ingredient_amount = i['amount'] / result_amount
                node = Ingredient(
                    i['name'], ingredient_amount*self.need_amount)
                await node.get_ingredients()
                this_recipe.append(node)
            self.recipes.append([this_recipe])

    def update_price(self, memory=None):
        if memory is None:
            ids = self.get_all_ids()
            data = memory_client.get_board_price(ids)
        else:
            data = memory

        if self.item_id in data:
            self.board_price = data[self.item_id]['buy']
            self.board_sale_price = data[self.item_id]['sale']
            self.sale_per_day = data[self.item_id]['sale_per_day']

        self.best_buy_price = min(
            self.npc_price, self.board_price)

        if len(self.recipes) == 0:
            self.original_price = self.best_buy_price
            self.best_price = self.best_buy_price

        for index, recipe in enumerate(self.recipes):
            original_price = 0
            direct_price = 0
            best_price = 0
            for node in recipe[0]:
                node.update_price(data)
                original_price += node.original_price*node.need_amount
                direct_price += node.best_buy_price*node.need_amount
                best_price += node.best_price*node.need_amount
            self.original_price = min(self.original_price, original_price)
            self.direct_price = min(self.direct_price, direct_price)
            self.best_price = min(self.best_price, best_price)
            self.recipes[index] += [original_price,
                                    direct_price, best_price]
        self.best_price = min(self.best_price, self.best_buy_price)

    def get_all_ids(self):
        ids = set()
        ids.add(self.item_id)
        for recipe in self.recipes:
            for i in recipe[0]:
                ids = ids.union(i.get_all_ids())
        return ids

    def display(self, rank=0, verbose=False):
        if rank == 0:
            if verbose:
                print("{:=^50s}".format("详细结果"))
            else:
                print("{:=^50s}".format("简略结果"))
            type_name = "成品"
        elif len(self.recipes) > 0:
            type_name = "半成品"
        else:
            type_name = "素材"
        indent = "\t"*rank
        info = indent + \
            "{}:{}*{:.1f}".format(type_name, self.item_name, self.need_amount)
        if self.best_buy_price == BIG_NUMBER:
            print(info+" ,未找到结果")
            return
        price_info = ", 最优为"
        if self.best_price == self.npc_price:
            price_info += " npc:"
        elif self.best_price == self.board_price:
            price_info += " 板子:"
        elif self.best_price == self.direct_price:
            price_info += " 直接合成:"
        elif self.best_price == self.direct_price:
            price_info += " 素材合成:"
        else:
            price_info += " 复杂线路:"

        price_info += "{:.2f}/个, 总价{:.2f}".format(
            self.best_price, self.best_price*self.need_amount)
        print(info+price_info)

        if verbose:
            for index, recipe in enumerate(self.recipes):
                print(indent+"\t配方{}:".format(index))
                if recipe[1] == recipe[2]:
                    print(
                        indent+"\t素材:{:.2f}, 最优线路:{:.2f}".format(recipe[1], recipe[3]))
                else:
                    print(
                        indent+"\t素材:{:.2f}, 半成品:{:.2f}, 最优线路:{:.2f}".format(recipe[1], recipe[2], recipe[3]))

                for i in recipe[0]:
                    i.display(rank+2, True)

        if rank == 0:
            print("{:-^50s}".format("利润核算"))
            if self.npc_price < BIG_NUMBER:
                print("npc购买成本:{:.2f}/个".format(self.npc_price))
            print("最优成本:{:.2f}/个".format(self.best_price))
            print("总成本:{:.2f}".format(self.best_price*self.need_amount))
            print("预估售价:{:.2f}/个".format(self.board_sale_price))
            interest = self.board_sale_price-self.best_price
            print("利润:{:.2f}/个".format(interest))
            print("利润率:{:.2%}".format(interest/self.best_price))
            print("总利润:{:.2f}".format(self.need_amount*interest))
            if self.sale_per_day == 0:
                print("注意：售出量极少, 1周内无售出")
            else:
                print("每日售出:{:.2f}".format(self.sale_per_day))
                print("每日利润上限:{:.2f}".format(self.sale_per_day*interest))
                print("最短售出时间:{:.2f}天".format(
                    self.need_amount/self.sale_per_day))
            print("{:=^50s}".format("查询结束"))
