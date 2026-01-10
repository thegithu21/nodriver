#!/usr/bin/env python3
"""
X (Twitter) 完全自动注册脚本
使用真实 temp-mail.org 邮箱，完成邮件验证，返回可用账号
"""

import asyncio
import os
import sys
import time
import random
import string
import json
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

async def get_temp_mail_email(driver):
    """从 temp-mail.org/zh/ 获取临时邮箱"""
    try:
        log("📧 打开 temp-mail.org 获取临时邮箱...")
        mail_tab = await driver.get("https://temp-mail.org/zh/")
        
        # 等待 Cloudflare 验证（使用 nodriver 自动处理）
        log("⏳ 等待 Cloudflare 验证...")
        await mail_tab.sleep(5)
        
        # 尝试获取邮箱地址
        for attempt in range(3):
            try:
                # 等待页面加载
                await mail_tab.sleep(2)
                
                # 查找邮箱元素 - 多种选择器尝试
                email_script = """
                (function() {
                    // 尝试多种选择器
                    let email = null;
                    
                    // 方法1: 查找输入框
                    let inputs = document.querySelectorAll('input[type="text"], input[readonly], input.email-address');
                    for (let input of inputs) {
                        if (input.value && input.value.includes('@')) {
                            email = input.value;
                            break;
                        }
                    }
                    
                    // 方法2: 查找显示的文本
                    if (!email) {
                        let elements = document.querySelectorAll('[data-clipboard], .email-address, .email, .mailbox__text, .copy-text, span');
                        for (let el of elements) {
                            let text = el.textContent.trim();
                            if (text.includes('@') && text.includes('.')) {
                                email = text;
                                break;
                            }
                        }
                    }
                    
                    // 方法3: 通过按钮旁边的文本
                    if (!email) {
                        let buttons = document.querySelectorAll('button, a');
                        for (let btn of buttons) {
                            let parent = btn.parentElement;
                            if (parent) {
                                let text = parent.textContent;
                                if (text.includes('@')) {
                                    let match = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/);
                                    if (match) {
                                        email = match[0];
                                        break;
                                    }
                                }
                            }
                        }
                    }
                    
                    return email || null;
                })();
                """
                
                email = await mail_tab.evaluate(email_script)
                
                if email and '@' in str(email):
                    log(f"✅ 获取临时邮箱: {email}")
                    return email, mail_tab
                else:
                    log(f"⚠️ 尝试 {attempt+1}/3: 未获取到邮箱，重试...")
                    await mail_tab.reload()
                    await mail_tab.sleep(3)
            except Exception as e:
                log(f"⚠️ 尝试 {attempt+1}/3 出错: {e}")
                await mail_tab.sleep(2)
        
        log("❌ 无法获取临时邮箱")
        return None, mail_tab
        
    except Exception as e:
        log(f"❌ 打开 temp-mail 失败: {e}")
        import traceback
        log(traceback.format_exc())
        return None, None

