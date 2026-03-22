# 📚 量化学习第02期：EMA 与 SMA 的区别及选择

> 2026-03-22 | 移动平均线家族的第二课

---

## 📌 一句话概括

SMA（简单移动平均）像「全班平均分」，每科权重一样；EMA（指数移动平均）像「期末加权平均」，最近的考试成绩占比更大——所以 EMA 对价格变化反应更快。

---

## 📖 概念详解

### SMA：简单移动平均（Simple Moving Average）

昨天我们已经学过了 SMA，今天简要回顾。SMA 就是把过去 N 个周期的收盘价加起来除以 N：

```
5日 SMA = (P1 + P2 + P3 + P4 + P5) / 5
```

它的核心特点：**每个数据点权重完全相等**。10 天前的价格和昨天的价格，影响力一模一样。

这就像一个没有记忆的系统——它只关心窗口里的数据「在场」，不管谁先来谁后来。

### EMA：指数移动平均（Exponential Moving Average）

EMA 的关键区别在于**指数递减的权重分配**：越近的价格，权重越大，越远的价格，权重越小，而且衰减是指数级的（不是线性的）。

用一个程序员能理解的类比：

- **SMA** → `deque(maxlen=N).mean()` —— 一个固定大小的滑动窗口，先进先出，权重相同
- **EMA** → 类似带衰减因子的递推公式 —— 不需要存历史数据，靠一个状态变量 + 新数据就能更新

这也是 EMA 在工程上的一大优势：**内存效率高**。计算 200 日 SMA 需要保留 200 个数据点，而计算 200 日 EMA 只需要保留上一次的 EMA 值。

### 两者延迟对比

| 特性 | SMA | EMA |
|------|-----|-----|
| 权重分配 | 等权 | 近期权重高，远期指数衰减 |
| 对价格变化反应速度 | 慢（延迟大） | 快（延迟小） |
| 信号噪声比 | 高（更平滑） | 较低（更灵敏但可能抖动） |
| 适合时间框架 | 长期趋势判断 | 短期交易、突破捕捉 |
| 计算复杂度 | O(N) 每次计算 | O(1) 递推更新 |
| 代表场景 | 200日均线判断牛熊 | 日内/短线 EMA 金叉死叉 |

一个直观的感受：当价格突然大涨时，EMA 会比 SMA 更快地「跟上」，但这也意味着 EMA 在震荡行情中更容易产生**假信号**。

---

## 📐 数学公式

### SMA 公式

```
SMA_N(t) = (1/N) × Σ P(t-i)    for i = 0 to N-1
```

- `N`：周期长度（如 5、20、50、200）
- `P(t-i)`：第 t-i 期的收盘价
- `t`：当前时间点

### EMA 公式

EMA 的计算分两步：

**第一步：计算平滑系数（Multiplier）**

```
α = 2 / (N + 1)
```

- `N`：EMA 的周期（和 SMA 一样，如 12、26、50）
- `α`：也叫平滑因子（smoothing factor），决定了新数据的权重

> ⚠️ 注意：α 不是一个固定值，它随 N 变化。N=10 时 α≈0.182，N=50 时 α≈0.039。

**第二步：递推计算**

```
EMA(t) = α × P(t) + (1 - α) × EMA(t-1)
```

- `P(t)`：今天的收盘价
- `EMA(t-1)`：昨天的 EMA 值
- `α`：今天的权重
- `1 - α`：昨天的 EMA 的权重

**初始值问题：** 第一天没有 EMA(t-1)，通常用**前 N 日的 SMA** 作为初始 EMA 值。

### 用递推展开理解权重分配

如果我们把递推公式展开：

```
EMA(t) = α × P(t) + (1-α) × [α × P(t-1) + (1-α) × EMA(t-2)]
        = α × P(t) + α(1-α) × P(t-1) + α(1-α)² × P(t-2) + ...
```

可以看到：
- 今天 P(t) 的权重 = α（最大）
- 昨天的权重 = α(1-α)
- 前天的权重 = α(1-α)²
- 每往前推一天，权重乘以 (1-α)

