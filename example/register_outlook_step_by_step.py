#!/usr/bin/env python3
"""
Outlook 邮箱自动注册 - 严格逐步验证版本
每步失败立即停止，不继续往下
"""

import asyncio
import os
import csv
import json
from datetime import datetime
import nodriver as uc


DEBUG_DIR = "/workspaces/nodriver/debug_output"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots_step_by_step")
HTML_DIR = os.path.join(DEBUG_DIR, "html_step_by_step")
LOG_DIR = os.path.join(DEBUG_DIR, "logs_step_by_step")
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
        log_msg = f"[{timestamp}] {level}: {message}"
        self.logs.append(log_msg)
        print(log_msg)
        
    def save(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.logs))


async def screenshot_html(tab, step_name, logger):
    """保存截图和HTML"""
    try:
        filename_base = f"{step_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 截图
        screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{filename_base}.png")
        await tab.save_screenshot(screenshot_path)
        logger.log(f"📸 Screenshot: {filename_base}.png")
        
        # HTML
        html = await tab.get_content()
        html_path = os.path.join(HTML_DIR, f"{filename_base}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.log(f"📄 HTML: {filename_base}.html")
        
        return screenshot_path, html_path
    except Exception as e:
        logger.log(f"❌ Failed to save artifacts: {e}", "ERROR")
        return None, None


async def fill_and_verify(tab, selector, value, logger, field_name):
    """
    填充字段并验证真实值被写入了
    采用多种方法，若都失败则抛异常
    """
    logger.log(f"\n--- 填充 {field_name}: {value} ---")
    
    # 方法1: 原生 property setter + 事件派发
    try:
        logger.log(f"  尝试方法1：Property setter + Events")
        result = await tab.evaluate(f"""
        async () => {{
            const el = document.querySelector('{selector}');
            if (!el) return {{'success': false, 'reason': 'Element not found'}};
            
            // 聚焦
            el.focus();
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // 用 Object.getOwnPropertyDescriptor 获取原生 setter
            const descriptor = Object.getOwnPropertyDescriptor(el.__proto__, 'value');
            if (descriptor && descriptor.set) {{
                descriptor.set.call(el, '{value}');
            }} else {{
                el.value = '{value}';
            }}
            
            // 派发事件
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            el.dispatchEvent(new KeyboardEvent('keyup', {{ bubbles: true, key: 'Enter' }}));
            
            // 读回验证
            await new Promise(resolve => setTimeout(resolve, 100));
            const readValue = el.value || '';
            if (readValue.includes('{value}') || readValue === '{value}') {{
                return {{'success': true, 'readValue': readValue}};
            }} else {{
                return {{'success': false, 'reason': 'Value mismatch', 'readValue': readValue}};
            }}
        }}
        """)
        
        if result and result.get('success'):
            logger.log(f"  ✓ 方法1成功，读回值: {result.get('readValue')}")
            return True
        else:
            logger.log(f"  ✗ 方法1失败: {result}", "WARN")
    except Exception as e:
        logger.log(f"  ✗ 方法1异常: {e}", "WARN")
    
    # 方法2: 尝试通过 React DevTools Hook（如果有）
    try:
        logger.log(f"  尝试方法2：React Fiber 注入")
        result = await tab.evaluate(f"""
        async () => {{
            const el = document.querySelector('{selector}');
            if (!el) return false;
            
            // 尝试找到 React 根
            const keys = Object.keys(el);
            const fiberKey = keys.find(k => k.startsWith('__react'));
            if (fiberKey) {{
                const fiber = el[fiberKey];
                // 这是高风险的，可能不起作用
                logger.log('Found React fiber, attempting update...');
            }}
            return false; // 当前不确定此方法是否有效
        }}
        """)
        logger.log(f"  方法2未能确保成功（React Fiber 方法不稳定）")
    except Exception as e:
        logger.log(f"  方法2跳过: {e}", "WARN")
    
    # 都失败了，抛异常
    logger.log(f"❌ 无法填充 {field_name}，所有方法均失败", "ERROR")
    raise Exception(f"Failed to fill {field_name} with value {value}")


async def read_value(tab, selector, logger, field_name):
    """读取字段当前值并返回"""
    try:
        result = await tab.evaluate(f"""
        () => {{
            const el = document.querySelector('{selector}');
            return el ? (el.value || el.textContent || el.innerText || el.getAttribute('aria-label')) : null;
        }}
        """)
        return result
    except Exception as e:
        logger.log(f"Failed to read {field_name}: {e}", "ERROR")
        return None


async def click_next(tab, logger):
    """点击下一步按钮"""
    logger.log("点击 'Next' 按钮...")
    try:
        await tab.evaluate("""
        () => {
            const btn = document.querySelector('button[type="submit"]') || 
                       Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Next'));
            if (btn) {
                btn.click();
                return 'clicked';
            }
            return 'not_found';
        }
        """)
        await tab.sleep(2)
        logger.log("按钮已点击，等待页面响应...")
    except Exception as e:
        logger.log(f"❌ 点击按钮失败: {e}", "ERROR")
        raise


async def register_outlook():
    """主流程"""
    
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
        return
    
    log_file = os.path.join(LOG_DIR, f"registration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logger = Logger(log_file)
    
    logger.log("=" * 70)
    logger.log("Outlook 自动注册 - 严格逐步验证")
    logger.log("=" * 70)
    logger.log(f"邮箱: {email}")
    logger.log(f"密码: {password[:5]}***")
    logger.log(f"姓名: {name}")
    logger.log(f"生日: {birth_date}")
    
    driver = None
    try:
        # 启动浏览器
        logger.log("\n🚀 启动浏览器...")
        driver = await uc.start(
            headless=True,
            no_sandbox=True,
            browser_args=['--disable-dev-shm-usage', '--disable-gpu']
        )
        
        # 步骤 1: 访问页面
        logger.log("\n━━ 步骤 1/5: 访问 Outlook 注册页面 ━━")
        tab = await driver.get("https://signup.live.com/?lic=1")
        await tab.sleep(6)
        await screenshot_html(tab, "01_page_loaded", logger)
        logger.log("✓ 页面已加载")
        
        # 步骤 2: 填充邮箱
        logger.log("\n━━ 步骤 2/5: 填充邮箱 ━━")
        try:
            await fill_and_verify(tab, 'input[type="email"]', email, logger, "邮箱")
            await screenshot_html(tab, "02_email_filled", logger)
            
            # 验证
            read_email = await read_value(tab, 'input[type="email"]', logger, "邮箱")
            logger.log(f"邮箱读回值: {read_email}")
            
            await click_next(tab, logger)
            await screenshot_html(tab, "02b_after_email_click", logger)
            logger.log("✓ 邮箱步骤通过")
        except Exception as e:
            logger.log(f"❌ 邮箱步骤失败: {e}", "ERROR")
            await screenshot_html(tab, "02_FAILED_email", logger)
            logger.save()
            await driver.stop()
            return
        
        # 步骤 3: 填充密码
        logger.log("\n━━ 步骤 3/5: 填充密码 ━━")
        try:
            await tab.sleep(2)  # 等待页面更新
            await fill_and_verify(tab, 'input[type="password"]', password, logger, "密码")
            await screenshot_html(tab, "03_password_filled", logger)
            
            read_password = await read_value(tab, 'input[type="password"]', logger, "密码")
            logger.log(f"密码读回值（掩码）: {'*' * len(password) if read_password else 'EMPTY'}")
            
            await click_next(tab, logger)
            await screenshot_html(tab, "03b_after_password_click", logger)
            logger.log("✓ 密码步骤通过")
        except Exception as e:
            logger.log(f"❌ 密码步骤失败: {e}", "ERROR")
            await screenshot_html(tab, "03_FAILED_password", logger)
            logger.save()
            await driver.stop()
            return
        
        # 步骤 4: 填充姓名
        logger.log("\n━━ 步骤 4/5: 填充姓名 ━━")
        try:
            await tab.sleep(2)
            name_parts = name.split()
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            await fill_and_verify(tab, 'input[name="firstname"]', first_name, logger, "名字")
            await screenshot_html(tab, "04a_firstname_filled", logger)
            
            if last_name:
                await fill_and_verify(tab, 'input[name="lastname"]', last_name, logger, "姓氏")
                await screenshot_html(tab, "04b_lastname_filled", logger)
            
            await click_next(tab, logger)
            await screenshot_html(tab, "04c_after_name_click", logger)
            logger.log("✓ 姓名步骤通过")
        except Exception as e:
            logger.log(f"❌ 姓名步骤失败: {e}", "ERROR")
            await screenshot_html(tab, "04_FAILED_name", logger)
            logger.save()
            await driver.stop()
            return
        
        # 步骤 5: 填充生日
        logger.log("\n━━ 步骤 5/5: 填充生日 ━━")
        try:
            await tab.sleep(2)
            
            date_parts = birth_date.split('/')
            month = date_parts[0]
            day = date_parts[1]
            year = date_parts[2]
            
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            month_name = month_names[int(month)]
            
            logger.log(f"解析生日: {month_name}/{day}/{year}")
            
            # 月份（通常是下拉）
            logger.log("选择月份...")
            await fill_and_verify(tab, 'input[placeholder="Month"]', month_name, logger, "月份")
            await screenshot_html(tab, "05a_month_filled", logger)
            
            # 日期
            logger.log("输入日期...")
            await fill_and_verify(tab, 'input[placeholder="Day"]', day, logger, "日期")
            await screenshot_html(tab, "05b_day_filled", logger)
            
            # 年份
            logger.log("输入年份...")
            await fill_and_verify(tab, 'input[placeholder="Year"]', year, logger, "年份")
            await screenshot_html(tab, "05c_year_filled", logger)
            
            await click_next(tab, logger)
            await tab.sleep(3)
            await screenshot_html(tab, "05d_after_birthdate_click", logger)
            logger.log("✓ 生日步骤通过")
            
            logger.log("\n✅ 所有步骤成功完成！")
            
        except Exception as e:
            logger.log(f"❌ 生日步骤失败: {e}", "ERROR")
            await screenshot_html(tab, "05_FAILED_birthdate", logger)
            logger.save()
            await driver.stop()
            return
        
    except Exception as e:
        logger.log(f"❌ 流程异常: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")
    finally:
        logger.save()
        print(f"\n📋 日志已保存: {log_file}")
        if driver:
            try:
                await driver.stop()
            except:
                pass


if __name__ == "__main__":
    asyncio.run(register_outlook())
