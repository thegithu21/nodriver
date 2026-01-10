# 🎯 调试输出目录使用指南

## 📂 目录结构概览

```
/workspaces/nodriver/debug_output/
├── logs/              # 📋 执行日志
├── screenshots/       # 🖼️  页面截图
├── html/             # 📄 页面源代码
├── README.md         # 📚 详细文档
└── show_debug_info.sh # 🔧 查看工具
```

## 🚀 快速开始

### 1. 查看所有调试信息
```bash
bash /workspaces/nodriver/debug_output/show_debug_info.sh
```

### 2. 查看最新日志
```bash
tail -f /workspaces/nodriver/debug_output/logs/register_*.log
```

### 3. 列出所有日志
```bash
ls -lht /workspaces/nodriver/debug_output/logs/
```

## 📋 日志文件

### 特点
- ✅ 自动时间戳命名：`register_YYYYMMDD_HHMMSS.log`
- ✅ 每行带时间戳：`[YYYY-MM-DD HH:MM:SS]`
- ✅ 同时输出到控制台和文件
- ✅ 完整保存所有执行信息

### 查看日志
```bash
# 实时查看最新日志
tail -f /workspaces/nodriver/debug_output/logs/register_*.log

# 查看特定日期的日志
cat /workspaces/nodriver/debug_output/logs/register_20260110*.log

# 搜索特定关键字
grep "错误\|Error\|✓" /workspaces/nodriver/debug_output/logs/register_*.log
```

## 🖼️ 截图文件

### 自动保存的截图
- `tempmail_page_*.png` - Temp-mail页面
- `tempmail_check_N_*.png` - 邮件检查过程
- `twitter_*.png` - Twitter注册过程

### 查看截图
```bash
# 列出所有截图
ls -lht /workspaces/nodriver/debug_output/screenshots/

# 在VS Code中打开
code /workspaces/nodriver/debug_output/screenshots/

# 在图像查看器中打开最新的截图
feh /workspaces/nodriver/debug_output/screenshots/$(ls -t /workspaces/nodriver/debug_output/screenshots/ | head -1)
```

## 📄 HTML源代码文件

### 保存的HTML文件
- `tempmail_source_*.html` - Temp-mail页面源代码
- `twitter_initial_page_*.html` - Twitter初始页面
- 其他关键步骤的HTML文件

### 分析HTML
```bash
# 列出所有HTML文件
ls -lht /workspaces/nodriver/debug_output/html/

# 在VS Code中打开
code /workspaces/nodriver/debug_output/html/

# 搜索特定元素
grep -i "input\|button\|form" /workspaces/nodriver/debug_output/html/tempmail_source_*.html
```

## 🔧 常用操作

### 清理旧文件
```bash
# 删除7天前的文件
find /workspaces/nodriver/debug_output -type f -mtime +7 -delete

# 删除所有文件（谨慎使用！）
find /workspaces/nodriver/debug_output -type f -delete
```

### 统计文件
```bash
# 统计文件数量
echo "日志: $(ls -1 /workspaces/nodriver/debug_output/logs | wc -l)"
echo "截图: $(ls -1 /workspaces/nodriver/debug_output/screenshots | wc -l)"
echo "HTML: $(ls -1 /workspaces/nodriver/debug_output/html | wc -l)"
```

### 导出日志
```bash
# 将所有日志合并到一个文件
cat /workspaces/nodriver/debug_output/logs/* > all_logs.txt

# 生成时间范围内的日志
grep "2026-01-10 10:4" /workspaces/nodriver/debug_output/logs/*.log > filtered_logs.txt
```

## 🎨 文件命名约定

所有生成的文件都遵循统一的时间戳格式：

```
name_YYYYMMDD_HHMMSS.ext

例子:
- register_20260110_104656.log
- tempmail_page_20260110_104705.png
- tempmail_source_20260110_104706.html
```

### 时间戳说明
- `YYYY` - 年份（4位）
- `MM` - 月份（2位，01-12）
- `DD` - 日期（2位，01-31）
- `HH` - 小时（2位，00-23）
- `MM` - 分钟（2位，00-59）
- `SS` - 秒钟（2位，00-59）

## 📊 文件大小管理

### 查看磁盘占用
```bash
du -sh /workspaces/nodriver/debug_output/
du -sh /workspaces/nodriver/debug_output/*
```

### 压缩旧日志
```bash
# 压缩7天前的日志
find /workspaces/nodriver/debug_output/logs -type f -mtime +7 -exec gzip {} \;
```

## 🔍 问题排查

### 找不到预期的文件
```bash
# 查看最新生成的所有文件
find /workspaces/nodriver/debug_output -type f -mmin -10

# 实时监控文件创建
watch -n 1 "ls -lht /workspaces/nodriver/debug_output/*/"
```

### 分析页面问题
```bash
# 查看HTML文件大小（如果为0可能是页面加载失败）
ls -lh /workspaces/nodriver/debug_output/html/

# 检查特定HTML文件的内容长度
wc -l /workspaces/nodriver/debug_output/html/*.html
```

## 📝 日志分析技巧

### 提取错误信息
```bash
grep -E "错误|Error|Exception|✗" /workspaces/nodriver/debug_output/logs/*.log
```

### 查看执行时间
```bash
# 计算日志生成的时间跨度
head -1 /workspaces/nodriver/debug_output/logs/register_*.log
tail -1 /workspaces/nodriver/debug_output/logs/register_*.log
```

### 统计关键步骤
```bash
# 统计特定步骤的出现次数
grep -c "✓" /workspaces/nodriver/debug_output/logs/*.log
grep -c "✗" /workspaces/nodriver/debug_output/logs/*.log
```

## 💡 最佳实践

1. **定期检查日志** - 每次运行后查看日志确保无错误
2. **保留关键截图** - 对问题时的截图进行备份
3. **分析HTML源代码** - 当找不到元素时检查HTML
4. **定期清理** - 删除超过一个月的旧文件
5. **记录时间戳** - 在报告问题时包含日志文件名和时间戳

## 🆘 获取帮助

遇到问题时，收集以下信息：
1. 相关的日志文件：`/workspaces/nodriver/debug_output/logs/register_*.log`
2. 失败时的截图：`/workspaces/nodriver/debug_output/screenshots/*.png`
3. 页面的HTML源代码：`/workspaces/nodriver/debug_output/html/*.html`

---

**最后更新**: 2026年1月10日  
**状态**: ✅ 调试系统正常运行