这就是「指数衰减」名字的由来。

---

## 🐍 Python 代码实战

```python
"""
EMA vs SMA 完整实战
对比两种移动平均线在 A 股上的表现
"""

import akshare as ak
import pandas as pd
import matplotlib.pyplot as plt

# ========== 1. 获取真实 A 股数据 ==========
print("获取贵州茅台(600519)近250个交易日的数据...")
df = ak.stock_zh_a_hist(
    symbol="600519",
    period="daily",
    start_date="20250301",
    end_date="20260322",
    adjust="qfq"  # 前复权
)

# 只保留需要的列，重命名方便操作
df = df[["日期", "收盘", "开盘", "最高", "最低", "成交量"]]
df.columns = ["date", "close", "open", "high", "low", "volume"]
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").sort_index()

print(f"共获取 {len(df)} 个交易日数据\n")

# ========== 2. 计算 SMA ==========
N = 20  # 周期设为 20 日
df[f"SMA_{N}"] = df["close"].rolling(window=N).mean()

# ========== 3. 手动计算 EMA（理解原理） ==========
alpha = 2 / (N + 1)
print(f"EMA 周期: {N}")
print(f"平滑系数 α = 2/({N}+1) = {alpha:.6f}")
print(f"即今天的收盘价权重为 {alpha*100:.2f}%，历史均值的权重为 {(1-alpha)*100:.2f}%\n")

# 用 SMA 作为初始值
df[f"EMA_{N}_manual"] = df["close"].rolling(window=N).mean()  # 初始 N 日用 SMA

# 从第 N+1 天开始递推
for i in range(N, len(df)):
    today_close = df["close"].iloc[i]
    yesterday_ema = df[f"EMA_{N}_manual"].iloc[i - 1]
    df.loc[df.index[i], f"EMA_{N}_manual"] = alpha * today_close + (1 - alpha) * yesterday_ema

# ========== 4. 用 pandas 验证（内置 EWM） ==========
# pandas 的 ewm 使用 span 参数，span = N 时等价于 α = 2/(N+1)
df[f"EMA_{N}_pandas"] = df["close"].ewm(span=N, adjust=False).mean()

# 验证手动计算和 pandas 内置是否一致
diff = (df[f"EMA_{N}_manual"] - df[f"EMA_{N}_pandas"]).abs().max()
print(f"手动计算 vs pandas 内置 最大差异: {diff:.10f}")
print(f"验证结果: {'✅ 完全一致' if diff < 1e-8 else '❌ 存在差异'}\n")

# ========== 5. 计算不同周期的 EMA 用于对比 ==========
for period in [5, 10, 20, 50]:
    df[f"EMA_{period}"] = df["close"].ewm(span=period, adjust=False).mean()
    df[f"SMA_{period}"] = df["close"].rolling(window=period).mean()

# ========== 6. 策略信号：EMA 金叉/死叉 ==========
ema_fast = df["EMA_5"]
ema_slow = df["EMA_20"]

df["signal"] = 0
df.loc[ema_fast > ema_slow, "signal"] = 1   # 金叉持有
df.loc[ema_fast < ema_slow, "signal"] = -1  # 死叉空仓

# 标记交叉点
df["cross"] = df["signal"].diff()
golden_cross = df[df["cross"] == 2]   # 从 -1 变 1
death_cross = df[df["cross"] == -2]   # 从 1 变 -1

print(f"EMA(5)/EMA(20) 交叉策略回测结果：")
print(f"  金叉次数: {len(golden_cross)}")
print(f"  死叉次数: {len(death_cross)}")
if not golden_cross.empty:
    print(f"  最近金叉日期: {golden_cross.index[-1].strftime('%Y-%m-%d')}")
if not death_cross.empty:
    print(f"  最近死叉日期: {death_cross.index[-1].strftime('%Y-%m-%d')}\n")

# ========== 7. 简单收益计算 ==========
df["daily_return"] = df["close"].pct_change()
df["strategy_return"] = df["signal"].shift(1) * df["daily_return"]

total_market = (1 + df["daily_return"].dropna()).prod()
total_strategy = (1 + df["strategy_return"].dropna()).prod()

print(f"期间买入持有收益: {(total_market - 1)*100:.2f}%")
print(f"EMA交叉策略收益:  {(total_strategy - 1)*100:.2f}%\n")

# ========== 8. 可视化 ==========
fig, axes = plt.subplots(3, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [3, 1.5, 1]})

# 子图1：价格 + SMA + EMA
ax1 = axes[0]
ax1.plot(df.index, df["close"], label="收盘价", color="black", linewidth=1, alpha=0.7)
ax1.plot(df.index, df[f"SMA_{N}"], label=f"SMA({N})", color="blue", linewidth=1.5, linestyle="--")
ax1.plot(df.index, df[f"EMA_{N}"], label=f"EMA({N})", color="red", linewidth=1.5)
ax1.plot(df.index, df["EMA_5"], label="EMA(5)", color="orange", linewidth=1, alpha=0.8)
ax1.plot(df.index, df["EMA_50"], label="EMA(50)", color="purple", linewidth=1, alpha=0.8)

# 标记交叉点
ax1.scatter(golden_cross.index, golden_cross["close"],
            marker="^", color="red", s=100, zorder=5, label="金叉(买入)")
ax1.scatter(death_cross.index, death_cross["close"],
            marker="v", color="green", s=100, zorder=5, label="死叉(卖出)")

ax1.set_title("贵州茅台(600519) — SMA vs EMA 对比", fontsize=14)
ax1.legend(loc="upper left", fontsize=9)
ax1.grid(True, alpha=0.3)

# 子图2：信号
ax2 = axes[1]
for i in range(len(df)):
    color = "red" if df["signal"].iloc[i] == 1 else "green" if df["signal"].iloc[i] == -1 else "gray"
    ax2.bar(df.index[i], df["signal"].iloc[i], color=color, width=1)
ax2.set_title("EMA(5)/EMA(20) 交易信号", fontsize=11)
ax2.set_yticks([-1, 0, 1])
ax2.set_yticklabels(["死叉/空仓", "无信号", "金叉/持有"])
ax2.grid(True, alpha=0.3)

# 子图3：累计收益对比
ax3 = axes[2]
cum_market = (1 + df["daily_return"].dropna()).cumprod()
cum_strategy = (1 + df["strategy_return"].dropna()).cumprod()
ax3.plot(cum_market.index, cum_market, label="买入持有", color="blue", linewidth=1.5)
ax3.plot(cum_strategy.index, cum_strategy, label="EMA交叉策略", color="red", linewidth=1.5)
ax3.set_title("累计收益对比", fontsize=11)
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("/tmp/ema_vs_sma.png", dpi=150, bbox_inches="tight")
print("图表已保存到 /tmp/ema_vs_sma.png")
```

