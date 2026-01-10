#!/usr/bin/env python3
"""
诊断脚本：检查 DOM 中是否真的存在邮箱输入框，以及 tab.find() 为什么找不到
"""

import asyncio
import nodriver as uc


async def main():
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )
    
    tab = await driver.get("https://signup.live.com/?lic=1")
    await tab.sleep(5)
    
    print("=== DOM 诊断 ===\n")
    
    # 1. 用 JavaScript 查询元素
    result = await tab.evaluate("""
    () => {
        const tests = {
            'by_type': document.querySelector('input[type="email"]'),
            'by_id': document.querySelector('#floatingLabelInput4'),
            'by_name': document.querySelector('input[name="Email"]'),
            'all_inputs': document.querySelectorAll('input').length,
            'all_inputs_with_email': Array.from(document.querySelectorAll('input')).filter(i => i.getAttribute('aria-label')?.includes('Email')).length,
        };
        return {
            by_type: !!tests.by_type,
            by_id: !!tests.by_id,
            by_name: !!tests.by_name,
            all_inputs: tests.all_inputs,
            all_inputs_with_email: tests.all_inputs_with_email,
        };
    }
    """)
    
    print(f"JavaScript 查询结果:")
    print(f"  input[type='email'] 存在: {result['by_type']}")
    print(f"  #floatingLabelInput4 存在: {result['by_id']}")
    print(f"  input[name='Email'] 存在: {result['by_name']}")
    print(f"  页面总 input 数: {result['all_inputs']}")
    print(f"  含 Email aria-label 的 input: {result['all_inputs_with_email']}")
    
    # 2. 尝试用 tab.find()
    print(f"\n尝试 tab.find():")
    try:
        elem = await tab.find('input[type="email"]', single=True)
        print(f"  tab.find('input[type=\"email\"]'): {elem}")
    except Exception as e:
        print(f"  tab.find('input[type=\"email\"]') 异常: {e}")
    
    try:
        elem = await tab.find('input', single=True)
        print(f"  tab.find('input', single=True): {elem}")
    except Exception as e:
        print(f"  tab.find('input', single=True) 异常: {e}")
    
    try:
        elems = await tab.find('input', single=False)
        print(f"  tab.find('input', single=False) 返回 {len(elems) if elems else 0} 个元素")
    except Exception as e:
        print(f"  tab.find('input', single=False) 异常: {e}")
    
    # 3. 检查是否有 iframe
    iframe_count = await tab.evaluate("() => document.querySelectorAll('iframe').length")
    print(f"\n页面中的 iframe 数: {iframe_count}")
    
    # 4. 保存截图和 HTML
    await tab.save_screenshot("/tmp/diagnosis.png")
    print(f"\n截图已保存: /tmp/diagnosis.png")
    
    html = await tab.get_content()
    with open("/tmp/diagnosis.html", "w") as f:
        f.write(html)
    print(f"HTML 已保存: /tmp/diagnosis.html")
    
    await driver.stop()


if __name__ == "__main__":
    asyncio.run(main())
