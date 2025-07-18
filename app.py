import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📈 NMDC Option Chain Tracker (NSE)")

# NSE headers to mimic browser
headers = {
    "User-Agent": "Mozilla/5.0"
}

# Function to get Option Chain Data
@st.cache_data(ttl=300)
def fetch_option_chain(symbol="NMDC"):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
    with requests.Session() as s:
        s.headers.update(headers)
        s.get("https://www.nseindia.com")
        r = s.get(url)
        data = r.json()
        return data

# Load data
with st.spinner("Fetching latest option chain data..."):
    data = fetch_option_chain()
    records = data['records']['data']
    expiry_dates = data['records']['expiryDates']

# Sidebar filters
selected_expiry = st.sidebar.selectbox("Select Expiry Date", expiry_dates)
min_strike = st.sidebar.number_input("Min Strike", 50, 150, 60)
max_strike = st.sidebar.number_input("Max Strike", 60, 200, 80)

# Filter by expiry
chain_data = []
for item in records:
    if item.get("expiryDate") == selected_expiry and min_strike <= item["strikePrice"] <= max_strike:
        ce = item.get("CE", {})
        pe = item.get("PE", {})
        row = {
            "Strike": item["strikePrice"],
            "CE_OI": ce.get("openInterest", 0),
            "CE_Chg_OI": ce.get("changeinOpenInterest", 0),
            "CE_IV": ce.get("impliedVolatility", 0),
            "CE_LTP": ce.get("lastPrice", 0),
            "PE_OI": pe.get("openInterest", 0),
            "PE_Chg_OI": pe.get("changeinOpenInterest", 0),
            "PE_IV": pe.get("impliedVolatility", 0),
            "PE_LTP": pe.get("lastPrice", 0),
        }
        chain_data.append(row)

df = pd.DataFrame(chain_data)

# Display table
st.subheader(f"Option Chain: NMDC – Expiry {selected_expiry}")
st.dataframe(df.sort_values("Strike"), use_container_width=True)

# Plot Open Interest
st.subheader("🔍 Open Interest Comparison")
fig = px.bar(df, x="Strike", y=["CE_OI", "PE_OI"], barmode="group",
             labels={"value": "Open Interest", "variable": "Type"},
             color_discrete_map={"CE_OI": "blue", "PE_OI": "orange"})
st.plotly_chart(fig, use_container_width=True)

# PCR Calculation
total_ce_oi = df["CE_OI"].sum()
total_pe_oi = df["PE_OI"].sum()
pcr = total_pe_oi / total_ce_oi if total_ce_oi else 0

col1, col2 = st.columns(2)
col1.metric("Total Call OI", f"{total_ce_oi:,}")
col2.metric("Total Put OI", f"{total_pe_oi:,}")
st.markdown(f"### 🧠 Put/Call Ratio (PCR): `{pcr:.2f}`")

# Timestamp
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")