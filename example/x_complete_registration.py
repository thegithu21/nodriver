#!/usr/bin/env python3
"""
X (Twitter) 完全自动化注册脚本
使用临时邮箱，自动完成整个注册流程，并返回账号密码
"""

import asyncio
import os
import sys
import time
import random
import string
import re
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
HTML_DIR = os.path.join(DEBUG_DIR, "html")
ACCOUNTS_DIR = os.path.join(DEBUG_DIR, "accounts")

# 创建目录
for dir_path in [DEBUG_DIR, SCREENSHOTS_DIR, LOGS_DIR, HTML_DIR, ACCOUNTS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# 生成日志文件名
LOG_FILE = os.path.join(LOGS_DIR, f"x_complete_register_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
ACCOUNT_FILE = os.path.join(ACCOUNTS_DIR, f"x_account_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

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

def generate_random_string(length=8):
    """生成随机字符串"""
    return "".join(random.choices(string.ascii_letters, k=length))

def generate_password():
    """生成强密码"""
    password = ""
    password += random.choice(string.ascii_uppercase)
    password += random.choice(string.ascii_lowercase)
    password += random.choice(string.digits)
    password += random.choice("!@#$%^&*")
    password += "".join(random.choices(string.ascii_letters + string.digits, k=8))
    return ''.join(random.sample(password, len(password)))

MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]

async def get_temp_email():
    """从 temp-mail.org 获取临时邮箱"""
    log("\n📧 获取临时邮箱...")
    
    temp_tab = await uc.driver.get("https://temp-mail.org")
    await temp_tab.sleep(5)
    
    try:
        # 尝试获取显示的邮箱地址
        email = await temp_tab.evaluate("""
            (function() {
                // 尝试多个可能的邮箱显示位置
                let elements = [
                    document.querySelector('input[type="email"]'),
                    document.querySelector('.mail-address'),
                    document.querySelector('[data-address]'),
                    document.querySelector('#mail-display'),
                    document.querySelector('.address-display')
                ];
                
                for (let el of elements) {
                    if (el) {
                        let value = el.value || el.textContent || el.getAttribute('data-address');
                        if (value && value.includes('@')) return value;
                    }
                }
                
                // 尝试从页面文本提取邮箱
                let text = document.body.innerText;
                let match = text.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+)/);
                if (match) return match[1];
                
                return null;
            })()
        """)
        
        if email:
            log(f"✓ 获取到临时邮箱: {email}")
            return email, temp_tab
        else:
            log("❌ 无法从页面获取邮箱")
            await save_screenshot(temp_tab, "tempmail_failed")
            return None, temp_tab
            
    except Exception as e:
        log(f"❌ 获取邮箱失败: {e}")
        return None, temp_tab

async def wait_for_verification_code(temp_tab, email, timeout=300):
    """等待验证邮件并提取验证码"""
    log(f"\n⏳ 等待验证邮件 (最长{timeout}秒)...")
    
    start_time = time.time()
    check_count = 0
    
    while time.time() - start_time < timeout:
        check_count += 1
        elapsed = int(time.time() - start_time)
        
        try:
            # 刷新页面查看新邮件
            await temp_tab.reload()
            await temp_tab.sleep(3)
            
            # 尝试找邮件
            email_item = await temp_tab.select("[class*='email-item']")
            
            if email_item:
                log(f"✓ 找到邮件 (第{check_count}次检查)")
                await email_item.click()
                await temp_tab.sleep(2)
                
                # 获取邮件内容
                email_content = await temp_tab.evaluate("""
                    (function() {
                        let content = document.body.innerText;
                        return content;
                    })()
                """)
                
                # 提取验证码 - 尝试多种格式
                patterns = [
                    r'\b\d{6}\b',           # 6位数字
                    r'\b\d{4,8}\b',         # 4-8位数字
                    r'code[:\s]+(\d+)',     # code: 123456
                    r'verify[:\s]+(\d+)',   # verify: 123456
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, email_content, re.IGNORECASE)
                    if match:
                        code = match.group(1) if '(' in pattern else match.group(0)
                        log(f"✓ 提取到验证码: {code}")
                        return code
                
                log(f"⚠️ 邮件中未找到验证码")
                log(f"邮件内容片段: {email_content[:200]}")
                
            else:
                log(f"⏳ 等待邮件中... (已等待 {elapsed}秒)")
                
        except Exception as e:
            log(f"⚠️ 检查邮件失败: {e}")
        
        if elapsed % 30 == 0 and elapsed > 0:
            log(f"💡 已等待{elapsed}秒，继续等待...")
        
        await temp_tab.sleep(5)
    
    log(f"❌ 在{timeout}秒内未收到验证邮件")
    return None

async def complete_x_registration():
    """完成X账号注册"""
    
    log("=" * 80)
    log("X (Twitter) 完全自动化注册 - 使用临时邮箱")
    log("=" * 80)
    log(f"日志文件: {LOG_FILE}")
    log(f"账号信息: {ACCOUNT_FILE}")
    
    # 启动浏览器
    log("\n📱 启动浏览器...")
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
        # 获取临时邮箱
        email, temp_tab = await get_temp_email()
        if not email:
            raise Exception("无法获取临时邮箱")
        
        account_info["email"] = email
        
        # 访问X注册页面
        log("\n🌐 访问X注册页面...")
        x_tab = await driver.get("https://x.com/i/flow/signup")
        await x_tab.sleep(3)
        await save_screenshot(x_tab, "x_start")
        
        # 生成账号信息
        password = generate_password()
        name = generate_random_string(10)
        month = MONTHS[random.randint(0, 11)]
        day = str(random.randint(1, 28))
        year = str(random.randint(1980, 2005))
        
        account_info["name"] = name
        account_info["password"] = password
        account_info["birth_date"] = f"{month} {day}, {year}"
        
        log(f"\n📝 账号信息:")
        log(f"  邮箱: {email}")
        log(f"  姓名: {name}")
        log(f"  密码: {password}")
        log(f"  生日: {month} {day}, {year}")
        
        # 寻找并点击创建账户
        log("\n🔍 寻找创建账户按钮...")
        try:
            create_btn = await x_tab.find("create account", best_match=True)
            if create_btn:
                await create_btn.click()
                await x_tab.sleep(2)
                log("✓ 点击创建账户")
        except Exception as e:
            log(f"⚠️ 创建账户按钮操作: {e}")
        
        # 填充邮箱
        log(f"\n📧 填充邮箱...")
        try:
            email_input = await x_tab.select("input[type='email']")
            if email_input:
                await email_input.send_keys(email)
                log("✓ 邮箱已填充")
                await x_tab.sleep(1)
        except Exception as e:
            log(f"❌ 邮箱填充失败: {e}")
        
        # 填充姓名
        log(f"👤 填充姓名...")
        try:
            name_input = await x_tab.select("input[type='text']")
            if name_input:
                await name_input.send_keys(name)
                log("✓ 姓名已填充")
                await x_tab.sleep(1)
        except Exception as e:
            log(f"⚠️ 姓名填充: {e}")
        
        # 填充出生日期
        log(f"📅 填充出生日期...")
        try:
            selects = await x_tab.select_all("select")
            if len(selects) >= 3:
                await selects[0].send_keys(month.title())
                await selects[1].send_keys(day)
                await selects[2].send_keys(year)
                log("✓ 出生日期已填充")
                await x_tab.sleep(2)
        except Exception as e:
            log(f"⚠️ 出生日期填充: {e}")
        
        await save_screenshot(x_tab, "x_form_filled")
        
        # 接受Cookie
        try:
            cookie_btn = await x_tab.find("accept all", best_match=True)
            if cookie_btn:
                await cookie_btn.click()
                await x_tab.sleep(1)
                log("✓ Cookie已接受")
        except:
            pass
        
        # 点击Next
        log("\n➡️ 点击Next按钮...")
        try:
            next_btn = await x_tab.find("next", best_match=True)
            if next_btn:
                await next_btn.click()
                await x_tab.sleep(3)
                log("✓ Next按钮已点击")
        except Exception as e:
            log(f"⚠️ Next按钮: {e}")
        
        await save_screenshot(x_tab, "x_after_next")
        
        # 处理可能的电话号码请求
        log("\n📱 检查是否需要电话号码...")
        try:
            phone_input = await x_tab.select("input[type='tel']")
            if phone_input:
                log("⚠️ 页面要求输入电话号码")
                # 尝试跳过或使用虚拟号码
                await save_screenshot(x_tab, "x_phone_request")
        except:
            pass
        
        # 点击Sign up
        log("\n✅ 寻找Sign up按钮...")
        try:
            signup_btn = await x_tab.find("Sign up", best_match=True)
            if signup_btn:
                await signup_btn.click()
                await x_tab.sleep(3)
                log("✓ Sign up按钮已点击")
        except Exception as e:
            log(f"⚠️ Sign up按钮: {e}")
        
        await save_screenshot(x_tab, "x_after_signup")
        
        # 等待验证邮件和验证码
        log("\n📨 等待验证邮件...")
        verification_code = await wait_for_verification_code(temp_tab, email, timeout=300)
        
        if verification_code:
            log(f"\n✓ 获得验证码: {verification_code}")
            
            # 填充验证码
            log("\n🔢 填充验证码...")
            try:
                code_inputs = await x_tab.select_all("input[type='text']")
                for code_input in code_inputs:
                    try:
                        placeholder = await code_input.get_attribute("placeholder")
                        if placeholder and ("code" in placeholder.lower() or "verify" in placeholder.lower()):
                            await code_input.send_keys(verification_code)
                            log("✓ 验证码已填充")
                            await x_tab.sleep(2)
                            break
                    except:
                        continue
            except Exception as e:
                log(f"⚠️ 验证码填充: {e}")
            
            await save_screenshot(x_tab, "x_after_verification")
        else:
            log("⚠️ 未能获得验证码，继续流程...")
        
        # 设置密码 (如果需要)
        log("\n🔐 检查密码设置...")
        try:
            password_input = await x_tab.select("input[type='password']")
            if password_input:
                await password_input.send_keys(password)
                log("✓ 密码已设置")
                await x_tab.sleep(2)
        except:
            pass
        
        # 最终确认和完成
        log("\n⏳ 等待注册完成...")
        await x_tab.sleep(5)
        
        # 检查是否到达主页或个人资料页
        current_url = x_tab.url
        current_title = x_tab.title
        
        log(f"\n最终页面:")
        log(f"  标题: {current_title}")
        log(f"  URL: {current_url}")
        
        if "home" in current_url.lower() or "x.com/home" in current_url:
            log("\n✅ 注册成功！")
            account_info["status"] = "success"
            account_info["username"] = email.split("@")[0]  # 使用邮箱前缀作为用户名
        else:
            log("\n⚠️ 注册流程可能未完全完成")
            account_info["status"] = "completed"
        
        await save_screenshot(x_tab, "x_final")
        
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
    
    # 保存账号信息
    log(f"\n💾 保存账号信息到: {ACCOUNT_FILE}")
    with open(ACCOUNT_FILE, 'w', encoding='utf-8') as f:
        json.dump(account_info, f, ensure_ascii=False, indent=2)
    
    return account_info

async def main():
    """主函数"""
    account_info = await complete_x_registration()
    
    # 显示结果
    print("\n" + "="*80)
    print("📊 注册结果")
    print("="*80)
    print(json.dumps(account_info, ensure_ascii=False, indent=2))
    print("="*80)
    
    return account_info

if __name__ == '__main__':
    result = asyncio.run(main())
    
    # 退出时返回状态码
    sys.exit(0 if result.get("status") == "success" else 1)
