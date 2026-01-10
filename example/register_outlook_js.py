#!/usr/bin/env python3
"""
Outlook 邮箱自动注册 - 使用 JavaScript 注入的版本
"""

import asyncio
import os
import csv
import json
from datetime import datetime
import nodriver as uc


# 配置
DEBUG_DIR = "/workspaces/nodriver/debug_output"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots_js")
CSV_FILE = os.path.join(DEBUG_DIR, "csv_accounts/accounts.csv")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


async def take_screenshot(tab, name):
    """保存截图"""
    try:
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        await tab.save_screenshot(filepath)
        print(f"   📸 {filename}")
        return filepath
    except:
        pass


async def register_outlook(email, password, name, birth_date):
    """注册 Outlook"""
    
    print(f"\n{'='*70}")
    print(f"  Outlook 邮箱自动注册 - JavaScript 注入版本")
    print(f"{'='*70}\n")
    
    # 启动浏览器
    print(f"🚀 启动浏览器...")
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )
    
    try:
        # 访问页面
        print(f"\n[1/5] 访问 Outlook 注册页面...")
        tab = await driver.get("https://signup.live.com/?lic=1")
        await tab.sleep(6)
        await take_screenshot(tab, "01_loaded")
        print(f"   ✓ 页面已加载")
        
        # 输入邮箱
        print(f"\n[2/5] 输入邮箱: {email}")
        js_code = f"""
        () => {{
            const emailInput = document.querySelector('input[type="email"]');
            if (emailInput) {{
                emailInput.value = '{email}';
                emailInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                emailInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return 'success';
            }}
            return 'failed';
        }}
        """
        result = await tab.evaluate(js_code)
        print(f"   ✓ 邮箱已输入")
        await take_screenshot(tab, "02_email")
        
        # 点击下一步
        js_click = """
        () => {
            const btn = document.querySelector('button[type="submit"]');
            if (btn) {
                btn.click();
                return 'clicked';
            }
            return 'not found';
        }
        """
        await tab.evaluate(js_click)
        await tab.sleep(3)
        await take_screenshot(tab, "03_after_email")
        print(f"   ✓ 已点击下一步")
        
        # 输入密码
        print(f"\n[3/5] 输入密码...")
        js_pwd = f"""
        () => {{
            const pwdInput = document.querySelector('input[type="password"]');
            if (pwdInput) {{
                pwdInput.value = '{password}';
                pwdInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'success';
            }}
            return 'not found';
        }}
        """
        result = await tab.evaluate(js_pwd)
        print(f"   结果: {result}")
        
        if result == 'not found':
            print(f"   ⚠️  未找到密码框，尝试查找所有输入框...")
            js_find_all = """
            () => {
                const inputs = Array.from(document.querySelectorAll('input'));
                return inputs.map((i, idx) => {
                    return {
                        idx,
                        type: i.type,
                        name: i.name,
                        id: i.id,
                        placeholder: i.placeholder
                    };
                });
            }
            """
            inputs = await tab.evaluate(js_find_all)
            for inp in inputs:
                print(f"      输入框 {inp['idx']}: type={inp['type']}, name={inp['name']}, id={inp['id']}")
        else:
            print(f"   ✓ 密码已输入")
            await take_screenshot(tab, "04_password")
            
            # 点击下一步
            await tab.evaluate(js_click)
            await tab.sleep(3)
            await take_screenshot(tab, "05_after_password")
            print(f"   ✓ 已点击下一步")
        
        # 输入名字
        print(f"\n[4/5] 输入名字: {name}")
        js_name = f"""
        () => {{
            // 尝试多种选择器
            let nameInput = document.querySelector('input[name="firstname"]') ||
                           document.querySelector('input[name="first_name"]') ||
                           document.querySelector('input[placeholder*="Name"]') ||
                           document.querySelectorAll('input[type="text"]')[0];
            
            if (nameInput) {{
                nameInput.value = '{name}';
                nameInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                return 'success';
            }}
            return 'not found';
        }}
        """
        result = await tab.evaluate(js_name)
        print(f"   结果: {result}")
        if result == 'success':
            await take_screenshot(tab, "06_name")
            await tab.evaluate(js_click)
            await tab.sleep(3)
            await take_screenshot(tab, "07_after_name")
            print(f"   ✓ 已点击下一步")
        
        # 等待完成
        print(f"\n[5/5] 等待完成...")
        for i in range(30):
            print(f"   等待中 {i+1}/30...", end='\r')
            await tab.sleep(1)
            if i % 10 == 0:
                await take_screenshot(tab, f"waiting_{i:02d}")
        
        print(f"\n   ✓ 完成")
        await take_screenshot(tab, "final")
        
        # 列出所有截图
        screenshots = sorted(os.listdir(SCREENSHOTS_DIR))
        print(f"\n✅ 注册流程完成!")
        print(f"\n📸 生成的截图 ({len(screenshots)} 张):")
        for idx, sc in enumerate(screenshots, 1):
            print(f"   {idx}. {sc}")
        
        print(f"\n📁 截图目录: {SCREENSHOTS_DIR}")
        
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
    """读取 CSV"""
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
        print(f"❌ 错误: {e}")
    
    return None


def main():
    """主函数"""
    print(f"\n{'='*70}")
    print(f"  📧 Outlook 邮箱自动注册")
    print(f"{'='*70}\n")
    
    # 读取账户
    print(f"📖 读取账户...")
    account = read_csv_account(CSV_FILE)
    
    if not account:
        print(f"❌ 无法读取")
        return 1
    
    print(f"✓ 账户: {account['email']}\n")
    
    # 注册
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
        return 1


if __name__ == "__main__":
    exit(main())
