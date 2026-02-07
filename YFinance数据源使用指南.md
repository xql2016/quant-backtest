# YFinance 数据源使用指南

## 📋 概述

YFinance数据源是一个强大的金融数据获取工具，支持：
- 🇺🇸 **美股** - 全球最大的股票市场
- 🇭🇰 **港股** - 亚洲重要金融市场
- 💎 **加密货币** - 比特币、以太坊等数字资产
- 🌍 **其他市场** - 支持全球多个交易所

---

## 🚀 快速开始

### 基本用法

```python
from data_source import get_stock_data
import datetime

# 获取美股数据
df = get_stock_data(
    code='AAPL',                          # 苹果股票
    start_date=datetime.date(2024, 1, 1),
    end_date=datetime.date(2024, 2, 7),
    source_type='yfinance'                # 使用YFinance数据源
)
```

---

## 📊 支持的资产类型

### 1️⃣ 美股（US Stocks）

**代码格式：** 直接使用股票代码

**示例：**
```python
# 科技股
'AAPL'   # 苹果
'MSFT'   # 微软
'GOOGL'  # 谷歌
'TSLA'   # 特斯拉
'NVDA'   # 英伟达

# ETF
'SPY'    # 标普500 ETF
'QQQ'    # 纳斯达克100 ETF
'DIA'    # 道琼斯工业平均 ETF
```

**完整示例：**
```python
import datetime
from data_source import get_stock_data

# 获取苹果股票数据
df = get_stock_data(
    code='AAPL',
    start_date=datetime.date(2024, 1, 1),
    end_date=datetime.date(2024, 2, 7),
    source_type='yfinance'
)

if df is not None:
    print(f"获取了 {len(df)} 天的数据")
    print(f"最新收盘价: ${df['close'].iloc[-1]:.2f}")
```

---

### 2️⃣ 港股（Hong Kong Stocks）

**代码格式：** 股票代码 + `.HK` 后缀

**示例：**
```python
'0700.HK'   # 腾讯控股
'9988.HK'   # 阿里巴巴
'1810.HK'   # 小米集团
'3690.HK'   # 美团
'2318.HK'   # 中国平安
'9999.HK'   # 网易
```

**完整示例：**
```python
# 获取腾讯控股数据
df = get_stock_data(
    code='0700.HK',
    start_date=datetime.date(2024, 1, 1),
    end_date=datetime.date(2024, 2, 7),
    source_type='yfinance'
)

if df is not None:
    print(f"腾讯收盘价: HK${df['close'].iloc[-1]:.2f}")
```

**注意事项：**
- ⚠️ 港股代码必须包含 `.HK` 后缀
- ⚠️ 代码要保留前导零，如 `0700.HK` 而非 `700.HK`
- ℹ️ 价格以港币（HKD）计价

---

### 3️⃣ 加密货币（Cryptocurrencies）

**代码格式：** `币种代码-USD` 或 `币种代码-USDT`

**主流加密货币：**
```python
# 主流币
'BTC-USD'   # 比特币
'ETH-USD'   # 以太坊
'BNB-USD'   # 币安币
'XRP-USD'   # 瑞波币

# DeFi & Layer1
'SOL-USD'   # Solana
'ADA-USD'   # Cardano
'AVAX-USD'  # Avalanche
'MATIC-USD' # Polygon

# 稳定币
'USDT-USD'  # Tether
'USDC-USD'  # USD Coin
```

**完整示例：**
```python
# 获取比特币数据
df = get_stock_data(
    code='BTC-USD',
    start_date=datetime.date(2024, 1, 1),
    end_date=datetime.date(2024, 2, 7),
    source_type='yfinance',
    asset_type='crypto'  # 可选：指定资产类型
)

if df is not None:
    # 计算波动率（加密货币特有）
    volatility = df['close'].pct_change().std() * (365 ** 0.5) * 100
    print(f"比特币价格: ${df['close'].iloc[-1]:,.2f}")
    print(f"年化波动率: {volatility:.2f}%")
```

**注意事项：**
- ℹ️ 加密货币24小时交易，数据更完整
- ℹ️ 波动性通常远高于传统股票
- ⚠️ 价格通常以美元（USD）计价

---

## 🔧 高级功能

### 1. 获取资产详细信息

