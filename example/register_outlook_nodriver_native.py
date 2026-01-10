#!/usr/bin/env python3
"""
Outlook 邮箱自动注册 - nodriver 原生 API 版本
使用 tab.type() + tab.find() + fail-fast 策略
每步失败立即停止并保存 HTML/截图/日志
"""

import asyncio
import os
import csv
import json
from datetime import datetime
import nodriver as uc


# 配置
DEBUG_DIR = "/workspaces/nodriver/debug_output"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots_native")
HTML_DIR = os.path.join(DEBUG_DIR, "html_native")
LOG_DIR = os.path.join(DEBUG_DIR, "logs_native")
CSV_FILE = os.path.join(DEBUG_DIR, "csv_accounts/accounts.csv")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


class Logger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.logs = []

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] {level}: {message}"
        self.logs.append(msg)
        print(msg)

    def save(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.logs))


async def save_artifacts(tab, step_name, logger):
    """保存截图和 HTML"""
    try:
        # 截图
        screenshot_name = f"{step_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_name)
        await tab.save_screenshot(screenshot_path)
        logger.log(f"截图: {screenshot_name}")
    except Exception as e:
        logger.log(f"截图失败: {e}", "WARN")

    try:
        # HTML
        html_name = f"{step_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        html_path = os.path.join(HTML_DIR, html_name)
        html_content = await tab.get_content()
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.log(f"HTML: {html_name}")
    except Exception as e:
        logger.log(f"HTML保存失败: {e}", "WARN")


