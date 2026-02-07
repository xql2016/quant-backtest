# 量化回测系统 - 模块化版本

## 📁 项目结构

```
quant/
├── data_source.py                          # 数据源获取模块
├── strategy_backtest.py                    # 策略与回测模块
├── 多策略可视化回测_小红书20260117.py      # Streamlit主界面
├── 独立使用示例.py                         # 独立使用示例
├── test_modules.py                         # 模块测试脚本
├── 模块化重构说明.md                       # 详细重构说明
├── README_模块化.md                        # 本文件
└── requirements.txt                        # 依赖包列表
```

## 🎯 模块化优势

### 1️⃣ **数据源模块** (`data_source.py`)

**职责：** 统一管理数据获取，支持多种数据源

**特点：**
- ✅ 抽象基类设计，易于扩展
- ✅ 统一数据格式标准
- ✅ 当前支持：AKShare（A股、港股、美股）
- ✅ 预留扩展：CSV、数据库等

**使用示例：**
```python
from data_source import get_stock_data
import datetime

# 获取A股数据
df = get_stock_data(
    code='000001',
    start_date=datetime.date(2023, 1, 1),
    end_date=datetime.date(2024, 1, 1),
    market='A股',
    source_type='akshare'
)
```

### 2️⃣ **策略与回测模块** (`strategy_backtest.py`)

**职责：** 实现交易策略和回测引擎

**特点：**
- ✅ 策略抽象基类，统一接口
- ✅ 6种内置策略（MACD、双均线、RSI、布林带、波段、多重底）
- ✅ 独立的回测引擎
- ✅ 完整的回测结果封装

**使用示例：**
```python
from strategy_backtest import StrategyFactory, BacktestEngine

# 创建策略
params = {'fast': 12, 'slow': 26, 'signal': 9}
strategy = StrategyFactory.create_strategy("MACD趋势策略", params)

# 运行回测
engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
result = engine.run(df, strategy)

# 查看结果
print(f"总收益率: {result.total_return:.2%}")
print(f"胜率: {result.win_rate:.2%}")
```

## 🚀 快速开始

### 方式1：使用Streamlit界面（推荐）

```bash
# 安装依赖
pip install -r requirements.txt

# 运行Streamlit应用
streamlit run 多策略可视化回测_小红书20260117.py
```

### 方式2：独立使用模块

```bash
# 运行示例脚本
python3 独立使用示例.py
```

### 方式3：在自己的代码中使用

```python
import datetime
from data_source import get_stock_data
from strategy_backtest import StrategyFactory, BacktestEngine

# 1. 获取数据
df = get_stock_data('000001', datetime.date(2023,1,1), datetime.date(2024,1,1), market='A股')

# 2. 创建策略
strategy = StrategyFactory.create_strategy("MACD趋势策略", {'fast': 12, 'slow': 26, 'signal': 9})

# 3. 运行回测
engine = BacktestEngine(initial_cash=100000, commission_rate=0.0003)
result = engine.run(df, strategy)

# 4. 使用结果
print(result.total_return)
```

## 📊 内置策略

| 策略名称 | 参数 | 说明 |
|---------|------|------|
| MACD趋势策略 | fast, slow, signal | DIF上穿DEA买入，下穿卖出 |
| 双均线策略(SMA) | short, long | 短线上穿长线买入，下穿卖出 |
| RSI超买超卖 | period, lower, upper | RSI<下轨买入，>上轨卖出 |
| 布林带突破 | period, std | 跌破下轨买入，突破上轨卖出 |
| 波段策略 | 8个参数 | 分批建仓、加仓、止盈 |
| 多重底入场策略 | fast, slow, signal, lookback等 | 底背离信号入场 |

## 🔧 扩展指南

### 添加新数据源

1. 继承 `DataSource` 基类
2. 实现 `fetch_data` 方法
3. 在 `DataSourceFactory` 中注册

```python
class TushareDataSource(DataSource):
    def fetch_data(self, code, start_date, end_date, **kwargs):
        # 实现数据获取逻辑
        # 返回标准格式的DataFrame
        pass
```

### 添加新策略

1. 继承 `Strategy` 基类
2. 实现 `calculate_signals` 方法
3. 实现 `get_strategy_name` 方法
4. 在 `StrategyFactory` 中注册

```python
class MyStrategy(Strategy):
    def calculate_signals(self, df):
        df = df.copy()
        df['signal'] = 0
        # 计算指标和生成信号
        return df
    
    def get_strategy_name(self):
        return "我的策略"
```

## 📝 测试

运行测试脚本验证模块：

```bash
python3 test_modules.py
```

**测试结果：**
- ✅ 策略模块：完全通过
- ⚠️ 数据源模块：需要网络权限（在Streamlit中正常工作）
- ⚠️ 集成测试：需要网络权限（在Streamlit中正常工作）

## 📦 依赖包

```
streamlit      # Web界面
pandas         # 数据处理
numpy          # 数值计算
matplotlib     # 可视化
akshare        # A股、港股数据
yfinance       # 美股数据
```

## 🎓 学习路径

1. **初学者：** 使用Streamlit界面进行回测
2. **进阶者：** 运行 `独立使用示例.py` 了解模块用法
3. **开发者：** 查看 `模块化重构说明.md` 了解架构设计
4. **高级用户：** 扩展自己的数据源和策略

## ⚙️ 配置说明

### 数据源配置

```python
# 使用AKShare（默认）
df = get_stock_data(code, start, end, market='A股', source_type='akshare')

# 使用CSV文件
df = get_stock_data(code, start, end, source_type='csv', csv_dir='./data')

# 使用数据库（需要先实现）
df = get_stock_data(code, start, end, source_type='database', connection_string='...')
```

### 回测配置

```python
engine = BacktestEngine(
    initial_cash=100000,      # 初始资金
    commission_rate=0.0003    # 双边手续费率
)
```

## 🐛 常见问题

### Q1: 数据获取失败？
**A:** 检查网络连接，确保能访问数据源API。AKShare需要网络访问权限。

### Q2: 如何添加自己的策略？
**A:** 参考 `strategy_backtest.py` 中的现有策略，继承 `Strategy` 基类实现。

### Q3: 如何使用本地数据？
**A:** 实现 `CSVDataSource` 或使用数据库数据源。

### Q4: 回测结果不准确？
**A:** 检查手续费率设置，确保数据质量，验证策略逻辑。

## 📈 性能优化

1. **数据缓存：** 使用 `@st.cache_data` 装饰器（已实现）
2. **批量回测：** 可以并行测试多个策略
3. **数据预处理：** 在数据源层面进行数据清洗

## 🔐 安全性

- 数据源模块不存储敏感信息
- 支持自定义数据源，可控制数据来源
- 回测结果仅供参考，不构成投资建议

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

- 查看 `模块化重构说明.md` 获取详细文档
- 运行 `独立使用示例.py` 查看使用案例
- 运行 `test_modules.py` 进行模块测试

---

**版本：** 2.0 (模块化版本)  
**更新日期：** 2026-02-07  
**作者：** 量化回测系统开发团队

🎉 **祝您使用愉快！**

