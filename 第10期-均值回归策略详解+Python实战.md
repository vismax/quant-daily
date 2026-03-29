# 📚 量化学习第10期：均值回归策略详解 + Python 实战

## 📌 一句话概括
均值回归策略基于价格会回归到历史均值的假设，通过识别过度偏离平均价格的资产来捕捉反转机会，是量化交易中经典的统计套利策略。

## 📖 概念详解

均值回归（Mean Reversion）是金融学中的一个核心概念，它基于这样一个假设：资产价格会围绕其内在价值或历史均值波动，最终回归到均衡水平。在量化交易中，均值回归策略认为市场价格如同弹簧，短期内的过度拉伸（上涨或下跌），往往伴随着向内在价值中枢（均值）的回拉。

从统计学角度看，均值回归策略利用价格偏离历史均值程度来识别交易机会。当价格显著高于或低于移动平均线时，策略预期价格将向均值回归。这种策略在震荡市场中表现尤为出色，因为它能够捕捉价格在相对稳定区间内的波动规律。常见的均值回归指标包括布林带（Bollinger Bands）、RSI相对强弱指标等，它们通过不同的数学方法来衡量价格与均值的关系。

从实战角度看，均值回归策略需要结合市场环境和资产特性。某些资产如外汇、大宗商品等天然具有均值回归特性，而趋势明显的股票则可能不适合纯均值回归策略。成功的均值回归策略需要考虑波动率、时间周期、止损设置等多个因素，同时需要严格的回测来验证策略的有效性。

## 📐 数学公式

### 均值回归的基本数学模型

**简单移动平均（SMA）计算：**
```
SMA_n = (P_1 + P_2 + ... + P_n) / n
```

**价格偏离度计算：**
```
Deviation = Current_Price - SMA_n
Z_Score = Deviation / Standard_Deviation
```

**布林带计算公式：**
```
Upper Band = SMA_n + k × Standard_Deviation
Lower Band = SMA_n - k × Standard_Deviation
Middle Band = SMA_n
```

其中k通常取2，代表2个标准差。

**Ornstein-Uhlenbeck (OU) 过程模型：**
```
dX_t = θ(μ - X_t)dt + σdW_t
```
其中：
- X_t：当前价格
- μ：长期均值
- θ：回归速度参数
- σ：波动率
- dW_t：维纳过程

## 🐍 Python 代码实战

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta

class MeanReversionStrategy:
    def __init__(self, symbol, window=20, std_multiplier=2):
        """
        均值回归策略类
        
        参数:
        symbol: 股票代码
        window: 移动平均窗口期
        std_multiplier: 标准差倍数（布林带宽度）
        """
        self.symbol = symbol
        self.window = window
        self.std_multiplier = std_multiplier
        
    def fetch_data(self, start_date, end_date):
        """获取股票数据"""
        stock = yf.Ticker(self.symbol)
        data = stock.history(start=start_date, end=end_date)
        return data
    
    def calculate_indicators(self, data):
        """计算技术指标"""
        # 计算移动平均线
        data['SMA'] = data['Close'].rolling(window=self.window).mean()
        
        # 计算标准差
        data['STD'] = data['Close'].rolling(window=self.window).std()
        
        # 计算布林带
        data['Upper_Band'] = data['SMA'] + (self.std_multiplier * data['STD'])
        data['Lower_Band'] = data['SMA'] - (self.std_multiplier * data['STD'])
        
        # 计算Z-Score
        data['Z_Score'] = (data['Close'] - data['SMA']) / data['STD']
        
        return data
    
    def generate_signals(self, data):
        """生成交易信号"""
        data['Signal'] = 0
        
        # 买入信号：价格跌破下轨或Z-Score < -2
        data.loc[(data['Close'] <= data['Lower_Band']) | 
                (data['Z_Score'] < -2), 'Signal'] = 1
        
        # 卖出信号：价格突破上轨或Z-Score > 2
        data.loc[(data['Close'] >= data['Upper_Band']) | 
                (data['Z_Score'] > 2), 'Signal'] = -1
        
        # 计算持仓
        data['Position'] = data['Signal'].replace(0, method='ffill')
        
        return data
    
    def backtest(self, data, initial_capital=100000):
        """策略回测"""
        data['Returns'] = data['Close'].pct_change()
        data['Strategy_Returns'] = data['Position'].shift(1) * data['Returns']
        
        # 计算累计收益
        data['Cumulative_Returns'] = (1 + data['Strategy_Returns']).cumprod()
        data['Portfolio_Value'] = initial_capital * data['Cumulative_Returns']
        
        return data
    
    def plot_results(self, data):
        """绘制策略结果"""
        plt.figure(figsize=(15, 10))
        
        # 子图1：价格和布林带
        plt.subplot(2, 1, 1)
        plt.plot(data.index, data['Close'], label='Close Price', alpha=0.7)
        plt.plot(data.index, data['SMA'], label='SMA', color='orange')
        plt.plot(data.index, data['Upper_Band'], label='Upper Band', color='red', linestyle='--')
        plt.plot(data.index, data['Lower_Band'], label='Lower Band', color='green', linestyle='--')
        
        # 标记买卖信号
        buy_signals = data[data['Signal'] == 1]
        sell_signals = data[data['Signal'] == -1]
        
        plt.scatter(buy_signals.index, buy_signals['Close'], 
                   color='green', marker='^', s=100, label='Buy Signal')
        plt.scatter(sell_signals.index, sell_signals['Close'], 
                   color='red', marker='v', s=100, label='Sell Signal')
        
        plt.title(f'{self.symbol} Mean Reversion Strategy')
        plt.legend()
        plt.grid(True)
        
        # 子图2：累计收益
        plt.subplot(2, 1, 2)
        plt.plot(data.index, data['Portfolio_Value'], label='Portfolio Value', color='blue')
        plt.axhline(y=100000, color='gray', linestyle='--', label='Initial Capital')
        plt.title('Portfolio Performance')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def run_strategy(self, start_date, end_date, initial_capital=100000):
        """运行完整策略"""
        # 获取数据
        data = self.fetch_data(start_date, end_date)
        
        # 计算指标
        data = self.calculate_indicators(data)
        
        # 生成信号
        data = self.generate_signals(data)
        
        # 回测
        data = self.backtest(data, initial_capital)
        
        # 绘制结果
        self.plot_results(data)
        
        return data

