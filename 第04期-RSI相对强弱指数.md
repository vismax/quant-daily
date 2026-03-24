# 量化学习第04期：RSI — 超买超卖指标

> 📅 2026-03-24 | 每天一篇，从零到一

---

## 📌 一句话概括

RSI（相对强弱指数）衡量的是价格"涨得有多猛还是跌得有多狠"，用 0-100 的分数告诉你市场是过热还是过冷。

---

## 📖 概念详解

RSI（Relative Strength Index）由 J. Welles Wilder Jr. 于 1978 年在《New Concepts in Technical Trading Systems》中首次提出。Wilder 本是房地产工程师，38 岁退休后转行期货交易，因为觉得当时的分析工具太粗糙，于是自己动手发明了 RSI、ATR、ADX 等一系列经典指标。

RSI 的核心思想是**自我比较**——不是和别的股票比，而是和自己最近的价格变化比。它计算一段时间内平均涨幅与平均跌幅的比值，将结果映射到 0-100 之间。RSI 不是告诉你"价格高不高"，而是告诉你"上涨动能强不强"。

- **RSI > 70**：传统上认为超买（Overbought），市场过热
- **RSI < 30**：传统上认为超卖（Oversold），市场过冷
- **RSI = 50**：多空分界线

⚠️ 但在强趋势中，RSI 可以长时间停留在超买/超卖区域。牛市中 RSI 会在 40-90 之间波动，熊市中则在 10-60 之间。因此绝不能机械地"70 就卖、30 就买"。

---

## 📐 数学公式

### Step 1：计算价格变动

$$\Delta_t = Close_t - Close_{t-1}$$

### Step 2：分离涨跌

$$Gain_t = \max(\Delta_t, 0), \quad Loss_t = \max(-\Delta_t, 0)$$

### Step 3：计算初始平均涨跌幅（以 14 期为例）

$$AvgGain_0 = \frac{1}{14}\sum_{i=1}^{14} Gain_i, \quad AvgLoss_0 = \frac{1}{14}\sum_{i=1}^{14} Loss_i$$

### Step 4：递推计算（Wilder 平滑法，类似 EMA）

$$AvgGain_t = \frac{AvgGain_{t-1} \times 13 + Gain_t}{14}$$

$$AvgLoss_t = \frac{AvgLoss_{t-1} \times 13 + Loss_t}{14}$$

### Step 5：计算 RS 和 RSI

$$RS = \frac{AvgGain}{AvgLoss}$$

$$\boxed{RSI = 100 - \frac{100}{1 + RS}}$$

> **直觉理解**：RS 是"平均涨"除以"平均跌"。RS = 1 时 RSI = 50（多空均衡）；RS 越大 RSI 越高，说明涨的动能越强。

---

## 🐍 Python 代码实战

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# ========== 1. 手动计算 RSI（理解原理） ==========
def calculate_rsi(prices, period=14):
    """手动实现 RSI，使用 Wilder 平滑法"""
    deltas = prices.diff()
    gain = deltas.clip(lower=0)
    loss = -deltas.clip(upper=0)

    # 初始均值（简单移动平均）
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Wilder 递推平滑
    for i in range(period, len(prices)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ========== 2. 获取数据 ==========
data = yf.download("AAPL", start="2025-01-01", end="2026-03-24")
prices = data["Close"]

# ========== 3. 计算 RSI ==========
rsi = calculate_rsi(prices, period=14)

# ========== 4. 简单 RSI 策略信号 ==========
# 买入：RSI 从下方穿过 30（超卖反弹）
# 卖出：RSI 从上方穿过 70（超买回落）
buy_signal = (rsi.shift(1) < 30) & (rsi >= 30)
sell_signal = (rsi.shift(1) > 70) & (rsi <= 70)

# ========== 5. 回测 ==========
position = 0
returns = []
buy_dates, sell_dates = [], []

for i in range(1, len(prices)):
    if buy_signal.iloc[i] and position == 0:
        position = 1
        buy_dates.append(prices.index[i])
    elif sell_signal.iloc[i] and position == 1:
        position = 0
        sell_dates.append(prices.index[i])
        returns.append((prices.iloc[i] - prices.iloc[buy_dates[-1]]) / prices.iloc[buy_dates[-1]])

total_return = sum(returns)
win_rate = len([r for r in returns if r > 0]) / len(returns) * 100 if returns else 0

print(f"交易次数: {len(returns)}")
print(f"总收益率: {total_return:.2%}")
print(f"胜率: {win_rate:.1f}%")

# ========== 6. 可视化 ==========
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), height_ratios=[2, 1],
                                 sharex=True)

