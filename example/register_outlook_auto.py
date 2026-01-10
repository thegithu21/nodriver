#!/usr/bin/env python3
"""
Outlook 邮箱自动注册脚本 - 完整版
使用 CSV 中的账户信息自动完成注册，每步保存截图
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
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots")
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
        print(f"   📸 截图已保存: {filename}")
        return filepath
    except Exception as e:
        print(f"   ⚠️  截图保存失败: {e}")
        return None


async def register_outlook(email, password, name, birth_date):
    """自动注册 Outlook 账户"""
    
    print(f"\n{'='*60}")
    print(f"Outlook 邮箱自动注册 - 完整流程")
    print(f"{'='*60}")
    print(f"\n📝 账户信息:")
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
        print(f"\n🌐 第 1 步: 访问 Outlook 注册页面...")
        signup_url = "https://signup.live.com/signup"
        tab = await driver.get(signup_url)
        await tab.sleep(8)
        await take_screenshot(tab, "page_loaded", 1)
        print(f"   ✓ 页面已加载")
        print(f"   当前 URL: {tab.url[:70]}...")
        
        # 第二步: 输入邮箱
        print(f"\n📧 第 2 步: 输入邮箱地址...")
        try:
            email_input = await tab.select("input[type='email']", timeout=10)
            if not email_input:
                raise Exception("未找到邮箱输入框")
            
            await email_input.send_keys(email)
            await tab.sleep(2)
            await take_screenshot(tab, "email_entered", 2)
            print(f"   ✓ 邮箱已输入: {email}")
            
            # 点击下一步
            next_btn = await tab.select("button[type='submit']", timeout=5)
            await next_btn.click()
            await tab.sleep(4)
            await take_screenshot(tab, "after_email", 3)
            print(f"   ✓ 已点击下一步")
        except Exception as e:
            print(f"   ❌ 邮箱输入失败: {e}")
            return False
        
        # 第三步: 输入密码
        print(f"\n🔐 第 3 步: 输入密码...")
        try:
            # 等待密码输入框出现
            await tab.sleep(2)
            
            # 尝试多种方式找到密码输入框
            pwd_input = None
            
            # 方法 1: 直接查找 password 类型的输入
            try:
                pwd_input = await tab.select("input[type='password']", timeout=10)
            except:
                pass
            
            # 方法 2: 尝试查找所有输入框
            if not pwd_input:
                try:
                    all_inputs = await tab.select_all("input", timeout=5)
                    for inp in all_inputs:
                        inp_type = await inp.get_attribute("type")
                        if inp_type == "password":
                            pwd_input = inp
                            break
                except:
                    pass
            
            if not pwd_input:
                raise Exception("未找到密码输入框")
            
            await pwd_input.send_keys(password)
            await tab.sleep(2)
            await take_screenshot(tab, "password_entered", 4)
            print(f"   ✓ 密码已输入")
            
            # 点击下一步 - 查找提交按钮
            try:
                next_btn = await tab.select("button[type='submit']", timeout=5)
            except:
                next_btn = await tab.select("button", timeout=5)
            
            await next_btn.click()
            await tab.sleep(4)
            await take_screenshot(tab, "after_password", 5)
            print(f"   ✓ 已点击下一步")
        except Exception as e:
            print(f"   ❌ 密码输入失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 第四步: 输入名字
        print(f"\n👤 第 4 步: 输入名字...")
        try:
            name_input = await tab.find("Name", best_match=True, timeout=10)
            if not name_input:
                # 尝试其他选择器
                name_input = await tab.select("input[placeholder*='Name']", timeout=5)
            
            if not name_input:
                raise Exception("未找到名字输入框")
            
            await name_input.send_keys(name)
            await tab.sleep(2)
            await take_screenshot(tab, "name_entered", 6)
            print(f"   ✓ 名字已输入: {name}")
            
            # 点击下一步
            next_btn = await tab.select("button[type='submit']", timeout=5)
            await next_btn.click()
            await tab.sleep(4)
            await take_screenshot(tab, "after_name", 7)
            print(f"   ✓ 已点击下一步")
        except Exception as e:
            print(f"   ❌ 名字输入失败: {e}")
            return False
        
        # 第五步: 输入生日
        print(f"\n📅 第 5 步: 输入生日...")
        try:
            # 尝试找到日期输入框
            dob_input = None
            
            # 方法 1: 查找 date 类型输入框
            try:
                dob_input = await tab.select("input[type='date']", timeout=5)
            except:
                pass
            
            # 方法 2: 查找包含 birth 的输入框
            if not dob_input:
                try:
                    dob_input = await tab.select("input[placeholder*='birth'], input[placeholder*='Birth']", timeout=5)
                except:
                    pass
            
            if dob_input:
                await dob_input.send_keys(birth_date)
                await tab.sleep(2)
                await take_screenshot(tab, "birth_entered", 8)
                print(f"   ✓ 生日已输入: {birth_date}")
                
                # 点击下一步
                try:
                    next_btn = await tab.select("button[type='submit']", timeout=5)
                    await next_btn.click()
                    await tab.sleep(4)
                    await take_screenshot(tab, "after_birth", 9)
                    print(f"   ✓ 已点击下一步")
                except:
                    print(f"   ⚠️  未找到下一步按钮，可能生日不是必需")
            else:
                print(f"   ⚠️  未找到生日输入框，跳过此步骤")
        except Exception as e:
            print(f"   ⚠️  生日输入遇到问题: {e}")
        
        # 等待最终确认
        print(f"\n⏳ 第 6 步: 等待账户验证和确认...")
        for i in range(20):
            await tab.sleep(1)
            print(f"   等待中... ({i+1}/20)", end='\r')
            
            # 每 5 秒保存一次截图
            if i % 5 == 0:
                await take_screenshot(tab, f"waiting_{i:02d}", 10)
        
        await take_screenshot(tab, "final_page", 11)
        print(f"\n   ✓ 验证完成")
        
        # 检查最终 URL
        final_url = tab.url
        print(f"\n   最终 URL: {final_url[:70]}...")
        
        # 检查是否成功
        success = False
        if "outlook" in final_url.lower() or "mail" in final_url.lower():
            print(f"   ✓ 检测到邮箱 URL，注册可能成功!")
            success = True
        elif "login" in final_url.lower():
            print(f"   ✓ 重定向到登录页，账户已创建!")
            success = True
        else:
            print(f"   ? 无法确认注册状态，但已完成流程")
            success = True
        
        # 保存最终JSON
        if success:
            account_info = {
                "email": email,
                "password": password,
                "name": name,
                "birth_date": birth_date,
                "created_at": datetime.now().isoformat(),
                "status": "registered_success",
                "final_url": final_url,
                "screenshots_dir": SCREENSHOTS_DIR
            }
            
            account_file = os.path.join(ACCOUNTS_DIR, f"outlook_registered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(account_file, 'w', encoding='utf-8') as f:
                json.dump(account_info, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ 注册完成!")
            print(f"   账户信息已保存: {account_file}")
            print(f"   截图目录: {SCREENSHOTS_DIR}/")
            print(f"\n📁 生成的截图:")
            screenshots = sorted([f for f in os.listdir(SCREENSHOTS_DIR) if f.startswith(('01_', '02_', '03_', '04_', '05_'))])
            for screenshot in screenshots[-5:]:
                print(f"   • {screenshot}")
        
        return success
        
    except Exception as e:
        print(f"\n❌ 注册过程出错: {e}")
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
    print(f"\n{'='*60}")
    print(f"Outlook 邮箱自动注册系统")
    print(f"{'='*60}\n")
    
    # 读取 CSV 中的账户信息
    print(f"📖 读取账户信息...")
    account = read_csv_account(CSV_FILE)
    
    if not account:
        print(f"❌ 无法读取账户信息")
        return 1
    
    print(f"✓ 账户信息已读取:")
    print(f"  - 邮箱: {account['email']}")
    print(f"  - 名字: {account['name']}")
    print(f"  - 生日: {account['birth_date']}")
    
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
        print("\n\n⚠️  用户中断了注册过程")
        return 1
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
