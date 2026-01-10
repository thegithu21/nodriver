#!/usr/bin/env python3
"""
Outlook 邮箱自动注册 - 使用 nodriver 原生方法
"""

import asyncio
import os
import csv
import json
from datetime import datetime
import nodriver as uc


# 配置
DEBUG_DIR = "/workspaces/nodriver/debug_output"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots_working")
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
    except Exception as e:
        print(f"   ❌ 截图失败: {e}")
        pass


async def register_outlook(email, password, name, birth_date):
    """注册 Outlook"""
    
    print(f"\n{'='*70}")
    print(f"  Outlook 邮箱自动注册 - 修复版本")
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
        
        # 多次重试等待页面完全加载
        page_ready = False
        for attempt in range(10):
            await tab.sleep(2)
            # 检查email输入框是否存在且可见
            try:
                email_input = await tab.find('input[type="email"]', single=True)
                if email_input:
                    page_ready = True
                    print(f"   ✓ 找到email输入框（尝试{attempt+1}）")
                    break
            except:
                if attempt == 9:
                    print(f"   ⚠️  在{attempt+1}次尝试后未找到email输入框")
        
        await take_screenshot(tab, "01_page_loaded")
        
        # 输入邮箱地址
        if page_ready:
            print(f"\n[2/5] 输入邮箱: {email}")
            try:
                email_input = await tab.find('input[type="email"]', single=True)
                
                # 清空并输入
                await email_input.clear()
                await email_input.type(email, delay=0.05)
                print(f"   ✓ 邮箱已输入")
                await take_screenshot(tab, "02_email_entered")
                
                await tab.sleep(2)
                
                # 点击下一步按钮
                print(f"\n[3/5] 点击下一步...")
                next_button = await tab.find('button[type="submit"]', single=True)
                await next_button.click()
                print(f"   ✓ 点击完成，等待密码页面...")
                
                # 等待密码输入框出现
                for attempt in range(15):
                    await tab.sleep(1)
                    try:
                        pwd_input = await tab.find('input[type="password"]', single=True)
                        if pwd_input:
                            print(f"   ✓ 密码页面已加载（等待{attempt+1}秒）")
                            break
                    except:
                        pass
                
                await take_screenshot(tab, "03_password_page")
                
                # 输入密码
                print(f"\n[4/5] 输入密码...")
                try:
                    pwd_input = await tab.find('input[type="password"]', single=True)
                    await pwd_input.clear()
                    await pwd_input.type(password, delay=0.05)
                    print(f"   ✓ 密码已输入")
                    await take_screenshot(tab, "04_password_entered")
                    
                    await tab.sleep(1)
                    
                    # 点击下一步
                    next_button = await tab.find('button[type="submit"]', single=True)
                    await next_button.click()
                    print(f"   ✓ 点击完成，等待名字页面...")
                    
                    await tab.sleep(5)
                    await take_screenshot(tab, "05_after_password")
                    
                except Exception as e:
                    print(f"   ❌ 密码输入失败: {e}")
                    await take_screenshot(tab, "error_password.png")
            
            except Exception as e:
                print(f"   ❌ 邮箱输入失败: {e}")
                await take_screenshot(tab, "error_email.png")
        
        print(f"\n✅ 截图已保存到: {SCREENSHOTS_DIR}")
        print(f"   总共生成 {len(os.listdir(SCREENSHOTS_DIR))} 张截图")
        
    except Exception as e:
        print(f"\n❌ 注册失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await driver.kill()


async def main():
    """主函数"""
    try:
        # 读取CSV
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            accounts = list(reader)
        
        if not accounts:
            print("❌ CSV文件为空")
            return
        
        # 使用第一个账户
        account = accounts[0]
        email = account.get('Email')
        password = account.get('Password')
        name = account.get('Name')
        birth_date = account.get('BirthDate')
        
        print(f"\n📧 从CSV读取账户信息:")
        print(f"   邮箱: {email}")
        print(f"   密码: {'*' * len(password)}")
        print(f"   名字: {name}")
        print(f"   生日: {birth_date}")
        
        await register_outlook(email, password, name, birth_date)
        
    except FileNotFoundError:
        print(f"❌ 找不到CSV文件: {CSV_FILE}")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
