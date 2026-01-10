#!/bin/bash

# Outlook 邮箱自动注册快速启动脚本
# 这个脚本会自动安装依赖并运行注册程序

set -e

echo "=================================================="
echo "Outlook 邮箱自动注册 - 快速启动"
echo "=================================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3"
    exit 1
fi

echo "✓ Python 版本:"
python3 --version

# 检查 nodriver
echo ""
echo "检查 nodriver..."
if python3 -c "import nodriver" 2>/dev/null; then
    echo "✓ nodriver 已安装"
else
    echo "⚠️  安装 nodriver..."
    pip install nodriver
fi

# 检查浏览器
echo ""
echo "检查浏览器..."
if command -v google-chrome-stable &> /dev/null; then
    echo "✓ Google Chrome 已安装:"
    google-chrome-stable --version
elif command -v chromium-browser &> /dev/null; then
    echo "✓ Chromium 已安装:"
    chromium-browser --version
else
    echo "⚠️  未找到 Chrome 或 Chromium，正在安装..."
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
fi

# 创建必要的目录
echo ""
echo "准备目录..."
mkdir -p /tmp/outlook_registration/accounts
mkdir -p /tmp/outlook_registration/screenshots

# 运行脚本
echo ""
echo "=================================================="
echo "开始注册..."
echo "=================================================="
echo ""

cd "$(dirname "${BASH_SOURCE[0]}")/.."
python3 example/register_outlook_simple.py

echo ""
echo "=================================================="
echo "完成！"
echo "=================================================="
echo ""
echo "账户信息已保存到: /tmp/outlook_registration/accounts/"
echo ""
