import os
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

st.title("IHSG WAR MODE")

BASE = os.path.dirname(__file__)
FILE = os.path.join(BASE, "reports/HEDGEFUND_TERMINAL.xlsx")

# ======================
# LOAD EXCEL
# ======================
@st.cache_data(ttl=30)
def load():
    return pd.read_excel(FILE, sheet_name=None)

try:
    data = load()
except:
    st.write("Excel belum ada")
    st.stop()

# ======================
# SELECT SHEET
# ======================
sheet = st.selectbox("Sheet", list(data.keys()))
df = data[sheet]

if df.empty:
    st.write("Sheet kosong")
    st.stop()

# ======================
# LIMIT DATA (PENTING)
# ======================
df = df.head(50)
df = df.fillna("")

# ======================
# CLEAN TEXT (ANTI SAFARI CRASH)
# ======================
def clean(x):
    if isinstance(x, str):
        return x.replace("{","").replace("}","")
    return x

df = df.applymap(clean)

# ======================
# TAMPILKAN TABLE RINGAN
# ======================
html = df.to_html(index=False)
st.markdown(html, unsafe_allow_html=True)

st.write("Updated:", datetime.now().strftime("%H:%M:%S"))