#!/bin/bash
# 调试目录查看工具

DEBUG_DIR="/workspaces/nodriver/debug_output"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  nodriver 调试输出目录 - 统一管理工具                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 显示目录结构
echo "📁 目录结构:"
tree -L 2 "$DEBUG_DIR" 2>/dev/null || {
    echo "  $DEBUG_DIR"
    for subdir in screenshots logs html; do
        echo "  ├── $subdir/"
        ls -1 "$DEBUG_DIR/$subdir" 2>/dev/null | sed 's/^/  │   /'
    done
}
echo ""

# 显示最新的日志
echo "📋 最新的日志文件:"
latest_log=$(ls -t "$DEBUG_DIR/logs"/*.log 2>/dev/null | head -1)
if [ -n "$latest_log" ]; then
    echo "  $latest_log"
    echo ""
    echo "  日志内容:"
    tail -20 "$latest_log" | sed 's/^/  /'
else
    echo "  还没有日志文件"
fi
echo ""

# 显示最新的截图
echo "🖼️  最新的截图:"
latest_screenshots=$(ls -t "$DEBUG_DIR/screenshots"/*.png 2>/dev/null | head -3)
if [ -n "$latest_screenshots" ]; then
    echo "$latest_screenshots" | sed 's/^/  /'
else
    echo "  还没有截图文件"
fi
echo ""

# 显示文件统计
echo "📊 文件统计:"
echo "  日志文件: $(ls -1 "$DEBUG_DIR/logs"/*.log 2>/dev/null | wc -l) 个"
echo "  截图文件: $(ls -1 "$DEBUG_DIR/screenshots"/*.png 2>/dev/null | wc -l) 个"
echo "  HTML文件: $(ls -1 "$DEBUG_DIR/html"/*.html 2>/dev/null | wc -l) 个"
echo ""

# 显示磁盘占用
echo "💾 磁盘占用:"
echo "  日志目录: $(du -sh "$DEBUG_DIR/logs" 2>/dev/null | cut -f1)"
echo "  截图目录: $(du -sh "$DEBUG_DIR/screenshots" 2>/dev/null | cut -f1)"
echo "  HTML目录: $(du -sh "$DEBUG_DIR/html" 2>/dev/null | cut -f1)"
echo "  总计: $(du -sh "$DEBUG_DIR" 2>/dev/null | cut -f1)"
echo ""

# 显示帮助信息
echo "🔧 常用命令:"
echo "  查看最新日志: tail -f $DEBUG_DIR/logs/register_*.log"
echo "  清理旧文件: find $DEBUG_DIR -type f -mtime +7 -delete"
echo "  查看所有日志: ls -lht $DEBUG_DIR/logs/"
echo "  查看所有截图: ls -lht $DEBUG_DIR/screenshots/"
echo ""
