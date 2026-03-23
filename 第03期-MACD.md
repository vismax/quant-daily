# 量化学习第03期：MACD — 趋势的"心跳"

## 📌 一句话概括
MACD（指数平滑异同移动平均线）通过比较两条不同周期 EMA 的差值及其变化速率，捕捉市场趋势的方向与动量转折，是量化交易中最经典的技术指标之一。

---

## 📖 概念详解

### 什么是 MACD？

MACD 全称 Moving Average Convergence Divergence（指数平滑异同移动平均线），由美国技术分析大师 Gerald Appel 于 1970 年代提出。它的核心思想很简单：**当短期均线和长期均线之间的距离在扩大时，趋势在加强；距离在缩小时，趋势在减弱。**

MACD 指标由三个部分组成：

| 组件 | 别名 | 含义 |
|------|------|------|
| **MACD 线（DIF）** | 快线 | 短期 EMA 与长期 EMA 的差值 |
| **信号线（DEA）** | 慢线 | MACD 线的 EMA（通常是 9 日） |
| **MACD 柱状图** | 柱体 | MACD 线与信号线的差值 × 2 |

### MACD 的交易逻辑

MACD 的本质是一个**动量振荡器**。它回答的核心问题是：趋势是在加速还是减速？

- **DIF > 0**（MACD 线在零轴上方）：短期价格高于长期价格，市场偏多头
- **DIF < 0**（MACD 线在零轴下方）：短期价格低于长期价格，市场偏空头
- **DIF 上穿信号线（金叉）**：多头力量增强，买入信号
- **DIF 下穿信号线（死叉）**：空头力量增强，卖出信号
- **柱状图由负转正**：空转多，趋势反转信号
- **柱状图由正转负**：多转空，趋势反转信号

---

## 📐 数学公式

### 标准参数（12, 26, 9）

**第一步：计算 EMA**

$$EMA_t = \alpha \cdot P_t + (1 - \alpha) \cdot EMA_{t-1}$$

其中 $\alpha = \frac{2}{N+1}$，$N$ 为周期，$P_t$ 为当日收盘价。

**第二步：计算 DIF（MACD 线）**

$$DIF_t = EMA_{12,t} - EMA_{26,t}$$

**第三步：计算 DEA（信号线）**

$$DEA_t = EMA_9(DIF_t) = \frac{2}{10} \cdot DIF_t + \frac{8}{10} \cdot DEA_{t-1}$$

**第四步：计算 MACD 柱状图**

$$MACD\_Histogram_t = 2 \times (DIF_t - DEA_t)$$

> 乘以 2 是为了让柱状图的数值更直观，放大差异以便观察。

---

## 🐍 Python 代码实战

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ========== 方法一：手动计算（理解原理） ==========
def ema(series, period):
    """计算指数移动平均线"""
    alpha = 2 / (period + 1)
    result = [series.iloc[0]]
    for i in range(1, len(series)):
        result.append(alpha * series.iloc[i] + (1 - alpha) * result[-1])
    return pd.Series(result, index=series.index)

def calculate_macd(close, fast=12, slow=26, signal=9):
    """
    手动计算 MACD 指标
    :param close: 收盘价 Series
    :param fast: 短期 EMA 周期，默认 12
    :param slow: 长期 EMA 周期，默认 26
    :param signal: 信号线 EMA 周期，默认 9
    :return: DataFrame 包含 dif, dea, macd 三列
    """
    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)
    dif = ema_fast - ema_slow       # MACD 线（快线）
    dea = ema(dif, signal)           # 信号线（慢线）
    macd_bar = 2 * (dif - dea)       # MACD 柱状图
    return pd.DataFrame({'dif': dif, 'dea': dea, 'macd': macd_bar})

# ========== 方法二：使用 pandas_ta 库（生产推荐） ==========
# pip install pandas_ta
# import pandas_ta as ta
# df.ta.macd(12, 26, 9, append=True)
# 会自动生成 MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9 三列

# ========== 模拟数据 + 可视化 ==========
np.random.seed(42)
n = 200
# 生成模拟价格：随机游走 + 趋势
returns = np.random.randn(n) * 0.02
price = 100 * np.exp(np.cumsum(returns + 0.001))  # 轻微上升趋势
dates = pd.date_range('2025-01-01', periods=n, freq='B')
df = pd.DataFrame({'close': price}, index=dates)

# 计算 MACD
macd_df = calculate_macd(df['close'])
df = df.join(macd_df)

# ========== 生成交易信号 ==========
df['signal'] = 0
# 金叉买入：DIF 上穿 DEA
df.loc[(df['dif'] > df['dea']) & (df['dif'].shift(1) <= df['dea'].shift(1)), 'signal'] = 1
# 死叉卖出：DIF 下穿 DEA
df.loc[(df['dif'] < df['dea']) & (df['dif'].shift(1) >= df['dea'].shift(1)), 'signal'] = -1

# 计算策略收益
df['returns'] = df['close'].pct_change()
df['strategy_returns'] = df['signal'].shift(1) * df['returns']
df['cum_market'] = (1 + df['returns']).cumprod()
df['cum_strategy'] = (1 + df['strategy_returns']).cumprod()

