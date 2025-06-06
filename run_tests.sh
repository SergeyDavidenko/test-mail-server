#!/bin/bash
# Test runner script for Test Mail Server

echo "🧪 Test Mail Server - Testing"
echo "=================================="

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Install dependencies:"
    echo "pip install -r requirements-dev.txt"
    exit 1
fi

# Function to print separator
separator() {
    echo ""
    echo "------------------------"
    echo ""
}

# Check arguments
case "$1" in
    "quick")
        echo "🚀 Quick tests..."
        pytest tests/test_simple.py -v
        ;;
    "config")
        echo "⚙️ Configuration tests..."
        pytest tests/test_config.py -v
        ;;
    "storage")
        echo "💾 Storage tests..."
        pytest tests/test_email_storage.py -v
        ;;
    "working")
        echo "✅ All working tests..."
        pytest tests/test_config.py tests/test_email_storage.py tests/test_simple.py -v
        ;;
    "coverage")
        echo "📊 Tests with code coverage..."
        pytest tests/test_config.py tests/test_email_storage.py tests/test_simple.py --cov=app --cov-report=term-missing
        ;;
    "unit")
        echo "🔬 Unit tests..."
        pytest -m unit -v
        ;;
    "api")
        echo "🔬 API tests..."
        pytest tests/test_api.py -v
        ;;
    "integration")
        echo "🔗 Integration tests..."
        pytest -m integration -v
        ;;
    "all")
        echo "🎯 All tests (including problematic ones)..."
        pytest -v
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Available commands:"
        echo "  quick       - Quick basic tests (recommended)"
        echo "  config      - Configuration tests"
        echo "  storage     - Email storage tests"
        echo "  working     - All working tests"
        echo "  coverage    - Tests with coverage analysis"
        echo "  unit        - Unit tests only"
        echo "  integration - Integration tests only"
        echo "  all         - All tests (may have errors)"
        echo "  help        - This help"
        echo ""
        echo "Examples:"
        echo "  $0 quick      # Quick start"
        echo "  $0 working    # All working tests"
        echo "  $0 coverage   # With coverage analysis"
        ;;
    "")
        echo "🚀 Running working tests by default..."
        separator
        pytest tests/test_simple.py tests/test_config.py tests/test_email_storage.py -v
        
        separator
        echo "✅ Tests completed!"
        echo ""
        echo "For other options run: $0 help"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Run '$0 help' for help"
        exit 1
        ;;
esac

separator
echo "🎉 Done!" 