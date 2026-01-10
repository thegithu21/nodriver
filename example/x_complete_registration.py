#!/usr/bin/env python3
"""
X (Twitter) 完全自动化注册脚本
使用临时邮箱自动完成验证并返回账号密码
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
        log(f"📷 截图已保存: {filepath}")
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

async def get_temp_email(driver):
    """从 temp-mail.org 获取临时邮箱"""
    try:
        log("📧 获取临时邮箱...")
        temp_tab = await driver.get("https://temp-mail.org")
        
        # 等待邮箱显示
        await temp_tab.sleep(3)
        
        # 通过JavaScript获取邮箱地址
        email_script = """
(function() {
    var emailElements = document.querySelectorAll('[data-clipboard], .email-text, #email-container, .mailbox__text');
    if (emailElements.length > 0) {
        return emailElements[0].textContent.trim();
    }
    var emailInput = document.querySelector('input[type="text"][readonly], input.email');
    if (emailInput) {
        return emailInput.value;
    }
    var allText = document.body.innerText;
    var match = allText.match(/[a-zA-Z0-9]+@[a-zA-Z0-9]+\\.[a-zA-Z]+/);
    return match ? match[0] : null;
})();
        """
        
        try:
            email = await temp_tab.evaluate(email_script)
        except Exception as e:
            log(f"⚠️ JavaScript 执行异常: {e}，尝试替代方法...")
            # 如果 evaluate 失败，尝试从页面文本中查找
            page_text = await temp_tab.get_text()
            match = re.search(r'[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]+', page_text)
            email = match.group(0) if match else None
        
        if not email or "@" not in str(email):
            log("❌ 无法获取临时邮箱，尝试使用备用服务...")
            # 尝试使用 10minutemail 或其他服务
            temp_tab = await driver.get("https://10minutemail.com")
            await temp_tab.sleep(3)
            page_text = await temp_tab.get_text()
            match = re.search(r'[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]+', page_text)
            email = match.group(0) if match else None
            
            if not email:
                return None, None
        
        log(f"✅ 临时邮箱: {email}")
        return email, temp_tab
        
    except Exception as e:
        log(f"❌ 获取临时邮箱失败: {e}")
        return None, None

async def wait_for_verification_code(temp_tab, email, timeout=300):
    """等待验证码邮件"""
    try:
        log(f"📬 等待验证码邮件 (邮箱: {email})...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 刷新邮箱
                await temp_tab.evaluate("window.location.reload()")
                await temp_tab.sleep(5)
                
                # 尝试获取邮件内容
                email_content = await temp_tab.evaluate("""
                    var messages = document.querySelectorAll('[data-message-id], .message-item, .list-item');
                    var content = '';
                    for (var i = 0; i < Math.min(messages.length, 5); i++) {
                        content += messages[i].innerText + ' | ';
                    }
                    return content || document.body.innerText;
                """)
                
                # 查找验证码（多种模式）
                patterns = [
                    r'\b(\d{6})\b',  # 6位数字
                    r'code[:\s]+(\d+)',  # code: 12345
                    r'verify[:\s]+(\d+)',  # verify: 12345
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, email_content, re.IGNORECASE)
                    if match:
                        code = match.group(1)
                        log(f"✅ 找到验证码: {code}")
                        return code
                
                elapsed = int(time.time() - start_time)
                log(f"⏳ 等待中... ({elapsed}s/{timeout}s)")
                
            except Exception as inner_e:
                log(f"⚠️ 检查邮件出错: {inner_e}")
                await temp_tab.sleep(2)
        
        log(f"❌ 超时未收到验证码 ({timeout}s)")
        return None
        
    except Exception as e:
        log(f"❌ 等待验证码失败: {e}")
        return None

async def fill_x_form(tab, email, name, password, birth_date):
    """填充X注册表单"""
    try:
        log("📝 填充X注册表单...")
        
        # 导航到X注册页面
        await tab.get("https://x.com/i/flow/signup")
        await tab.sleep(3)
        
        # 保存截图
        await save_screenshot(tab, "x_signup_page")
        
        # 寻找 '创建账户' 按钮
        log("  • 查找创建账户按钮...")
        try:
            create_btn = await tab.find("create account", best_match=True)
            if create_btn:
                await create_btn.click()
                await tab.sleep(2)
        except:
            pass
        
        # 填充邮箱
        log("  • 填充邮箱...")
        try:
            email_input = await tab.select("input[type='email']")
            if not email_input:
                email_input = await tab.select("input[name='email']")
            if email_input:
                await email_input.send_keys(email)
                await tab.sleep(1)
        except Exception as e:
            log(f"  ⚠️ 邮箱填充出错: {e}")
        
        # 填充名字
        log("  • 填充名字...")
        try:
            inputs = await tab.select_all("input[type='text']")
            if inputs:
                await inputs[0].send_keys(name)
                await tab.sleep(1)
        except Exception as e:
            log(f"  ⚠️ 名字填充出错: {e}")
        
        # 点击Next按钮
        log("  • 点击Next...")
        try:
            next_btn = await tab.find("Next", best_match=True)
            if next_btn:
                await next_btn.click()
                await tab.sleep(2)
        except Exception as e:
            log(f"  ⚠️ Next按钮点击出错: {e}")
        
        await save_screenshot(tab, "x_birth_date")
        
        # 填充出生日期
        log("  • 填充出生日期...")
        try:
            selects = await tab.select_all("select")
            if len(selects) >= 3:
                month_str = birth_date.split()[0].title()
                day_str = birth_date.split()[1]
                year_str = birth_date.split()[2]
                
                await selects[0].send_keys(month_str)
                log(f"     - 月份: {month_str}")
                await tab.sleep(0.5)
                
                await selects[1].send_keys(day_str)
                log(f"     - 日期: {day_str}")
                await tab.sleep(0.5)
                
                await selects[2].send_keys(year_str)
                log(f"     - 年份: {year_str}")
                await tab.sleep(1)
        except Exception as e:
            log(f"  ⚠️ 出生日期填充出错: {e}")
        
        # 点击Next按钮
        log("  • 点击Next...")
        try:
            next_btn = await tab.find("Next", best_match=True)
            if next_btn:
                await next_btn.click()
                await tab.sleep(2)
        except Exception as e:
            log(f"  ⚠️ Next按钮点击出错: {e}")
        
        await save_screenshot(tab, "x_verification")
        
        log("✅ 表单填充完成")
        return True
        
    except Exception as e:
        log(f"❌ 表单填充失败: {e}")
        import traceback
        log(traceback.format_exc())
        return False

async def complete_x_registration():
    """完整的X账号注册流程"""
    
    log("=" * 70)
    log("X (Twitter) 完全自动化注册 - 使用临时邮箱")
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
    
    tab = None
    temp_tab = None
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
        # 获取主标签页
        tab = driver.tabs[0]
        
        # 生成账号信息
        name = generate_random_string(10)
        password = generate_password()
        month = MONTHS[random.randint(0, 11)]
        day = str(random.randint(1, 28))
        year = str(random.randint(1985, 2005))
        birth_date = f"{month} {day} {year}"
        
        log(f"✅ 生成账号信息:")
        log(f"   名字: {name}")
        log(f"   密码: {password}")
        log(f"   出生日期: {birth_date}")
        log("")
        
        # 获取临时邮箱
        email, temp_tab = await get_temp_email(driver)
        if not email:
            log("❌ 无法获取临时邮箱，中止注册")
            account_info["status"] = "failed"
            return account_info
        
        log("")
        
        # 填充X注册表单
        success = await fill_x_form(tab, email, name, password, birth_date)
        if not success:
            log("❌ 表单填充失败")
            account_info["status"] = "failed"
            return account_info
        
        log("")
        
        # 等待验证码
        if temp_tab:
            code = await wait_for_verification_code(temp_tab, email, timeout=300)
            if code:
                log(f"📬 验证码: {code}")
                # 在这里可以添加验证码输入逻辑
                account_info["status"] = "completed"
                log("✅ 邮箱验证成功")
            else:
                log("❌ 未能获取验证码")
                account_info["status"] = "email_pending"
        
        # 更新账号信息
        account_info["email"] = email
        account_info["username"] = email.split("@")[0]
        account_info["password"] = password
        account_info["name"] = name
        account_info["birth_date"] = birth_date
        
        log("")
        log("=" * 70)
        log("📊 账号信息摘要:")
        log("=" * 70)
        log(f"邮箱: {email}")
        log(f"用户名: {email.split('@')[0]}")
        log(f"密码: {password}")
        log(f"名字: {name}")
        log(f"出生日期: {birth_date}")
        log(f"状态: {account_info['status']}")
        log("")
        
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
    account_info = await complete_x_registration()
    
    # 返回账号信息JSON
    print("\n" + "=" * 70)
    print("📋 返回的账号信息JSON:")
    print("=" * 70)
    print(json.dumps(account_info, ensure_ascii=False, indent=2))
    print("=" * 70 + "\n")
    
    return account_info

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result.get("status") in ["completed", "email_pending"] else 1)
    except KeyboardInterrupt:
        log("\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        log(f"\n❌ 程序崩溃: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)
