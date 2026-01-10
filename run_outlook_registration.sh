#!/bin/bash

# Outlook 邮箱自动注册快速启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  📧 Outlook 邮箱自动注册"
echo "=========================================="
echo ""

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "❌ 未找到 Python"
    exit 1
fi

# 检查 CSV 文件
CSV_FILE="$PROJECT_DIR/debug_output/csv_accounts/accounts.csv"
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ CSV 文件不存在: $CSV_FILE"
    exit 1
fi

echo "✓ 环境检查通过"
echo ""
echo "📋 账户信息:"
tail -1 "$CSV_FILE" | awk -F',' '{print "  📧 " $1}'
echo ""

# 检查注册脚本
REGISTER_SCRIPT="$PROJECT_DIR/example/register_outlook_js.py"
if [ ! -f "$REGISTER_SCRIPT" ]; then
    echo "❌ 注册脚本不存在: $REGISTER_SCRIPT"
    exit 1
fi

echo "🚀 启动注册流程..."
echo ""

cd "$PROJECT_DIR"
python "$REGISTER_SCRIPT"

echo ""
echo "=========================================="
echo "✅ 注册流程已完成"
echo "=========================================="
echo ""
echo "📸 截图位置:"
echo "   $PROJECT_DIR/debug_output/screenshots_js/"
echo ""
echo "📄 完整报告:"
echo "   $PROJECT_DIR/debug_output/REGISTRATION_COMPLETE.md"
