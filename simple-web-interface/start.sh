#!/bin/bash

echo "🌍 Language Learning Web Interface"
echo "==================================="
echo ""
echo "Starting local web server on port 8080..."
echo ""
echo "📱 Open in your browser:"
echo "   http://localhost:8080"
echo ""
echo "⚠️  Make sure your backend is running on port 8000!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$(dirname "$0")"
python3 -m http.server 8080