async def find_element(tab, selectors, timeout=15, logger=None):
    """尝试找元素，支持多个选择器，若失败返回 None"""
    if isinstance(selectors, str):
        selectors = [selectors]

    for selector in selectors:
        for attempt in range(timeout):
            try:
                element = await tab.find(selector, single=True)
                if element:
                    if logger:
                        logger.log(f"✓ 找到元素: {selector}")
                    return element
            except:
                pass
            await tab.sleep(1)

    if logger:
        logger.log(f"✗ 未找到任何元素 (尝试的选择器: {selectors})", "ERROR")
    return None


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
    logger = Logger(log_file)

    logger.log("=" * 70)
    logger.log("Outlook 邮箱自动注册 - nodriver 原生 API 版本")
    logger.log("=" * 70)
    logger.log(f"邮箱: {email}")
    logger.log(f"密码: {password[:5]}***")
    logger.log(f"姓名: {name}")
    logger.log(f"生日: {birth_date}")

    # 启动浏览器
    logger.log("启动浏览器...")
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )

    try:
        # 步骤 1: 访问页面
        logger.log("\n--- 步骤 1: 访问页面 ---")
        tab = await driver.get("https://signup.live.com/?lic=1")
        await tab.sleep(3)
        await save_artifacts(tab, "01_page_loaded", logger)
        logger.log("✓ 页面已加载")

        # 步骤 2: 输入邮箱
        logger.log("\n--- 步骤 2: 输入邮箱 ---")
        email_input = await find_element(
            tab,
            ['input[type="email"]', 'input[name="Email"]', '#floatingLabelInput4'],
            timeout=10,
            logger=logger
        )
        if not email_input:
            logger.log("✗ 未能找到邮箱输入框", "ERROR")
            await save_artifacts(tab, "02_email_not_found", logger)
            raise Exception("Email input not found")

        await email_input.clear()
        await email_input.type(email, delay=0.05)
        await tab.sleep(1)
        
        # 验证写入
        actual_value = await email_input.element_eval("el => el.value")
        logger.log(f"  邮箱输入后的值: {actual_value}")
        if email not in actual_value and actual_value:
            logger.log(f"  ⚠️  值部分匹配", "WARN")
        elif not actual_value:
            logger.log(f"  ✗ 邮箱输入框仍为空！", "ERROR")
            await save_artifacts(tab, "02_email_empty", logger)
            raise Exception("Email input failed - value is empty")

        await save_artifacts(tab, "02_email_filled", logger)
        logger.log("✓ 邮箱已输入")

        # 点击下一步
        logger.log("点击下一步按钮...")
        next_btn = await find_element(tab, 'button[type="submit"]', timeout=5, logger=logger)
        if not next_btn:
            logger.log("✗ 未找到下一步按钮", "ERROR")
            await save_artifacts(tab, "02_button_not_found", logger)
            raise Exception("Next button not found")
        
        await next_btn.click()
        await tab.sleep(3)
        await save_artifacts(tab, "03_after_email_click", logger)

        # 步骤 3: 输入密码
        logger.log("\n--- 步骤 3: 输入密码 ---")
        pwd_input = await find_element(
            tab,
            ['input[type="password"]', 'input[aria-label*="password" i]', 'input[name="Password"]'],
            timeout=10,
            logger=logger
        )
        if not pwd_input:
            logger.log("✗ 未能找到密码输入框", "ERROR")
            await save_artifacts(tab, "03_password_not_found", logger)
            raise Exception("Password input not found")

        await pwd_input.clear()
        await pwd_input.type(password, delay=0.05)
        await tab.sleep(1)

        # 验证写入
        actual_value = await pwd_input.element_eval("el => el.value")
        logger.log(f"  密码输入后的值长度: {len(actual_value)}")
        if len(actual_value) < len(password) / 2:
            logger.log(f"  ✗ 密码输入不完整！", "ERROR")
            await save_artifacts(tab, "03_password_incomplete", logger)
            raise Exception("Password input failed - incomplete")

        await save_artifacts(tab, "03_password_filled", logger)
        logger.log("✓ 密码已输入")

        # 点击下一步
        logger.log("点击下一步按钮...")
        next_btn = await find_element(tab, 'button[type="submit"]', timeout=5, logger=logger)
        if not next_btn:
            logger.log("✗ 未找到下一步按钮", "ERROR")
            await save_artifacts(tab, "03_button_not_found", logger)
            raise Exception("Next button not found")
        
        await next_btn.click()
        await tab.sleep(3)
        await save_artifacts(tab, "04_after_password_click", logger)

        # 步骤 4: 输入姓名
        logger.log("\n--- 步骤 4: 输入姓名 ---")
        name_parts = name.split()
        
        # 尝试输入名字
        first_name_input = await find_element(
            tab,
            ['input[name="firstname"]', 'input[aria-label*="first" i]', 'input[id*="FirstName"]'],
            timeout=10,
            logger=logger
        )
        if not first_name_input:
            logger.log("✗ 未能找到名字输入框", "ERROR")
            await save_artifacts(tab, "04_name_not_found", logger)
            raise Exception("First name input not found")

        await first_name_input.clear()
        await first_name_input.type(name_parts[0], delay=0.05)
        await tab.sleep(1)

        # 尝试输入姓氏
        if len(name_parts) > 1:
            last_name_input = await find_element(
                tab,
                ['input[name="lastname"]', 'input[aria-label*="last" i]', 'input[id*="LastName"]'],
                timeout=10,
                logger=logger
            )
            if last_name_input:
                await last_name_input.clear()
                await last_name_input.type(name_parts[1], delay=0.05)
                await tab.sleep(1)
            else:
                logger.log("⚠️  未找到姓氏输入框，跳过", "WARN")

        await save_artifacts(tab, "04_name_filled", logger)
        logger.log("✓ 姓名已输入")

        # 点击下一步
        logger.log("点击下一步按钮...")
        next_btn = await find_element(tab, 'button[type="submit"]', timeout=5, logger=logger)
        if not next_btn:
            logger.log("✗ 未找到下一步按钮", "ERROR")
            await save_artifacts(tab, "04_button_not_found", logger)
            raise Exception("Next button not found")
        
        await next_btn.click()
        await tab.sleep(3)
        await save_artifacts(tab, "05_after_name_click", logger)

        # 步骤 5: 输入生日
        logger.log("\n--- 步骤 5: 输入生日 ---")
        
        # 解析生日
        date_parts = birth_date.split('/')
        month = date_parts[0]
        day = date_parts[1]
        year = date_parts[2]
        
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[int(month)]
        
        logger.log(f"解析生日: 月={month_name}, 日={day}, 年={year}")

        # 尝试填充月份（下拉框）
        logger.log("填充月份...")
        month_dropdown = await find_element(
            tab,
            ['[aria-label*="Month"]', 'select[name*="month"]', 'div[id*="month"]'],
            timeout=10,
            logger=logger
        )
        if month_dropdown:
            try:
                await month_dropdown.click()
                await tab.sleep(1)
                # 尝试找月份选项
                options = await tab.find('[role="option"]', single=False)
                for opt in options:
                    text = await opt.element_eval("el => el.textContent")
                    if month_name in text:
                        await opt.click()
                        logger.log(f"✓ 月份已选择: {month_name}")
                        break
            except Exception as e:
                logger.log(f"⚠️  月份选择失败: {e}", "WARN")
        else:
            logger.log("⚠️  未找到月份选择器", "WARN")

        # 尝试填充日期
        logger.log("填充日期...")
        day_input = await find_element(
            tab,
            ['[aria-label*="Day"]', 'input[name*="day"]', 'input[placeholder*="Day"]'],
            timeout=10,
            logger=logger
        )
        if day_input:
            await day_input.clear()
            await day_input.type(day, delay=0.05)
            logger.log(f"✓ 日期已输入: {day}")
        else:
            logger.log("⚠️  未找到日期输入框", "WARN")

        # 尝试填充年份
        logger.log("填充年份...")
        year_input = await find_element(
            tab,
            ['[aria-label*="Year"]', 'input[name*="year"]', 'input[placeholder*="Year"]'],
            timeout=10,
            logger=logger
        )
        if year_input:
            await year_input.clear()
            await year_input.type(year, delay=0.05)
            logger.log(f"✓ 年份已输入: {year}")
        else:
            logger.log("⚠️  未找到年份输入框", "WARN")

        await tab.sleep(2)
        await save_artifacts(tab, "05_birthdate_filled", logger)

        # 点击下一步
        logger.log("点击下一步按钮...")
        next_btn = await find_element(tab, 'button[type="submit"]', timeout=5, logger=logger)
        if next_btn:
            await next_btn.click()
            await tab.sleep(3)
            await save_artifacts(tab, "06_after_birthdate_click", logger)
            logger.log("✓ 已点击下一步")
        else:
            logger.log("⚠️  未找到最终的下一步按钮", "WARN")

        logger.log("\n✅ 流程完成（无致命错误）")

    except Exception as e:
        logger.log(f"\n❌ 流程中止: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")

    finally:
        logger.save()
        print(f"\n📋 日志已保存: {log_file}")
        await driver.stop()


if __name__ == "__main__":
    asyncio.run(register_outlook())
