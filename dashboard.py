import os
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

BASE = os.path.dirname(__file__)
FILE = os.path.join(BASE, "reports/HEDGEFUND_TERMINAL.xlsx")

st.title("IHSG WAR MODE")

# =====================
# DEVICE DETECTION
# =====================
is_mobile = st.sidebar.checkbox("Mobile mode", value=False)

# =====================
# LOAD
# =====================
@st.cache_data(ttl=30)
def load():
    return pd.read_excel(FILE, sheet_name=None)

try:
    data = load()
except:
    st.write("Excel belum ada")
    st.stop()

# =====================
# MOBILE MODE (SAFE)
# =====================
if is_mobile:

    st.warning("Mobile Safe Mode")

    sheet = st.selectbox("Sheet", list(data.keys()))
    df = data[sheet]

    df = df.head(40).fillna("")

    html = df.to_html(index=False)
    st.markdown(html, unsafe_allow_html=True)

    st.stop()

# =====================
# DESKTOP MODE
# =====================
for sheet, df in data.items():

    if sheet.upper() == "DASHBOARD":
        continue

    st.subheader(sheet)

    df = df.fillna("")
    st.dataframe(df, use_container_width=True)

    if "Foreign Net" in df.columns:
        try:
            chart_df = df.copy()
            chart_df["Foreign Net"] = pd.to_numeric(chart_df["Foreign Net"], errors="coerce")
            st.bar_chart(chart_df.set_index(df.columns[0])["Foreign Net"])
        except:
            pass

st.sidebar.write("Updated:", datetime.now().strftime("%H:%M:%S"))