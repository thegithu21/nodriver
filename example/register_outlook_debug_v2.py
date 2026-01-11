#!/usr/bin/env python3
"""
Outlook 邮箱自动注册 - 调试版
检查验证错误并到达生日页面
"""

import asyncio
import os
import csv
from datetime import datetime
import nodriver as uc


# 配置
DEBUG_DIR = "/workspaces/nodriver/debug_output"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots_debug")
HTML_DIR = os.path.join(DEBUG_DIR, "html_debug")
LOG_DIR = os.path.join(DEBUG_DIR, "logs_debug")
CSV_FILE = os.path.join(DEBUG_DIR, "csv_accounts/accounts.csv")

for d in [SCREENSHOTS_DIR, HTML_DIR, LOG_DIR]:
    os.makedirs(d, exist_ok=True)


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
        screenshot_name = f"{step_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_name)
        await tab.save_screenshot(screenshot_path)
        logger.log(f"📸 截图: {screenshot_name}")
    except Exception as e:
        logger.log(f"截图失败: {e}", "WARN")

    try:
        html_name = f"{step_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        html_path = os.path.join(HTML_DIR, html_name)
        html_content = await tab.get_content()
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.log(f"📄 HTML: {html_name}")
    except Exception as e:
        logger.log(f"HTML保存失败: {e}", "WARN")


