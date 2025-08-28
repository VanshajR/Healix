#!/bin/bash

# Healix Deployment Verification Script
# This script verifies that all deployment components are properly configured

echo "🔍 Healix Deployment Verification"
echo "=================================="

# Check if files exist
echo "📁 Checking deployment files..."

files=(
    "Dockerfile"
    "docker-compose.yml"
    "deploy.sh"
    ".env.template"
    "DEPLOYMENT.md"
    "requirements.txt"
    "web_app.py"
    "templates/index.html"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

# Check script permissions
echo ""
echo "🔐 Checking permissions..."
if [ -x "deploy.sh" ]; then
    echo "✅ deploy.sh is executable"
else
    echo "❌ deploy.sh is not executable"
fi

# Check Docker configuration syntax
echo ""
echo "🐳 Validating Docker configuration..."
if command -v docker &> /dev/null; then
    if docker-compose config > /dev/null 2>&1; then
        echo "✅ docker-compose.yml syntax is valid"
    else
        echo "⚠️  docker-compose.yml syntax may have issues"
    fi
else
    echo "ℹ️  Docker not installed (optional for verification)"
fi

# Check Python syntax
echo ""
echo "🐍 Validating Python files..."
python_files=("web_app.py" "admin.py" "main.py")

for file in "${python_files[@]}"; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo "✅ $file syntax is valid"
    else
        echo "❌ $file has syntax errors"
    fi
done

# Check template files
echo ""
echo "🌐 Checking web templates..."
template_count=$(find templates -name "*.html" 2>/dev/null | wc -l)
echo "✅ Found $template_count HTML templates"

# Check environment template
echo ""
echo "⚙️  Checking configuration..."
if grep -q "DATABASE_URL" .env.template; then
    echo "✅ Environment template has DATABASE_URL"
else
    echo "❌ Environment template missing DATABASE_URL"
fi

if grep -q "ADMIN_ID" .env.template; then
    echo "✅ Environment template has ADMIN_ID"
else
    echo "❌ Environment template missing ADMIN_ID"
fi

echo ""
echo "🎉 Verification complete!"
echo ""
echo "📖 Next steps:"
echo "1. Run: ./deploy.sh"
echo "2. Choose deployment option"
echo "3. Access application as configured"
echo ""
echo "📚 For detailed instructions, see DEPLOYMENT.md"