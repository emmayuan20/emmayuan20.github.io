import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date

# ======================
# Page Configuration
# ======================
st.set_page_config(page_title="China A-Share Analysis Tool | Beginner-Friendly", layout="wide")
st.title("📊 China A-Share Stock Analysis Tool (Beginner-Friendly Edition)")
st.subheader("Valuation Thermometer | Buy/Sell Signal Dashboard | Risk Assessment | Portfolio Recommendation")

# ======================
# Risk Warning
# ======================
with st.expander("⚠️ IMPORTANT RISK WARNING (Please Read Carefully)", expanded=True):
    st.markdown("""
    1. This tool uses data from CSMAR database only, intended for **academic assignment demonstration only**, not constituting any actual investment advice.
    2. Stock investment involves high risks. Past performance does not guarantee future results. Do not make real investment decisions based on this tool.
    3. Market volatility, policy changes, industry cycles, and other factors may affect stock prices. Invest cautiously and within your means.
    4. This tool provides data reference only and assumes no liability for any losses incurred from investment activities.
    """)

# ======================
# Sidebar: Risk Assessment
# ======================
st.sidebar.header("📝 Investor Risk Profile Assessment")
st.sidebar.caption("Complete the assessment to receive portfolio recommendations based on your preferences")

q1 = st.sidebar.radio("1. What is your investment horizon?",
                      ["Short-term (1-6 months)", "Medium-term (6 months-2 years)", "Long-term (2+ years)"], index=1)
q2 = st.sidebar.radio("2. If a stock you own drops 10% in one month, what would you do?",
                      ["Sell immediately to avoid further losses", "Hold and wait for rebound", "Buy more to lower average cost"], index=1)
q3 = st.sidebar.radio("3. What is the maximum loss you can accept on a single stock?",
                      ["≤5%", "6%-15%", "16%-30%", ">30%"], index=1)
q4 = st.sidebar.radio("4. What is your expected investment return?",
                      ["Conservative (5%-10% annualized)", "Balanced (10%-20% annualized)", "High return (20%+ annualized)"], index=1)
q5 = st.sidebar.radio("5. How would you describe your stock investment knowledge?",
                      ["No knowledge", "Basic understanding", "Familiar", "Very professional"], index=1)

# Scoring
score = 0
score += 2 if q1 == "Short-term (1-6 months)" else 5 if q1 == "Medium-term (6 months-2 years)" else 8
score += 2 if q2 == "Sell immediately to avoid further losses" else 5 if q2 == "Hold and wait for rebound" else 8
score += 1 if q3 == "≤5%" else 4 if q3 == "6%-15%" else 7 if q3 == "16%-30%" else 10
score += 2 if q4 == "Conservative (5%-10% annualized)" else 6 if q4 == "Balanced (10%-20% annualized)" else 10
score += 1 if q5 == "No knowledge" else 4 if q5 == "Basic understanding" else 7 if q5 == "Familiar" else 10

if score <= 15:
    risk_type = "Conservative"
elif score <= 30:
    risk_type = "Moderate"
elif score <= 45:
    risk_type = "Balanced"
else:
    risk_type = "Aggressive"

if st.sidebar.button("📊 View My Risk Profile"):
    st.sidebar.success(f"✅ Your Risk Profile: {risk_type} (Score: {score}/50)")
    desc = {
        "Conservative": "Risk-averse, prioritizes capital preservation, accepts lower returns",
        "Moderate": "Balances capital safety and returns, accepts moderate fluctuations",
        "Balanced": "Willing to take certain risks, seeks medium-to-high returns",
        "Aggressive": "Pursues high returns, accepts significant volatility and potential capital loss"
    }
    st.sidebar.write(f"👉 Characteristics: {desc[risk_type]}")

# ======================
# Sidebar: Data Source (Local Excel)
# ======================
st.sidebar.markdown("---")
st.sidebar.header("📂 Data Source")
st.sidebar.info("Using local file: `TRD_Dalyr.xlsx`")

st.sidebar.subheader("📅 Date Range")
start_date = st.sidebar.date_input("Start Date", date(2024, 1, 1))
end_date = st.sidebar.date_input("End Date", date.today())

