#!/usr/bin/env python3
"""
测试 Outlook 页面结构
"""

import asyncio
import os
import sys
import nodriver as uc

async def main():
    # 创建调试目录
    debug_dir = "/workspaces/nodriver/debug_output"
    os.makedirs(debug_dir, exist_ok=True)
    
    print("启动浏览器...")
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_args=[
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
        ]
    )
    
    try:
        print("访问 Outlook...")
        tab = await driver.get("https://outlook.com/")
        await tab.sleep(5)
        
        # 保存初始页面 HTML
        html = await tab.get_content()
        html_file = os.path.join(debug_dir, "outlook_initial.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"初始页面已保存: {html_file}")
        
        # 保存截图
        screenshot = os.path.join(debug_dir, "outlook_initial.png")
        await tab.save_screenshot(screenshot)
        print(f"初始截图已保存: {screenshot}")
        
        # 查找按钮
        print("\n查找 'Create account' 按钮...")
        try:
            buttons = await tab.select_all("button")
            print(f"  找到 {len(buttons)} 个按钮")
            
            # 打印按钮文本
            for i, button in enumerate(buttons[:20]):
                try:
                    text = await button.get_text()
                    if text.strip():
                        print(f"    按钮 {i}: {text.strip()[:50]}")
                except:
                    pass
        except Exception as e:
            print(f"  错误: {e}")
        
        # 查找所有文本中包含"Create"的元素
        print("\n查找包含 'Create' 的元素...")
        try:
            content = await tab.get_content()
            if "Create free account" in content:
                print("  ✓ 页面中包含 'Create free account' 文本")
            else:
                print("  ✗ 页面中不包含 'Create free account' 文本")
        except Exception as e:
            print(f"  错误: {e}")
        
        # 查找输入框
        print("\n查找输入框...")
        try:
            inputs = await tab.select_all("input")
            print(f"  找到 {len(inputs)} 个输入框")
        except Exception as e:
            print(f"  错误: {e}")
        
        # 等待更多内容加载
        print("\n等待页面加载...")
        await tab.sleep(10)
        
        # 再次保存页面
        html = await tab.get_content()
        html_file = os.path.join(debug_dir, "outlook_after_load.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"加载后页面已保存: {html_file}")
        
        # 再次保存截图
        screenshot = os.path.join(debug_dir, "outlook_after_load.png")
        await tab.save_screenshot(screenshot)
        print(f"加载后截图已保存: {screenshot}")
        
        print("\n✅ 测试完成")
        
    finally:
        print("\n关闭浏览器...")
        await driver.stop()

if __name__ == '__main__':
    asyncio.run(main())