# 使用示例
if __name__ == "__main__":
    # 创建策略实例
    strategy = MeanReversionStrategy('AAPL', window=20, std_multiplier=2)
    
    # 设置时间范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1年数据
    
    # 运行策略
    results = strategy.run_strategy(start_date, end_date, initial_capital=100000)
    
    # 输出策略统计
    total_return = results['Portfolio_Value'].iloc[-1] / 100000 - 1
    print(f"总收益率: {total_return:.2%}")
    print(f"年化收益率: {(1 + total_return)**(365/len(results)) - 1:.2%}")
```

## 💡 实战应用

### 1. 布林带均值回归策略
布林带是最常用的均值回归指标之一。当价格触及或突破布林带上下轨时，往往意味着价格过度偏离，有回归中轨的需求。实战中，可以结合成交量确认信号，当价格突破下轨时成交量放大，可能预示着底部形成。

### 2. RSI均值回归策略
RSI指标通过测量价格变动的速度和幅度，判断市场超买超卖状态。当RSI低于30时认为市场超卖，高于70时认为超买。均值回归策略可以在RSI极端区域寻找反转机会，但需要结合趋势方向避免在强趋势中逆势操作。

### 3. 统计套利配对交易
均值回归策略在配对交易中应用广泛。通过找到相关性高的两只股票，当它们的价格比率偏离历史均值时，做多相对低估的股票，做空相对高估的股票，等待比率回归正常时平仓获利。这种策略可以有效对冲市场风险。

### 4. 波动率调整
不同资产的波动特性不同，需要根据历史波动率调整策略参数。高波动率资产可以使用更宽的布林带（如2.5倍标准差），低波动率资产可以使用较窄的布林带（如1.5倍标准差）。

## ⚠️ 常见陷阱

### 1. 趋势陷阱
在强趋势市场中，均值回归策略可能会持续亏损。当市场处于明显的上升或下降趋势时，价格可能长时间偏离均值而不回归。此时应该避免使用纯均值回归策略，或者结合趋势过滤条件。

### 2. 过度拟合陷阱
过度优化历史参数可能导致策略在实盘中表现不佳。例如，过分追求历史最高收益率而选择过于激进的参数，可能导致实盘中频繁交易和大幅回撤。应该使用稳健的参数选择方法和样本外测试。

### 3. 流动性陷阱
在低流动性市场中，即使价格偏离均值，也可能因为缺乏对手方而无法顺利成交。特别是在小盘股或交易量极低的品种中，需要考虑流动性因素和冲击成本。

### 4. 黑天鹅事件
极端市场条件下，传统的均值回归模型可能失效。在金融危机、突发事件等情况下，价格可能永久性地偏离历史均值，此时机械地应用均值回归策略会导致巨大亏损。

### 5. 忽略交易成本
频繁的均值回归交易会产生大量的交易成本，包括佣金、滑点等。如果策略的盈利空间不足以覆盖交易成本，长期来看可能是亏损的。需要在回测中充分考虑交易成本的影响。

## 🎯 今日小练习

### 练习1：布林带参数优化
使用历史数据测试不同参数组合下的布林带策略表现：
- 窗口期：10, 20, 30, 50
- 标准差倍数：1.5, 2.0, 2.5, 3.0
- 找出最优参数组合并分析其稳定性

### 练习2：多时间框架分析
在同一只股票上应用不同时间框架的均值回归策略：
- 短期：5日均线，1倍标准差
- 中期：20日均线，2倍标准差  
- 长期：60日均线，2倍标准差
- 分析不同时间框架信号的协调性

### 练习3：风险调整收益计算
计算策略的以下风险指标：
- 夏普比率（Sharpe Ratio）
- 最大回撤（Maximum Drawdown）
- 索提诺比率（Sortino Ratio）
- 卡玛比率（Calmar Ratio）
- 分析策略的风险收益特征

### 练习4：动态参数调整
研究如何根据市场波动率动态调整布林带参数：
- 使用ATR（平均真实波幅）调整标准差倍数
- 根据市场波动率状态切换策略参数
- 测试动态参数策略的表现

## 🔗 参考来源

1. **CMC Markets - Mean Reversion Trading Strategies**
   https://www.cmcmarkets.com/en-gb/trading-strategy/mean-reversion
   - 权威金融教育平台提供的均值回归策略详解，包含理论基础和实战应用

2. **TradeFundrr - Mean Reversion Trading Techniques: A Complete Guide**
   https://tradefundrr.com/mean-reversion-trading-techniques/
   - 详细的均值回归交易技术指南，涵盖策略原理、实施方法和风险控制

3. **知乎专栏 - 均值回归：10个实战交易策略**
   https://zhuanlan.zhihu.com/p/1979225320151335736
   - 中文市场环境下均值回归策略的实战分析和案例分享

---
*本系列内容由量化交易教学助手天天制作，持续更新中...*