### 关键代码解读

| 代码 | 含义 |
|------|------|
| `df["close"].rolling(N).mean()` | SMA：滑动窗口均值 |
| `df["close"].ewm(span=N, adjust=False).mean()` | EMA：指数加权移动平均 |
| `alpha = 2 / (N + 1)` | EMA 的平滑系数 |
| `ewm(span=N)` | span 参数就是周期 N，内部自动算 α |
| `adjust=False` | 使用递推公式（和我们手动算的一致） |

> 💡 `adjust=True`（默认）会用完整历史数据加权，结果更精确但计算量更大。`adjust=False` 用递推公式，更贴近实际交易场景。

---

## 💡 实战应用

### 1. 经典黄金交叉 / 死亡交叉

最常见的用法是**双均线交叉**：

- **金叉**：短期 EMA 上穿长期 EMA → 买入信号
- **死叉**：短期 EMA 下穿长期 EMA → 卖出信号

常用参数组合：
- EMA(5) / EMA(20)：适合短线
- EMA(12) / EMA(26)：MACD 的基础（明天讲！）
- EMA(20) / EMA(50)：适合中线
- SMA(50) / SMA(200)：经典的「牛熊分界线」

### 2. 最佳实践：SMA + EMA 混合使用

很多成熟交易者的做法是**不要只选一个，而是组合使用**：