# ========== 可视化 ==========
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True,
                          gridspec_kw={'height_ratios': [2, 1, 1]})

# 图1：价格 + 买卖信号
ax1 = axes[0]
ax1.plot(df.index, df['close'], label='价格', color='#333', linewidth=1.2)
buy_signals = df[df['signal'] == 1]
sell_signals = df[df['signal'] == -1]
ax1.scatter(buy_signals.index, buy_signals['close'], marker='^',
            color='red', s=100, label='买入信号', zorder=5)
ax1.scatter(sell_signals.index, sell_signals['close'], marker='v',
            color='green', s=100, label='卖出信号', zorder=5)
ax1.set_title('MACD 交易策略演示', fontsize=14, fontweight='bold')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)

# 图2：MACD 线 + 信号线
ax2 = axes[1]
ax2.plot(df.index, df['dif'], label='DIF (快线)', color='#1E88E5', linewidth=1)
ax2.plot(df.index, df['dea'], label='DEA (慢线)', color='#FF6F00', linewidth=1)
ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax2.legend(loc='upper left')
ax2.set_title('MACD 线与信号线', fontsize=11)
ax2.grid(True, alpha=0.3)

# 图3：MACD 柱状图
ax3 = axes[2]
colors = ['#E53935' if v >= 0 else '#1E88E5' for v in df['macd']]
ax3.bar(df.index, df['macd'], color=colors, width=1, alpha=0.7)
ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax3.set_title('MACD 柱状图', fontsize=11)
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('macd_strategy.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"买入信号次数: {(df['signal'] == 1).sum()}")
print(f"卖出信号次数: {(df['signal'] == -1).sum()}")
print(f"市场累计收益: {df['cum_market'].iloc[-1]:.4f}")
print(f"策略累计收益: {df['cum_strategy'].iloc[-1]:.4f}")
```

---

## 💡 实战应用

### 1. 经典金叉死叉策略
最基本的用法：DIF 上穿 DEA 买入，下穿卖出。简单但滞后，建议结合其他指标过滤。

### 2. 零轴判断多空格局
- DIF 和 DEA 都在零轴**上方**运行 → 强多头，逢低做多
- DIF 和 DEA 都在零轴**下方**运行 → 强空头，逢高做空
- 在零轴附近金叉/死叉的信号**比远离零轴的信号更可靠**

### 3. 背离信号（进阶）
- **顶背离**：价格创新高，MACD 没有创新高 → 多头动能衰竭，警惕回调
- **底背离**：价格创新低，MACD 没有创新低 → 空头动能衰竭，关注反弹
- 背离是 MACD 最有价值的高级用法，但需要大量练习来识别

### 4. 柱状图观察动量变化
柱状图的**高度变化**比方向变化更有参考意义：
- 柱状图逐根变短 → 动量在衰减
- 柱状图从极值开始缩回 → 趋势可能接近转折

---

## ⚠️ 常见陷阱

### ❌ 1. 滞后性是 MACD 的先天缺陷
MACD 基于移动平均线计算，本质是**滞后指标**。等到金叉确认时，一波上涨可能已经走了一半。**不要指望 MACD 抄到最低点。**

### ❌ 2. 震荡市中频繁假信号
在横盘震荡行情中，MACD 会在零轴附近反复交叉，产生大量假信号。**MACD 适合趋势行情，不适合震荡行情。**

### ❌ 3. 参数过度优化
不同的 fast/slow/signal 参数组合会产生完全不同的结果。不要用历史数据拟合出一组"完美参数"就以为找到了圣杯——很可能是过拟合。

### ❌ 4. 单一指标决策
MACD 只反映动量，不反映支撑阻力、成交量、市场情绪等。至少搭配一个非同类指标（如成交量或 RSI）做交叉验证。

---

## 🎯 今日小练习

**题目：手动验证 MACD 计算**

给定以下 5 天的收盘价序列：`[100, 102, 105, 103, 108]`

1. 手动计算 3 日 EMA（提示：$\alpha = \frac{2}{4} = 0.5$，第一天 EMA = 第一天收盘价）
2. 计算 3 日 DIF（假设 3 日快线 EMA - 模拟的 5 日慢线 EMA）
3. 观察这 5 天中 DIF 的变化趋势是加速上升还是减速上升？

**加分挑战：** 用上面的 Python 代码，将模拟数据改为某只 A 股的真实数据（用 `akshare` 获取），观察 MACD 策略在真实数据上的表现。

---

## 🔗 参考来源

1. [量化通 - MACD 指標完整教學](https://quantpass.org/macd-2/) — 台湾量化通提供的 MACD 完整教程，公式清晰
2. [Alpharithms - Calculating the MACD in Python](https://www.alpharithms.com/calculate-macd-python-272222/) — Python 算法交易 MACD 实战
3. [量化投资进阶：MACD指标的量化交易实战指南 - 百度智能云](https://cloud.baidu.com/article/3790667) — 中文 MACD 量化策略回测指南
