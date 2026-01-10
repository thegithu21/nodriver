#!/usr/bin/env python3
"""
X (Twitter) 账号自动注册脚本
支持自动填充信息，包含完整的日志和截图保存
"""

import asyncio
import os
import sys
import time
import random
import string
import re
from datetime import datetime

# 导入 nodriver
try:
    import nodriver as uc
except (ModuleNotFoundError, ImportError):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import nodriver as uc

# 设置调试输出目录
DEBUG_DIR = "/workspaces/nodriver/debug_output"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots")
LOGS_DIR = os.path.join(DEBUG_DIR, "logs")
HTML_DIR = os.path.join(DEBUG_DIR, "html")

# 创建目录
for dir_path in [DEBUG_DIR, SCREENSHOTS_DIR, LOGS_DIR, HTML_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# 生成日志文件名
LOG_FILE = os.path.join(LOGS_DIR, f"x_account_register_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# 日志记录器
class Logger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.file_handle = open(log_file, 'w', encoding='utf-8')
    
    def write(self, message):
        print(message, end='')
        self.file_handle.write(message)
        self.file_handle.flush()
    
    def close(self):
        self.file_handle.close()

logger = Logger(LOG_FILE)

def log(message):
    """输出日志（带时间戳）"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.write(f"[{timestamp}] {message}\n")

async def save_screenshot(tab, prefix=""):
    """保存截图"""
    try:
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png" if prefix else f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        await tab.save_screenshot(filepath)
        return filepath
    except Exception as e:
        log(f"❌ 截图保存失败: {e}")
        return None

# 月份列表
MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]

def generate_random_string(length=8):
    """生成随机字符串"""
    return "".join(random.choices(string.ascii_letters, k=length))

async def register_x_account():
    """注册X账号"""
    
    log("=" * 70)
    log("X (Twitter) 账号自动注册")
    log("=" * 70)
    log(f"日志文件: {LOG_FILE}")
    log(f"调试目录: {DEBUG_DIR}")
    log("")
    
    # 启动浏览器
    log("📱 启动浏览器...")
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_executable_path="/usr/bin/google-chrome",
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )
    
    try:
        # 生成账号信息
        email = f"{generate_random_string()}@{generate_random_string()}.com"
        name = generate_random_string(8)
        month = MONTHS[random.randint(0, 11)]
        day = str(random.randint(1, 28))
        year = str(random.randint(1980, 2005))
        
        log(f"\n📝 生成的账号信息:")
        log(f"  邮箱: {email}")
        log(f"  姓名: {name}")
        log(f"  生日: {month} {day}, {year}")
        
        # 访问X注册页面
        log(f"\n🌐 访问 X 注册页面...")
        tab = await driver.get("https://x.com/i/flow/signup")
        await tab.sleep(3)
        
        # 保存初始页面截图
        await save_screenshot(tab, "x_signup_initial")
        
        # 寻找创建账户按钮
        log("🔍 寻找 '创建账户' 按钮...")
        try:
            create_btn = await tab.find("create account", best_match=True)
            if create_btn:
                log("✓ 找到创建账户按钮，点击...")
                await create_btn.click()
                await tab.sleep(2)
        except Exception as e:
            log(f"⚠️  创建账户按钮操作失败: {e}")
        
        # 填充邮箱
        log(f"\n📧 填充邮箱: {email}")
        try:
            email_input = await tab.select("input[type='email']")
            if email_input:
                await email_input.send_keys(email)
                log("✓ 邮箱已填充")
            else:
                log("❌ 找不到邮箱输入框")
        except Exception as e:
            log(f"❌ 邮箱填充失败: {e}")
        
        await tab.sleep(1)
        
        # 填充姓名
        log(f"👤 填充姓名: {name}")
        try:
            name_input = await tab.select("input[type='text']")
            if name_input:
                await name_input.send_keys(name)
                log("✓ 姓名已填充")
        except Exception as e:
            log(f"❌ 姓名填充失败: {e}")
        
        await tab.sleep(1)
        
        # 填充出生日期
        log(f"📅 填充出生日期: {month} {day}, {year}")
        try:
            selects = await tab.select_all("select")
            if len(selects) >= 3:
                await selects[0].send_keys(month.title())  # 月份
                log(f"✓ 月份已填充: {month}")
                
                await selects[1].send_keys(day)  # 日期
                log(f"✓ 日期已填充: {day}")
                
                await selects[2].send_keys(year)  # 年份
                log(f"✓ 年份已填充: {year}")
        except Exception as e:
            log(f"❌ 出生日期填充失败: {e}")
        
        await tab.sleep(2)
        
        # 保存表单填充后的截图
        await save_screenshot(tab, "x_signup_form_filled")
        
        # 接受Cookie
        log("\n🍪 接受Cookie...")
        try:
            cookie_btn = await tab.find("accept all", best_match=True)
            if cookie_btn:
                await cookie_btn.click()
                log("✓ Cookie已接受")
                await tab.sleep(1)
        except Exception as e:
            log(f"⚠️  Cookie操作失败: {e}")
        
        # 点击Next按钮
        log("\n➡️  点击 'Next' 按钮...")
        try:
            next_btn = await tab.find("next", best_match=True)
            if next_btn:
                await next_btn.click()
                log("✓ Next按钮已点击")
                await tab.sleep(3)
        except Exception as e:
            log(f"❌ Next按钮点击失败: {e}")
        
        # 保存Next后的截图
        await save_screenshot(tab, "x_signup_after_next")
        
        # 点击Sign up按钮
        log("\n✅ 寻找 'Sign up' 按钮...")
        try:
            signup_btn = await tab.find("Sign up", best_match=True)
            if signup_btn:
                log("✓ 找到Sign up按钮")
                await signup_btn.click()
                log("✓ Sign up按钮已点击")
                await tab.sleep(3)
        except Exception as e:
            log(f"⚠️  Sign up按钮操作失败: {e}")
        
        # 保存最终截图
        final_screenshot = await save_screenshot(tab, "x_signup_final")
        
        log(f"\n📊 页面信息:")
        log(f"  标题: {tab.title}")
        log(f"  URL: {tab.url}")
        
        log("\n" + "=" * 70)
        log("✅ 注册流程完成！")
        log("=" * 70)
        log(f"最后截图: {final_screenshot}")
        log(f"账号邮箱: {email}")
        log(f"所有日志已保存到: {LOG_FILE}")
        
        # 继续等待以查看页面最终状态
        log("\n⏳ 等待10秒以查看最终页面状态...")
        await tab.sleep(10)
        
    except Exception as e:
        log(f"\n❌ 发生错误: {e}")
        import traceback
        log(traceback.format_exc())
    finally:
        try:
            driver.stop()
        except:
            pass
        logger.close()

async def main():
    """主函数"""
    await register_x_account()

if __name__ == '__main__':
    asyncio.run(main())
