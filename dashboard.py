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
    xls = pd.ExcelFile(FILE)

    data = {}
    for sheet in xls.sheet_names:
        data[sheet] = xls.parse(sheet)

    return data

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
    st.subheader(f"📊 {sheet_name}")

    df = df.fillna("")
    percent_cols = ["ROE","RevenueGrowth","Margin"]

    for c in percent_cols:
        if c in df.columns:
            df[c] = df[c].apply(
                lambda x: f"{x*100:.1f}%" if isinstance(x,(int,float)) else x
            )

    st.dataframe(df, use_container_width=True)

    if df.empty:
        st.warning("Sheet kosong")
        continue

    # auto chart kalau ada foreign
    if "Foreign Net" in df.columns:
        st.bar_chart(df.set_index(df.columns[0])["Foreign Net"])

# =========================
# LAST UPDATE
# =========================
st.sidebar.write("Last update:", datetime.now())