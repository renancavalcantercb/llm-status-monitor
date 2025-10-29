#!/bin/bash
# Run tests with pytest

set -e

echo "🧪 Running LLM Status Monitor Tests"
echo "===================================="

# Run pytest
python -m pytest "$@"

echo ""
echo "✅ Tests completed"
echo "📊 Coverage report: htmlcov/index.html"
