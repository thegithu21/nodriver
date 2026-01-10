#!/usr/bin/env python3
"""
Outlook 邮箱自动注册脚本 - 最终版本 v3
处理 SPA 和 iframe，使用更智能的等待机制
"""

import asyncio
import os
import csv
import json
from datetime import datetime
from pathlib import Path
import nodriver as uc


# 配置
DEBUG_DIR = "/workspaces/nodriver/debug_output"
ACCOUNTS_DIR = os.path.join(DEBUG_DIR, "accounts")
CSV_DIR = os.path.join(DEBUG_DIR, "csv_accounts")
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots_final")
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
        print(f"   📸 {filename}")
        return filepath
    except Exception as e:
        print(f"   ⚠️  截图失败: {e}")
        return None


async def wait_and_fill_input(tab, selector, value, timeout=10, desc="输入框"):
    """等待输入框出现并填充"""
    start_time = asyncio.get_event_loop().time()
    
    while True:
        try:
            elem = await tab.select(selector, timeout=1)
            if elem:
                # 清空后填充
                await elem.triple_click()
                await tab.sleep(0.2)
                await elem.send_keys(value)
                await tab.sleep(0.5)
                print(f"   ✓ 已填充 {desc}: {value[:20]}")
                return True
        except:
            pass
        
        if asyncio.get_event_loop().time() - start_time > timeout:
            print(f"   ⚠️  超时: 未找到 {desc}")
            return False
        
        await tab.sleep(0.5)


async def click_button(tab, timeout=5, desc="按钮"):
    """查找并点击提交按钮"""
    start_time = asyncio.get_event_loop().time()
    
    while True:
        try:
            # 方法 1: 提交按钮
            btn = await tab.select("button[type='submit']", timeout=1)
            if btn:
                print(f"   ✓ 点击 {desc}")
                await btn.click()
                return True
        except:
            pass
        
        try:
            # 方法 2: data-action="submit"
            btn = await tab.select("button[data-action='submit']", timeout=1)
            if btn:
                print(f"   ✓ 点击 {desc}")
                await btn.click()
                return True
        except:
            pass
        
        try:
            # 方法 3: 文字包含 Next/Continue
            buttons = await tab.select_all("button", timeout=1)
            for btn in buttons:
                try:
                    text = await btn.get_text()
                    if any(x in text for x in ['Next', 'Continue', 'Sign up', 'Create']):
                        print(f"   ✓ 点击 {desc}: {text.strip()}")
                        await btn.click()
                        return True
                except:
                    pass
        except:
            pass
        
        if asyncio.get_event_loop().time() - start_time > timeout:
            print(f"   ⚠️  未找到 {desc}")
            return False
        
        await tab.sleep(0.5)


