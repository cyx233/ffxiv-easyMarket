import json
import requests
import time
import os


class PriceClient:
    def __init__(self):
        url = "https://universalis.app/api/marketable"
        r = requests.get(url)
        self.marketable = set(r.json())
        dir_path = os.path.abspath(os.path.dirname(__file__))
        self.file_path = os.path.join(dir_path, "price_memory.json")
        self.server = "豆豆柴"
        if os.path.exists(self.file_path):
            with open(self.file_path) as f:
                self.memory = json.load(f)
        else:
            self.memory = {}

    def close(self):
        with open(self.file_path, "w") as f:
            json.dump(self.memory, f)

    def get_board_price(self, item_id, price_threshold=0.1, time_limit=1200):
        if str(item_id) in self.memory:
            if time.time() - self.memory[str(item_id)]['time'] < time_limit:
                return self.memory[str(item_id)]['buy'], self.memory[str(item_id)]['sale']
        assert price_threshold >= 0
        if item_id not in self.marketable:
            return
        url = "https://universalis.app/api/{}/{}".format(self.server, item_id)
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
                if price <= best_price*(1+price_threshold):
                    money += quantity*price
                    amount += quantity
                    if amount > 99:
                        break
            avg_buy = money/amount

            money = 0
            amount = 0
            avg_sale = 0
            for i in result['recentHistory']:
                price = i['pricePerUnit']
                quantity = i['quantity']
                if price <= best_price*(1+price_threshold):
                    money += quantity*price
                    amount += quantity
                    if amount > 99:
                        break
            if amount > 0:
                avg_sale = money/amount

            self.memory[item_id] = {
                'time': time.time(), 'buy': avg_buy, 'sale': avg_sale}
            return avg_buy, avg_sale
        else:
            price("Network failed when get price!")

    def get_direct_price(self):
        pass


price_client = PriceClient()
