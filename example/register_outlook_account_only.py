#!/usr/bin/env python3
"""
Outlook 邮箱账户信息生成脚本（不含浏览器自动化）
生成有效的账户信息，保存到 CSV 和 JSON，供手动注册或批量创建
"""

import os
import json
import csv
import random
import string
from datetime import datetime
from pathlib import Path


# 配置
DEBUG_DIR = "/workspaces/nodriver/debug_output"
ACCOUNTS_DIR = os.path.join(DEBUG_DIR, "accounts")
CSV_DIR = os.path.join(DEBUG_DIR, "csv_accounts")
SCREENSHOTS_DIR = os.path.join(DEBUG_DIR, "screenshots")
CSV_FILE = os.path.join(CSV_DIR, "accounts.csv")

# 创建目录
for dir_path in [DEBUG_DIR, ACCOUNTS_DIR, CSV_DIR, SCREENSHOTS_DIR]:
    os.makedirs(dir_path, exist_ok=True)


def generate_random_email_base(length=12):
    """生成随机邮箱前缀"""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_random_password(length=16):
    """生成随机密码 - 需要包含大小写字母、数字和符号"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = []
    
    # 确保包含必要的字符类型
    password.append(random.choice(string.ascii_uppercase))
    password.append(random.choice(string.ascii_lowercase))
    password.append(random.choice(string.digits))
    password.append(random.choice("!@#$%^&*"))
    
    # 填充剩余长度
    for _ in range(length - 4):
        password.append(random.choice(chars))
    
    # 随机打乱
    random.shuffle(password)
    return "".join(password)


def generate_random_name():
    """生成随机名字"""
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Robert", "Lisa",
                   "James", "Mary", "William", "Patricia", "Richard", "Jennifer", "Charles", "Linda"]
    last_names = ["Smith", "Johnson", "Brown", "Taylor", "Williams", "Jones", "Garcia",
                  "Lee", "Miller", "Davis", "Wilson", "Moore", "Anderson", "Thomas"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_random_birth_date():
    """生成随机出生日期"""
    year = random.randint(1970, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # 避免月底问题
    return f"{month:02d}/{day:02d}/{year}"


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
        
        return True
    except Exception as e:
        print(f"   ❌ CSV 保存失败: {e}")
        return False


def save_to_json(email, password, name, birth_date):
    """将账户信息保存到 JSON 文件"""
    try:
        account_info = {
            "email": email,
            "password": password,
            "name": name,
            "birth_date": birth_date,
            "created_at": datetime.now().isoformat(),
            "status": "generated",
            "notes": "账户信息已生成，需要手动在 Outlook 注册或通过自动化工具完成注册"
        }
        
        account_file = os.path.join(ACCOUNTS_DIR, f"outlook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(account_file, 'w', encoding='utf-8') as f:
            json.dump(account_info, f, indent=2, ensure_ascii=False)
        
        return account_file
    except Exception as e:
        print(f"   ❌ JSON 保存失败: {e}")
        return None


def generate_outlook_account():
    """生成 Outlook 账户信息"""
    email = f"{generate_random_email_base()}@outlook.com"
    password = generate_random_password()
    name = generate_random_name()
    birth_date = generate_random_birth_date()
    
    print(f"\n{'='*60}")
    print(f"Outlook 邮箱账户信息生成")
    print(f"{'='*60}")
    print(f"\n📝 生成的账户信息:")
    print(f"   邮箱: {email}")
    print(f"   密码: {password}")
    print(f"   名字: {name}")
    print(f"   生日: {birth_date}\n")
    
    # 保存到 JSON
    print(f"💾 保存账户信息到 JSON...")
    json_file = save_to_json(email, password, name, birth_date)
    if json_file:
        print(f"   ✓ JSON 已保存: {json_file}")
    
    # 保存到 CSV
    print(f"📊 保存账户信息到 CSV...")
    if save_to_csv(email, password, name, birth_date):
        print(f"   ✓ CSV 已保存: {CSV_FILE}")
    
    print(f"\n✅ 账户信息已生成!")
    print(f"\n📁 文件位置:")
    print(f"   CSV: {CSV_FILE}")
    print(f"   JSON: {ACCOUNTS_DIR}/")
    print(f"\n📋 说明:")
    print(f"   1. 上述账户信息已保存到 CSV 和 JSON")
    print(f"   2. 请手动在 https://signup.live.com 注册")
    print(f"   3. 或使用浏览器自动化工具完成注册")
    print(f"   4. 注册完成后，使用上述邮箱和密码登录")
    
    return {
        "email": email,
        "password": password,
        "name": name,
        "birth_date": birth_date
    }


def main():
    """主函数"""
    try:
        account = generate_outlook_account()
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断了生成过程")
        return 1
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