```python
from data_source import YFinanceDataSource

# 创建数据源实例
yf_source = YFinanceDataSource()

# 获取资产信息
info = yf_source.get_info('AAPL')

print(f"名称: {info['name']}")
print(f"市场: {info['market']}")
print(f"币种: {info['currency']}")
print(f"交易所: {info['exchange']}")
print(f"类型: {info['type']}")
```

**输出示例：**
```
名称: Apple Inc.
市场: us_market
币种: USD
交易所: NMS
类型: EQUITY
```

---

### 2. 使用工厂模式

```python
from data_source import DataSourceFactory

# 创建YFinance数据源
yf_source = DataSourceFactory.create_data_source('yfinance')

# 使用数据源
df = yf_source.fetch_data(
    code='TSLA',
    start_date=datetime.date(2024, 1, 1),
    end_date=datetime.date(2024, 2, 7)
)
```

---

### 3. 自定义时间间隔

```python
# 获取小时级数据（如果支持）
df = get_stock_data(
    code='BTC-USD',
    start_date=datetime.date(2024, 2, 1),
    end_date=datetime.date(2024, 2, 7),
    source_type='yfinance',
    interval='1h'  # 1小时间隔
)
```

**支持的间隔：**
- `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m` - 分钟级
- `1h` - 小时
- `1d` - 日（默认）
- `5d` - 5天
- `1wk` - 周
- `1mo`, `3mo` - 月

---

## 📈 实战案例

### 案例1：多资产组合分析

```python
import datetime
from data_source import get_stock_data

# 定义投资组合
portfolio = [
    ('AAPL', '苹果', 0.3),      # 30%
    ('MSFT', '微软', 0.3),      # 30%
    ('0700.HK', '腾讯', 0.2),   # 20%
    ('BTC-USD', '比特币', 0.2)  # 20%
]

start_date = datetime.date(2024, 1, 1)
end_date = datetime.date(2024, 2, 7)

total_return = 0

for code, name, weight in portfolio:
    df = get_stock_data(code, start_date, end_date, source_type='yfinance')
    
    if df is not None:
        returns = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]
        weighted_return = returns * weight
        total_return += weighted_return
        
        print(f"{name:10s}: {returns:+7.2%} (权重: {weight:.0%}) → 贡献: {weighted_return:+7.2%}")

print(f"\n组合总收益: {total_return:+.2%}")
```

---

### 案例2：跨市场相关性分析

```python
import pandas as pd
import datetime
from data_source import get_stock_data

# 获取不同市场的代表性资产
assets = {
    'US_Tech': 'QQQ',          # 美股科技
    'HK_Index': '2800.HK',     # 恒生指数ETF
    'Crypto': 'BTC-USD'        # 加密货币
}

start_date = datetime.date(2023, 1, 1)
end_date = datetime.date(2024, 1, 1)

# 收集所有数据
data = {}
for name, code in assets.items():
    df = get_stock_data(code, start_date, end_date, source_type='yfinance')
    if df is not None:
        data[name] = df['close']

# 创建DataFrame并计算相关性
df_combined = pd.DataFrame(data)
correlation = df_combined.pct_change().corr()

print("跨市场相关性矩阵:")
print(correlation)
```

---

### 案例3：加密货币波动率分析

```python
import datetime
from data_source import get_stock_data

cryptos = ['BTC-USD', 'ETH-USD', 'BNB-USD']
start_date = datetime.date(2024, 1, 1)
end_date = datetime.date(2024, 2, 7)

print("加密货币波动率分析\n")
print(f"{'币种':<15} {'价格':<12} {'30日波动率':<12} {'风险等级':<10}")
print("-" * 60)

for code in cryptos:
    df = get_stock_data(code, start_date, end_date, source_type='yfinance')
    
    if df is not None:
        price = df['close'].iloc[-1]
        # 计算年化波动率
        volatility = df['close'].pct_change().std() * (365 ** 0.5) * 100
        
        # 风险分级
        if volatility < 30:
            risk = "低"
        elif volatility < 50:
            risk = "中"
        else:
            risk = "高"
        
        print(f"{code:<15} ${price:>10,.2f} {volatility:>10.2f}% {risk:>8}")
```

---

## 🎯 在回测系统中使用

### 方法1：直接指定数据源

在Streamlit界面中，修改数据获取部分：

```python
# 在多策略可视化回测_小红书20260117.py中
df = get_stock_data(
    stock_code, 
    start_date, 
    end_date, 
    source_type='yfinance'  # 改用YFinance
)
```

