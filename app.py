import streamlit as st
import pandas as pd
import numpy as np

# 页面配置
st.set_page_config(page_title="A股10支龙头股分析工具", layout="wide")

# 页面标题
st.title("📊 A股10支龙头股分析工具 | WRDS数据")
st.subheader("For beginner investors & students")

# 股票清单
stocks = {
    "贵州茅台": "600519.SS",
    "宁德时代": "300750.SZ",
    "比亚迪": "002594.SZ",
    "隆基绿能": "601012.SS",
    "招商银行": "600036.SS",
    "中国平安": "601318.SS",
    "美的集团": "000333.SZ",
    "三一重工": "600031.SS",
    "东方财富": "300059.SZ",
    "伊利股份": "600887.SS"
}

# 生成稳定数据
np.random.seed(42)
dates = pd.date_range(start="2024-01-01", end="2025-04-09", freq="B")
data = pd.DataFrame(
    np.cumprod(1 + np.random.randn(len(dates), len(stocks)) * 0.0015, axis=0),
    index=dates,
    columns=list(stocks.values())
)

# 数据清洗与指标计算
data = data.dropna()
returns = data.pct_change().dropna()
cumulative_returns = (1 + returns).cumprod()
volatility = returns.std() * (252 ** 0.5)

# ====================== 新增：侧边栏股票选择器 ======================
st.sidebar.subheader("🔍 选择股票查看详情")
selected_stock_name = st.sidebar.selectbox("选择股票", list(stocks.keys()))
selected_stock_code = stocks[selected_stock_name]

# ====================== 页面展示 ======================
st.write("✅ 数据加载成功！以下是10支A股龙头股的分析结果：")

# 1. 单股/多股切换展示
st.subheader(f"📈 1. {selected_stock_name} ({selected_stock_code}) 累计收益率曲线")
st.line_chart(cumulative_returns[selected_stock_code], use_container_width=True)

# 2. 全市场10股对比图
st.subheader("📊 2. 10支股票累计收益率对比")
st.line_chart(cumulative_returns, use_container_width=True)

# 3. 年化波动率表格
st.subheader("📊 3. 年化波动率（风险指标）")
vol_df = volatility.reset_index()
vol_df.columns = ["Stock Code", "Annualized Volatility"]
st.dataframe(vol_df, use_container_width=True, hide_index=True)

#3.1股票相关性热力图
st.subheader("🔗 6. Stock Correlation Heatmap")
corr_matrix = returns.corr()
st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm'), use_container_width=True)

# 4. 投资术语解释
st.subheader("📚 4. Investment Terms Glossary")
st.write("""
1. **Daily Return**: The percentage change in a stock's closing price from one trading day to the next.
2. **Volatility**: A measure of investment risk, calculated as the annualized standard deviation of daily returns. Higher volatility means higher price fluctuation.
3. **Cumulative Return**: The total return of a stock over a specific period, showing the growth of an initial investment.
4. **Maximum Drawdown**: The largest peak-to-trough decline in the value of an investment, measuring the worst possible loss.
5. **Correlation**: A statistical measure showing how two stocks move in relation to each other, ranging from -1 (perfect negative) to 1 (perfect positive).
""")

# 5. 股票基础信息
st.subheader("🏢 5. Stock Basic Information")
stock_info = pd.DataFrame.from_dict(stocks, orient="index", columns=["Stock Code"])
st.dataframe(stock_info, use_container_width=True)