- 用**长期 SMA（如 200 日）** 判断大趋势方向（只在大趋势向上时做多）
- 用**短期 EMA（如 5 日、10 日）** 精确把握入场时机

这就像用 `git log --oneline` 看大方向（SMA），用 `git diff` 看细节变化（EMA）。

### 3. EMA 作为动态支撑/阻力

EMA 常常充当动态的支撑位和阻力位。在上升趋势中，价格回调到 EMA 附近往往有支撑；在下降趋势中，反弹到 EMA 附近往往有阻力。

### 4. 不同周期的选择建议

| 交易风格 | 推荐均线类型 | 推荐周期 |
|----------|------------|---------|
| 日内交易 | EMA | 5, 10, 20 |
| 波段交易 | EMA | 20, 50 |
| 中线投资 | SMA 或 EMA | 50, 100, 200 |
| 长期投资 | SMA | 200, 250 |

---

## ⚠️ 常见陷阱

### 1. 震荡行情中的「假交叉」

这是新手最容易踩的坑。在横盘震荡市中，EMA 因为灵敏度更高，会产生大量的假交叉信号——来回打脸，手续费都能把你磨死。

**解法：** 加一个趋势过滤条件，比如只在大周期 EMA 向上时才允许做多信号生效。或者配合 ADX 指标判断市场是否有明确趋势。

### 2. 参数过度优化

很多人会花大量时间「调参」，找到一组在过去表现完美的 EMA 周期组合——然后实盘就亏了。这是典型的**过拟合**。

**解法：** 用「常识性」的周期参数（5、10、20、50、200），不要用优化器去搜 7.3 天这种奇怪的参数。

### 3. 忽略 EMA 的「初始化效应」

EMA 的前 N 个数据点是不准确的（因为初始值用的是 SMA 估计）。如果你只看最近 30 天的数据去算 50 日 EMA，前半段的数据其实不太靠谱。

**解法：** 至少准备 `3 × N` 个数据点才开始认真使用 EMA 信号。

### 4. 把 EMA 当成预测工具

EMA 是**滞后指标**（lagging indicator），它反映的是已经发生的价格变化，不是预测未来。EMA 上穿不代表一定会涨，只是说明近期的价格重心在上移。

---

## 🎯 今日小练习

**任务：** 对比同一只股票在不同市场环境下的 SMA/EMA 表现

1. 选一只 A 股（比如 `akshare` 获取 000001 平安银行近 1 年数据）
2. 计算 20 日 SMA 和 20 日 EMA
3. 画在一张图上，找出两者差距最大的 3 个时间点
4. 思考：那些差距大的时刻，市场在发生什么？

提示：差距大意味着价格正在经历**快速变化**，EMA 更紧贴价格而 SMA 还在「追赶」。

```python
# 提示代码骨架
df["gap"] = df["EMA_20"] - df["SMA_20"]
top_gap_days = df["gap"].abs().nlargest(3)
print("EMA和SMA差距最大的3天：")
print(top_gap_days)
```

---

## 🔗 参考来源

- [EMA 指標完整教學 — 量化通](https://quantpass.org/ema/) — EMA 计算原理与实战教学
- [Simple Moving Average(SMA) and Exponential Moving Average(EMA) — Medium](https://medium.com/@muhammadsohaib3434/simple-moving-average-sma-and-exponential-moving-average-ema-c63e1372b129) — Python 实现代码参考
- [SMA Vs EMA — Online NIFM](https://www.onlinenifm.com/blog/post/288/technical-analysis/sma-vs-ema-simple-moving-average-or-exponential-moving-average) — 交易策略场景选择
- [EMA 图解：计算原理、与SMA区别 — Moneta Markets](https://www.monetamarkets.com/cn/strategy/what-is-ema-exponential-moving-average-trading-strategy/) — 对比表格与实战策略

---

*由天天整理 ☀️ 明晚见！*
