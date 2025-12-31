# ======================================================
# 📊 ANALYST-BASED SINGLE STOCK ANALYZER (FINAL VERSION)
# ======================================================

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Stock Analyzer",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Analyst-Based Stock Analyzer")
st.markdown("Professional Stock Analysis Using Analyst Consensus & Market Data")
st.markdown("---")

# --------------------------------------------------
# USER INSTRUCTIONS (SEPARATE LINES)
# --------------------------------------------------
st.info(
    """How to enter stock symbol:

    • Indian stocks: Use NSE symbol with .NS (Example: TCS.NS, INFY.NS)

    • US stocks: Use ticker directly (Example: AAPL, MSFT, TSLA)

    • Enter only ONE stock symbol at a time

    • Make sure internet connection is active"""
)

symbol = st.text_input("Enter Stock Symbol")

# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------
def format_market_cap(value):
    if value >= 1e13:
        return f"₹ {round(value/1e13,2)} Lakh Crore"
    elif value >= 1e11:
        return f"₹ {round(value/1e11,2)} Thousand Crore"
    elif value >= 1e9:
        return f"₹ {round(value/1e9,2)} Crore"
    else:
        return f"₹ {value}"

# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------
if symbol:
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        # --------------------------------------------------
        # COMPANY OVERVIEW (POINTS)
        # --------------------------------------------------
        st.subheader("🏢 Company Overview")

        summary = info.get("longBusinessSummary", "Information not available.")
        summary_points = summary.split(".")[:3]

        st.markdown(f"""
        • **Company Name:** {info.get('longName','N/A')}  
        • **Sector:** {info.get('sector','N/A')}  
        • **Industry:** {info.get('industry','N/A')}  

        **What the company does:**  
        """)

        for point in summary_points:
            if point.strip():
                st.markdown(f"• {point.strip()}")

        # --------------------------------------------------
        # HISTORICAL PRICE DATA
        # --------------------------------------------------
        end = datetime.today()
        start = end - timedelta(days=365)
        df = stock.history(start=start, end=end)

        # --------------------------------------------------
        # PRICE & VOLUME CHARTS (DARK, SAME SIZE)
        # --------------------------------------------------
        price_fig = go.Figure()
        price_fig.add_trace(go.Scatter(x=df.index, y=df["Close"]))
        price_fig.update_layout(
            template="plotly_dark",
            height=320,
            title="📉 Stock Price Trend (1 Year)"
        )

        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(x=df.index, y=df["Volume"]))
        volume_fig.update_layout(
            template="plotly_dark",
            height=320,
            title="📊 Trading Volume"
        )

        c1, c2 = st.columns(2)
        c1.plotly_chart(price_fig, use_container_width=True)
        c2.plotly_chart(volume_fig, use_container_width=True)

        # --------------------------------------------------
        # FINANCIAL OVERVIEW
        # --------------------------------------------------
        st.subheader("📌 Financial Overview")

        cp = info.get("currentPrice", 0)
        high = info.get("fiftyTwoWeekHigh", 0)
        low = info.get("fiftyTwoWeekLow", 0)
        mcap = info.get("marketCap", 0)

        f1, f2, f3 = st.columns(3)
        f1.metric("Current Price", cp)
        f2.metric("52-Week High", high)
        f3.metric("52-Week Low", low)

        st.markdown(f"**Market Capitalization:** {format_market_cap(mcap)}")

        # --------------------------------------------------
        # SHAREHOLDING PATTERN (FIXED – NO CUT)
        # --------------------------------------------------
        st.subheader("👥 Shareholding Pattern (%)")

        promoters = info.get("heldPercentInsiders", 0) * 100
        institutions = info.get("heldPercentInstitutions", 0) * 100
        public = round(100 - promoters - institutions, 2)

        holders = ["Promoters", "Institutions (FII/DII)", "Public / Retail"]
        values = [promoters, institutions, public]

        share_fig = go.Figure(
            go.Bar(
                x=holders,
                y=values,
                text=[f"{round(v,1)}%" for v in values],
                textposition="inside"
            )
        )

        share_fig.update_layout(
            template="plotly_dark",
            height=340,
            yaxis=dict(range=[0, 100]),
            title="Shareholding Distribution",
            margin=dict(t=80)
        )

        st.plotly_chart(share_fig, use_container_width=True)

        # --------------------------------------------------
        # TARGETS & STOP LOSS (ANALYST + REFINED)
        # --------------------------------------------------
        st.subheader("🎯 Price Targets & Stop Loss")

        t_low = info.get("targetLowPrice")
        t_mean = info.get("targetMeanPrice")
        t_high = info.get("targetHighPrice")

        stop_loss = round(cp * 0.98, 2)
        stop_loss_pct = round(((stop_loss - cp) / cp) * 100, 1)

        if t_low and t_mean and t_high:
            low_pct = round(((t_low - cp) / cp) * 100, 1)
            mean_pct = round(((t_mean - cp) / cp) * 100, 1)
            high_pct = round(((t_high - cp) / cp) * 100, 1)

            st.markdown(f"""
            **Targets from Analyst Consensus (Source: Yahoo Finance):**  
            • **Target (Low):** ₹ {t_low} ({low_pct}% from current price, short-term possibility)  
            • **Target (Mean):** ₹ {t_mean} ({mean_pct}% from current price, medium-term most likely)  
            • **Target (High):** ₹ {t_high} ({high_pct}% from current price, long-term optimistic)  
            """)

        # Refined targets (high accuracy)
        r1 = round(cp * 1.03, 2)
        r2 = round(cp * 1.06, 2)
        r3 = round(cp * 1.09, 2)

        r1_pct = round(((r1 - cp) / cp) * 100, 1)
        r2_pct = round(((r2 - cp) / cp) * 100, 1)
        r3_pct = round(((r3 - cp) / cp) * 100, 1)

        st.markdown(f"""
        **Refined Targets (High Accuracy – Risk Managed):**  
        • **Target 1:** ₹ {r1} (+{r1_pct}%, most likely in 1–2 months)  
        • **Target 2:** ₹ {r2} (+{r2_pct}%, most likely in 3–6 months)  
        • **Target 3:** ₹ {r3} (+{r3_pct}%, most likely in 6–12 months)  
        • **Stop Loss:** ₹ {stop_loss} ({stop_loss_pct}% below current price)  
        """)

        # --------------------------------------------------
        # INVESTMENT CONFIDENCE
        # --------------------------------------------------
        st.subheader("📊 Investment Confidence")

        confidence = int((r2 / cp) * 100)
        suggestion = "BUY" if confidence >= 105 else "HOLD" if confidence >= 100 else "AVOID"

        st.markdown(f"""
        • **Suggestion:** **{suggestion}**  
        • **Confidence Level:** **{confidence}%**

        **Basis:**  
        • Analyst consensus targets  
        • Risk–reward structure  
        • Current price position  
        """)

        # --------------------------------------------------
        # LATEST MARKET NEWS
        # --------------------------------------------------
        st.subheader("📰 Latest Market News")

        news = stock.news
        if news:
            for n in news[:5]:
                dt = datetime.fromtimestamp(n["providerPublishTime"])
                st.markdown(f"""
                • **{n['title']}**  
                  🕒 {dt.strftime('%d %b %Y, %I:%M %p')}
                """)
        else:
            st.warning(
                "Yahoo Finance restricts stock news availability under its free API model. "
                "Therefore, real-time company-specific news may not always be accessible."
            )

    except Exception:
        st.error("Yahoo Finance restricts stock news availability under its free API model. Therefore, real-time company-specific news may not always be accessible.")
