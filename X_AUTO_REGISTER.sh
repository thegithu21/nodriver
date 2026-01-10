#!/bin/bash
# X 账号自动注册快速启动脚本

SCRIPT_DIR="/workspaces/nodriver/example"
DEBUG_DIR="/workspaces/nodriver/debug_output"

echo "================================"
echo "X (Twitter) 自动注册系统"
echo "================================"
echo ""

# 显示菜单
show_menu() {
    echo "请选择操作:"
    echo "1. 注册新的X账号"
    echo "2. 查看最新账号信息"
    echo "3. 查看所有生成的账号"
    echo "4. 查看最近的日志"
    echo "5. 查看截图目录"
    echo "6. 清理日志和截图"
    echo "0. 退出"
    echo ""
    read -p "请输入选项 (0-6): " choice
}

# 注册新账号
register_account() {
    echo ""
    echo "开始自动注册新X账号..."
    echo ""
    cd "$SCRIPT_DIR"
    python x_auto_register_simple.py
    echo ""
    echo "✅ 注册完成！请查看上方的JSON信息"
    echo ""
}

# 查看最新账号
show_latest_account() {
    echo ""
    if [ -z "$(ls -t "$DEBUG_DIR/accounts/"x_account_*.json 2>/dev/null | head -1)" ]; then
        echo "❌ 没有生成的账号文件"
        return
    fi
    
    latest_file=$(ls -t "$DEBUG_DIR/accounts/"x_account_*.json 2>/dev/null | head -1)
    echo "最新账号信息 ($latest_file):"
    echo ""
    cat "$latest_file"
    echo ""
}

# 查看所有账号
show_all_accounts() {
    echo ""
    account_count=$(ls "$DEBUG_DIR/accounts/"x_account_*.json 2>/dev/null | wc -l)
    
    if [ "$account_count" -eq 0 ]; then
        echo "❌ 没有生成的账号文件"
        return
    fi
    
    echo "✅ 找到 $account_count 个账号文件"
    echo ""
    echo "文件列表:"
    ls -1 "$DEBUG_DIR/accounts/"x_account_*.json | while read file; do
        echo ""
        echo "📁 $(basename $file)"
        cat "$file" | jq -r '"  邮箱: \(.email)\n  用户名: \(.username)\n  密码: \(.password)\n  状态: \(.status)"' 2>/dev/null || cat "$file"
    done
    echo ""
}

# 查看最近的日志
show_recent_logs() {
    echo ""
    log_count=$(ls "$DEBUG_DIR/logs/"x_register_*.log 2>/dev/null | wc -l)
    
    if [ "$log_count" -eq 0 ]; then
        echo "❌ 没有日志文件"
        return
    fi
    
    latest_log=$(ls -t "$DEBUG_DIR/logs/"x_register_*.log 2>/dev/null | head -1)
    echo "最近的日志文件: $(basename $latest_log)"
    echo ""
    echo "=================="
    tail -50 "$latest_log"
    echo "=================="
    echo ""
}

# 查看截图目录
show_screenshots() {
    echo ""
    screenshot_count=$(ls "$DEBUG_DIR/screenshots/"x_*.png 2>/dev/null | wc -l)
    
    if [ "$screenshot_count" -eq 0 ]; then
        echo "❌ 没有截图文件"
        return
    fi
    
    echo "✅ 找到 $screenshot_count 个截图文件"
    echo ""
    echo "截图列表:"
    ls -lh "$DEBUG_DIR/screenshots/"x_*.png | awk '{print "  " $9 " (" $5 ")"}'
    echo ""
}

# 清理文件
cleanup_files() {
    echo ""
    read -p "确认删除所有日志和截图? (y/n): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        rm -f "$DEBUG_DIR/logs/"x_register_*.log
        rm -f "$DEBUG_DIR/screenshots/"x_*.png
        echo "✅ 清理完成"
    else
        echo "❌ 已取消"
    fi
    echo ""
}

# 主循环
while true; do
    show_menu
    
    case $choice in
        1) register_account ;;
        2) show_latest_account ;;
        3) show_all_accounts ;;
        4) show_recent_logs ;;
        5) show_screenshots ;;
        6) cleanup_files ;;
        0) 
            echo "👋 再见!"
            exit 0
            ;;
        *) 
            echo "❌ 无效的选项"
            ;;
    esac
done
