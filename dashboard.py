import os
import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🏛️ IHSG WAR MODE DASHBOARD")

BASE = os.path.dirname(__file__)
FILE = os.path.join(BASE, "reports/HEDGEFUND_TERMINAL.xlsx")

# =========================
# AUTO REFRESH
# =========================
refresh = st.sidebar.slider("Refresh (detik)", 10, 120, 30)

if "t" not in st.session_state:
    st.session_state.t = time.time()

if time.time() - st.session_state.t > refresh:
    st.session_state.t = time.time()
    st.rerun()

# =========================
# LOAD EXCEL
# =========================
@st.cache_data(ttl=10)
def load():
    return pd.read_excel(FILE, sheet_name=None)

try:
    data = load()
except:
    st.error("Excel belum tersedia")
    st.stop()

# =========================
# SHEET SELECTOR
# =========================
sheets = list(data.keys())
sheet = st.sidebar.selectbox("Pilih Sheet", sheets)

df = data[sheet]

st.subheader(sheet)

if df.empty:
    st.warning("Sheet kosong")
    st.stop()

# =========================
# SAFARI SAFE CLEAN
# =========================
def clean(x):
    if isinstance(x, str):
        return (
            x.replace("{","")
             .replace("}","")
             .replace("$","")
             .replace("[","")
             .replace("]","")
        )
    return x

df = df.fillna("")
df = df.applymap(clean)

# limit rows (penting utk iPhone)
df = df.head(200)

# persen formatting
percent_cols = ["ROE","RevenueGrowth","Margin"]
for c in percent_cols:
    if c in df.columns:
        df[c] = df[c].apply(
            lambda x: f"{x*100:.1f}%" if isinstance(x,(int,float)) else x
        )

st.dataframe(df, use_container_width=True)

# =========================
# FOREIGN CHART
# =========================
if "Foreign Net" in df.columns:
    try:
        chart_df = df.copy()
        chart_df["Foreign Net"] = pd.to_numeric(chart_df["Foreign Net"], errors="coerce")
        st.bar_chart(chart_df.set_index(df.columns[0])["Foreign Net"])
    except:
        pass

# =========================
# FOOTER
# =========================
st.sidebar.text("Last update")
st.sidebar.text(datetime.now().strftime("%H:%M:%S"))