import os
import streamlit as st
import pandas as pd
import time
import requests
import io
from datetime import datetime

# ===== SAFARI FIX =====
st.set_option("client.showErrorDetails", False)

st.markdown(
    """
    <style>
    .stMarkdown {white-space: pre-wrap;}
    </style>
    """,
    unsafe_allow_html=True,
)

BASE = os.path.dirname(__file__)
FILE = os.path.join(BASE, "reports/HEDGEFUND_TERMINAL.xlsx")

st.set_page_config(layout="wide")
st.title("🏛️ IHSG WAR MODE DASHBOARD")

# =========================
# AUTO REFRESH
# =========================
refresh = st.sidebar.slider("Refresh (detik)", 5, 60, 15)

# auto refresh manual loop
if "last_run" not in st.session_state:
    st.session_state.last_run = time.time()

if time.time() - st.session_state.last_run > refresh:
    st.session_state.last_run = time.time()
    st.rerun()

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=5)
def load():
    return pd.read_excel(FILE, sheet_name=None)

try:
    data = load()
except:
    st.error("Excel belum ada")
    st.stop()
# =========================
# AUTO SHOW ALL SHEETS
# =========================
for sheet_name, df in data.items():

    if sheet_name.upper() == "DASHBOARD":
        continue

    st.divider()
    st.subheader(sheet_name)

    if df.empty:
        st.warning("Sheet kosong")
        continue

    df = df.fillna("")

    # ===== SAFARI SANITIZE =====
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

    df = df.applymap(clean)

    # format persen
    percent_cols = ["ROE","RevenueGrowth","Margin"]
    for c in percent_cols:
        if c in df.columns:
            df[c] = df[c].apply(
                lambda x: f"{x*100:.1f}%" if isinstance(x,(int,float)) else x
            )

    st.dataframe(df, use_container_width=True)

    if "Foreign Net" in df.columns:
        try:
            chart_df = df.copy()
            chart_df["Foreign Net"] = pd.to_numeric(chart_df["Foreign Net"], errors="coerce")
            st.bar_chart(chart_df.set_index(df.columns[0])["Foreign Net"])
        except:
            pass

# =========================
# LAST UPDATE
# =========================
st.sidebar.text(f"Last update: {datetime.now().strftime('%H:%M:%S')}")