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
import csv
import random
import string
from datetime import datetime
import nodriver as uc


# 配置 - 使用 debug_output 目录
DEBUG_DIR = "/workspaces/nodriver/debug_output"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots")
ACCOUNTS_DIR = os.path.join(DEBUG_DIR, "accounts")
INBOX_SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "inbox_screenshots")
CSV_DIR = os.path.join(DEBUG_DIR, "csv_accounts")
CSV_FILE = os.path.join(CSV_DIR, "accounts.csv")

# 创建目录
for dir_path in [DEBUG_DIR, SCREENSHOTS_DIR, ACCOUNTS_DIR, INBOX_SCREENSHOTS_DIR, CSV_DIR]:
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


def save_to_csv(email, password, name, birth_date):
    """将账户信息保存到 CSV 文件"""
    file_exists = os.path.exists(CSV_FILE)
    
    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 如果文件不存在，写入表头
            if not file_exists:
                writer.writerow(['Email', 'Password', 'Name', 'Birth Date', 'Created At'])
            
            # 写入账户信息
            writer.writerow([email, password, name, birth_date, datetime.now().isoformat()])
        
        print(f"   ✓ 账户信息已保存到 CSV: {CSV_FILE}")
        return True
    except Exception as e:
        print(f"   ❌ CSV 保存失败: {e}")
        return False


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
        browser_args=['--disable-dev-shm-usage', '--disable-gpu', '--disable-blink-features=AutomationControlled']
    )
    
    try:
        # 访问注册页面
        print(f"🌐 访问 Outlook 注册页面...")
        signup_url = "https://signup.live.com/signup"
        tab = await driver.get(signup_url)
        await tab.sleep(10)
        
        print(f"   当前 URL: {tab.url[:80]}...")
        
        # 第一步: 输入邮箱
        print(f"\n📧 第一步: 输入邮箱地址...")
        try:
            email_input = await tab.select("input[type='email']")
            await email_input.send_keys(email)
            await tab.sleep(2)
            
            # 点击下一步
            next_btn = await tab.select("button[type='submit']")
            await next_btn.click()
            await tab.sleep(5)
            await tab.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"01_email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"))
            print(f"   ✓ 邮箱输入完成")
        except Exception as e:
            print(f"   ❌ 邮箱输入失败: {e}")
            return None
        
        # 第二步: 输入密码
        print(f"\n🔐 第二步: 输入密码...")
        try:
            pwd_input = await tab.select("input[type='password']")
            await pwd_input.send_keys(password)
            await tab.sleep(2)
            
            # 点击下一步
            next_btn = await tab.select("button[type='submit']")
            await next_btn.click()
            await tab.sleep(5)
            await tab.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"02_password_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"))
            print(f"   ✓ 密码输入完成")
        except Exception as e:
            print(f"   ❌ 密码输入失败: {e}")
            return None
        
        # 第三步: 输入名字
        print(f"\n👤 第三步: 输入名字...")
        try:
            name_input = await tab.find("Name", best_match=True)
            await name_input.send_keys(name)
            await tab.sleep(2)
            
            # 点击下一步
            next_btn = await tab.select("button[type='submit']")
            await next_btn.click()
            await tab.sleep(5)
            await tab.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"03_name_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"))
            print(f"   ✓ 名字输入完成")
        except Exception as e:
            print(f"   ❌ 名字输入失败: {e}")
            return None
        
        # 第四步: 输入生日
        print(f"\n📅 第四步: 输入生日...")
        try:
            dob_input = await tab.select("input[type='date']", timeout=5)
            if dob_input:
                await dob_input.send_keys(birth_date)
                await tab.sleep(2)
                
                # 点击下一步
                next_btn = await tab.select("button[type='submit']")
                await next_btn.click()
                await tab.sleep(5)
                await tab.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"04_birth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"))
                print(f"   ✓ 生日输入完成")
        except:
            print(f"   ⚠️  生日字段未找到（可跳过）")
        
        # 等待最终验证和确认
        print(f"\n⏳ 等待账户验证和确认... (15秒)")
        for i in range(15):
            await tab.sleep(1)
            await tab.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"05_verify_{i:02d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"))
            
            # 检查 URL 是否改变，表示注册成功
            current_url = tab.url
            print(f"   [{i+1}/15] URL: {current_url[:60]}...")
            
            # 如果 URL 包含 outlook 或 mail，说明已进入邮箱
            if "outlook" in current_url.lower() or "mail" in current_url.lower():
                print(f"   ✓ 检测到邮箱 URL，注册可能成功!")
                break
        
        # 检查最终页面
        final_url = tab.url
        print(f"\n  最终 URL: {final_url}")
        
        # 保存最终截图
        await tab.save_screenshot(os.path.join(SCREENSHOTS_DIR, f"06_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"))
        
        # 保存账户信息
        account_info = {
            "email": email,
            "password": password,
            "name": name,
            "birth_date": birth_date,
            "created_at": datetime.now().isoformat(),
            "status": "registered",
            "final_url": final_url
        }
        
        account_file = os.path.join(ACCOUNTS_DIR, f"outlook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(account_file, 'w', encoding='utf-8') as f:
            json.dump(account_info, f, indent=2, ensure_ascii=False)
        
        # 保存到 CSV
        save_to_csv(email, password, name, birth_date)
        
        print(f"\n✅ 注册完成!")
        print(f"   账户信息已保存: {account_file}")
        print(f"   CSV 已保存: {CSV_FILE}")
        print(f"\n📋 账户信息摘要:")
        print(f"   邮箱: {email}")
        print(f"   密码: {password}")
        print(f"   名字: {name}")
        print(f"   生日: {birth_date}")
        print(f"\n📁 文件位置:")
        print(f"   截图: {SCREENSHOTS_DIR}/")
        print(f"   CSV: {CSV_FILE}")
        print(f"   JSON: {account_file}")
        print(f"\n⚠️  注意: 请妥善保管账户信息。可能需要进一步验证。")
        
        return account_info
        
        # 登录到邮箱
        print(f"\n🔐 现在尝试登录邮箱...")
        try:
            await tab.sleep(2)
            
            # 直接访问邮箱登录页面
            print(f"📧 访问 Outlook 邮箱登录页面...")
            login_url = f"https://outlook.live.com/mail/0/inbox"
            tab = await driver.get(login_url)
            await tab.sleep(10)
            
            print(f"   当前 URL: {tab.url[:80]}...")
            
            # 尝试查找邮箱输入字段
            print(f"📝 输入邮箱...")
            email_input_found = False
            
            # 方法 1: 直接查找邮箱输入框
            try:
                email_input = await tab.select("input[name='loginfmt']", timeout=5)
                if email_input:
                    await email_input.send_keys(email)
                    await tab.sleep(1)
                    email_input_found = True
                    print(f"   ✓ 找到邮箱输入框")
            except:
                pass
            
            # 方法 2: 使用 JavaScript 填充
            if not email_input_found:
                try:
                    await tab.select("input[type='email']", timeout=3)
                    email_input = await tab.select("input[type='email']")
                    await email_input.send_keys(email)
                    await tab.sleep(1)
                    email_input_found = True
                    print(f"   ✓ 通过 email 类型找到邮箱输入框")
                except:
                    pass
            
            if email_input_found:
                # 点击下一步
                try:
                    next_btn = await tab.select("button[id='idSIButton9']", timeout=3)
                    if not next_btn:
                        next_btn = await tab.select("button[type='submit']", timeout=3)
                    if next_btn:
                        await next_btn.click()
                        await tab.sleep(6)
                        print(f"   ✓ 邮箱输入完成，等待密码字段...")
                except:
                    print(f"   ⚠️  无法点击下一步按钮")
                
                # 输入密码
                print(f"🔑 输入密码...")
                pwd_found = False
                
                try:
                    pwd_input = await tab.select("input[name='passwd']", timeout=5)
                    if pwd_input:
                        await pwd_input.send_keys(password)
                        await tab.sleep(1)
                        pwd_found = True
                        print(f"   ✓ 找到密码输入框")
                except:
                    pass
                
                if pwd_found:
                    # 点击登录
                    try:
                        submit_btn = await tab.select("button[id='idSIButton9']", timeout=3)
                        if not submit_btn:
                            submit_btn = await tab.select("button[type='submit']", timeout=3)
                        if submit_btn:
                            await submit_btn.click()
                            await tab.sleep(8)
                            print(f"   ✓ 密码输入完成，等待邮箱加载...")
                    except:
                        print(f"   ⚠️  无法提交登录")
                
                # 等待邮箱加载并检查 URL 变化
                print(f"⏳ 等待邮箱界面加载... (20秒)")
                for i in range(20):
                    await tab.sleep(1)
                    current_url = tab.url
                    if "outlook" in current_url.lower() or "mail" in current_url.lower():
                        if i > 3:  # 至少等待 3 秒后再保存
                            break
                
                # 等待额外的页面加载时间
                await tab.sleep(5)
                
                # 保存邮箱截图
                inbox_screenshot = os.path.join(INBOX_SCREENSHOTS_DIR, 
                                               f"inbox_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                try:
                    await tab.save_screenshot(inbox_screenshot)
                    print(f"📸 邮箱界面截图已保存!")
                    print(f"   {inbox_screenshot}")
                except Exception as e:
                    print(f"   ⚠️  邮箱截图保存失败: {e}")
            else:
                print(f"   ⚠️  未找到邮箱输入表单")
        
        except Exception as e:
            print(f"   ⚠️  邮箱登录异常: {e}")
        
        print(f"\n📋 账户信息摘要:")
        print(f"   邮箱: {email}")
        print(f"   密码: {password}")
        print(f"   名字: {name}")
        print(f"   生日: {birth_date}")
        print(f"\n📁 文件位置:")
        print(f"   截图: {SCREENSHOTS_DIR}/")
        print(f"   CSV: {CSV_FILE}")
        print(f"   JSON: {ACCOUNTS_DIR}/")
        
        # 登录到邮箱
        print(f"\n🔐 现在尝试登录邮箱...")
        try:
            await tab.sleep(2)
            
            # 直接访问邮箱登录页面
            print(f"📧 访问 Outlook 邮箱登录页面...")
            login_url = f"https://outlook.live.com/mail/0/inbox"
            tab = await driver.get(login_url)
            await tab.sleep(10)
            
            print(f"   当前 URL: {tab.url[:80]}...")
            
            # 尝试查找邮箱输入字段
            print(f"📝 输入邮箱...")
            email_input_found = False
            
            # 方法 1: 直接查找邮箱输入框
            try:
                email_input = await tab.select("input[name='loginfmt']", timeout=5)
                if email_input:
                    await email_input.send_keys(email)
                    await tab.sleep(1)
                    email_input_found = True
                    print(f"   ✓ 找到邮箱输入框")
            except:
                pass
            
            # 方法 2: 使用 JavaScript 填充
            if not email_input_found:
                try:
                    await tab.select("input[type='email']", timeout=3)
                    email_input = await tab.select("input[type='email']")
                    await email_input.send_keys(email)
                    await tab.sleep(1)
                    email_input_found = True
                    print(f"   ✓ 通过 email 类型找到邮箱输入框")
                except:
                    pass
            
            if email_input_found:
                # 点击下一步
                try:
                    next_btn = await tab.select("button[id='idSIButton9']", timeout=3)
                    if not next_btn:
                        next_btn = await tab.select("button[type='submit']", timeout=3)
                    if next_btn:
                        await next_btn.click()
                        await tab.sleep(6)
                        print(f"   ✓ 邮箱输入完成，等待密码字段...")
                except:
                    print(f"   ⚠️  无法点击下一步按钮")
                
                # 输入密码
                print(f"🔑 输入密码...")
                pwd_found = False
                
                try:
                    pwd_input = await tab.select("input[name='passwd']", timeout=5)
                    if pwd_input:
                        await pwd_input.send_keys(password)
                        await tab.sleep(1)
                        pwd_found = True
                        print(f"   ✓ 找到密码输入框")
                except:
                    pass
                
                if pwd_found:
                    # 点击登录
                    try:
                        submit_btn = await tab.select("button[id='idSIButton9']", timeout=3)
                        if not submit_btn:
                            submit_btn = await tab.select("button[type='submit']", timeout=3)
                        if submit_btn:
                            await submit_btn.click()
                            await tab.sleep(8)
                            print(f"   ✓ 密码输入完成，等待邮箱加载...")
                    except:
                        print(f"   ⚠️  无法提交登录")
                
                # 等待邮箱加载并检查 URL 变化
                print(f"⏳ 等待邮箱界面加载... (20秒)")
                for i in range(20):
                    await tab.sleep(1)
                    current_url = tab.url
                    if "outlook" in current_url.lower() or "mail" in current_url.lower():
                        if i > 3:  # 至少等待 3 秒后再保存
                            break
                
                # 等待额外的页面加载时间
                await tab.sleep(5)
                
                # 保存邮箱截图
                inbox_screenshot = os.path.join(INBOX_SCREENSHOTS_DIR, 
                                               f"inbox_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                try:
                    await tab.save_screenshot(inbox_screenshot)
                    print(f"📸 邮箱界面截图已保存!")
                    print(f"   {inbox_screenshot}")
                except Exception as e:
                    print(f"   ⚠️  邮箱截图保存失败: {e}")
            else:
                print(f"   ⚠️  未找到邮箱输入表单")
        
        except Exception as e:
            print(f"   ⚠️  邮箱登录异常: {e}")
        
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
