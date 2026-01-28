#!/bin/bash

# Presentation Evaluation Tool - Quick Setup Script
# This script sets up the tool for local testing

echo "🚀 Presentation Evaluation Tool - Setup"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.11 from python.org"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Get your Anthropic API key from: https://console.anthropic.com/"
echo "2. Run: export ANTHROPIC_API_KEY='your-key-here'"
echo "3. Run: export SECRET_KEY='any-random-string'"
echo "4. Run: python app.py"
echo "5. Open: http://localhost:5000"
echo ""
echo "Or use the quick start command:"
echo "ANTHROPIC_API_KEY='your-key' SECRET_KEY='random' python app.py"
echo ""
echo "For deployment to Render.com, see DEPLOYMENT_GUIDE.md"
echo ""
