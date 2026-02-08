#!/bin/bash

echo "🏛️ Setting up IHSG Ultimate Scanner Environment"
echo "=============================================="

# Step 1: Create venv if not exists
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
else
  echo "✅ venv already exists"
fi

# Step 2: Activate venv
echo "⚡ Activating venv..."
source venv/bin/activate

# Step 3: Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Step 4: Install dependencies
echo "📚 Installing requirements..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo "Next time just run:"
echo "   bash start.sh"
echo ""
