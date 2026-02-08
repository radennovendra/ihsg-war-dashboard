#!/bin/bash

echo "🏷️ Generating IDX Sector Map..."
echo "=============================="

source venv/bin/activate
python3 generate_sector_map_bulletproof.py

echo "✅ Sector map ready: data/idx_sector_map.csv"