# ======================
# Load Data from Local Excel
# ======================
@st.cache_data
def load_local_data(file_path):
    """Load and clean CSMAR daily trading data from local Excel file."""
    try:
        df_raw = pd.read_excel(file_path)

        # Column mapping (support both Chinese and English)
        column_mapping = {
            '证券代码': 'stkcd',
            'Stkcd': 'stkcd',
            '交易日期': 'trddt',
            'Trddt': 'trddt',
            '收盘价': 'clsprc',
            'Clsprc': 'clsprc',
            '考虑现金红利再投资的日个股回报率': 'dretwd',
            '日个股回报率': 'dretwd',
            'Dretwd': 'dretwd',
        }
        df_raw.rename(columns=column_mapping, inplace=True)
        df_raw.columns = df_raw.columns.str.lower()

        required_cols = ['stkcd', 'trddt', 'clsprc', 'dretwd']
        missing = [col for col in required_cols if col not in df_raw.columns]
        if missing:
            st.error(f"Missing columns: {missing}. Available: {list(df_raw.columns)}")
            return None, None

        # Parse dates
        df_raw['trddt'] = pd.to_datetime(df_raw['trddt'], errors='coerce')
        df_raw = df_raw.dropna(subset=['trddt', 'dretwd', 'clsprc'])
        df_raw['stkcd'] = df_raw['stkcd'].astype(str).str.zfill(6)

        stock_codes = sorted(df_raw['stkcd'].unique())
        stock_dict = {code: code for code in stock_codes}

        return df_raw, stock_dict
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

DATA_FILE = "TRD_Dalyr.xlsx"
df_raw, stock_dict = load_local_data(DATA_FILE)

# ======================
# Stock Selection
# ======================
st.sidebar.subheader("📈 Stock Selection")
selected_stocks = []

if df_raw is not None and stock_dict is not None:
    stock_codes = list(stock_dict.keys())
    st.sidebar.success(f"✅ Loaded {len(stock_codes)} A-share stocks")
    selected_stocks = st.sidebar.multiselect(
        "Select multiple stocks for comparison",
        stock_codes,
        default=[]
    )
else:
    st.sidebar.error("Failed to load data. Please ensure 'TRD_Dalyr.xlsx' is in the same folder as this script.")