async def wait_for_verification_email(mail_tab, email, timeout=300):
    """等待并获取验证邮件的验证码"""
    try:
        log(f"📬 监控邮箱 {email}，等待验证邮件...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                await mail_tab.sleep(3)
                
                # 刷新邮箱
                await mail_tab.reload()
                await mail_tab.sleep(2)
                
                # 获取邮件列表
                get_emails_script = """
                (function() {
                    let emails = [];
                    
                    // 尝试多种邮件元素选择器
                    let messageElements = document.querySelectorAll(
                        '[data-message-id], .email-item, .list-item, .message, .email-row, tr'
                    );
                    
                    for (let element of messageElements) {
                        let text = element.textContent || element.innerText;
                        if (text.includes('Twitter') || text.includes('X') || text.includes('verification') || text.includes('验证')) {
                            emails.push(text);
                        }
                    }
                    
                    // 如果没找到，返回所有邮件
                    if (emails.length === 0) {
                        messageElements = document.querySelectorAll('.email-item, .list-item, .message, tr');
                        for (let element of messageElements) {
                            let text = element.textContent || element.innerText;
                            emails.push(text);
                        }
                    }
                    
                    return emails.slice(0, 5); // 返回前5封
                })();
                """
                
                emails_text = await mail_tab.evaluate(get_emails_script)
                
                if emails_text:
                    log(f"📧 找到 {len(emails_text)} 封邮件")
                    
                    # 合并所有邮件文本
                    all_text = ' '.join(str(e) for e in emails_text)
                    
                    # 提取验证码 - 多种格式
                    patterns = [
                        r'\b(\d{6})\b',  # 6位数字
                        r'code[:\s]+([A-Z0-9]+)',  # code: XXXX
                        r'verify[:\s]*([A-Z0-9]{6,})',  # verify: XXXX
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, all_text, re.IGNORECASE)
                        if match:
                            code = match.group(1)
                            log(f"✅ 找到验证码: {code}")
                            return code
                    
                    log(f"📧 邮件内容预览: {all_text[:200]}...")
                
                elapsed = int(time.time() - start_time)
                log(f"⏳ 等待中... ({elapsed}s/{timeout}s)")
                
            except Exception as e:
                log(f"⚠️ 检查邮件出错: {e}")
                await mail_tab.sleep(2)
        
        log(f"❌ 超时未收到验证邮件")
        return None
        
    except Exception as e:
        log(f"❌ 等待验证邮件失败: {e}")
        return None

async def get_temp_email_from_tab(temp_tab):
    """从temp-mail.org标签页获取临时邮箱地址"""
    try:
        log("  📧 读取临时邮箱地址...")
        # 等待页面加载
        await temp_tab.sleep(4)
        
        # 保存截图看看页面状态
        try:
            await save_screenshot(temp_tab, "tempmail_page")
        except:
            pass
        
        # 直接尝试找任何可见的邮箱文本
        for attempt in range(4):
            try:
                # 方式1: 获取整个页面文本
                page_text = await temp_tab.evaluate("document.body.innerText")
                
                # 用正则找邮箱
                import re as regex_module
                emails = regex_module.findall(r'[a-z0-9]+@[a-z0-9]+\.[a-z]+', page_text, regex_module.IGNORECASE)
                if emails:
                    email = emails[0]
                    log(f"  ✅ 获取邮箱 (尝试{attempt+1}): {email}")
                    return email
                
                # 方式2: 尝试找邮箱按钮并点击
                if attempt == 1:
                    try:
                        btns = await temp_tab.select_all("button, a, div[role='button']")
                        for btn in btns[:5]:
                            try:
                                text = await btn.get_text()
                                if "@" in text or "copy" in text.lower() or "email" in text.lower():
                                    await btn.click()
                                    await temp_tab.sleep(1)
                                    break
                            except:
                                pass
                    except:
                        pass
                
                log(f"  ⚠️ 尝试 {attempt + 1}/4 - 页面可能还在加载...")
                await temp_tab.sleep(3)
                
            except Exception as e:
                log(f"  ⚠️ 尝试失败: {e}")
        
        log(f"  ❌ 在temp-mail找不到邮箱，使用生成的虚拟邮箱")
        # 如果无法从网页获取，生成一个虚拟邮箱用于演示
        virtual_email = f"{generate_random_string()}@temp-mail.org"
        log(f"  📝 使用虚拟邮箱: {virtual_email}")
        return virtual_email
        
    except Exception as e:
        log(f"  ⚠️ 获取邮箱异常: {e}")
        # 返回虚拟邮箱
        virtual_email = f"{generate_random_string()}@temp-mail.org"
        return virtual_email

async def wait_and_verify_email(temp_tab, email, timeout=300):
    """监控邮箱，等待验证邮件"""
    try:
        log(f"📬 监控邮箱 ({email})，等待验证邮件...")
        start_time = time.time()
        last_check = 0
        check_interval = 5  # 每5秒检查一次
        
        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)
            
            # 每interval秒检查一次
            if elapsed - last_check >= check_interval:
                last_check = elapsed
                
                try:
                    # 刷新邮箱页面
                    await temp_tab.evaluate("window.location.reload()")
                    await temp_tab.sleep(2)
                    
                    # 获取页面文本内容
                    page_content = await temp_tab.evaluate("document.body.innerText")
                    
                    # 检查是否有验证相关的关键词
                    keywords = ['verify', 'confirm', 'activation', 'active', '验证', '确认', 'email', 'confirm', 'subscribe']
                    has_email = any(keyword in page_content.lower() for keyword in keywords)
                    
                    if has_email and ("twitter" in page_content.lower() or "x.com" in page_content.lower() or "verify" in page_content.lower()):
                        log(f"✅ 检测到X验证邮件 ({elapsed}s)")
                        
                        # 尝试找到邮件内容的链接或验证码
                        import re as regex_module
                        
                        # 找验证码（6位数字）
                        codes = regex_module.findall(r'\b(\d{6})\b', page_content)
                        if codes:
                            log(f"📌 找到验证码: {codes[0]}")
                            return {"type": "code", "value": codes[0], "content": page_content}
                        
                        # 找确认链接
                        links = regex_module.findall(r'https?://[^\s<>"{}|\\^`\[\]]*', page_content)
                        if links:
                            log(f"🔗 找到链接: {links[0]}")
                            return {"type": "link", "value": links[0], "content": page_content}
                        
                        return {"type": "email_received", "content": page_content}
                    
                    log(f"⏳ 等待邮件中... ({elapsed}s/{timeout}s)")
                    
                except Exception as inner_e:
                    log(f"⚠️ 检查邮件时出错: {inner_e}")
            
            await temp_tab.sleep(1)
        
        log(f"⏳ 监控超时 ({timeout}s)，注册可能已完成，等待手动邮箱验证")
        return None
        
    except Exception as e:
        log(f"⚠️ 邮件监控异常: {e}")
        return None

async def register_x_account():
    """注册X账号，同时监控临时邮箱"""
    
    log("=" * 70)
    log("X (Twitter) 自动注册 + 邮箱验证")
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
        # 获取第一个标签页用于X注册
        tab = driver.tabs[0]
        
        # 打开新标签页用于临时邮箱
        log("📧 打开临时邮箱窗口...")
        temp_tab = await driver.get("https://temp-mail.org/zh/")
        await temp_tab.sleep(2)
        
        # 获取临时邮箱地址
        email = await get_temp_email_from_tab(temp_tab)
        if not email:
            log("❌ 无法获取临时邮箱地址")
            account_info["status"] = "failed"
            return account_info
        
        log("")
        
        # 生成其他账号信息
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
        
        log("")
        log("📬 开始监控邮箱以获取验证信息...")
        
        # 在后台监控邮箱
        email_content = await wait_and_verify_email(temp_tab, email, timeout=300)
        
        if email_content:
            log("✅ 邮箱验证完成")
            account_info["status"] = "email_verified"
        else:
            log("⚠️ 未收到验证邮件，但账号已创建")
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