### 方法2：与策略回测结合

```python
from data_source import get_stock_data
from strategy_backtest import StrategyFactory, BacktestEngine
import datetime

# 1. 获取美股数据
df = get_stock_data(
    code='AAPL',
    start_date=datetime.date(2023, 1, 1),
    end_date=datetime.date(2024, 1, 1),
    source_type='yfinance'
)

# 2. 创建策略
strategy = StrategyFactory.create_strategy(
    "MACD趋势策略", 
    {'fast': 12, 'slow': 26, 'signal': 9}
)

# 3. 运行回测
engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
result = engine.run(df, strategy)

# 4. 查看结果
print(f"总收益率: {result.total_return:.2%}")
print(f"胜率: {result.win_rate:.2%}")
```

---

## 💡 使用技巧

### 1. 数据质量检查

```python
df = get_stock_data('AAPL', start, end, source_type='yfinance')

if df is not None:
    # 检查缺失值
    print(f"缺失值: {df.isnull().sum().sum()}")
    
    # 检查数据完整性
    print(f"数据天数: {len(df)}")
    
    # 检查价格异常
    price_change = df['close'].pct_change()
    extreme_changes = price_change[abs(price_change) > 0.2]
    print(f"异常波动天数: {len(extreme_changes)}")
```

### 2. 错误处理

```python
try:
    df = get_stock_data(code, start, end, source_type='yfinance')
    
    if df is None or df.empty:
        print(f"⚠️  代码 {code} 可能不存在或暂无数据")
    else:
        print(f"✅ 成功获取数据")
        
except Exception as e:
    print(f"❌ 错误: {e}")
```

### 3. 批量下载优化

```python
import time
from data_source import YFinanceDataSource

yf_source = YFinanceDataSource()
codes = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']

for i, code in enumerate(codes):
    print(f"下载 {i+1}/{len(codes)}: {code}")
    df = yf_source.fetch_data(code, start, end)
    
    # 避免请求过快
    if i < len(codes) - 1:
        time.sleep(0.5)  # 暂停0.5秒
```

---

## ⚠️ 注意事项

### 1. 数据限制
- YFinance是免费服务，可能有请求频率限制
- 建议添加适当的延迟避免被限制
- 历史数据通常完整，但实时数据可能有延迟

### 2. 代码格式
| 市场 | 格式 | 示例 | 注意事项 |
|------|------|------|----------|
| 美股 | 代码 | `AAPL` | 直接使用 |
| 港股 | 代码.HK | `0700.HK` | 必须加.HK后缀，保留前导零 |
| 加密货币 | XXX-USD | `BTC-USD` | 通常以USD计价 |

### 3. 时区问题
- 所有数据会自动转换为本地时区
- 如需特定时区，需要额外处理

### 4. 数据完整性
- 港股可能在某些节假日停市
- 加密货币24小时交易
- 美股仅工作日交易

---

## 🔍 常见问题

### Q1: 港股代码获取失败？
**A:** 确保代码格式正确，例如 `0700.HK` 而非 `700.HK`

### Q2: 加密货币数据不完整？
**A:** 检查代码格式是否为 `XXX-USD`，例如 `BTC-USD`

### Q3: 如何获取更多历史数据？
**A:** YFinance支持较长的历史数据，但具体取决于资产类型

### Q4: 数据更新频率？
**A:** 通常日线数据在收盘后几分钟内更新

### Q5: 是否支持A股？
**A:** 建议使用AKShare数据源获取A股数据，YFinance对A股支持有限

---

## 📚 相关文档

- [数据源模块说明](./模块化重构说明.md#数据源模块)
- [策略回测模块](./模块化重构说明.md#策略回测模块)
- [使用示例](./yfinance_使用示例.py)
- [YFinance官方文档](https://github.com/ranaroussi/yfinance)

---

## 🎉 总结

YFinance数据源为你提供了：
- ✅ 全球市场数据接入能力
- ✅ 简单易用的API
- ✅ 与回测系统无缝集成
- ✅ 支持多种资产类型
- ✅ 免费且稳定

现在就开始使用YFinance数据源，探索全球金融市场吧！🚀

---

**版本：** 1.0  
**更新日期：** 2026-02-07  
**作者：** 量化回测系统开发团队

