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
    
    # 检查浏览器可执行文件是否存在
    chrome_paths = [
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            log(f"  ✓ 找到浏览器: {path}")
            break
    
    if not chrome_path:
        log(f"  ⚠️  未找到浏览器路径，使用 nodriver 自动查找...")
    else:
        log(f"  使用浏览器路径: {chrome_path}")
    
    try:
        log(f"  🔧 启动参数:")
        log(f"     headless=False")
        log(f"     no_sandbox=True")
        log(f"     browser_executable_path={chrome_path}")
        
        driver = await uc.start(
            headless=True,  # 使用 headless 模式来避免连接问题
            no_sandbox=True,
            browser_executable_path=chrome_path,
            browser_args=[
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--disable-extensions',
                '--use-gl=swiftshader',
                '--disable-gpu-sandbox',
            ]
        )
        log(f"  ✓ 浏览器启动成功")
    except Exception as e:
        log(f"❌ 浏览器启动失败: {e}")
        log(f"  错误信息: {str(e)}")
        raise
    
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
        log("🌐 访问 Outlook 注册页面...")
        try:
            # 直接访问注册页面
            signup_url = "https://go.microsoft.com/fwlink/p/?linkid=2125440&clcid=0x409&culture=en-us&country=us"
            tab = await driver.get(signup_url)
            log("  ⏳ 等待页面加载...")
            await tab.sleep(8)
            
            # 获取当前 URL 以验证页面加载
            current_url = tab.url
            log(f"  ✓ 当前URL: {current_url}")
            
            await save_screenshot(tab, "signup_page_direct")
        except Exception as e:
            log(f"  ❌ 访问注册页面失败: {e}")
            raise
        
        # 第一步: 输入电子邮件
        log("\n📧 第一步: 输入电子邮件地址")
        try:
            # 查找邮箱输入框
            log("  🔍 查找邮箱输入框...")
            email_input = None
            email_selectors = [
                "input[type='email']",
                "input[name='email']",
                "input[placeholder*='email']",
                "input[placeholder*='Email']",
                "input[id*='email']",
            ]
            
            for selector in email_selectors:
                try:
                    elements = await tab.select_all(selector)
                    if elements:
                        email_input = elements[0]
                        log(f"  ✓ 找到邮箱输入框: {selector}")
                        break
                except:
                    pass
            
            if not email_input:
                # 使用 find 方法查找邮箱标签附近的输入框
                try:
                    log("  尝试使用 find 方法查找邮箱输入框...")
                    email_input = await tab.find("Email")
                    log(f"  ✓ 使用 find 方法找到邮箱输入框")
                except:
                    log("  ❌ 仍无法找到邮箱输入框")
                    raise TimeoutError("Cannot find email input")
            
            log(f"  输入邮箱: {email}")
            await email_input.send_keys(email)
            await tab.sleep(1)
            
            # 点击下一步按钮
            log("  🔍 查找下一步按钮...")
            next_btn = None
            next_selectors = [
                "button:has-text('Next')",
                "button:has-text('下一步')",
                "button[type='submit']",
                "button:visible",
            ]
            
            for selector in next_selectors:
                try:
                    elements = await tab.select_all(selector)
                    if elements:
                        next_btn = elements[0]
                        log(f"  ✓ 找到下一步按钮: {selector}")
                        break
                except:
                    pass
            
            if next_btn:
                log("  点击下一步...")
                await next_btn.click()
                await tab.sleep(3)
                await save_screenshot(tab, "email_entered")
            else:
                log("  ⚠️  未找到下一步按钮，尝试按 Enter...")
                await email_input.send_keys('\n')
                await tab.sleep(3)
                await save_screenshot(tab, "email_entered")
            
        except Exception as e:
            log(f"  ❌ 邮箱输入失败: {e}")
            await save_screenshot(tab, "email_error")
            # 收集调试信息
            log("\n  📊 调试信息收集:")
            try:
                page_html = await tab.get_content()
                html_file = os.path.join(DEBUG_DIR, f"page_html_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(page_html)
                log(f"    HTML 已保存: {html_file}")
            except Exception as e2:
                log(f"    HTML 保存失败: {e2}")
            
            return None
        
        # 第二步: 输入密码
        log("\n🔐 第二步: 输入密码")
        try:
            log("  🔍 查找密码输入框...")
            password_input = None
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[id*='password']",
            ]
            
            for selector in password_selectors:
                try:
                    elements = await tab.select_all(selector)
                    if elements:
                        password_input = elements[0]
                        log(f"  ✓ 找到密码输入框: {selector}")
                        break
                except:
                    pass
            
            if not password_input:
                try:
                    log("  尝试使用 find 方法查找密码输入框...")
                    password_input = await tab.find("Password")
                    log(f"  ✓ 使用 find 方法找到密码输入框")
                except:
                    log("  ❌ 无法找到密码输入框")
                    raise TimeoutError("Cannot find password input")
            
            log(f"  输入密码...")
            await password_input.send_keys(password)
            await tab.sleep(1)
            
            # 点击下一步按钮
            log("  🔍 查找下一步按钮...")
            next_btn = None
            next_selectors = [
                "button:has-text('Next')",
                "button:has-text('下一步')",
                "button[type='submit']",
            ]
            
            for selector in next_selectors:
                try:
                    elements = await tab.select_all(selector)
                    if elements:
                        next_btn = elements[-1]  # 获取最后一个 Next 按钮
                        log(f"  ✓ 找到下一步按钮: {selector}")
                        break
                except:
                    pass
            
            if next_btn:
                log("  点击下一步...")
                await next_btn.click()
                await tab.sleep(3)
                await save_screenshot(tab, "password_entered")
            else:
                log("  ⚠️  未找到下一步按钮，尝试按 Enter...")
                await password_input.send_keys('\n')
                await tab.sleep(3)
                await save_screenshot(tab, "password_entered")
            
        except Exception as e:
            log(f"  ❌ 密码输入失败: {e}")
            await save_screenshot(tab, "password_error")
            
            # 收集调试信息
            log("\n  📊 调试信息收集:")
            try:
                page_html = await tab.get_content()
                html_file = os.path.join(DEBUG_DIR, f"page_html_password_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(page_html)
                log(f"    HTML 已保存: {html_file}")
            except Exception as e2:
                log(f"    HTML 保存失败: {e2}")
            
            return None
        
        # 第三步: 输入名字
        log("\n👤 第三步: 输入用户名称")
        try:
            log("  🔍 查找名字输入框...")
            name_input = None
            name_selectors = [
                "input[type='text']",
                "input[name='firstName']",
                "input[placeholder*='name']",
                "input[placeholder*='Name']",
                "input[id*='name']",
            ]
            
            for selector in name_selectors:
                try:
                    elements = await tab.select_all(selector)
                    if elements:
                        name_input = elements[0]
                        log(f"  ✓ 找到名字输入框: {selector}")
                        break
                except:
                    pass
            
            if not name_input:
                try:
                    log("  尝试使用 find 方法查找名字输入框...")
                    name_input = await tab.find("Name")
                    log(f"  ✓ 使用 find 方法找到名字输入框")
                except:
                    log("  ❌ 无法找到名字输入框")
                    raise TimeoutError("Cannot find name input")
            
            log(f"  输入名字: {name}")
            # 清除任何已有文本
            await name_input.send_keys(name)
            await tab.sleep(1)
            
            # 点击下一步按钮
            log("  🔍 查找下一步按钮...")
            next_btn = None
            next_selectors = [
                "button:has-text('Next')",
                "button:has-text('下一步')",
                "button[type='submit']",
            ]
            
            for selector in next_selectors:
                try:
                    elements = await tab.select_all(selector)
                    if elements:
                        next_btn = elements[-1]
                        log(f"  ✓ 找到下一步按钮: {selector}")
                        break
                except:
                    pass
            
            if next_btn:
                log("  点击下一步...")
                await next_btn.click()
                await tab.sleep(3)
                await save_screenshot(tab, "name_entered")
            else:
                log("  ⚠️  未找到下一步按钮，尝试按 Enter...")
                await name_input.send_keys('\n')
                await tab.sleep(3)
                await save_screenshot(tab, "name_entered")
            
        except Exception as e:
            log(f"  ❌ 名字输入失败: {e}")
            await save_screenshot(tab, "name_error")
            
            # 收集调试信息
            log("\n  📊 调试信息收集:")
            try:
                page_html = await tab.get_content()
                html_file = os.path.join(DEBUG_DIR, f"page_html_name_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(page_html)
                log(f"    HTML 已保存: {html_file}")
            except Exception as e2:
                log(f"    HTML 保存失败: {e2}")
            
            return None
        
        # 第四步: 输入出生日期
        log("\n📅 第四步: 输入出生日期")
        try:
            log("  🔍 查找出生日期输入框...")
            birth_input = None
            birth_selectors = [
                "input[placeholder*='Birth date']",
                "input[placeholder*='birth']",
                "input[type='date']",
                "input[id*='birth']",
            ]
            
            for selector in birth_selectors:
                try:
                    elements = await tab.select_all(selector)
                    if elements:
                        birth_input = elements[0]
                        log(f"  ✓ 找到出生日期输入框: {selector}")
                        break
                except:
                    pass
            
            if birth_input:
                log(f"  输入出生日期: {birth_date}")
                await birth_input.send_keys(birth_date)
                await tab.sleep(1)
                
                # 点击下一步按钮
                log("  🔍 查找下一步按钮...")
                next_btn = None
                next_selectors = [
                    "button:has-text('Next')",
                    "button:has-text('下一步')",
                    "button[type='submit']",
                ]
                
                for selector in next_selectors:
                    try:
                        elements = await tab.select_all(selector)
                        if elements:
                            next_btn = elements[-1]
                            log(f"  ✓ 找到下一步按钮: {selector}")
                            break
                    except:
                        pass
                
                if next_btn:
                    log("  点击下一步...")
                    await next_btn.click()
                    await tab.sleep(3)
                    await save_screenshot(tab, "birth_entered")
                else:
                    log("  ⚠️  未找到下一步按钮，尝试按 Enter...")
                    await birth_input.send_keys('\n')
                    await tab.sleep(3)
                    await save_screenshot(tab, "birth_entered")
            else:
                log("  ⚠️  未找到出生日期输入框（可能可跳过）")
                await save_screenshot(tab, "birth_not_found")
            
        except Exception as e:
            log(f"  ⚠️  出生日期输入失败（可能可跳过）: {e}")
            await save_screenshot(tab, "birth_error")
        
        # 等待验证或确认页面
        log("\n⏳ 等待验证流程...")
        for i in range(10):
            await tab.sleep(1)
            await save_screenshot(tab, f"verification_page_{i}")
            
            # 检查是否有错误信息
            try:
                page_html = await tab.get_content()
                if "error" in page_html.lower() or "invalid" in page_html.lower():
                    log(f"  ⚠️  可能出现错误信息，检查截图...")
            except:
                pass
        
        # 检查最终 URL 和页面状态
        try:
            final_url = tab.url
            log(f"\n  ✓ 最终URL: {final_url}")
            
            page_html = await tab.get_content()
            
            if "outlook" in final_url.lower() or "mail" in final_url.lower():
                log("\n✅ 账户创建流程已完成!")
                log("  账户已成功创建或需要进一步验证")
            else:
                log("\n⚠️  页面 URL 变化，注意可能需要进一步操作")
        except Exception as e:
            log(f"\n  URL 检查失败: {e}")
        
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
        try:
            driver.stop()
        except:
            pass
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
