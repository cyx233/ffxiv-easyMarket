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

# EasyMarket
自用工具, 整合了XIVAPI和Universails

更加流场的市场体验，简化手动比价计算

## 目前功能：

1. 通过XIVAPI查询合成树和ncp价格
2. 通过Universalis查询近期板子价格
3. 从合成树计算最优成本，包括半成品合成与素材合成

## TODO：

1. hq, nq的区分
2. 更加详细的市场数据

## Requirements
```txt
python>=3.6.0
asyncio
aiohttp
requests
```

## 示例
在与easyMarket **同文件夹** 中新建用户文件main.py。

### 注意:过高的每秒请求数（post_per_sec）会导致访问失败

如果在 https://xivapi.com/ 注册的话可以在用户界面找到private key，填入api_key提高访问次数限制
```python
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

# 相关工作
XIVAPI： https://xivapi.com/

pyxivapi: https://github.com/xivapi/xivapi-py

XIVAPI中文分支: https://cafemaker.wakingsands.com/

Universails: https://universalis.app/
