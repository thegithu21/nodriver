import asyncio
import nodriver as uc

async def main():
    browser = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_executable_path="/usr/bin/google-chrome",
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )
    
    tab = await browser.get('https://nowsecure.nl')
    
    print("等待 CF...")
    for wait in [15, 15]:  # 先15s → 再加15s
        await asyncio.sleep(wait)
        print(f"{wait}s 后标题:", tab.title)
        if "Just a moment" not in tab.title:
            break
        print("挑战还在，重载页面...")
        await tab.reload()
    
    print("最终标题:", tab.title)
    print("URL:", tab.url)
    
    browser.stop()

if __name__ == '__main__':
    asyncio.run(main())