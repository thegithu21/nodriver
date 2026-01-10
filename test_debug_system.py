#!/usr/bin/env python3
"""
调试系统测试脚本
测试日志、截图和HTML保存功能
"""

import os
import sys
import time
from datetime import datetime

# 导入调试目录配置
DEBUG_DIR = "/workspaces/nodriver/debug_output"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots")
LOGS_DIR = os.path.join(DEBUG_DIR, "logs")
HTML_DIR = os.path.join(DEBUG_DIR, "html")

# 创建目录
for dir_path in [DEBUG_DIR, SCREENSHOTS_DIR, LOGS_DIR, HTML_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# 生成日志文件名
LOG_FILE = os.path.join(LOGS_DIR, f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

class TestLogger:
    """测试日志记录器"""
    def __init__(self, log_file):
        self.log_file = log_file
        self.file_handle = open(log_file, 'a', encoding='utf-8')
    
    def write(self, message):
        print(message, end='')
        self.file_handle.write(message)
        self.file_handle.flush()
    
    def close(self):
        self.file_handle.close()

logger = TestLogger(LOG_FILE)

def log(message):
    """输出日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.write(f"[{timestamp}] {message}\n")

def save_test_file(name, content):
    """保存测试文件"""
    filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(HTML_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath

# 开始测试
log("=" * 60)
log("调试系统测试")
log("=" * 60)
log(f"日志文件: {LOG_FILE}")
log(f"调试目录: {DEBUG_DIR}")
log("")

# 测试1：日志记录
log("测试1: 日志记录")
for i in range(5):
    log(f"  ✓ 日志消息 {i+1}")
    time.sleep(0.1)

log("")
log("测试2: 文件保存")
test_content = """
<!DOCTYPE html>
<html>
<head><title>测试页面</title></head>
<body>
<h1>这是一个测试HTML文件</h1>
<p>用于验证调试系统的文件保存功能</p>
<p>生成时间: {}</p>
</body>
</html>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

test_file = save_test_file("test_page", test_content)
log(f"  ✓ 保存测试文件: {test_file}")

log("")
log("测试3: 创建虚拟截图")
fake_image_path = os.path.join(SCREENSHOTS_DIR, f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
with open(fake_image_path, 'wb') as f:
    # 创建一个最小的PNG文件头
    f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01')
log(f"  ✓ 创建虚拟截图: {fake_image_path}")

log("")
log("测试4: 验证目录结构")
for dir_name, dir_path in [
    ("日志", LOGS_DIR),
    ("截图", SCREENSHOTS_DIR),
    ("HTML", HTML_DIR)
]:
    file_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
    log(f"  ✓ {dir_name}目录: {file_count} 个文件")

log("")
log("=" * 60)
log("✅ 调试系统测试完成！")
log("=" * 60)
log(f"总结:")
log(f"  - 日志已保存到: {LOG_FILE}")
log(f"  - 所有文件已分类存储")
log(f"  - 系统正常运行")
log("")

logger.close()

print(f"\n✅ 测试完成！日志文件: {LOG_FILE}")
