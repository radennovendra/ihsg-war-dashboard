#!/bin/bash

echo "🏛️ IHSG Hedge Fund Automation Started"
echo "======================================"

source venv/bin/activate

# ==============================
# BUILD UNIVERSE IF NOT EXIST
# ==============================

if [ ! -f "data/universe_institutional.csv" ]; then
  echo "⚡ Building Institutional Universe..."
  python3 build_institutional_universe.py
fi


# ==============================
# UPDATE FOREIGN DATA
# ==============================

echo "🌍 Updating foreign data from IDX..."
python3 flow_engine/foreign_auto.py


# ==============================
# STORE FOREIGN SNAPSHOT
# ==============================

echo "📦 Saving daily foreign snapshot..."
python3 flow_engine/foreign_store.py


# ==============================
# RUN SCANNER
# ==============================

echo "📈 Running scanner..."
python3 scanner.py


# ==============================
# START ENTRY ENGINE
# ==============================

echo "⚡ Starting Entry Alert Engine..."
python3 entry_engine.py


echo "✅ Automation running."