async def check_url(tab, logger):
    """检查当前 URL"""
    try:
        url = tab.url
        logger.log(f"当前 URL: {url}")
        return url
    except:
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
    logger.log("Outlook 邮箱自动注册 - 调试版")
    logger.log("=" * 70)
    logger.log(f"邮箱: {email}")
    logger.log(f"密码: {password[:5]}***")
    logger.log(f"姓名: {name}")
    logger.log(f"生日: {birth_date}")

    # 启动浏览器
    logger.log("\n🚀 启动浏览器...")
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )

    try:
        # 步骤 1: 访问页面
        logger.log("\n--- 步骤 1: 访问页面 ---")
        tab = await driver.get("https://signup.live.com/?lic=1")
        await tab.sleep(5)
        await check_url(tab, logger)
        await save_artifacts(tab, "01_page_loaded", logger)
        logger.log("✓ 页面已加载")

        # 步骤 2: 输入邮箱
        logger.log("\n--- 步骤 2: 输入邮箱 ---")
        email_input = await tab.select('input[type="email"]', timeout=10)
        logger.log(f"✓ 找到邮箱输入框")
        
        await email_input.clear_input()
        await email_input.send_keys(email)
        logger.log(f"✓ 邮箱已输入: {email}")
        
        await save_artifacts(tab, "02_email_filled", logger)
        await tab.sleep(2)

        # 点击下一步
        logger.log("点击下一步按钮...")
        next_btn = await tab.select('button[type="submit"]', timeout=5)
        await next_btn.click()
        logger.log("✓ 已点击下一步")
        await tab.sleep(7)  # 等待更长时间

        # 检查 URL 和内容
        await check_url(tab, logger)
        await save_artifacts(tab, "03_after_email", logger)
        
        # 检查是否有错误
        html = await tab.get_content()
        if "password" in html.lower():
            logger.log("✓ 检测到密码字段 - 邮箱验证成功")
        elif "error" in html.lower() or "alert" in html.lower():
            logger.log("⚠️  检测到错误信息 - 邮箱可能未通过验证", "WARN")
            # 提取错误文本
            import re
            errors = re.findall(r'<[^>]*role="alert"[^>]*>([^<]+)</[^>]*>', html)
            for error in errors:
                logger.log(f"  错误内容: {error}")
        else:
            logger.log("⚠️  无法确定页面状态", "WARN")

        # 步骤 3: 等待密码字段或继续
        logger.log("\n--- 步骤 3: 查找密码输入框 ---")
        for attempt in range(1, 6):
            try:
                pwd_input = await tab.select('input[type="password"]', timeout=2)
                if pwd_input:
                    logger.log(f"✓ 找到密码输入框（第 {attempt} 次尝试成功）")
                    break
            except:
                logger.log(f"⏳ 第 {attempt} 次尝试未找到密码框，继续等待...")
                await tab.sleep(2)
        else:
            logger.log("❌ 经过 5 次尝试仍未找到密码输入框", "ERROR")
            await save_artifacts(tab, "03_password_not_found", logger)
            raise Exception("Password field not found after multiple attempts")

        # 输入密码
        logger.log("\n--- 步骤 4: 输入密码 ---")
        await pwd_input.clear_input()
        await pwd_input.send_keys(password)
        logger.log(f"✓ 密码已输入")
        
        await save_artifacts(tab, "04_password_filled", logger)
        await tab.sleep(1)
        
        # 点击下一步
        logger.log("点击下一步按钮...")
        next_btn = await tab.select('button[type="submit"]', timeout=5)
        await next_btn.click()
        logger.log("✓ 已点击下一步")
        await tab.sleep(5)
        await save_artifacts(tab, "05_after_password", logger)

        # 步骤 5: 输入名字
        logger.log("\n--- 步骤 5: 输入名字 ---")
        name_parts = name.split(' ', 1)
        first_name_input = await tab.select('input[name="firstname"]', timeout=10)
        logger.log(f"✓ 找到名字输入框")
        
        await first_name_input.clear_input()
        await first_name_input.send_keys(name_parts[0])
        logger.log(f"✓ 名字已输入: {name_parts[0]}")
        
        if len(name_parts) > 1:
            try:
                last_name_input = await tab.select('input[name="lastname"]', timeout=5)
                await last_name_input.clear_input()
                await last_name_input.send_keys(name_parts[1])
                logger.log(f"✓ 姓氏已输入: {name_parts[1]}")
            except:
                logger.log(f"⚠️  未找到姓氏输入框", "WARN")
        
        await save_artifacts(tab, "06_name_filled", logger)
        await tab.sleep(1)
        
        # 点击下一步
        logger.log("点击下一步按钮...")
        next_btn = await tab.select('button[type="submit"]', timeout=5)
        await next_btn.click()
        logger.log("✓ 已点击下一步")
        await tab.sleep(5)
        await check_url(tab, logger)
        await save_artifacts(tab, "07_after_name", logger)

        # 步骤 6: 输入生日 ===== KEY STEP =====
        logger.log("\n" + "="*70)
        logger.log("--- 步骤 6: 输入生日 ===== 关键步骤 =====")
        logger.log("="*70)
        
        parts = birth_date.split('-') if '-' in birth_date else birth_date.split('/')
        if len(parts) == 3:
            if '-' in birth_date:  # YYYY-MM-DD
                year, month, day = parts[0], parts[1], parts[2]
            else:  # MM/DD/YYYY
                month, day, year = parts[0], parts[1], parts[2]
        else:
            logger.log(f"✗ 生日格式错误: {birth_date}", "ERROR")
            raise Exception(f"Invalid date format: {birth_date}")
        
        logger.log(f"生日解析: 年={year}, 月={month}, 日={day}")
        
        # 多个选择器尝试
        selectors_day = [
            'input[aria-label*="Day"]',
            'input[placeholder*="Day"]',
            'input[placeholder="DD"]',
        ]
        
        selectors_month = [
            'input[aria-label*="Month"]',
            'input[placeholder*="Month"]',
            'input[placeholder="MM"]',
        ]
        
        selectors_year = [
            'input[aria-label*="Year"]',
            'input[placeholder*="Year"]',
            'input[placeholder="YYYY"]',
        ]
        
        day_found = False
        for selector in selectors_day:
            try:
                day_input = await tab.select(selector, timeout=2)
                if day_input:
                    logger.log(f"✓ 找到日期输入框")
                    await day_input.clear_input()
                    await day_input.send_keys(day)
                    logger.log(f"✓ 日期已输入: {day}")
                    day_found = True
                    break
            except:
                continue
        
        if not day_found:
            logger.log(f"⚠️  未找到日期输入框", "WARN")
        
        month_found = False
        for selector in selectors_month:
            try:
                month_input = await tab.select(selector, timeout=2)
                if month_input:
                    logger.log(f"✓ 找到月份输入框")
                    await month_input.clear_input()
                    await month_input.send_keys(month)
                    logger.log(f"✓ 月份已输入: {month}")
                    month_found = True
                    break
            except:
                continue
        
        if not month_found:
            logger.log(f"⚠️  未找到月份输入框", "WARN")
        
        year_found = False
        for selector in selectors_year:
            try:
                year_input = await tab.select(selector, timeout=2)
                if year_input:
                    logger.log(f"✓ 找到年份输入框")
                    await year_input.clear_input()
                    await year_input.send_keys(year)
                    logger.log(f"✓ 年份已输入: {year}")
                    year_found = True
                    break
            except:
                continue
        
        if not year_found:
            logger.log(f"⚠️  未找到年份输入框", "WARN")

        await save_artifacts(tab, "08_birthdate_page_loaded", logger)
        logger.log("\n✅ 成功到达生日页面并填充所有字段！")
        logger.log("="*70)

    except Exception as e:
        logger.log(f"\n❌ 流程中止: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")

    finally:
        driver.stop()
        logger.save()
        print(f"\n📝 日志已保存: {log_file}")


if __name__ == "__main__":
    asyncio.run(register_outlook())
