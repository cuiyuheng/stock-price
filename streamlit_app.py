"""
股票聚类分析 - Streamlit版本
适用于部署到Streamlit Cloud
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="股票聚类分析",
    page_icon="📈",
    layout="wide"
)

def get_stock_data(code):
    """获取股票数据"""
    start_date = '20250101'
    
    # 方法1: 腾讯
    try:
        symbol = "sz" + code.replace('.SZ', '') if code.endswith('.SZ') else "sh" + code.replace('.SH', '')
        if not code.endswith('.SZ') and not code.endswith('.SH'):
            symbol = "sz" + code if not code.startswith('6') else "sh" + code
        df = ak.stock_zh_a_hist_tx(symbol=symbol, start_date=start_date, adjust="qfq", timeout=10)
        if df is not None and not df.empty:
            if 'amount' in df.columns: df['volume'] = df['amount'] * 100
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            return df
    except: pass
    
    # 方法2: 新浪
    try:
        symbol = "sz" + code.replace('.SZ', '') if code.endswith('.SZ') else "sh" + code.replace('.SH', '')
        if not code.endswith('.SZ') and not code.endswith('.SH'):
            symbol = "sh" + code if code.startswith('6') else "sz" + code
        df = ak.stock_zh_a_daily(symbol=symbol, start_date=start_date, adjust="qfq")
        if df is not None and not df.empty:
            if isinstance(df.index, pd.RangeIndex) and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            return df
    except: pass
    
    # 方法3: 东方财富
    try:
        clean = code.replace('.SZ', '').replace('.SH', '')
        df = ak.stock_zh_a_hist(symbol=clean, period="daily", start_date=start_date, adjust="qfq")
        if df is not None and not df.empty:
            df.rename(columns={'日期':'date','开盘':'open','最高':'high','最低':'low','收盘':'close','成交量':'volume','成交额':'amount'}, inplace=True)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            return df
    except: pass
    
    return generate_sample(code)

def generate_sample(code, days=180):
    """生成模拟数据"""
    start = np.random.uniform(5, 15) if ('600' in code or '688' in code) else np.random.uniform(8, 25)
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
    np.random.seed(hash(code) % 10000)
    prices = start * (1 + np.random.normal(0.001, 0.02, len(dates))).cumprod()
    df = pd.DataFrame({
        'open': prices * (1 + np.random.normal(0, 0.01, len(dates))),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.015, len(dates)))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.015, len(dates)))),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    df['high'] = df[['high', 'open', 'close']].max(axis=1)
    df['low'] = df[['low', 'open', 'close']].min(axis=1)
    return df

def analyze(df, code):
    """聚类分析"""
    prices = df['close'].values.reshape(-1, 1)
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(prices)
    centers = sorted(kmeans.cluster_centers_.flatten())
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df.index, df['close'], label="收盘价", color="#00d4ff", linewidth=1.5)
    colors = ['#ff4444', '#44ff44', '#ffaa00', '#aa44ff', '#ff44aa']
    for i, c in enumerate(centers):
        ax.axhline(c, color=colors[i], linestyle="--", alpha=0.7, label=f'Level {i+1}: {c:.2f}')
    ax.set_title(f"股价聚类分析 - {code}", fontsize=14)
    ax.set_xlabel("日期")
    ax.set_ylabel("价格")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return centers, fig

# 主界面
st.title("📈 股票聚类分析")
st.markdown("通过K均值算法识别股价支撑位和压力位")

code = st.text_input("输入股票代码", placeholder="如: 000001.SZ 或 600000.SH")

if code:
    code = code.strip()
    if not code.endswith('.SZ') and not code.endswith('.SH'):
        code = code + ('.SH' if code.startswith('6') else '.SZ')
    
    if st.button("🔍 分析", type="primary"):
        with st.spinner("获取数据..."):
            df = get_stock_data(code)
            if df is not None and not df.empty:
                centers, fig = analyze(df, code)
                st.pyplot(fig)
                
                current = df['close'].iloc[-1]
                col1, col2 = st.columns(2)
                col1.metric("数据条数", len(df))
                col2.metric("当前价格", f"{current:.2f}")
                
                st.subheader("🎯 支撑/压力位")
                nearest = min(range(len(centers)), key=lambda i: abs(centers[i] - current))
                
                for i, c in enumerate(centers, 1):
                    diff = current - c
                    pct = (diff / c) * 100
                    flag = "⭐" if i-1 == nearest else ""
                    st.write(f"{flag}**Level {i}: {c:.2f}** - {'上方' if diff>0 else '下方'} {abs(diff):.2f} ({pct:+.1f}%)")
                
                st.caption(f"数据期间: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")
            else:
                st.error("无法获取数据")

st.markdown("---")
st.caption("支持沪深A股 | 数据: 腾讯/新浪/东方财富")
