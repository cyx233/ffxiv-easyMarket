# EasyMarket
自用工具, 整合了XIVAPI和Universails

更加简易的市场体验，避免手动比价计算的烦恼。

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

    result = await client.get_recipe_route("复制长椅")
    result.display()

    await client.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN,
                        format='%(message)s', datefmt='%H:%M')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_example_results())
```
## 效果
```bash
$ python prepare.py
成品:复制长椅, 最优为 复杂线路:3675.58, 近期成交14975.00
        配方0:
        素材:3675.58, 半成品:5612.96, 最优线路:3675.58
                素材:风化涂料, 最优为 板子:2628.67
                半成品:矮人银锭, 最优为 半成品:558.41
                        配方0:
                        素材:605.41, 半成品:605.41, 最优线路:605.41
                                素材:暗银矿, 最优为 板子:293.00
                                素材:灵银矿, 最优为 板子:234.41
                                素材:火之水晶, 最优为 板子:78.00
                        配方1:
                        素材:558.41, 半成品:558.41, 最优线路:558.41
                                素材:暗银矿, 最优为 板子:293.00
                                素材:灵银矿, 最优为 板子:234.41
                                素材:冰之水晶, 最优为 板子:31.00
                半成品:钛铜锭, 最优为 半成品:434.50
                        配方0:
                        素材:481.50, 半成品:481.50, 最优线路:481.50
                                素材:钛铜矿, 最优为 板子:299.50
                                素材:白钛矿, 最优为 板子:104.00
                                素材:火之水晶, 最优为 板子:78.00
                        配方1:
                        素材:434.50, 半成品:434.50, 最优线路:434.50
                                素材:钛铜矿, 最优为 板子:299.50
                                素材:白钛矿, 最优为 板子:104.00
                                素材:冰之水晶, 最优为 板子:31.00
                素材:冰之水晶, 最优为 板子:31.00
                素材:土之水晶, 最优为 板子:23.00
```

# 相关工作
XIVAPI： https://xivapi.com/

pyxivapi: https://github.com/xivapi/xivapi-py

XIVAPI中文分支: https://cafemaker.wakingsands.com/

Universails: https://universalis.app/