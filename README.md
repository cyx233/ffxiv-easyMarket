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
=======================查询结果=======================
成品:复制长椅*2, 最优为 复杂线路:18300.15/个, 总价36600.30
        配方0:
        素材:21744.15, 半成品:20625.67, 最优线路:18300.15
                素材:风化涂料*2.0, 最优为 板子:2628.67/个, 总价5257.33
                半成品:矮人银锭*12.0, 最优为 半成品:1607.41/个, 总价19288.97
                        配方0:
                        素材:1929.41, 半成品:1929.41, 最优线路:1929.41
                                素材:暗银矿*48.0, 最优为 板子:289.00/个, 总价13872.00
                                素材:灵银矿*12.0, 最优为 板子:234.41/个, 总价2812.97
                                素材:火之水晶*84.0, 最优为 板子:77.00/个, 总价6468.00
                        配方1:
                        素材:1607.41, 半成品:1607.41, 最优线路:1607.41
                                素材:暗银矿*48.0, 最优为 板子:289.00/个, 总价13872.00
                                素材:灵银矿*12.0, 最优为 板子:234.41/个, 总价2812.97
                                素材:冰之水晶*84.0, 最优为 板子:31.00/个, 总价2604.00
                半成品:钛铜锭*12.0, 最优为 板子:945.00/个, 总价11340.00
                        配方0:
                        素材:1841.00, 半成品:1841.00, 最优线路:1841.00
                                素材:钛铜矿*48.0, 最优为 板子:299.50/个, 总价14376.00
                                素材:白钛矿*12.0, 最优为 板子:104.00/个, 总价1248.00
                                素材:火之水晶*84.0, 最优为 板子:77.00/个, 总价6468.00
                        配方1:
                        素材:1519.00, 半成品:1519.00, 最优线路:1519.00
                                素材:钛铜矿*48.0, 最优为 板子:299.50/个, 总价14376.00
                                素材:白钛矿*12.0, 最优为 板子:104.00/个, 总价1248.00
                                素材:冰之水晶*84.0, 最优为 板子:31.00/个, 总价2604.00
                素材:冰之水晶*14.0, 最优为 板子:31.00/个, 总价434.00
                素材:土之水晶*14.0, 最优为 板子:20.00/个, 总价280.00
-----------------------利润核算-----------------------
最优成本:18300.15/个
预估售价:14975.00/个
利润:-3325.15/个
总利润:-6650.30
利润率:-18.17%
=======================查询结束=======================
```

# 相关工作
XIVAPI： https://xivapi.com/

pyxivapi: https://github.com/xivapi/xivapi-py

XIVAPI中文分支: https://cafemaker.wakingsands.com/

Universails: https://universalis.app/