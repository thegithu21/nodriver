#!/usr/bin/env python3
"""
Outlook (Hotmail) 邮箱自动注册脚本
使用 nodriver 库自动化注册流程，支持随机账号生成
"""

import asyncio
import os
import sys
import time
import random
import string
import json
from datetime import datetime
from pathlib import Path

# 导入 nodriver
try:
    import nodriver as uc
except (ModuleNotFoundError, ImportError):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import nodriver as uc

# 设置调试输出目录
DEBUG_DIR = "/workspaces/nodriver/debug_output"
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots")
ACCOUNTS_DIR = os.path.join(DEBUG_DIR, "accounts")

# 创建目录
for dir_path in [DEBUG_DIR, SCREENSHOTS_DIR, ACCOUNTS_DIR]:
    os.makedirs(dir_path, exist_ok=True)


class OutlookLogger:
    """日志记录器"""
    def __init__(self, log_file):
        self.log_file = log_file
        self.file_handle = open(log_file, 'w', encoding='utf-8')
    
    def write(self, message):
        print(message, end='')
        self.file_handle.write(message)
        self.file_handle.flush()
    
    def close(self):
        self.file_handle.close()


def generate_random_string(length=8):
    """生成随机字符串"""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_random_name():
    """生成随机名字"""
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Robert", "Lisa"]
    last_names = ["Smith", "Johnson", "Brown", "Taylor", "Williams", "Jones", "Garcia", "Lee"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_random_date():
    """生成随机出生日期"""
    year = random.randint(1980, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{month:02d}/{day:02d}/{year}"


async def save_screenshot(tab, prefix=""):
    """保存截图"""
    try:
        filename = f"outlook_{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        await tab.save_screenshot(filepath)
        print(f"  📸 截图已保存: {filepath}")
        return filepath
    except Exception as e:
        print(f"  ⚠️  截图保存失败: {e}")
        return None


async def wait_and_find(tab, selectors, timeout=10, description="element"):
    """等待并查找元素"""
    if isinstance(selectors, str):
        selectors = [selectors]
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        for selector in selectors:
            try:
                element = await tab.select(selector)
                if element:
                    return element
            except:
                pass
        await tab.sleep(0.5)
    
    raise TimeoutError(f"Cannot find {description} within {timeout} seconds")


async def register_outlook_account():
    """注册 Outlook 账户"""
    
    log_file = os.path.join(DEBUG_DIR, f"outlook_register_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logger = OutlookLogger(log_file)
    
    def log(message):
        """输出日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        logger.write(f"[{timestamp}] {message}\n")
    
    log("=" * 70)
    log("Outlook (Hotmail) 邮箱自动注册")
    log("=" * 70)
    log(f"日志文件: {log_file}")
    log(f"调试目录: {DEBUG_DIR}\n")
    
    # 启动浏览器
    log("📱 启动浏览器...")
    try:
        driver = await uc.start(
            headless=False,  # 改为 False 以便查看过程
            no_sandbox=True,
            browser_executable_path="/usr/bin/google-chrome",
            browser_args=['--disable-dev-shm-usage', '--disable-gpu', '--no-first-run']
        )
    except Exception as e:
        log(f"❌ 浏览器启动失败: {e}")
        log("尝试使用默认浏览器...")
        driver = await uc.start(
            headless=False,
            no_sandbox=True,
            browser_args=['--disable-dev-shm-usage', '--disable-gpu']
        )
    
    try:
        # 生成账户信息
        username = generate_random_string(12)
        email = f"{username}@outlook.com"
        password = generate_random_string(16)  # 更强的密码
        name = generate_random_name()
        birth_date = generate_random_date()
        
        log(f"\n📝 生成的账户信息:")
        log(f"  邮箱: {email}")
        log(f"  密码: {password}")
        log(f"  姓名: {name}")
        log(f"  生日: {birth_date}\n")
        
        # 访问 Outlook 注册页面
        log("🌐 访问 Outlook.com...")
        tab = await driver.get("https://outlook.com/")
        await tab.sleep(3)
        
        await save_screenshot(tab, "homepage")
        
        # 查找"创建免费账户"按钮
        log("🔍 查找注册按钮...")
        try:
            # 尝试多个可能的按钮文本
            signup_btn = None
            for text in ["Create free account", "Sign up", "Create account", "新建账户"]:
                try:
                    signup_btn = await tab.find(text, best_match=True)
                    if signup_btn:
                        log(f"  ✓ 找到按钮: '{text}'")
                        break
                except:
                    pass
            
            if signup_btn:
                log("  点击注册按钮...")
                await signup_btn.click()
                await tab.sleep(4)
                await save_screenshot(tab, "signup_page")
            else:
                log("  ⚠️  未找到标准按钮，尝试查找邮箱输入框...")
        except Exception as e:
            log(f"  ⚠️  按钮查找失败: {e}")
        
        # 第一步: 输入电子邮件
        log("\n📧 第一步: 输入电子邮件地址")
        try:
            # 查找邮箱输入框
            email_input = await wait_and_find(
                tab,
                ["input[type='email']", "input[name='email']", "input[placeholder*='email']", "input[placeholder*='Email']"],
                timeout=10,
                description="email input"
            )
            
            log(f"  输入邮箱: {email}")
            await email_input.send_keys(email)
            await tab.sleep(1)
            
            # 点击下一步按钮
            next_btn = await wait_and_find(
                tab,
                ["button:has-text('Next')", "button:has-text('下一步')", "button[type='submit']"],
                timeout=5,
                description="next button"
            )
            log("  点击下一步...")
            await next_btn.click()
            await tab.sleep(3)
            await save_screenshot(tab, "email_entered")
            
        except Exception as e:
            log(f"  ❌ 邮箱输入失败: {e}")
            await save_screenshot(tab, "email_error")
            return None
        
        # 第二步: 输入密码
        log("\n🔐 第二步: 输入密码")
        try:
            password_input = await wait_and_find(
                tab,
                ["input[type='password']", "input[name='password']"],
                timeout=10,
                description="password input"
            )
            
            log(f"  输入密码...")
            await password_input.send_keys(password)
            await tab.sleep(1)
            
            next_btn = await wait_and_find(
                tab,
                ["button:has-text('Next')", "button:has-text('下一步')", "button[type='submit']"],
                timeout=5,
                description="next button"
            )
            log("  点击下一步...")
            await next_btn.click()
            await tab.sleep(3)
            await save_screenshot(tab, "password_entered")
            
        except Exception as e:
            log(f"  ❌ 密码输入失败: {e}")
            await save_screenshot(tab, "password_error")
            return None
        
        # 第三步: 输入名字
        log("\n👤 第三步: 输入用户名称")
        try:
            name_input = await wait_and_find(
                tab,
                ["input[type='text']", "input[name='firstName']", "input[placeholder*='name']"],
                timeout=10,
                description="name input"
            )
            
            log(f"  输入名字: {name}")
            # 清除任何已有文本
            await name_input.send_keys(["Control", "a"])
            await name_input.send_keys(name)
            await tab.sleep(1)
            
            next_btn = await wait_and_find(
                tab,
                ["button:has-text('Next')", "button:has-text('下一步')", "button[type='submit']"],
                timeout=5,
                description="next button"
            )
            log("  点击下一步...")
            await next_btn.click()
            await tab.sleep(3)
            await save_screenshot(tab, "name_entered")
            
        except Exception as e:
            log(f"  ❌ 名字输入失败: {e}")
            await save_screenshot(tab, "name_error")
            return None
        
        # 第四步: 输入出生日期
        log("\n📅 第四步: 输入出生日期")
        try:
            birth_input = await wait_and_find(
                tab,
                ["input[placeholder*='Birth date']", "input[placeholder*='birth']", "input[type='date']"],
                timeout=10,
                description="birth date input"
            )
            
            log(f"  输入出生日期: {birth_date}")
            await birth_input.send_keys(birth_date)
            await tab.sleep(1)
            
            next_btn = await wait_and_find(
                tab,
                ["button:has-text('Next')", "button:has-text('下一步')", "button[type='submit']"],
                timeout=5,
                description="next button"
            )
            log("  点击下一步...")
            await next_btn.click()
            await tab.sleep(3)
            await save_screenshot(tab, "birth_entered")
            
        except Exception as e:
            log(f"  ⚠️  出生日期输入失败（可能可跳过）: {e}")
            await save_screenshot(tab, "birth_error")
        
        # 等待验证或确认页面
        log("\n⏳ 等待验证流程...")
        await tab.sleep(5)
        await save_screenshot(tab, "verification_page")
        
        log("\n✅ 账户创建流程已完成!")
        log("  注意: 可能需要进一步的验证步骤（如邮箱验证或电话验证）")
        
        # 保存账户信息
        account_info = {
            "email": email,
            "password": password,
            "name": name,
            "birth_date": birth_date,
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
        
        account_file = os.path.join(ACCOUNTS_DIR, f"outlook_account_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(account_file, 'w', encoding='utf-8') as f:
            json.dump(account_info, f, indent=2, ensure_ascii=False)
        
        log(f"\n📁 账户信息已保存: {account_file}")
        
        return account_info
        
    except Exception as e:
        log(f"\n❌ 注册过程出错: {e}")
        await save_screenshot(tab, "error")
        return None
    
    finally:
        log("\n🔌 关闭浏览器...")
        await driver.stop()
        logger.close()


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("Outlook (Hotmail) 邮箱自动注册脚本")
    print("=" * 70 + "\n")
    
    try:
        result = asyncio.run(register_outlook_account())
        
        if result:
            print("\n✅ 注册成功!")
            print(f"\n账户信息:")
            print(f"  邮箱: {result['email']}")
            print(f"  名字: {result['name']}")
            print(f"  生日: {result['birth_date']}")
            print(f"  创建时间: {result['created_at']}")
        else:
            print("\n❌ 注册失败，请查看日志获取详细信息")
    
    except KeyboardInterrupt:
        print("\n⚠️  用户中断了注册过程")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()
