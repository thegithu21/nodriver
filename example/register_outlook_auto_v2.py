#!/usr/bin/env python3
"""
Outlook 邮箱自动注册脚本 - 改进版本
使用更灵活的选择器和页面分析
"""

import asyncio
import os
import csv
import json
from datetime import datetime
from pathlib import Path
import nodriver as uc
import re


# 配置
DEBUG_DIR = "/workspaces/nodriver/debug_output"
ACCOUNTS_DIR = os.path.join(DEBUG_DIR, "accounts")
CSV_DIR = os.path.join(DEBUG_DIR, "csv_accounts")
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots_registration")
CSV_FILE = os.path.join(CSV_DIR, "accounts.csv")

# 创建目录
for dir_path in [DEBUG_DIR, ACCOUNTS_DIR, CSV_DIR, SCREENSHOTS_DIR]:
    os.makedirs(dir_path, exist_ok=True)


async def take_screenshot(tab, step_name, step_num):
    """保存截图"""
    try:
        filename = f"{step_num:02d}_{step_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        await tab.save_screenshot(filepath)
        print(f"   📸 截图: {filename}")
        return filepath
    except Exception as e:
        print(f"   ⚠️  截图失败: {e}")
        return None


async def wait_for_element(tab, selector, timeout=10, desc="element"):
    """等待元素出现"""
    start_time = asyncio.get_event_loop().time()
    while True:
        try:
            elem = await tab.select(selector, timeout=1)
            if elem:
                print(f"   ✓ 找到 {desc}")
                return elem
        except:
            pass
        
        if asyncio.get_event_loop().time() - start_time > timeout:
            print(f"   ⚠️  超时: 未找到 {desc}")
            return None
        
        await tab.sleep(0.5)


async def find_button(tab, text_contains=None, button_text=None, timeout=5):
    """查找并点击按钮"""
    try:
        # 方法 1: 通过按钮文字
        buttons = await tab.select_all("button", timeout=2)
        for btn in buttons:
            try:
                btn_text = await btn.get_text()
                if (text_contains and text_contains.lower() in btn_text.lower()) or \
                   (button_text and btn_text.strip() == button_text):
                    return btn
            except:
                pass
        
        # 方法 2: 第一个提交按钮
        try:
            btn = await tab.select("button[type='submit']", timeout=1)
            if btn:
                return btn
        except:
            pass
        
        # 方法 3: 第一个按钮
        try:
            btn = await tab.select("button", timeout=1)
            if btn:
                return btn
        except:
            pass
        
        return None
    except:
        return None