# 价格图
ax1.plot(prices.index, prices, label="Close", color="#2196F3", linewidth=1.5)
for bd in buy_dates:
    ax1.axvline(bd, color="green", alpha=0.3, linestyle="--")
for sd in sell_dates:
    ax1.axvline(sd, color="red", alpha=0.3, linestyle="--")
ax1.set_ylabel("Price ($)")
ax1.set_title("AAPL Price with RSI Strategy Signals")
ax1.legend()
ax1.grid(alpha=0.3)

# RSI 图
ax2.plot(rsi.index, rsi, label="RSI(14)", color="#FF9800", linewidth=1.5)
ax2.axhline(y=70, color="red", linestyle="--", alpha=0.7, label="Overbought (70)")
ax2.axhline(y=30, color="green", linestyle="--", alpha=0.7, label="Oversold (30)")
ax2.axhline(y=50, color="gray", linestyle="-", alpha=0.3, label="Neutral (50)")
ax2.fill_between(rsi.index, 70, 100, alpha=0.1, color="red")
ax2.fill_between(rsi.index, 0, 30, alpha=0.1, color="green")
ax2.set_ylabel("RSI")
ax2.set_xlabel("Date")
ax2.legend(loc="upper left")
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("rsi_strategy.png", dpi=150)
plt.show()
```

---

## 💡 实战应用

### 1. 超买超卖信号（基础用法）
- RSI < 30 后回升穿越 30 → 买入信号
- RSI > 70 后回落穿越 70 → 卖出信号

### 2. RSI 背离（进阶用法）
- **顶背离**：价格创新高，但 RSI 没有创新高 → 上涨动能衰竭，可能反转
- **底背离**：价格创新低，但 RSI 没有创新低 → 下跌动能衰竭，可能反弹
- 背离比超买超卖信号更可靠，但需要等待价格确认

### 3. RSI 区间交易
- 在横盘震荡行情中，RSI 的超买超卖信号准确率较高
- 在强趋势行情中，RSI 可能长时间停留在极值区域，此时信号不可靠

### 4. 多周期 RSI 配合
- 短期 RSI（如 6 日）灵敏但噪音多
- 长期 RSI（如 24 日）稳定但滞后
- 短期 RSI 穿越长期 RSI 可作为趋势确认

---

## ⚠️ 常见陷阱

| 陷阱 | 说明 | 应对方法 |
|------|------|----------|
| 强趋势中信号失效 | 牛市中 RSI 可长期 > 70，熊市中长期 < 30 | 结合趋势判断，顺势方向只取一侧信号 |
| 机械套用 70/30 | 不同股票、不同市场环境的超买超卖阈值不同 | 根据历史数据调整阈值，或使用动态阈值 |
| 频繁交易 | 震荡市中 RSI 反复穿越阈值导致过度交易 | 增加过滤条件，如等待 RSI 回到 50 后再入场 |
| 忽视背离确认 | 背离可能发生多次才真正反转 | 等待价格突破确认，不要在第一次背离就重仓 |
| 参数选择不当 | 14 期是默认值，不一定适合所有策略 | 测试不同周期，短期交易用 7-9，波段用 14-21 |

---

## 🎯 今日小练习

1. **基础题**：用 Python 手动计算贵州茅台（600519.SS）最近 100 天的 RSI，并标注超买超卖区间
2. **进阶题**：实现一个 RSI 背离检测函数，自动识别价格与 RSI 的顶背离和底背离
3. **思考题**：为什么在强上升趋势中 RSI > 70 不一定代表要卖出？试着用"动能"的角度解释

---

## 🔗 参考来源

- [Investopedia - Relative Strength Index (RSI)](https://www.investopedia.com/terms/r/rsi.asp)
- [Fidelity - RSI 技术指标详解](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/RSI)
- [Quant Wiki 中文量化百科 - RSI](https://quant-wiki.com/basic/quant/%E7%9B%B8%E5%AF%B9%E5%BC%BA%E5%BC%B1%E6%8C%87%E6%95%B0_Relative%20Strength%20Index/)
