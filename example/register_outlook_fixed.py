#!/usr/bin/env python3
"""
Outlook 邮箱自动注册 - 修复版本
每个步骤保存：截图、HTML 和日志
"""

import asyncio
import os
import csv
import json
from datetime import datetime
import nodriver as uc


# 配置
DEBUG_DIR = "/workspaces/nodriver/debug_output"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots_fixed")
HTML_DIR = os.path.join(DEBUG_DIR, "html_fixed")
LOG_DIR = os.path.join(DEBUG_DIR, "logs_fixed")
CSV_FILE = os.path.join(DEBUG_DIR, "csv_accounts/accounts.csv")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


class RegistrationLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.logs = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {level}: {message}"
        self.logs.append(log_msg)
        print(log_msg)
        
    def save(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.logs))


async def take_screenshot(tab, name, logger):
    """保存截图"""
    try:
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        await tab.save_screenshot(filepath)
        logger.log(f"截图已保存: {filename}")
        return filepath
    except Exception as e:
        logger.log(f"截图失败: {e}", "ERROR")
        return None


async def save_html(tab, name, logger):
    """保存页面 HTML"""
    try:
        html = await tab.get_content()
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(HTML_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.log(f"HTML 已保存: {filename}")
        return filepath
    except Exception as e:
        logger.log(f"HTML 保存失败: {e}", "ERROR")
        return None


async def wait_and_log(tab, seconds, step_name, logger):
    """等待并记录"""
    logger.log(f"等待 {seconds} 秒...")
    for i in range(seconds):
        await tab.sleep(1)
        if i % 3 == 0:
            logger.log(f"  等待中... ({i}/{seconds})")


async def fill_input_field(tab, selector, value, logger, field_name):
    """填充输入框 - 多种方法尝试"""
    logger.log(f"尝试填充 {field_name}: {value}")
    
    # 方法 1: JavaScript 直接填充
    try:
        result = await tab.evaluate(f"""
        () => {{
            const input = document.querySelector('{selector}');
            if (input) {{
                input.focus();
                input.value = '{value}';
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                input.dispatchEvent(new KeyboardEvent('keyup', {{ bubbles: true }}));
                return 'success';
            }}
            return 'not_found';
        }}
        """)
        if result == 'success':
            # 验证真实值已写入
            try:
                read = await tab.evaluate(f"() => {{ const el = document.querySelector('{selector}'); return el ? el.value || el.textContent || el.innerText : null; }}")
                if read and str(read).strip().find(str(value).strip()) != -1:
                    logger.log(f"  ✓ {field_name} 已填充且验证通过 (方法1)")
                    return True
                else:
                    logger.log(f"  ✗ {field_name} 验证失败，实际值: {read}", "WARN")
            except Exception as e:
                logger.log(f"  ✗ 验证过程失败: {e}", "WARN")
    except Exception as e:
        logger.log(f"  ✗ 方法1失败: {e}", "WARN")
    
    # 方法 2: 逐字输入
    try:
        element = await tab.select(selector)
        if element:
            await element.click()
            await tab.sleep(0.5)
            for char in str(value):
                await tab.send_keys(char)
                await tab.sleep(0.05)
            # 验证逐字输入后实际值
            try:
                read = await tab.evaluate(f"() => {{ const el = document.querySelector('{selector}'); return el ? el.value || el.textContent || el.innerText : null; }}")
                if read and str(read).strip().find(str(value).strip()) != -1:
                    logger.log(f"  ✓ {field_name} 已填充且验证通过 (方法2)")
                    return True
                else:
                    logger.log(f"  ✗ {field_name} 验证失败 (方法2)，实际值: {read}", "WARN")
            except Exception as e:
                logger.log(f"  ✗ 方法2验证失败: {e}", "WARN")
    except Exception as e:
        logger.log(f"  ✗ 方法2失败: {e}", "WARN")
    
    logger.log(f"  ✗ 无法填充 {field_name}", "ERROR")
    return False


async def select_dropdown(tab, selector, value, logger, field_name):
    """选择下拉框"""
    logger.log(f"尝试选择 {field_name}: {value}")
    
    # 方法 1: 点击并选择
    try:
        element = await tab.select(selector)
        if element:
            await element.click()
            await tab.sleep(1)
            logger.log(f"  已打开下拉框")
            
            # 查找选项
            option_result = await tab.evaluate(f"""
            () => {{
                const options = document.querySelectorAll('[role="option"]');
                for (let opt of options) {{
                    if (opt.textContent.includes('{value}')) {{
                        opt.click();
                        return 'selected';
                    }}
                }}
                return 'not_found';
            }}
            """)
            if option_result == 'selected':
                # 验证下拉选择后的状态
                try:
                    read = await tab.evaluate(f"() => {{ const el = document.querySelector('{selector}'); if (!el) return null; return el.textContent || el.value || el.innerText || el.getAttribute('aria-label'); }}")
                    logger.log(f"  选择后读取到: {read}")
                    await tab.sleep(1)
                    logger.log(f"  ✓ {field_name} 已选择")
                    return True
                except Exception as e:
                    logger.log(f"  ✗ 下拉选择后验证失败: {e}", "WARN")
    except Exception as e:
        logger.log(f"  ✗ 下拉框选择失败: {e}", "WARN")
    
    return False


async def register_outlook():
    """主注册流程"""
    
    # 读取账户信息
    email = None
    password = None
    name = None
    birth_date = None
    
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row['Email']
            password = row['Password']
            name = row['Name']
            birth_date = row['Birth Date']
            break
    
    if not all([email, password, name, birth_date]):
        print("❌ 账户信息不完整")
        return False
    
    # 初始化日志
    log_file = os.path.join(LOG_DIR, f"registration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logger = RegistrationLogger(log_file)
    
    logger.log("=" * 70)
    logger.log("Outlook 邮箱自动注册 - 修复版本")
    logger.log("=" * 70)
    logger.log(f"邮箱: {email}")
    logger.log(f"密码: {password[:5]}***")
    logger.log(f"姓名: {name}")
    logger.log(f"生日: {birth_date}")
    
    # 启动浏览器
    print("\n🚀 启动浏览器...")
    logger.log("启动浏览器...")
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )
    
    try:
        # 步骤 1: 访问页面
        logger.log("\n--- 步骤 1: 访问 Outlook 注册页面 ---")
        print("\n[1/6] 访问 Outlook 注册页面...")
        tab = await driver.get("https://signup.live.com/?lic=1")
        await wait_and_log(tab, 6, "page_load", logger)
        await take_screenshot(tab, "01_page_loaded", logger)
        await save_html(tab, "01_page_loaded", logger)
        logger.log("✓ 页面已加载")
        
        # 步骤 2: 填充邮箱
        logger.log("\n--- 步骤 2: 填充邮箱 ---")
        print(f"\n[2/6] 填充邮箱: {email}")
        success = await fill_input_field(tab, 'input[type="email"]', email, logger, "邮箱")
        if not success:
            success = await fill_input_field(tab, 'input[name="email"]', email, logger, "邮箱 (name)")
        
        await take_screenshot(tab, "02_email_filled", logger)
        await save_html(tab, "02_email_filled", logger)
        
        # 点击下一步
        logger.log("点击下一步按钮...")
        await tab.evaluate("""
        () => {
            const btn = document.querySelector('button[type="submit"]') || 
                       document.querySelector('button:contains("下一步")') ||
                       Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Next'));
            if (btn) btn.click();
        }
        """)
        await wait_and_log(tab, 4, "after_email", logger)
        await take_screenshot(tab, "03_after_email_click", logger)
        await save_html(tab, "03_after_email_click", logger)
        
        # 步骤 3: 填充密码
        logger.log("\n--- 步骤 3: 填充密码 ---")
        print(f"\n[3/6] 填充密码...")
        success = await fill_input_field(tab, 'input[type="password"]', password, logger, "密码")
        if not success:
            success = await fill_input_field(tab, 'input[name="password"]', password, logger, "密码 (name)")
        
        await take_screenshot(tab, "04_password_filled", logger)
        await save_html(tab, "04_password_filled", logger)
        
        # 点击下一步
        logger.log("点击下一步按钮...")
        await tab.evaluate("""
        () => {
            const btn = document.querySelector('button[type="submit"]') || 
                       Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Next'));
            if (btn) btn.click();
        }
        """)
        await wait_and_log(tab, 4, "after_password", logger)
        await take_screenshot(tab, "05_after_password_click", logger)
        await save_html(tab, "05_after_password_click", logger)
        
        # 步骤 4: 填充姓名
        logger.log("\n--- 步骤 4: 填充姓名 ---")
        print(f"\n[4/6] 填充姓名: {name}")
        success = await fill_input_field(tab, 'input[name="firstname"]', name.split()[0], logger, "名字")
        if len(name.split()) > 1:
            success = await fill_input_field(tab, 'input[name="lastname"]', name.split()[1], logger, "姓氏")
        
        await take_screenshot(tab, "06_name_filled", logger)
        await save_html(tab, "06_name_filled", logger)
        
        # 点击下一步
        logger.log("点击下一步按钮...")
        await tab.evaluate("""
        () => {
            const btn = document.querySelector('button[type="submit"]') || 
                       Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Next'));
            if (btn) btn.click();
        }
        """)
        await wait_and_log(tab, 4, "after_name", logger)
        await take_screenshot(tab, "07_after_name_click", logger)
        await save_html(tab, "07_after_name_click", logger)
        
        # 步骤 5: 填充生日
        logger.log("\n--- 步骤 5: 填充生日 ---")
        print(f"\n[5/6] 填充生日: {birth_date}")
        
        # 解析生日
        date_parts = birth_date.split('/')
        month = date_parts[0]  # MM
        day = date_parts[1]    # DD
        year = date_parts[2]   # YYYY
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[int(month)]
        
        logger.log(f"月份: {month_name}, 日: {day}, 年: {year}")
        
        # 尝试填充月份
        logger.log("填充月份...")
        await select_dropdown(tab, '[aria-label*="Month"]', month_name, logger, "月份")
        
        # 尝试填充日期
        logger.log("填充日期...")
        await fill_input_field(tab, '[aria-label*="Day"]', day, logger, "日期")
        
        # 尝试填充年份
        logger.log("填充年份...")
        await fill_input_field(tab, '[aria-label*="Year"]', year, logger, "年份")
        
        await take_screenshot(tab, "08_birthdate_filled", logger)
        await save_html(tab, "08_birthdate_filled", logger)

        # 检测生日字段错误提示（例如: "Enter your birthdate."）
        try:
            error_found = await tab.evaluate("""
            () => {
                const texts = Array.from(document.querySelectorAll('[role="alert"], .error, .message, .ms-Text'))
                    .map(e => e.textContent || '').join('\n');
                if (texts && /enter your birthdate/i.test(texts)) return true;
                // 也尝试查找直显的提示文字
                const nodes = Array.from(document.querySelectorAll('div, span, p'))
                    .map(n => n.textContent || '');
                for (let t of nodes) {
                    if (/enter your birthdate/i.test(t)) return true;
                }
                return false;
            }
            """)
            if error_found:
                logger.log("检测到生日输入错误提示，停止并保存调查材料", "ERROR")
                await take_screenshot(tab, "08_birthdate_error", logger)
                await save_html(tab, "08_birthdate_error", logger)
                raise Exception("Birthdate validation error shown on page")
        except Exception as e:
            # 如果是我们主动抛出的异常，继续向上抛
            if str(e).startswith('Birthdate validation error'):
                raise
            logger.log(f"检测生日错误时出现异常: {e}", "WARN")
        
        # 点击下一步
        logger.log("点击下一步按钮...")
        await tab.evaluate("""
        () => {
            const btn = document.querySelector('button[type="submit"]') || 
                       Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Next'));
            if (btn) btn.click();
        }
        """)
        await wait_and_log(tab, 4, "after_birthdate", logger)
        await take_screenshot(tab, "09_after_birthdate_click", logger)
        await save_html(tab, "09_after_birthdate_click", logger)
        
        # 步骤 6: 等待注册完成
        logger.log("\n--- 步骤 6: 等待注册完成 ---")
        print(f"\n[6/6] 等待注册完成...")
        await wait_and_log(tab, 6, "completion", logger)
        await take_screenshot(tab, "10_registration_complete", logger)
        await save_html(tab, "10_registration_complete", logger)
        
        logger.log("✓ 注册流程完成")
        
    except Exception as e:
        logger.log(f"❌ 注册失败: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")
        
    finally:
        logger.save()
        print(f"\n📋 日志已保存: {log_file}")
        await driver.stop()


if __name__ == "__main__":
    asyncio.run(register_outlook())