# ======================
# Technical Indicators (based on local data)
# ======================
def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = (-delta.clip(upper=0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def prepare_stock_data(df, stkcd, start, end):
    """Filter data for one stock and compute technical indicators."""
    mask = (df['stkcd'] == stkcd) & (df['trddt'] >= pd.to_datetime(start)) & (df['trddt'] <= pd.to_datetime(end))
    sub = df[mask].copy().sort_values('trddt')
    if sub.empty:
        return None
    sub['MA5'] = sub['clsprc'].rolling(5).mean()
    sub['MA20'] = sub['clsprc'].rolling(20).mean()
    sub['RSI'] = calculate_rsi(sub['clsprc'], window=14)
    sub['return_20d'] = sub['clsprc'].pct_change(20) * 100  # 20-day momentum
    sub['cumulative'] = (1 + sub['dretwd']).cumprod()
    return sub

# ======================
# Load Data Button
# ======================
fetch = st.sidebar.button("🚀 Load Data + Generate Charts + Portfolio Recommendation")

if fetch:
    if not selected_stocks:
        st.sidebar.warning("Please select at least one stock")
    elif df_raw is None:
        st.sidebar.error("Data file not loaded properly")
    else:
        with st.spinner("Processing local CSMAR data..."):
            # Prepare data for all selected stocks
            stock_data = {}
            for stkcd in selected_stocks:
                sub = prepare_stock_data(df_raw, stkcd, start_date, end_date)
                if sub is not None:
                    stock_data[stkcd] = sub
                else:
                    st.warning(f"No data for {stkcd} in selected date range.")

            if not stock_data:
                st.error("No valid data for any selected stock.")
                st.stop()

            # Combine for cumulative return chart
            final_df = pd.concat(stock_data.values(), ignore_index=True)
            st.session_state["final_df"] = final_df
            st.session_state["stock_data"] = stock_data
            st.success(f"✅ Processed CSMAR data for {len(stock_data)} stock(s)")

# ======================
# Module 1: Valuation Thermometer (Price Percentile)
# ======================
st.header("🌡️ Module 1: Price Level Thermometer (based on historical price percentile)")
if "stock_data" in st.session_state and selected_stocks:
    stock_data = st.session_state["stock_data"]
    available = list(stock_data.keys())
    if not available:
        st.warning("No data available.")
    else:
        val_stock = st.selectbox("Select a stock to view price level", available, key="val_select")
        sub = stock_data[val_stock]
        current_price = sub['clsprc'].iloc[-1]
        price_history = sub['clsprc'].values

        if len(price_history) >= 20:
            percentile = (np.sum(price_history <= current_price) / len(price_history)) * 100
            percentile = round(percentile, 1)

            if percentile < 30:
                level, tip = "Low Price Zone", f"{val_stock} is trading near its lower historical range."
            elif percentile <= 70:
                level, tip = "Mid Price Zone", f"{val_stock} is trading in the middle of its historical range."
            else:
                level, tip = "High Price Zone", f"{val_stock} is trading near its upper historical range."

            st.markdown(f"### {val_stock} Price Level Status")
            st.progress(percentile / 100, text=f"{level} (Price Percentile: {percentile}%)")
            st.write(f"📝 Interpretation: Current price is higher than {percentile}% of historical prices in the selected period.")
            st.info(tip)
            st.caption("💡 Note: This is not a valuation metric (no fundamentals), only a historical price comparison.")
        else:
            st.warning(f"⚠️ Insufficient data to calculate percentile for {val_stock}.")
else:
    st.info("Please select stocks and click 'Load Data' to begin")

st.markdown("---")

# ======================
# Module 2: Buy/Sell Signal Dashboard (Local Data Only)
# ======================
st.header("📟 Module 2: Simple Buy/Sell Signal Dashboard (based on local data)")
if "stock_data" in st.session_state and selected_stocks:
    stock_data = st.session_state["stock_data"]
    available = list(stock_data.keys())
    if not available:
        st.warning("No data available.")
    else:
        signal_stock = st.selectbox("Select a stock to view signals", available, key="signal_select")
        sub = stock_data[signal_stock].dropna().tail(60)  # last 60 days for signals

        if len(sub) >= 20:
            latest = sub.iloc[-1]
            ma5_above_ma20 = latest['MA5'] > latest['MA20']
            trend_signal = "✅ Bullish (Short-term MA > Long-term MA)" if ma5_above_ma20 else "❌ Bearish (Short-term MA < Long-term MA)"

            rsi = round(latest['RSI'], 1) if not pd.isna(latest['RSI']) else None
            if rsi is not None:
                if rsi < 30:
                    rsi_signal = f"✅ RSI={rsi} (Oversold)"
                elif rsi > 70:
                    rsi_signal = f"⚠️ RSI={rsi} (Overbought)"
                else:
                    rsi_signal = f"✅ RSI={rsi} (Normal)"
            else:
                rsi_signal = "❓ RSI unavailable"

            momentum = latest.get('return_20d', np.nan)
            if not pd.isna(momentum):
                mom_signal = f"✅ +{momentum:.1f}% (20d)" if momentum > 0 else f"❌ {momentum:.1f}% (20d)"
            else:
                mom_signal = "❓ Momentum unavailable"

            close_vs_ma20 = "✅ Above MA20" if latest['clsprc'] > latest['MA20'] else "❌ Below MA20"

            col1, col2 = st.columns(2)
            with col1:
                st.info("📈 Trend Signal")
                st.write(trend_signal)
                st.info("📊 Momentum (20d)")
                st.write(mom_signal)
            with col2:
                st.info("⚡ RSI Signal")
                st.write(rsi_signal)
                st.info("📉 Price vs MA20")
                st.write(close_vs_ma20)

            st.markdown("### 📝 Conclusion")
            if ma5_above_ma20 and rsi and rsi < 30:
                st.success("Bullish setup with oversold RSI. Potential upward reversal.")
            elif ma5_above_ma20 and rsi and rsi > 70:
                st.warning("Bullish but overbought. Short-term caution.")
            elif not ma5_above_ma20 and rsi and rsi > 70:
                st.error("Bearish and overbought. Downside risk elevated.")
            elif not ma5_above_ma20 and rsi and rsi < 30:
                st.warning("Bearish but oversold. Watch for rebound.")
            elif ma5_above_ma20:
                st.info("Bullish trend, but RSI neutral. No extreme signal.")
            elif not ma5_above_ma20:
                st.info("Bearish trend, but RSI neutral. No extreme signal.")
            else:
                st.info("Mixed signals. No clear direction.")
            st.caption("💡 Based on local CSMAR data (price only). Volume data not available.")
        else:
            st.warning(f"⚠️ {signal_stock} - Insufficient data for signals.")
else:
    st.info("Please select stocks and click 'Load Data' to begin")

st.markdown("---")

# ======================
# Cumulative Return Chart
# ======================
st.header("📈 Interactive Cumulative Return Chart")
if "final_df" in st.session_state and not st.session_state["final_df"].empty:
    df = st.session_state["final_df"]
    fig = px.line(df, x="trddt", y="cumulative", color="stkcd",
                  title=f"Cumulative Return Comparison ({start_date} - {end_date})",
                  labels={"cumulative": "Cumulative Return", "trddt": "Date", "stkcd": "Stock Code"},
                  template="plotly_white",
                  hover_data={"trddt": ":%Y-%m-%d", "cumulative": ":+.2%", "stkcd": True})
    fig.update_layout(hovermode="x unified", legend_title="Stock Code", height=500)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please load data to view the chart")

# ======================
# Data Table
# ======================
st.header("📋 Interactive Data Table")
if "final_df" in st.session_state and not st.session_state["final_df"].empty:
    display_df = st.session_state["final_df"][["trddt", "stkcd", "clsprc", "dretwd", "cumulative"]].sort_values("trddt", ascending=False)
    st.dataframe(
        display_df,
        use_container_width=True,
        height=300,
        column_config={
            "trddt": "Date",
            "stkcd": "Stock Code",
            "clsprc": "Close Price",
            "dretwd": "Daily Return",
            "cumulative": "Cumulative Return"
        }
    )
else:
    st.info("No data available")

# ======================
# Portfolio Recommendation (Scoring-based, no strict filters)
# ======================
st.header("🎯 Portfolio Recommendation Based on Your Risk Profile")
if "final_df" in st.session_state and selected_stocks and not st.session_state["final_df"].empty:
    if st.button("🔍 Generate Portfolio Recommendation"):
        df = st.session_state["final_df"]
        analysis_rows = []
        for stkcd in selected_stocks:
            sub = df[df["stkcd"] == stkcd]
            if sub.empty:
                continue
            total_ret = (sub["cumulative"].iloc[-1] - 1) * 100
            ann_vol = sub["dretwd"].std() * np.sqrt(252) * 100
            max_dd = ((sub["cumulative"] / sub["cumulative"].cummax()) - 1).min() * 100
            pos_ratio = (sub["dretwd"] > 0).mean() * 100
            analysis_rows.append({
                "Stock Code": stkcd,
                "Total Return (%)": total_ret,
                "Annualized Volatility (%)": ann_vol,
                "Maximum Drawdown (%)": max_dd,
                "Positive Days (%)": pos_ratio
            })
        ana_df = pd.DataFrame(analysis_rows)

        # Scoring function based on risk type
        def compute_score(row, risk):
            if risk == "Conservative":
                return (50 - row["Annualized Volatility (%)"]) + (50 + row["Maximum Drawdown (%)"]) + row["Positive Days (%)"]
            elif risk == "Moderate":
                return (30 - abs(row["Annualized Volatility (%)"] - 25)) + (30 - abs(row["Maximum Drawdown (%)"] + 20)) + row["Total Return (%)"] / 5
            elif risk == "Balanced":
                return (30 - abs(row["Annualized Volatility (%)"] - 35)) + row["Total Return (%)"] / 3 + row["Positive Days (%)"] / 2
            else:  # Aggressive
                return row["Annualized Volatility (%)"] + row["Total Return (%)"] * 2

        ana_df["Score"] = ana_df.apply(lambda r: compute_score(r, risk_type), axis=1)
        ana_df = ana_df.sort_values("Score", ascending=False).reset_index(drop=True)

        top_n = 3 if risk_type in ["Conservative", "Moderate"] else 4 if risk_type == "Balanced" else 5
        recommended = ana_df.head(top_n).copy()

        recommended["Total Return (%)"] = recommended["Total Return (%)"].round(2)
        recommended["Annualized Volatility (%)"] = recommended["Annualized Volatility (%)"].round(2)
        recommended["Maximum Drawdown (%)"] = recommended["Maximum Drawdown (%)"].round(2)
        recommended["Positive Days (%)"] = recommended["Positive Days (%)"].round(2)
        recommended["Score"] = recommended["Score"].round(2)

        st.success(f"📌 Top {len(recommended)} recommended stocks for {risk_type} profile (sorted by match score)")
        st.dataframe(
            recommended[["Stock Code", "Total Return (%)", "Annualized Volatility (%)", 
                        "Maximum Drawdown (%)", "Positive Days (%)", "Score"]],
            use_container_width=True,
            hide_index=True
        )
        st.caption("💡 Recommendation is based on a relative scoring system, not strict pass/fail criteria.")
else:
    st.info("Please load data first")

st.markdown("---")
st.error("📢 FINAL RISK REMINDER: This tool is for academic purposes only and does not constitute investment advice.")
st.caption("✅ User Guide: Complete risk assessment → Select stocks → Load data → View analysis")



# ===================== 金融术语小白AI解释器=====================

# Dependencies: pip install streamlit openai
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import locale

# 强制设置标准输出编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 设置环境变量
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'en_US.UTF-8'
# ... 以下是你的原有代码 ...

import streamlit as st
from openai import OpenAI

# ---------- Page configuration ----------
st.set_page_config(
    page_title="Green Hand Investment Assistant",
    page_icon="📈",
    layout="centered"
)

# ---------- Read API key from secrets ----------
try:
    api_key = st.secrets["DEEPSEEK_API_KEY"]
except KeyError:
    st.error("❌ API key not found. Please set DEEPSEEK_API_KEY in .streamlit/secrets.toml")
    st.stop()

# ---------- Sidebar (no manual key input needed) ----------
st.sidebar.title("🔑 Configuration Status")
st.sidebar.success("✅ API key loaded")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Instructions")
st.sidebar.markdown(
    """
    1. Enter a financial term below  
    2. Click the "Explain" button, and AI will explain it in plain language  
    """
)
st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: This app has a preset API key. No manual entry needed.")

# ---------- Main interface ----------
st.title("📈 Green Hand Investment Assistant")
st.markdown("> Explain complex financial terms in the simplest way")

with st.expander("🌟 Beginner's Must-Read · Investment Tips", expanded=True):
    st.markdown(
        """
        - **Don't invest in what you don't understand**: Avoid buying stocks or funds you're unfamiliar with.  
        - **Invest with spare money**: Only use money you won't need in the short term; never borrow to invest.  
        - **Diversify risk**: Don't put all your eggs in one basket.  
        - **Hold for the long term**: Short-term fluctuations are normal; good companies need time to grow.  
        - **Learn before you buy**: Understand basic terms (P/E ratio, ROE, turnover rate, etc.) before taking action.  
        """
    )

st.markdown("---")

st.subheader("🤖 Financial Term Plain Language Explainer")
st.markdown("Enter a financial term/stock code that confuses you, and AI will explain it like a friend chatting.")

term = st.text_input("📝 Financial Term", placeholder="e.g., P/E ratio, Northbound capital, ROE, turnover rate...")

if st.button("✨ Explain to me", type="primary"):
    if not term.strip():
        st.warning("⚠️ Please enter a financial term")
    else:
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )
            system_prompt = (
                "You are a friendly, patient investment teacher who teaches complete beginners about finance. "
                "The user will input a financial term. Please explain it in the most common, everyday language. "
                "Use metaphors, examples, or storytelling as much as possible. Avoid technical terms. "
                "Keep the response under 150 words, so that even an elementary school student can understand."
            )
            user_prompt = f"Explain the financial term in plain language: {term}"

            with st.spinner("🤔 Thinking in plain language..."):
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
            explanation = response.choices[0].message.content
            st.success("✅ Explanation:")
            st.markdown(f"> {explanation}")
            st.caption("💬 If there's another term you don't understand, just enter it next.")
        except Exception as e:
            st.error(f"❌ API call error: {e}")
            st.info("Please check if the API key is correct and if your account balance is sufficient.")

st.markdown("---")
st.caption("📚 Try these: P/E ratio | Northbound capital | Blue-chip stocks | Turnover rate | Dollar-cost averaging")


 # ====================== 结束 ======================
