# EasyMarket
combined XIVAPI and Universails

REALLY EASY to get prices and recipes.

## Features：

1. search recipes and NPC prices from XIVAPI.
2. search market prices from Universalis.
3. calculate costs and profits according to all possible recipes and give advices.

## TODO：

1. difference between hq and nq
2. batch search

## Requirements
```txt
python>=3.6.0
asyncio
aiohttp
requests
```

## Examples


### post_per_sec will cause access failures

If you register at https://xivapi.com/, you can find the private key in the user interface, fill in api_key to increase the number of visits
```python
# main.py
import asyncio
import logging
from easyMarket import MarketClient


async def fetch_example_results():
    client = MarketClient(
        post_per_sec=10,
        server="豆豆柴",
        api_key="YOUR PRIVATE KEY" # 可选
        )

    result = await client.get_recipe_route("复制长椅", amount=2)
    result.display()

    await client.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN,
                        format='%(message)s', datefmt='%H:%M')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_example_results())
```

# Related Work
XIVAPI： https://xivapi.com/

pyxivapi: https://github.com/xivapi/xivapi-py

XIVAPI中文分支: https://cafemaker.wakingsands.com/

Universails: https://universalis.app/
