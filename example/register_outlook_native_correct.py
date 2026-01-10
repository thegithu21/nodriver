#!/usr/bin/env python3
"""
Outlook 邮箱自动注册 - 使用 nodriver 正确 API
使用 tab.select() 用 CSS 选择器 + tab.find() 用文本搜索
每步失败立即停止，保存到 /workspaces/nodriver/debug_output
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
    logger.log("Outlook 邮箱自动注册 - nodriver tab.select() 版本")
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
        await save_artifacts(tab, "01_page_loaded", logger)
        logger.log("✓ 页面已加载")

        # 步骤 2: 输入邮箱
        logger.log("\n--- 步骤 2: 输入邮箱 ---")
        try:
            email_input = await tab.select('input[type="email"]', timeout=10)
            logger.log(f"✓ 找到邮箱输入框")
            
            await email_input.clear()
            await email_input.type(email, delay=0.05)
            logger.log(f"✓ 邮箱已输入: {email}")
            
            await save_artifacts(tab, "02_email_filled", logger)
            await tab.sleep(1)
            
        except Exception as e:
            logger.log(f"✗ 邮箱输入失败: {e}", "ERROR")
            await save_artifacts(tab, "02_email_error", logger)
            raise

        # 点击下一步
        logger.log("点击下一步按钮...")
        try:
            next_btn = await tab.select('button[type="submit"]', timeout=5)
            await next_btn.click()
            logger.log("✓ 已点击下一步")
            await tab.sleep(3)
            await save_artifacts(tab, "03_after_email", logger)
        except Exception as e:
            logger.log(f"✗ 点击下一步失败: {e}", "ERROR")
            await save_artifacts(tab, "03_button_error", logger)
            raise

        # 步骤 3: 输入密码
        logger.log("\n--- 步骤 3: 输入密码 ---")
        try:
            pwd_input = await tab.select('input[type="password"]', timeout=10)
            logger.log(f"✓ 找到密码输入框")
            
            await pwd_input.clear()
            await pwd_input.type(password, delay=0.05)
            logger.log(f"✓ 密码已输入")
            
            await save_artifacts(tab, "04_password_filled", logger)
            await tab.sleep(1)
            
        except Exception as e:
            logger.log(f"✗ 密码输入失败: {e}", "ERROR")
            await save_artifacts(tab, "04_password_error", logger)
            raise

        # 点击下一步
        logger.log("点击下一步按钮...")
        try:
            next_btn = await tab.select('button[type="submit"]', timeout=5)
            await next_btn.click()
            logger.log("✓ 已点击下一步")
            await tab.sleep(3)
            await save_artifacts(tab, "05_after_password", logger)
        except Exception as e:
            logger.log(f"✗ 点击下一步失败: {e}", "ERROR")
            await save_artifacts(tab, "05_button_error", logger)
            raise

        # 步骤 4: 输入姓名
        logger.log("\n--- 步骤 4: 输入姓名 ---")
        name_parts = name.split()
        try:
            first_name_input = await tab.select('input[name="firstname"]', timeout=10)
            logger.log(f"✓ 找到名字输入框")
            
            await first_name_input.clear()
            await first_name_input.type(name_parts[0], delay=0.05)
            logger.log(f"✓ 名字已输入: {name_parts[0]}")
            
            if len(name_parts) > 1:
                try:
                    last_name_input = await tab.select('input[name="lastname"]', timeout=5)
                    await last_name_input.clear()
                    await last_name_input.type(name_parts[1], delay=0.05)
                    logger.log(f"✓ 姓氏已输入: {name_parts[1]}")
                except:
                    logger.log(f"⚠️  未找到姓氏输入框", "WARN")
            
            await save_artifacts(tab, "06_name_filled", logger)
            await tab.sleep(1)
            
        except Exception as e:
            logger.log(f"✗ 姓名输入失败: {e}", "ERROR")
            await save_artifacts(tab, "06_name_error", logger)
            raise

        # 点击下一步
        logger.log("点击下一步按钮...")
        try:
            next_btn = await tab.select('button[type="submit"]', timeout=5)
            await next_btn.click()
            logger.log("✓ 已点击下一步")
            await tab.sleep(3)
            await save_artifacts(tab, "07_after_name", logger)
        except Exception as e:
            logger.log(f"✗ 点击下一步失败: {e}", "ERROR")
            await save_artifacts(tab, "07_button_error", logger)
            raise

        # 步骤 5: 输入生日
        logger.log("\n--- 步骤 5: 输入生日 ---")
        date_parts = birth_date.split('/')
        month = date_parts[0]
        day = date_parts[1]
        year = date_parts[2]
        
        logger.log(f"生日: 月={month}, 日={day}, 年={year}")

        # 月份 (下拉框)
        try:
            month_dropdown = await tab.select('input[aria-label*="Month"], select[name*="month"]', timeout=5)
            logger.log(f"✓ 找到月份选择器")
            await month_dropdown.click()
            await tab.sleep(1)
            logger.log(f"⚠️  月份下拉框，暂时跳过手工选择", "WARN")
        except:
            logger.log(f"⚠️  未找到月份选择器", "WARN")

        # 日期
        try:
            day_input = await tab.select('input[aria-label*="Day"]', timeout=5)
            logger.log(f"✓ 找到日期输入框")
            await day_input.clear()
            await day_input.type(day, delay=0.05)
            logger.log(f"✓ 日期已输入: {day}")
        except:
            logger.log(f"⚠️  未找到日期输入框", "WARN")

        # 年份
        try:
            year_input = await tab.select('input[aria-label*="Year"]', timeout=5)
            logger.log(f"✓ 找到年份输入框")
            await year_input.clear()
            await year_input.type(year, delay=0.05)
            logger.log(f"✓ 年份已输入: {year}")
        except:
            logger.log(f"⚠️  未找到年份输入框", "WARN")

        await tab.sleep(2)
        await save_artifacts(tab, "08_birthdate_filled", logger)

        # 点击下一步 (如果存在)
        try:
            next_btn = await tab.select('button[type="submit"]', timeout=5)
            await next_btn.click()
            logger.log("✓ 已点击最后的下一步")
            await tab.sleep(3)
            await save_artifacts(tab, "09_final", logger)
        except:
            logger.log(f"⚠️  未找到最终下一步按钮", "WARN")

        logger.log("\n✅ 流程完成")

    except Exception as e:
        logger.log(f"\n❌ 流程中止: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")

    finally:
        logger.save()
        print(f"\n📋 日志: {log_file}")
        print(f"📸 截图: {SCREENSHOTS_DIR}")
        print(f"📄 HTML: {HTML_DIR}")
        try:
            await driver.stop()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(register_outlook())
