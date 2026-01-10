# Twitter create account with temp-mail.org
# 使用临时邮箱注册推特账户
# ultrafunkamsterdam

import asyncio
import logging
import random
import string
import re
import time
import os
from datetime import datetime

try:
    import nodriver as uc
except (ModuleNotFoundError, ImportError):
    import sys

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

# 生成日志文件名（包含时间戳）
LOG_FILE = os.path.join(LOGS_DIR, f"register_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# 配置日志记录器，同时输出到文件和控制台
class DualLogger:
    """同时输出到控制台和文件的日志记录器"""
    def __init__(self, log_file):
        self.log_file = log_file
        self.file_handle = open(log_file, 'a', encoding='utf-8')
    
    def write(self, message):
        print(message, end='')
        self.file_handle.write(message)
        self.file_handle.flush()
    
    def close(self):
        self.file_handle.close()

# 创建日志记录器
logger = DualLogger(LOG_FILE)

def log(message):
    """输出日志信息到控制台和文件"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.write(f"[{timestamp}] {message}\n")

def save_screenshot(file_path, prefix=""):
    """生成完整的截图路径"""
    filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png" if prefix else f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    return os.path.join(SCREENSHOTS_DIR, filename)

def save_html(content, prefix=""):
    """保存HTML内容到文件"""
    filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html" if prefix else f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(HTML_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath

months = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]

randstr = lambda k: "".join(random.choices(string.ascii_letters, k=k))


async def get_temp_mail(tab):
    """
    从 temp-mail.org 获取临时邮箱
    """
    log("\n========== 获取临时邮箱 ==========")
    
    # 访问 temp-mail.org
    await tab.get("https://temp-mail.org")
    await tab.sleep(5)  # 等待页面完全加载
    
    # 保存截图用于调试
    try:
        screenshot_path = save_screenshot("tempmail_page")
        await tab.save_screenshot(screenshot_path)
        log(f"页面截图: {screenshot_path}")
    except Exception as e:
        log(f"保存截图失败: {e}")
    
    # 获取页面 HTML 用于调试
    try:
        html = await tab.get_content()
        log(f"页面HTML长度: {len(html)}")
        html_file = save_html(html, "tempmail_source")
        log(f"页面源代码已保存: {html_file}")
        
        # 查找所有包含 @ 的文本
        emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', html)
        if emails:
            log(f"在HTML中找到邮箱: {emails}")
    except Exception as e:
        log(f"获取HTML失败: {e}")
    
    # 尝试多种方式获取邮箱地址
    email_methods = [
        ("input#mail", "ID选择器 #mail"),
        ("input.mail", "CLASS选择器 .mail"),
        ("input[name='mail']", "NAME属性 mail"),
        ("input[type='email']", "TYPE=email"),
        ("#email-display", "ID email-display"),
        (".email-display", "CLASS email-display"),
        ("[data-testid='email']", "data-testid=email"),
    ]
    
    for selector, description in email_methods:
        try:
            element = await tab.select(selector)
            if element:
                value = await element.get_attribute("value")
                if not value:
                    value = await element.get_text()
                if value and "@" in value:
                    log(f"✓ 使用{description}获取到邮箱: {value}")
                    return value
        except:
            pass
    
    # 尝试从 JavaScript 执行获取
    try:
        email = await tab.evaluate("""
            (function() {
                // 尝试多个选择器
                let element = document.querySelector('input[type="email"]') ||
                             document.querySelector('input#mail') ||
                             document.querySelector('input.email-address') ||
                             document.querySelector('[data-testid="email"]');
                if (element) return element.value;
                
                // 尝试从文本内容获取
                let text = document.body.innerText;
                let match = text.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+)/);
                if (match) return match[1];
                
                return null;
            })()
        """)
        if email:
            log(f"✓ 通过JavaScript获取到邮箱: {email}")
            return email
    except Exception as e:
        log(f"JavaScript执行失败: {e}")
    
    # 最后的尝试：查找所有输入框和显示元素
    try:
        inputs = await tab.select_all("input")
        for inp in inputs:
            value = await inp.get_attribute("value")
            if value and "@" in value and "." in value:
                log(f"✓ 从输入框获取到邮箱: {value}")
                return value
    except:
        pass
    
    raise Exception("无法从 temp-mail.org 获取临时邮箱")


async def wait_for_verification_code(tab, email, max_wait=300):
    """
    等待验证邮件，提取验证码
    """
    log(f"\n========== 等待验证邮件 ==========")
    log(f"邮箱: {email}")
    log(f"最长等待时间: {max_wait}秒")
    
    start_time = time.time()
    check_count = 0
    
    while time.time() - start_time < max_wait:
        check_count += 1
        log(f"\n[检查 #{check_count}] 检查邮件中...")
        
        try:
            # 保存当前页面状态
            try:
                html = await tab.get_content()
                html_file = save_html(html, f"tempmail_check_{check_count}")
                log(f"检查状态已保存: {html_file}")
            except:
                pass
            
            # 查找邮件列表中的第一条邮件
            email_item = await tab.select("div[class*='email-item']")
            
            if email_item:
                log("✓ 发现邮件！")
                
                # 点击邮件打开
                await email_item.click()
                await tab.sleep(2)
                
                # 获取邮件内容
                email_body = await tab.select("div[class*='email-body']")
                if email_body:
                    content = await email_body.get_text()
                    log(f"\n邮件内容:\n{content}")
                    
                    # 提取验证码 - 6位数字或其他格式
                    codes = re.findall(r'\b\d{6}\b', content)
                    if codes:
                        code = codes[0]
                        log(f"✓ 提取到验证码: {code}")
                        return code
                    
                    # 尝试其他格式的验证码
                    codes = re.findall(r'\b\d{4,8}\b', content)
                    if codes:
                        code = codes[0]
                        log(f"✓ 提取到验证码: {code}")
                        return code
                    
                    # 尝试查找 "code" 或 "pin" 后的数字
                    match = re.search(r'(?:code|pin|verify)[:\s]+(\d+)', content, re.IGNORECASE)
                    if match:
                        code = match.group(1)
                        log(f"✓ 提取到验证码: {code}")
                        return code
                    
                    raise Exception("邮件中找不到验证码")
                
            else:
                elapsed = int(time.time() - start_time)
                log(f"⏳ 还未收到邮件 (已等待 {elapsed}秒)")
                
        except Exception as e:
            elapsed = int(time.time() - start_time)
            log(f"检查失败: {e} (已等待 {elapsed}秒)")
        
        # 等待后再次检查
        await tab.sleep(5)
    
    raise Exception(f"在 {max_wait} 秒内未收到验证邮件")


async def register_twitter_with_tempmail():
    """
    使用临时邮箱注册 Twitter 账户
    """
    log("=" * 50)
    log("开始注册 Twitter 账户 (使用临时邮箱)")
    log("=" * 50)
    log(f"日志文件: {LOG_FILE}")
    log(f"调试目录: {DEBUG_DIR}")
    
    # 启动浏览器
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_executable_path="/usr/bin/google-chrome",
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )
    
    try:
        # 创建两个标签页：一个用于获取邮箱，一个用于注册
        tab_mail = await driver.get("https://temp-mail.org")
        await tab_mail.sleep(3)
        
        # 获取临时邮箱
        email = await get_temp_mail(tab_mail)
        
        # 访问 Twitter 注册页面
        log("\n========== 访问 Twitter 注册页面 ==========")
        tab_twitter = await driver.get("https://twitter.com")
        await tab_twitter.sleep(2)
        
        # 点击创建账户按钮
        log('寻找"创建账户"按钮')
        create_account = await tab_twitter.find("create account", best_match=True)
        if not create_account:
            # 保存调试信息
            screenshot_path = save_screenshot("twitter_no_create_button")
            await tab_twitter.save_screenshot(screenshot_path)
            html = await tab_twitter.get_content()
            html_file = save_html(html, "twitter_initial_page")
            raise Exception("找不到'创建账户'按钮")
        
        log('✓ 点击"创建账户"按钮')
        await create_account.click()
        await tab_twitter.sleep(3)
        
        # 填充邮箱
        log("\n========== 填充注册信息 ==========")
        log(f"填充邮箱: {email}")
        
        # 查找邮箱输入框
        email_input = await tab_twitter.select("input[type='email']")
        
        if not email_input:
            # 如果没有邮箱输入框，尝试点击"使用邮箱"链接
            use_email = await tab_twitter.find("use email", best_match=True)
            if use_email:
                log('✓ 点击"使用邮箱"链接')
                await use_email.click()
                await tab_twitter.sleep(2)
                email_input = await tab_twitter.select("input[type='email']")
        
        if not email_input:
            screenshot_path = save_screenshot("twitter_no_email_input")
            await tab_twitter.save_screenshot(screenshot_path)
            html = await tab_twitter.get_content()
            html_file = save_html(html, "twitter_before_email")
            raise Exception("找不到邮箱输入框")
        
        await email_input.send_keys(email)
        
        # 填充姓名
        log(f"填充姓名: {randstr(8)}")
        name_input = await tab_twitter.select("input[type='text']")
        if name_input:
            await name_input.send_keys(randstr(8))
        
        # 填充出生日期
        log("填充出生日期")
        selects = await tab_twitter.select_all("select")
        if len(selects) >= 3:
            month, day, year = selects[0], selects[1], selects[2]
            
            await month.send_keys(months[random.randint(0, 11)].title())
            await day.send_keys(str(random.randint(1, 28)))
            await year.send_keys(str(random.randint(1980, 2005)))
        
        # 接受 Cookie
        cookie_accept = await tab_twitter.find("accept all", best_match=True)
        if cookie_accept:
            log('✓ 接受 Cookie')
            await cookie_accept.click()
            await tab_twitter.sleep(1)
        
        # 点击下一步
        log("点击'下一步'按钮")
        next_btn = await tab_twitter.find(text="next", best_match=True)
        if next_btn:
            await next_btn.mouse_click()
            await tab_twitter.sleep(3)
        
        # 等待验证邮件
        verification_code = await wait_for_verification_code(tab_mail, email)
        
        # 填充验证码
        log("\n========== 填充验证码 ==========")
        log(f"验证码: {verification_code}")
        
        code_input = await tab_twitter.select("input[type='text'][placeholder*='code']")
        if not code_input:
            code_input = await tab_twitter.select("input[type='text']")
        
        if code_input:
            await code_input.send_keys(verification_code)
            await tab_twitter.sleep(1)
            
            # 提交验证码
            submit_btn = await tab_twitter.find("verify", best_match=True)
            if submit_btn:
                await submit_btn.click()
                await tab_twitter.sleep(3)
        
        # 保存截图
        screenshot_path = save_screenshot("twitter_registered")
        await tab_twitter.save_screenshot(screenshot_path)
        
        log(f"\n✓ 注册完成！")
        log(f"最后截图: {screenshot_path}")
        log(f"临时邮箱: {email}")
        
    except Exception as e:
        log(f"\n✗ 错误: {e}")
        import traceback
        log(traceback.format_exc())
    finally:
        driver.stop()
        logger.close()


async def main():
    await register_twitter_with_tempmail()


if __name__ == '__main__':
    asyncio.run(main())
