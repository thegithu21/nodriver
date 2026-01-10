#!/usr/bin/env python3
"""
Outlook 邮箱自动注册脚本（简化版）
使用 nodriver 库自动化 Outlook 邮箱注册流程

使用方法:
    python register_outlook_simple.py

该脚本会:
1. 自动启动浏览器
2. 生成随机邮箱地址、密码和用户信息
3. 访问 Outlook 注册页面
4. 自动填写注册表单
5. 保存注册信息和截图
"""

import asyncio
import os
import json
import random
import string
from datetime import datetime
import nodriver as uc


# 配置
DEBUG_DIR = "/tmp/outlook_registration"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots")
ACCOUNTS_DIR = os.path.join(DEBUG_DIR, "accounts")

# 创建目录
for dir_path in [DEBUG_DIR, SCREENSHOTS_DIR, ACCOUNTS_DIR]:
    os.makedirs(dir_path, exist_ok=True)


def generate_random_email_base(length=12):
    """生成随机邮箱前缀"""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_random_password(length=16):
    """生成随机密码"""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(random.choices(chars, k=length))


def generate_random_name():
    """生成随机名字"""
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Robert", "Lisa",
                   "James", "Mary", "William", "Patricia", "Richard", "Jennifer"]
    last_names = ["Smith", "Johnson", "Brown", "Taylor", "Williams", "Jones", "Garcia",
                  "Lee", "Miller", "Davis", "Wilson", "Moore", "Taylor", "Anderson"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


async def register_outlook():
    """自动注册 Outlook 账户"""
    
    # 生成账户信息
    email_base = generate_random_email_base()
    email = f"{email_base}@outlook.com"
    password = generate_random_password()
    name = generate_random_name()
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    birth_year = random.randint(1980, 2005)
    birth_date = f"{birth_month:02d}/{birth_day:02d}/{birth_year}"
    
    print(f"\n{'='*60}")
    print(f"Outlook 邮箱自动注册")
    print(f"{'='*60}")
    print(f"\n📝 生成的账户信息:")
    print(f"   邮箱: {email}")
    print(f"   密码: {password}")
    print(f"   名字: {name}")
    print(f"   生日: {birth_date}\n")
    
    # 启动浏览器
    print(f"📱 启动浏览器...")
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )
    
    try:
        # 访问注册页面
        print(f"🌐 访问 Outlook 注册页面...")
        signup_url = "https://go.microsoft.com/fwlink/p/?linkid=2125440&clcid=0x409"
        tab = await driver.get(signup_url)
        await tab.sleep(8)
        
        print(f"   当前 URL: {tab.url[:80]}...")
        
        # 第一步: 输入邮箱
        print(f"\n📧 第一步: 输入邮箱地址...")
        email_input = await tab.select("input[type='email']")
        await email_input.send_keys(email)
        await tab.sleep(1)
        
        # 点击下一步
        next_btn = await tab.select("button[type='submit']")
        await next_btn.click()
        await tab.sleep(4)
        print(f"   ✓ 邮箱输入完成")
        
        # 第二步: 输入密码
        print(f"\n🔐 第二步: 输入密码...")
        pwd_input = await tab.select("input[type='password']")
        await pwd_input.send_keys(password)
        await tab.sleep(1)
        
        # 点击下一步
        next_btn = await tab.select("button[type='submit']")
        await next_btn.click()
        await tab.sleep(4)
        print(f"   ✓ 密码输入完成")
        
        # 第三步: 输入名字
        print(f"\n👤 第三步: 输入名字...")
        name_input = await tab.find("Name", best_match=True)
        await name_input.send_keys(name)
        await tab.sleep(1)
        
        # 点击下一步
        next_btn = await tab.select("button[type='submit']")
        await next_btn.click()
        await tab.sleep(4)
        print(f"   ✓ 名字输入完成")
        
        # 第四步: 输入生日（可能会跳过）
        print(f"\n📅 第四步: 输入生日...")
        try:
            dob_input = await tab.select("input[type='date']", timeout=5)
            if dob_input:
                await dob_input.send_keys(birth_date)
                await tab.sleep(1)
                
                # 点击下一步
                next_btn = await tab.select("button[type='submit']")
                await next_btn.click()
                await tab.sleep(4)
                print(f"   ✓ 生日输入完成")
        except:
            print(f"   ⚠️  生日字段未找到（可跳过）")
        
        # 等待验证
        print(f"\n⏳ 等待页面验证... (10秒)")
        await tab.sleep(10)
        
        # 保存账户信息
        account_info = {
            "email": email,
            "password": password,
            "name": name,
            "birth_date": birth_date,
            "created_at": datetime.now().isoformat(),
            "status": "registered"
        }
        
        account_file = os.path.join(ACCOUNTS_DIR, f"outlook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(account_file, 'w', encoding='utf-8') as f:
            json.dump(account_info, f, indent=2, ensure_ascii=False)
        
        # 保存截图
        screenshot = os.path.join(SCREENSHOTS_DIR, f"final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        await tab.save_screenshot(screenshot)
        
        print(f"\n✅ 注册完成!")
        print(f"   账户信息已保存: {account_file}")
        print(f"   截图已保存: {screenshot}")
        print(f"\n📋 账户信息摘要:")
        print(f"   邮箱: {email}")
        print(f"   密码: {password}")
        print(f"   名字: {name}")
        print(f"   生日: {birth_date}")
        print(f"\n注意: 请妥善保管账户信息。可能需要进一步验证（邮箱、电话等）。")
        
        return account_info
        
    except Exception as e:
        print(f"\n❌ 出错: {e}")
        return None
    
    finally:
        print(f"\n🔌 关闭浏览器...")
        try:
            driver.stop()
        except:
            pass


def main():
    """主函数"""
    try:
        result = asyncio.run(register_outlook())
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了注册过程")
        return 1
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
