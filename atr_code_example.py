import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

def calculate_atr(high, low, close, period=14):
    """
    计算平均真实波幅（ATR）
    
    参数:
    high -- 最高价序列
    low -- 最低价序列  
    close -- 收盘价序列
    period -- ATR计算周期，默认14
    
    返回:
    atr -- ATR值序列
    """
    # 计算真实波幅（TR）
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    
    # 计算ATR
    atr = tr.rolling(window=period).mean()
    
    return atr

def atr_trading_strategy(data, atr_multiplier=2):
    """
    基于ATR的交易策略
    
    参数:
    data -- 包含价格数据的DataFrame
    atr_multiplier -- ATR倍数，用于设置止损
    
    返回:
    signals -- 交易信号
    """
    df = data.copy()
    
    # 计算ATR
    df['ATR'] = calculate_atr(df['High'], df['Low'], df['Close'])
    
    # 设置动态止损
    df['Stop_Loss_Long'] = df['Close'] - (df['ATR'] * atr_multiplier)
    df['Stop_Loss_Short'] = df['Close'] + (df['ATR'] * atr_multiplier)
    
    # 设置入场信号（简化版）
    df['Signal'] = 0
    # 当价格突破前高且ATR上升时做多
    df.loc[(df['Close'] > df['Close'].shift(1)) & (df['ATR'] > df['ATR'].shift(1)), 'Signal'] = 1
    # 当价格跌破前低且ATR上升时做空
    df.loc[(df['Close'] < df['Close'].shift(1)) & (df['ATR'] > df['ATR'].shift(1)), 'Signal'] = -1
    
    return df

def plot_atr_analysis(data):
    """
    绘制ATR分析图表
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # 价格和ATR止损线
    ax1.plot(data['Close'], label='Close Price', color='blue', alpha=0.7)
    ax1.plot(data['Stop_Loss_Long'], label='Stop Loss Long', color='red', linestyle='--')
    ax1.plot(data['Stop_Loss_Short'], label='Stop Loss Short', color='green', linestyle='--')
    ax1.set_title('Price with ATR-based Stop Loss')
    ax1.legend()
    ax1.grid(True)
    
    # ATR值
    ax2.plot(data['ATR'], label='ATR', color='purple')
    ax2.set_title('Average True Range')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('/root/codespace/quant-daily/atr_analysis.png')
    plt.close()

def main():
    # 获取股票数据
    ticker = 'AAPL'
    data = yf.download(ticker, start='2023-01-01', end='2024-01-01')
    
    # 计算ATR和交易信号
    strategy_data = atr_trading_strategy(data)
    
    # 绘制图表
    plot_atr_analysis(strategy_data)
    
    # 显示最近20天的数据
    print(f"\n{ticker} ATR分析（最近20天）：")
    print(strategy_data[['Close', 'ATR', 'Stop_Loss_Long', 'Stop_Loss_Short', 'Signal']].tail(20))
    
    # 计算一些统计信息
    print(f"\nATR统计信息：")
    print(f"ATR均值: {strategy_data['ATR'].mean():.2f}")
    print(f"ATR最大值: {strategy_data['ATR'].max():.2f}")
    print(f"ATR最小值: {strategy_data['ATR'].min():.2f}")
    
    # 计算波动率等级
    atr_mean = strategy_data['ATR'].mean()
    current_atr = strategy_data['ATR'].iloc[-1]
    
    if current_atr > atr_mean * 1.5:
        volatility_level = "高波动"
    elif current_atr > atr_mean * 0.8:
        volatility_level = "中等波动"
    else:
        volatility_level = "低波动"
    
    print(f"\n当前波动状态: {volatility_level}")
    print(f"当前ATR: {current_atr:.2f}")
    print(f"平均ATR: {atr_mean:.2f}")

if __name__ == "__main__":
    main()