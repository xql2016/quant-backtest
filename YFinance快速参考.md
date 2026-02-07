# YFinance 数据源快速参考

## 🎯 一键复制代码

### 美股

```python
from data_source import get_stock_data
import datetime

# 苹果
df = get_stock_data('AAPL', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')

# 特斯拉
df = get_stock_data('TSLA', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')

# 微软
df = get_stock_data('MSFT', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')

# 英伟达
df = get_stock_data('NVDA', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')
```

### 港股

```python
# 腾讯控股
df = get_stock_data('0700.HK', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')

# 阿里巴巴
df = get_stock_data('9988.HK', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')

# 小米集团
df = get_stock_data('1810.HK', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')

# 美团
df = get_stock_data('3690.HK', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')
```

### 加密货币

```python
# 比特币
df = get_stock_data('BTC-USD', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')

# 以太坊
df = get_stock_data('ETH-USD', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')

# 币安币
df = get_stock_data('BNB-USD', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')

# Solana
df = get_stock_data('SOL-USD', datetime.date(2024,1,1), datetime.date(2024,2,7), source_type='yfinance')
```

## 📋 代码格式速查

| 市场 | 格式 | 示例 |
|------|------|------|
| 美股 | `代码` | `AAPL`, `TSLA`, `MSFT` |
| 港股 | `代码.HK` | `0700.HK`, `9988.HK`, `1810.HK` |
| 加密货币 | `XXX-USD` | `BTC-USD`, `ETH-USD`, `BNB-USD` |

## 🔥 热门资产代码

### 美股科技股
```
AAPL  - 苹果
MSFT  - 微软
GOOGL - 谷歌
AMZN  - 亚马逊
NVDA  - 英伟达
TSLA  - 特斯拉
META  - Meta (Facebook)
```

### 港股
```
0700.HK  - 腾讯控股
9988.HK  - 阿里巴巴
1810.HK  - 小米集团
3690.HK  - 美团
2318.HK  - 中国平安
9999.HK  - 网易
```

### 加密货币
```
BTC-USD   - 比特币
ETH-USD   - 以太坊
BNB-USD   - 币安币
XRP-USD   - 瑞波币
SOL-USD   - Solana
ADA-USD   - Cardano
AVAX-USD  - Avalanche
MATIC-USD - Polygon
```

## 💻 完整示例

### 回测美股

```python
from data_source import get_stock_data
from strategy_backtest import StrategyFactory, BacktestEngine
import datetime

# 1. 获取数据
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
print(f"收益率: {result.total_return:.2%}")
print(f"胜率: {result.win_rate:.2%}")
```

## 📞 常见问题

**Q: 港股代码怎么输入？**  
A: 必须加 `.HK` 后缀，如 `0700.HK`

**Q: 加密货币支持哪些？**  
A: 大多数主流加密货币，格式为 `XXX-USD`

**Q: 数据免费吗？**  
A: 是的，YFinance是免费服务

**Q: 数据实时吗？**  
A: 有延迟，通常延迟15-20分钟

## 📚 详细文档

- [YFinance数据源使用指南](./YFinance数据源使用指南.md) - 完整文档
- [yfinance_使用示例.py](./yfinance_使用示例.py) - 可运行示例

---

**快速运行示例：**
```bash
python3 yfinance_使用示例.py
```

