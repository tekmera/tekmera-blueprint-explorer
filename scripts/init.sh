#!/bin/bash
echo "🚀 Setting up Tekmera Fusion Explorer..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "⚙️ Installing Tekmera package..."
pip install -e .

echo "✅ Setup complete!"
echo ""
echo "🎯 Usage:"
echo "  source venv/bin/activate"
echo "  tekmera ./blueprints"
echo "  tekmera ./blueprints/CLIENTS/EY/production"
echo ""
echo "🔍 Starting Tekmera with EY production blueprints..."
tekmera ./blueprints/CLIENTS/EY/production