async def register_outlook(email, password, name, birth_date):
    """自动注册 Outlook 账户"""
    
    print(f"\n{'='*70}")
    print(f"  🚀 Outlook 邮箱自动注册 - 最终版本 v3")
    print(f"{'='*70}")
    print(f"\n📋 账户信息:")
    print(f"   📧 {email}")
    print(f"   🔐 密码已设置")
    print(f"   👤 {name}")
    print(f"   📅 {birth_date}\n")
    
    # 启动浏览器
    print(f"🚀 启动浏览器...")
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_args=[
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-blink-features=AutomationControlled',
            '--no-first-run',
            '--disable-extensions',
        ]
    )
    
    try:
        # ========== 步骤 1: 访问注册页面 ==========
        print(f"[1/6] 🌐 访问 Outlook 注册页面...")
        tab = await driver.get("https://signup.live.com/?lic=1")
        
        # 等待页面加载 JavaScript
        for i in range(20):
            try:
                # 检查邮箱输入框是否存在
                email_input = await tab.select("input[type='email']", timeout=1)
                if email_input:
                    print(f"   ✓ 页面已加载")
                    await take_screenshot(tab, "1_page_loaded", 1)
                    break
            except:
                pass
            
            await tab.sleep(0.5)
        else:
            print(f"   ⚠️  页面加载超时，继续尝试...")
        
        # ========== 步骤 2: 输入邮箱 ==========
        print(f"\n[2/6] 📧 输入邮箱...")
        if not await wait_and_fill_input(tab, "input[type='email']", email, desc="邮箱"):
            # 保存调试信息
            try:
                html = await tab.get_content()
                with open(os.path.join(DEBUG_DIR, "debug_page.html"), 'w') as f:
                    f.write(html)
                print(f"   💾 HTML 已保存用于调试")
            except:
                pass
            return False
        
        await take_screenshot(tab, "2_email_entered", 2)
        
        # 点击下一步
        if not await click_button(tab, desc="下一步"):
            return False
        
        await tab.sleep(3)
        await take_screenshot(tab, "3_after_email", 3)
        
        # ========== 步骤 3: 输入密码 ==========
        print(f"\n[3/6] 🔐 输入密码...")
        
        if not await wait_and_fill_input(tab, "input[type='password']", password, timeout=15, desc="密码"):
            print(f"   ❌ 无法找到密码输入框，页面可能有问题")
            await take_screenshot(tab, "error_no_password_field", 99)
            return False
        
        await take_screenshot(tab, "4_password_entered", 4)
        
        # 点击下一步
        if not await click_button(tab, desc="下一步"):
            return False
        
        await tab.sleep(3)
        await take_screenshot(tab, "5_after_password", 5)
        
        # ========== 步骤 4: 输入名字 ==========
        print(f"\n[4/6] 👤 输入名字...")
        
        # 尝试多种名字输入框选择器
        name_found = False
        for selector in [
            "input[name='firstname']",
            "input[name='first_name']",
            "input[placeholder*='Name']",
            "input[placeholder*='name']",
            "input[name='name']"
        ]:
            try:
                elem = await tab.select(selector, timeout=2)
                if elem:
                    await elem.send_keys(name)
                    await tab.sleep(0.5)
                    print(f"   ✓ 已填充名字: {name}")
                    name_found = True
                    break
            except:
                pass
        
        if not name_found:
            # 扫描所有文本输入框
            try:
                all_inputs = await tab.select_all("input[type='text']", timeout=3)
                if all_inputs:
                    await all_inputs[0].send_keys(name)
                    print(f"   ✓ 已填充名字: {name}")
                    name_found = True
            except:
                pass
        
        if not name_found:
            print(f"   ⚠️  未找到名字输入框，跳过此步骤")
        
        await take_screenshot(tab, "6_name_entered", 6)
        
        # 点击下一步
        if not await click_button(tab, timeout=5, desc="下一步"):
            print(f"   ⚠️  未找到下一步按钮")
        
        await tab.sleep(3)
        await take_screenshot(tab, "7_after_name", 7)
        
        # ========== 步骤 5: 输入生日 ==========
        print(f"\n[5/6] 📅 输入生日...")
        
        # 解析生日
        parts = birth_date.split('/')
        if len(parts) == 3:
            month, day, year = parts
            
            # 尝试找月份下拉框
            for selector in ["select[name*='month']", "select[name*='Month']", "select"]:
                try:
                    elem = await tab.select(selector, timeout=2)
                    if elem:
                        await elem.send_keys(month)
                        print(f"   ✓ 已选择月份")
                        break
                except:
                    pass
            
            await tab.sleep(1)
            
            # 尝试找日期下拉框
            selects = await tab.select_all("select", timeout=2)
            if len(selects) > 1:
                try:
                    await selects[1].send_keys(day)
                    print(f"   ✓ 已选择日期")
                except:
                    pass
            
            await tab.sleep(1)
            
            # 尝试找年份下拉框
            if len(selects) > 2:
                try:
                    await selects[2].send_keys(year)
                    print(f"   ✓ 已选择年份")
                except:
                    pass
        
        await take_screenshot(tab, "8_birth_entered", 8)
        
        # 点击下一步
        if not await click_button(tab, timeout=5, desc="下一步"):
            print(f"   ⚠️  未找到下一步按钮")
        
        await tab.sleep(3)
        await take_screenshot(tab, "9_after_birth", 9)
        
        # ========== 步骤 6: 等待完成 ==========
        print(f"\n[6/6] ⏳ 等待账户创建完成...")
        
        for i in range(40):
            print(f"   等待中 ({i+1}/40 秒)...", end='\r')
            await tab.sleep(1)
            
            if i % 10 == 0:
                await take_screenshot(tab, f"waiting_{i:02d}", 10)
        
        print(f"\n   ✓ 完成")
        
        final_url = tab.url
        print(f"\n   🔗 最终 URL: {final_url[:60]}...")
        
        await take_screenshot(tab, "final", 11)
        
        # ========== 保存结果 ==========
        print(f"\n{'='*70}")
        print(f"✅ 注册流程完成!")
        print(f"{'='*70}\n")
        
        # 列出所有截图
        screenshots = sorted(os.listdir(SCREENSHOTS_DIR))
        print(f"📸 已保存 {len(screenshots)} 张截图:")
        for idx, sc in enumerate(screenshots, 1):
            print(f"   {idx:2d}. {sc}")
        
        # 保存账户信息
        account_info = {
            "email": email,
            "password": password,
            "name": name,
            "birth_date": birth_date,
            "created_at": datetime.now().isoformat(),
            "final_url": final_url,
            "screenshots_count": len(screenshots),
            "screenshots_dir": SCREENSHOTS_DIR
        }
        
        account_file = os.path.join(ACCOUNTS_DIR, f"account_registered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(account_file, 'w') as f:
            json.dump(account_info, f, indent=2)
        
        print(f"\n💾 账户信息: {account_file}")
        print(f"📁 截图目录: {SCREENSHOTS_DIR}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print(f"\n🔌 关闭浏览器...")
        try:
            driver.stop()
        except:
            pass


def read_csv_account(csv_file):
    """从 CSV 读取账户"""
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
    except Exception as e:
        print(f"❌ 读取 CSV 失败: {e}")
    
    return None


def main():
    """主函数"""
    print(f"\n{'='*70}")
    print(f"  📧 Outlook 邮箱自动注册系统")
    print(f"{'='*70}\n")
    
    # 读取账户信息
    print(f"📖 读取账户信息...")
    account = read_csv_account(CSV_FILE)
    
    if not account:
        print(f"❌ 无法读取账户")
        return 1
    
    print(f"✓ 账户信息已读取: {account['email']}\n")
    
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
        print("\n\n⚠️  已中止")
        return 1
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