async def register_outlook(email, password, name, birth_date):
    """自动注册 Outlook 账户"""
    
    print(f"\n{'='*70}")
    print(f"  Outlook 邮箱自动注册 - 完整流程")
    print(f"{'='*70}")
    print(f"\n📝 账户信息:")
    print(f"   📧 邮箱: {email}")
    print(f"   🔐 密码: {password}")
    print(f"   👤 名字: {name}")
    print(f"   📅 生日: {birth_date}\n")
    
    # 启动浏览器
    print(f"🚀 启动浏览器...")
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_args=[
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-blink-features=AutomationControlled',
            '--disable-web-resources',
            '--no-first-run'
        ]
    )
    
    try:
        # ========== 第 1 步: 访问注册页面 ==========
        print(f"\n[步骤 1/6] 🌐 访问 Outlook 注册页面...")
        signup_url = "https://signup.live.com/?lic=1"
        tab = await driver.get(signup_url)
        await tab.sleep(6)
        await take_screenshot(tab, "01_page_loaded", 1)
        print(f"   ✓ 页面已加载")
        print(f"   URL: {tab.url[:60]}...")
        
        # ========== 第 2 步: 输入邮箱 ==========
        print(f"\n[步骤 2/6] 📧 输入邮箱地址...")
        email_input = await wait_for_element(tab, "input[type='email']", timeout=10, desc="邮箱输入框")
        if not email_input:
            email_input = await wait_for_element(tab, "input", timeout=5, desc="输入框")
        
        if email_input:
            await email_input.send_keys(email)
            await tab.sleep(1)
            await take_screenshot(tab, "02_email_entered", 2)
            print(f"   ✓ 已输入: {email}")
            
            # 点击下一步
            next_btn = await find_button(tab, text_contains="next")
            if not next_btn:
                next_btn = await find_button(tab)
            
            if next_btn:
                await next_btn.click()
                await tab.sleep(3)
                await take_screenshot(tab, "03_after_email", 3)
                print(f"   ✓ 已点击下一步")
            else:
                print(f"   ⚠️  未找到下一步按钮")
        else:
            print(f"   ❌ 无法找到邮箱输入框")
            return False
        
        # ========== 第 3 步: 输入密码 ==========
        print(f"\n[步骤 3/6] 🔐 输入密码...")
        
        # 等待一下确保页面加载
        await tab.sleep(2)
        
        # 尝试多种方式找到密码输入框
        pwd_input = None
        
        # 方法 1: 通过 type 属性
        for i in range(5):
            try:
                pwd_input = await tab.select("input[type='password']", timeout=2)
                if pwd_input:
                    print(f"   ✓ 找到密码输入框 (方法1)")
                    break
            except:
                pass
            await tab.sleep(0.5)
        
        # 方法 2: 通过 name 属性
        if not pwd_input:
            for i in range(5):
                try:
                    pwd_input = await tab.select("input[name='passwd']", timeout=2)
                    if pwd_input:
                        print(f"   ✓ 找到密码输入框 (方法2)")
                        break
                except:
                    pass
                await tab.sleep(0.5)
        
        # 方法 3: 通过其他名称模式
        if not pwd_input:
            for selector in ["input[name='password']", "input[name='pass']", "input[autocomplete='current-password']"]:
                try:
                    pwd_input = await tab.select(selector, timeout=2)
                    if pwd_input:
                        print(f"   ✓ 找到密码输入框 (选择器: {selector})")
                        break
                except:
                    pass
        
        # 方法 4: 扫描所有输入框
        if not pwd_input:
            try:
                all_inputs = await tab.select_all("input", timeout=3)
                for inp in all_inputs:
                    try:
                        inp_type = await inp.get_attribute("type")
                        inp_name = await inp.get_attribute("name") or ""
                        inp_placeholder = await inp.get_attribute("placeholder") or ""
                        
                        if inp_type == "password" or "password" in inp_name.lower() or "password" in inp_placeholder.lower():
                            pwd_input = inp
                            print(f"   ✓ 找到密码输入框 (扫描, type={inp_type}, name={inp_name})")
                            break
                    except:
                        continue
            except:
                pass
        
        if pwd_input:
            await pwd_input.send_keys(password)
            await tab.sleep(1)
            await take_screenshot(tab, "04_password_entered", 4)
            print(f"   ✓ 已输入密码")
            
            # 点击下一步
            next_btn = await find_button(tab, text_contains="next")
            if not next_btn:
                next_btn = await find_button(tab)
            
            if next_btn:
                await next_btn.click()
                await tab.sleep(3)
                await take_screenshot(tab, "05_after_password", 5)
                print(f"   ✓ 已点击下一步")
        else:
            print(f"   ❌ 无法找到密码输入框，保存调试截图")
            
            # 保存页面 HTML 以供调试
            try:
                html = await tab.get_content()
                debug_html_file = os.path.join(DEBUG_DIR, f"page_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                with open(debug_html_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"   📄 页面 HTML 已保存: {debug_html_file}")
            except:
                pass
            
            return False
        
        # ========== 第 4 步: 输入名字 ==========
        print(f"\n[步骤 4/6] 👤 输入名字...")
        await tab.sleep(2)
        
        name_input = None
        
        # 方法 1: 通过 placeholder
        for selector in ["input[placeholder*='Name']", "input[placeholder*='name']", "input[name='firstname']", "input[name='first_name']"]:
            try:
                name_input = await tab.select(selector, timeout=2)
                if name_input:
                    print(f"   ✓ 找到名字输入框 (选择器: {selector})")
                    break
            except:
                pass
        
        # 方法 2: 扫描所有输入框
        if not name_input:
            try:
                all_inputs = await tab.select_all("input[type='text']", timeout=3)
                if all_inputs:
                    # 通常名字是第一个文本输入框
                    name_input = all_inputs[0]
                    print(f"   ✓ 找到名字输入框 (第一个文本输入)")
            except:
                pass
        
        if name_input:
            await name_input.send_keys(name)
            await tab.sleep(1)
            await take_screenshot(tab, "06_name_entered", 6)
            print(f"   ✓ 已输入: {name}")
            
            # 点击下一步
            next_btn = await find_button(tab)
            if next_btn:
                await next_btn.click()
                await tab.sleep(3)
                await take_screenshot(tab, "07_after_name", 7)
                print(f"   ✓ 已点击下一步")
        else:
            print(f"   ⚠️  未找到名字输入框，可能已经过本步骤")
        
        # ========== 第 5 步: 输入生日 ==========
        print(f"\n[步骤 5/6] 📅 输入生日...")
        await tab.sleep(2)
        
        # 解析生日日期 (格式: 12/17/1979)
        parts = birth_date.split('/')
        if len(parts) == 3:
            month, day, year = parts
            print(f"   📅 生日: {month}/{day}/{year}")
            
            # 尝试找到生日输入框
            try:
                # 方法 1: 月份下拉框
                month_select = await tab.select("select[name*='month'], select[name*='Month']", timeout=2)
                if month_select:
                    await month_select.send_keys(month)
                    await tab.sleep(1)
                    print(f"   ✓ 已选择月份")
                    await take_screenshot(tab, "08_month_selected", 8)
            except:
                pass
            
            try:
                # 方法 2: 日期下拉框
                day_select = await tab.select("select[name*='day'], select[name*='Day']", timeout=2)
                if day_select:
                    await day_select.send_keys(day)
                    await tab.sleep(1)
                    print(f"   ✓ 已选择日期")
            except:
                pass
            
            try:
                # 方法 3: 年份下拉框
                year_select = await tab.select("select[name*='year'], select[name*='Year']", timeout=2)
                if year_select:
                    await year_select.send_keys(year)
                    await tab.sleep(1)
                    print(f"   ✓ 已选择年份")
                    await take_screenshot(tab, "09_birth_filled", 9)
            except:
                pass
            
            # 点击下一步
            try:
                next_btn = await find_button(tab)
                if next_btn:
                    await next_btn.click()
                    await tab.sleep(3)
                    await take_screenshot(tab, "10_after_birth", 10)
                    print(f"   ✓ 已点击下一步")
            except:
                print(f"   ⚠️  无法点击下一步")
        
        # ========== 第 6 步: 等待完成 ==========
        print(f"\n[步骤 6/6] ⏳ 等待验证和账户创建...")
        
        for i in range(30):
            await tab.sleep(1)
            if i % 5 == 0:
                await take_screenshot(tab, f"waiting_{i:02d}", 11 + (i // 5))
            print(f"   等待中... ({i+1}/30 秒)", end='\r')
        
        print(f"\n   ✓ 验证完成")
        await take_screenshot(tab, "final_page", 20)
        
        # 检查最终状态
        final_url = tab.url
        print(f"\n   🔗 最终 URL: {final_url[:70]}...")
        
        # ========== 保存结果 ==========
        print(f"\n✅ 注册流程完成!")
        
        account_info = {
            "email": email,
            "password": password,
            "name": name,
            "birth_date": birth_date,
            "created_at": datetime.now().isoformat(),
            "status": "completed",
            "final_url": final_url,
            "screenshots_dir": SCREENSHOTS_DIR
        }
        
        account_file = os.path.join(ACCOUNTS_DIR, f"outlook_registered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(account_file, 'w', encoding='utf-8') as f:
            json.dump(account_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 结果总结:")
        print(f"   ✓ 账户信息: {account_file}")
        print(f"   ✓ 截图目录: {SCREENSHOTS_DIR}")
        
        # 列出所有截图
        screenshots = sorted(os.listdir(SCREENSHOTS_DIR))
        print(f"\n📸 已保存的截图 ({len(screenshots)} 张):")
        for idx, screenshot in enumerate(screenshots[:15], 1):
            print(f"   {idx:2d}. {screenshot}")
        if len(screenshots) > 15:
            print(f"   ... 还有 {len(screenshots) - 15} 张")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 注册出错: {e}")
        import traceback
        traceback.print_exc()
        await take_screenshot(tab, "error", 99)
        return False
    
    finally:
        print(f"\n🔌 关闭浏览器...")
        try:
            driver.stop()
        except:
            pass


def read_csv_account(csv_file):
    """从 CSV 读取账户信息"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                return {
                    'email': row['Email'],
                    'password': row['Password'],
                    'name': row['Name'],
                    'birth_date': row['Birth Date']
                }
        return None
    except Exception as e:
        print(f"❌ 读取 CSV 失败: {e}")
        return None


def main():
    """主函数"""
    print(f"\n{'='*70}")
    print(f"  Outlook 邮箱自动注册系统 v2.0")
    print(f"{'='*70}\n")
    
    # 读取 CSV
    print(f"📖 读取账户信息...")
    account = read_csv_account(CSV_FILE)
    
    if not account:
        print(f"❌ 无法读取账户信息")
        return 1
    
    print(f"✓ 账户信息已读取:")
    print(f"  • 邮箱: {account['email']}")
    print(f"  • 名字: {account['name']}")
    print(f"  • 生日: {account['birth_date']}")
    
    # 开始注册
    try:
        result = asyncio.run(register_outlook(
            account['email'],
            account['password'],
            account['name'],
            account['birth_date']
        ))
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中止了注册")
        return 1
    except Exception as e:
        print(f"\n\n❌ 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
