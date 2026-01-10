# Twitter create account
# demo for undetected_nodriver
# ultrafunkamsterdam


import asyncio
import logging
import random
import string

logging.basicConfig(level=30)

try:
    import nodriver as uc
except (ModuleNotFoundError, ImportError):
    import os
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import nodriver as uc

months = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]


async def main():
    driver = await uc.start(
        headless=True,
        no_sandbox=True,
        browser_executable_path="/usr/bin/google-chrome",
        browser_args=['--disable-dev-shm-usage', '--disable-gpu']
    )

    tab = await driver.get("https://twitter.com")

    # wait for text to appear instead of a static number of seconds to wait
    # this does not always work as expected, due to speed.
    print('finding the "create account" button')
    create_account = await tab.find("create account", best_match=True)

    print('"create account" => click')
    await create_account.click()

    print("finding the email input field")
    await tab.sleep(2)  # 等待页面加载
    
    # 先检查页面内容
    print("page title:", tab.title)
    print("page url:", tab.url)
    
    email = await tab.select("input[type=email]")

    # sometimes, email field is not shown, because phone is being asked instead
    # when this occurs, find the small text which says "use email instead"
    if not email:
        print("email field not found, taking screenshot...")
        screenshot = await tab.save_screenshot("/tmp/twitter_step1.png")
        print(f"screenshot saved: {screenshot}")
        
        # 尝试多种方式查找"use email"链接
        use_mail_instead = await tab.find("use email instead")
        if not use_mail_instead:
            print("trying 'use email' instead...")
            use_mail_instead = await tab.find("use email")
        if not use_mail_instead:
            print("trying 'email' instead...")
            use_mail_instead = await tab.find("email", best_match=True)
        
        if not use_mail_instead:
            print("'use email' button not found, taking another screenshot...")
            screenshot = await tab.save_screenshot("/tmp/twitter_step2.png")
            print(f"screenshot saved: {screenshot}")
            print("page title:", tab.title)
            print("page url:", tab.url)
            # 尝试找电话字段，看看是否在电话流程
            phone_input = await tab.select("input[type=tel]")
            if phone_input:
                print("Found phone input instead, attempting to find alternative...")
            raise Exception("Cannot find 'use email instead' button")
        # and click it
        await use_mail_instead.click()

        # now find the email field again
        email = await tab.select("input[type=email]")

    randstr = lambda k: "".join(random.choices(string.ascii_letters, k=k))

    # send keys to email field
    print('filling in the "email" input field')
    await email.send_keys("".join([randstr(8), "@", randstr(8), ".com"]))

    # find the name input field
    print("finding the name input field")
    name = await tab.select("input[type=text]")

    # again, send random text
    print('filling in the "name" input field')
    await name.send_keys(randstr(8))

    # since there are 3 select fields on the tab, we can use unpacking
    # to assign each field
    print('finding the "month" , "day" and "year" fields in 1 go')
    sel_month, sel_day, sel_year = await tab.select_all("select")

    # await sel_month.focus()
    print('filling in the "month" input field')
    await sel_month.send_keys(months[random.randint(0, 11)].title())

    # await sel_day.focus()
    # i don't want to bother with month-lengths and leap years
    print('filling in the "day" input field')
    await sel_day.send_keys(str(random.randint(0, 28)))

    # await sel_year.focus()
    # i don't want to bother with age restrictions
    print('filling in the "year" input field')
    await sel_year.send_keys(str(random.randint(1980, 2005)))

    await tab

    # let's handle the cookie nag as well
    cookie_bar_accept = await tab.find("accept all", best_match=True)
    if cookie_bar_accept:
        await cookie_bar_accept.click()

    await tab.sleep(1)

    next_btn = await tab.find(text="next", best_match=True)
    # for btn in reversed(next_btns):
    await next_btn.mouse_click()

    print("sleeping 2 seconds")
    await tab.sleep(2)  # visually see what part we're actually in

    print('finding "next" button')
    next_btn = await tab.find(text="next", best_match=True)
    print('clicking "next" button')
    try:
        # 尝试使用click()而不是mouse_click()
        await next_btn.click()
    except Exception as e:
        print(f"click() 失败: {e}")
        # 如果点击失败，尝试mouse_click
        try:
            await next_btn.mouse_click()
        except Exception as e2:
            print(f"mouse_click() 失败: {e2}")
            # 最后尝试直接执行JavaScript点击
            await tab.evaluate("document.querySelector('button[aria-label=\"Next\"]').click()")
    
    await tab.sleep(3)

    # just wait for some button, before we continue
    try:
        await tab.select("[role=button]")
    except:
        pass

    print('finding "sign up"  button')
    try:
        sign_up_btn = await tab.find("Sign up", best_match=True)
        # we need the second one
        print('clicking "sign up"  button')
        await sign_up_btn.click()
    except Exception as e:
        print(f"找不到Sign up按钮: {e}")

    print('the rest of the "implementation" is out of scope')
    # further implementation outside of scope
    await tab.sleep(10)

    # verification code per mail


if __name__ == "__main__":
    # since asyncio.run never worked (for me)
    # i use
    uc.loop().run_until_complete(main())
