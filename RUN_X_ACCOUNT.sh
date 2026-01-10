#!/bin/bash
# X账号自动注册 - 快速启动脚本

echo "╔═══════════════════════════════════════════════════════╗"
echo "║    X (Twitter) 账号自动注册 - 快速启动器              ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示选项
echo "${BLUE}📋 选择要执行的操作:${NC}"
echo ""
echo "1) 运行X账号注册脚本"
echo "2) 查看最新日志"
echo "3) 查看调试信息"
echo "4) 查看最新截图"
echo "5) 清理旧文件"
echo "6) 显示完整信息"
echo "0) 退出"
echo ""
read -p "请选择 (0-6): " choice

case $choice in
    1)
        echo ""
        echo "${BLUE}🚀 启动X账号注册脚本...${NC}"
        echo ""
        cd /workspaces/nodriver/example
        python register_x_account.py
        ;;
    2)
        echo ""
        echo "${BLUE}📋 查看最新日志...${NC}"
        echo ""
        tail -50 /workspaces/nodriver/debug_output/logs/x_account_register_*.log | tail -50
        ;;
    3)
        echo ""
        echo "${BLUE}📊 显示调试信息...${NC}"
        echo ""
        bash /workspaces/nodriver/debug_output/show_debug_info.sh
        ;;
    4)
        echo ""
        echo "${BLUE}🖼️  显示最新截图...${NC}"
        echo ""
        ls -lh /workspaces/nodriver/debug_output/screenshots/ | tail -10
        ;;
    5)
        echo ""
        echo "${YELLOW}⚠️  清理7天前的旧文件...${NC}"
        find /workspaces/nodriver/debug_output -type f -mtime +7 -delete
        echo "${GREEN}✓ 清理完成${NC}"
        ;;
    6)
        echo ""
        echo "${BLUE}📊 完整信息${NC}"
        echo ""
        bash /workspaces/nodriver/debug_output/show_debug_info.sh
        ;;
    0)
        echo ""
        echo "${YELLOW}👋 再见!${NC}"
        exit 0
        ;;
    *)
        echo ""
        echo "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

echo ""
echo "${GREEN}✅ 操作完成${NC}"
echo ""
