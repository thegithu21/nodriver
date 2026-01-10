#!/usr/bin/env python3
"""
X (Twitter) 自动注册脚本 - 简化版
使用系统生成的邮箱自动完成注册并返回账号信息
"""

import asyncio
import os
import sys
import time
import random
import string
import json
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
ACCOUNTS_DIR = os.path.join(DEBUG_DIR, "accounts")

# 创建目录
for dir_path in [DEBUG_DIR, SCREENSHOTS_DIR, LOGS_DIR, ACCOUNTS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# 生成日志文件名
timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOGS_DIR, f"x_register_{timestamp_str}.log")
ACCOUNT_FILE = os.path.join(ACCOUNTS_DIR, f"x_account_{timestamp_str}.json")

# 日志记录器
class Logger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.file_handle = open(log_file, 'w', encoding='utf-8')
    
    def write(self, message):
        print(message, end='', flush=True)
        self.file_handle.write(message)
        self.file_handle.flush()
    
    def close(self):
        if self.file_handle:
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
    return "".join(random.choices(string.ascii_lowercase, k=length))

def generate_password():
    """生成强密码"""
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%"
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%")
    ]
    password += random.choices(chars, k=8)
    random.shuffle(password)
    return "".join(password)

async def register_x_account():
    """注册X账号"""
    
    log("=" * 70)
    log("X (Twitter) 自动注册")
    log("=" * 70)
    log(f"日志文件: {LOG_FILE}")
    log(f"账号文件: {ACCOUNT_FILE}")
    log("")
    
    # 启动浏览器
    log("📱 启动浏览器...")
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_executable_path="/usr/bin/google-chrome",
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )
    
    account_info = {
        "status": "failed",
        "email": None,
        "username": None,
        "password": None,
        "name": None,
        "birth_date": None,
        "created_at": datetime.now().isoformat()
    }
    
    try:
        tab = driver.tabs[0]
        
        # 生成账号信息
        email = f"{generate_random_string()}@{generate_random_string(6)}.com"
        name = generate_random_string(10)
        password = generate_password()
        month = MONTHS[random.randint(0, 11)]
        day = str(random.randint(1, 28))
        year = str(random.randint(1985, 2005))
        birth_date = f"{month} {day} {year}"
        
        log(f"✅ 生成账号信息:")
        log(f"   邮箱: {email}")
        log(f"   名字: {name}")
        log(f"   密码: {password}")
        log(f"   出生日期: {birth_date}")
        log("")
        
        # 访问X注册页面
        log("🌐 访问 X 注册页面...")
        await tab.get("https://x.com/i/flow/signup")
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
            log(f"⚠️ 创建账户按钮操作失败: {e}")
        
        # 填充邮箱
        log(f"📧 填充邮箱: {email}")
        try:
            # 尝试多种方法查找邮箱字段
            email_input = await tab.select("input[type='email']")
            if not email_input:
                email_input = await tab.select("input[placeholder*='email'], input[placeholder*='Email']")
            if not email_input:
                # 尝试查找所有输入字段，通常第一个是邮箱
                inputs = await tab.select_all("input[type='text']")
                if inputs and len(inputs) > 0:
                    email_input = inputs[0]
            
            if email_input:
                # 清空字段
                await email_input.click()
                await tab.sleep(0.5)
                # 选中所有文本
                await email_input.keyboard.hotkey("control", "a")
                await tab.sleep(0.2)
                # 发送邮箱
                await email_input.send_keys(email)
                log("✓ 邮箱已填充")
            else:
                log("❌ 找不到邮箱输入框，尝试使用JavaScript填充...")
                # 使用JavaScript填充
                await tab.evaluate(f"""
                    var emailInput = document.querySelector('input[type="email"]') || 
                                     document.querySelector('input[placeholder*="email"]') ||
                                     document.querySelector('input[placeholder*="Email"]');
                    if (emailInput) {{
                        emailInput.value = '{email}';
                        emailInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        emailInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                """)
                log("✓ 邮箱已通过JavaScript填充")
        except Exception as e:
            log(f"⚠️ 邮箱填充失败: {e}")
        
        await tab.sleep(1)
        
        # 填充姓名
        log(f"👤 填充姓名: {name}")
        try:
            inputs = await tab.select_all("input[type='text']")
            if inputs:
                await inputs[0].send_keys(name)
                log("✓ 姓名已填充")
        except Exception as e:
            log(f"❌ 姓名填充失败: {e}")
        
        await tab.sleep(1)
        
        # 点击Next按钮（寻找出生日期）
        log("⏭️ 点击Next按钮...")
        try:
            next_btn = await tab.find("Next", best_match=True)
            if next_btn:
                await next_btn.click()
                log("✓ Next按钮已点击")
                await tab.sleep(2)
        except Exception as e:
            log(f"⚠️ Next按钮点击失败: {e}")
        
        # 保存截图
        await save_screenshot(tab, "x_birthdate_form")
        
        # 填充出生日期
        log(f"📅 填充出生日期: {birth_date}")
        try:
            selects = await tab.select_all("select")
            if len(selects) >= 3:
                await selects[0].send_keys(month.title())  # 月份
                log(f"✓ 月份已填充: {month}")
                
                await selects[1].send_keys(day)  # 日期
                log(f"✓ 日期已填充: {day}")
                
                await selects[2].send_keys(year)  # 年份
                log(f"✓ 年份已填充: {year}")
                
                await tab.sleep(1)
            else:
                log(f"⚠️ 找不到所有的日期选择器 (找到: {len(selects)})")
        except Exception as e:
            log(f"❌ 出生日期填充失败: {e}")
        
        # 保存表单填充后的截图
        await save_screenshot(tab, "x_form_filled")
        
        # 点击Next按钮
        log("⏭️ 点击Next按钮...")
        try:
            next_btn = await tab.find("Next", best_match=True)
            if next_btn:
                await next_btn.click()
                log("✓ Next按钮已点击")
                await tab.sleep(2)
        except Exception as e:
            log(f"⚠️ Next按钮点击失败: {e}")
        
        # 保存验证页面截图
        await save_screenshot(tab, "x_verification_page")
        
        # 更新账号信息
        account_info["email"] = email
        account_info["username"] = email.split("@")[0]
        account_info["password"] = password
        account_info["name"] = name
        account_info["birth_date"] = birth_date
        account_info["status"] = "pending_verification"
        
        log("")
        log("=" * 70)
        log("📊 账号信息摘要:")
        log("=" * 70)
        log(f"邮箱: {email}")
        log(f"用户名: {email.split('@')[0]}")
        log(f"密码: {password}")
        log(f"名字: {name}")
        log(f"出生日期: {birth_date}")
        log(f"状态: 等待邮箱验证")
        log("")
        log("🔗 请在浏览器中打开邮箱链接完成验证")
        log("")
        
        # 保持浏览器打开以便手动验证
        log("⏳ 浏览器将保持打开状态（30秒）...")
        await tab.sleep(30)
        
        return account_info
        
    except Exception as e:
        log(f"❌ 发生错误: {e}")
        import traceback
        log(traceback.format_exc())
        account_info["status"] = "error"
        return account_info
        
    finally:
        # 保存账号信息
        try:
            log(f"💾 保存账号信息到: {ACCOUNT_FILE}")
            with open(ACCOUNT_FILE, 'w', encoding='utf-8') as f:
                json.dump(account_info, f, ensure_ascii=False, indent=2)
            log("✅ 账号信息已保存")
        except Exception as e:
            log(f"❌ 保存账号信息失败: {e}")
        
        # 关闭浏览器
        try:
            await driver.stop()
        except:
            pass
        
        # 关闭日志文件
        logger.close()

async def main():
    """主函数"""
    account_info = await register_x_account()
    
    # 返回账号信息JSON
    print("\n" + "=" * 70)
    print("📋 返回的账号信息JSON:")
    print("=" * 70)
    print(json.dumps(account_info, ensure_ascii=False, indent=2))
    print("=" * 70)
    print(f"\n账号信息已保存到: {ACCOUNT_FILE}")
    print(f"日志已保存到: {LOG_FILE}\n")
    
    return account_info

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序崩溃: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
