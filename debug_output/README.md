# 调试输出目录说明

这个目录用于存放所有自动化脚本运行过程中生成的调试信息。

## 目录结构

```
debug_output/
├── logs/              # 日志文件
│   └── register_YYYYMMDD_HHMMSS.log    # 每次运行的详细日志
├── screenshots/       # 截图文件
│   ├── tempmail_page_YYYYMMDD_HHMMSS.png
│   ├── tempmail_check_N_YYYYMMDD_HHMMSS.png
│   ├── twitter_initial_page_YYYYMMDD_HHMMSS.png
│   ├── twitter_registered_YYYYMMDD_HHMMSS.png
│   └── ...
└── html/             # HTML源代码文件
    ├── tempmail_source_YYYYMMDD_HHMMSS.html
    ├── tempmail_check_1_YYYYMMDD_HHMMSS.html
    ├── twitter_initial_page_YYYYMMDD_HHMMSS.html
    ├── twitter_before_email_YYYYMMDD_HHMMSS.html
    └── ...
```

## 文件说明

### logs/ 目录
- `register_YYYYMMDD_HHMMSS.log`: 每次脚本运行时的完整日志
  - 包含所有打印信息和时间戳
  - 用于调试和排查问题

### screenshots/ 目录
- `tempmail_page_*.png`: temp-mail.org 页面的截图
- `tempmail_check_N_*.png`: 邮件检查过程中的页面状态
- `twitter_*.png`: Twitter 注册过程中的各个步骤的截图
- 用于可视化调试，理解页面结构和问题所在

### html/ 目录
- `tempmail_source_*.html`: temp-mail.org 的页面源代码
- `tempmail_check_N_*.html`: 邮件检查时的页面源代码
- `twitter_*.html`: Twitter 页面的源代码
- 用于分析 DOM 结构和元素属性

## 如何使用

### 查看最新的日志
```bash
tail -f /workspaces/nodriver/debug_output/logs/register_*.log
```

### 查看特定步骤的截图
```bash
ls -lt /workspaces/nodriver/debug_output/screenshots/ | head -10
```

### 清理旧的调试文件
```bash
# 删除7天前的文件
find /workspaces/nodriver/debug_output/ -type f -mtime +7 -delete
```

## 时间戳格式

所有文件名中的时间戳格式为：`YYYYMMDD_HHMMSS`

例如：`register_20260110_103045.log` 表示 2026年1月10日 10:30:45 生成的日志

## 脚本集成

各个脚本已配置为自动将调试信息保存到此目录：
- `make_twitter_account_tempmail.py`: 完整集成日志、截图和HTML保存
- 所有日志都包含时间戳，便于追踪执行流程
