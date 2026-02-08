#!/bin/bash

echo "🏛️ IHSG Hedge Fund Automation Started"
echo "==================================="

source venv/bin/activate

# Build institutional universe if missing
if [ ! -f "data/universe_institutional.csv" ]; then
  echo "⚡ Building Institutional Universe first..."
  python3 build_institutional_universe.py
fi

echo "🌍 Updating foreign data from IDX..."
python3 flow_engine/idx_downloader.py

echo "📦 Saving daily foreign snapshot..."
python3 flow_engine/foreign_store.py

echo "📈 Running scanner..."
python3 scanner.py

echo "✅ Done."
