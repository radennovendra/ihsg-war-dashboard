#!/bin/bash
# ============================================
# RESET INSTALLER FOR IHSG ULTIMATE SCANNER
# Stable rebuild using Python 3.12 + clean venv
# ============================================

echo "🏛️ IHSG Ultimate Scanner Reset Installer"
echo "======================================="
echo ""

# Move into project folder
PROJECT_DIR=~/Desktop/IHSG/ihsg_ultimate_scanner
cd "$PROJECT_DIR" || exit

echo "📌 Project folder:"
pwd
echo ""

# Check python3.12 exists
if ! command -v python3.12 &> /dev/null
then
    echo "❌ Python 3.12 not found."
    echo "👉 Install it first from:"
    echo "   https://www.python.org/downloads/mac-osx/"
    exit 1
fi

echo "✅ Python 3.12 found:"
python3.12 --version
echo ""

# Remove old venv
echo "🧹 Removing old virtual environment..."
rm -rf venv

# Create new venv
echo "⚙️ Creating fresh venv..."
python3.12 -m venv venv

# Activate venv
echo "🚀 Activating venv..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f requirements.txt ]; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found. Installing core packages..."
    pip install pandas yfinance requests openpyxl
fi

echo ""
echo "✅ Reset complete!"
echo "---------------------------------------"
echo "Now run:"
echo "   source venv/bin/activate"
echo "   bash start.sh"
echo ""
