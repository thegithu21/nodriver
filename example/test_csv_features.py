#!/usr/bin/env python3
"""
测试脚本：验证新增的 CSV 导出和邮箱截图功能
"""

import os
import csv
import json
from pathlib import Path
from datetime import datetime


def print_section(title):
    """打印分割线"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def check_csv_file(csv_path):
    """检查 CSV 文件"""
    if not os.path.exists(csv_path):
        print(f"⚠️  CSV 文件不存在: {csv_path}")
        return False
    
    print(f"✅ CSV 文件存在: {csv_path}")
    print(f"   文件大小: {os.path.getsize(csv_path)} 字节")
    
    # 读取并显示内容
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if rows:
                print(f"   📊 记录数: {len(rows)}")
                print(f"\n   📋 CSV 内容预览:")
                print(f"   {'-'*60}")
                
                # 显示表头
                headers = list(rows[0].keys())
                print(f"   {'Email':<30} | {'Password':<15} | {'Name':<15}")
                print(f"   {'-'*60}")
                
                # 显示前 5 条记录
                for i, row in enumerate(rows[:5]):
                    email = row.get('Email', '')[:30]
                    password = '*' * len(row.get('Password', ''))
                    name = row.get('Name', '')[:15]
                    print(f"   {email:<30} | {password:<15} | {name:<15}")
                
                if len(rows) > 5:
                    print(f"   ... 还有 {len(rows)-5} 条记录")
                print(f"   {'-'*60}\n")
            else:
                print(f"   ⚠️  CSV 文件为空")
            
            return len(rows) > 0
    except Exception as e:
        print(f"   ❌ 读取 CSV 失败: {e}")
        return False


def check_json_files(accounts_dir):
    """检查 JSON 账户文件"""
    if not os.path.exists(accounts_dir):
        print(f"⚠️  账户目录不存在: {accounts_dir}")
        return False
    
    json_files = list(Path(accounts_dir).glob('*.json'))
    
    if not json_files:
        print(f"⚠️  未找到 JSON 文件")
        return False
    
    print(f"✅ 找到 {len(json_files)} 个 JSON 文件:")
    
    for json_file in json_files[-5:]:  # 显示最后 5 个
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"\n   📄 {json_file.name}")
                print(f"      邮箱: {data.get('email', 'N/A')}")
                print(f"      名字: {data.get('name', 'N/A')}")
                print(f"      生日: {data.get('birth_date', 'N/A')}")
                print(f"      状态: {data.get('status', 'N/A')}")
        except Exception as e:
            print(f"   ❌ 读取失败: {e}")
    
    if len(json_files) > 5:
        print(f"\n   ... 还有 {len(json_files)-5} 个文件")
    
    return True


def check_screenshots(screenshots_dir):
    """检查截图文件"""
    if not os.path.exists(screenshots_dir):
        print(f"⚠️  截图目录不存在: {screenshots_dir}")
        return False
    
    screenshot_files = list(Path(screenshots_dir).glob('*.png'))
    
    if not screenshot_files:
        print(f"⚠️  未找到任何截图")
        return False
    
    print(f"✅ 找到 {len(screenshot_files)} 张截图:")
    
    for screenshot in sorted(screenshot_files)[-5:]:
        size_kb = os.path.getsize(screenshot) / 1024
        print(f"   📸 {screenshot.name:<40} ({size_kb:.1f} KB)")
    
    if len(screenshot_files) > 5:
        print(f"   ... 还有 {len(screenshot_files)-5} 张截图")
    
    return True


def check_inbox_screenshots(inbox_dir):
    """检查邮箱截图"""
    if not os.path.exists(inbox_dir):
        print(f"⚠️  邮箱截图目录不存在: {inbox_dir}")
        print(f"   提示: 这是正常的，需要成功登录邮箱才会生成")
        return None  # 返回 None 表示可选的
    
    inbox_files = list(Path(inbox_dir).glob('*.png'))
    
    if not inbox_files:
        print(f"⚠️  未找到邮箱截图")
        print(f"   提示: 邮箱登录可能失败或未完成")
        return False
    
    print(f"✅ 找到 {len(inbox_files)} 张邮箱截图:")
    
    for screenshot in sorted(inbox_files):
        size_kb = os.path.getsize(screenshot) / 1024
        print(f"   📧 {screenshot.name:<40} ({size_kb:.1f} KB)")
    
    return True


def check_gitignore():
    """检查 .gitignore 配置"""
    gitignore_path = "/workspaces/nodriver/.gitignore"
    
    if not os.path.exists(gitignore_path):
        print(f"❌ .gitignore 文件不存在")
        return False
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含 CSV 相关的忽略规则
    csv_patterns = [
        'csv_accounts/',
        '*.csv',
        'inbox_screenshots/'
    ]
    
    found_patterns = []
    for pattern in csv_patterns:
        if pattern in content:
            found_patterns.append(pattern)
    
    if found_patterns:
        print(f"✅ .gitignore 已正确配置")
        print(f"   已添加以下忽略规则:")
        for pattern in found_patterns:
            print(f"   • {pattern}")
        return True
    else:
        print(f"❌ .gitignore 缺少必要的忽略规则")
        return False


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  Outlook 邮箱注册脚本 - 功能验证测试")
    print("="*70)
    
    # 定义要检查的目录
    simple_version_paths = {
        'base': '/tmp/outlook_registration',
        'csv': '/tmp/outlook_registration/csv_accounts/accounts.csv',
        'accounts': '/tmp/outlook_registration/accounts',
        'screenshots': '/tmp/outlook_registration/screenshots',
        'inbox_screenshots': '/tmp/outlook_registration/inbox_screenshots',
    }
    
    full_version_paths = {
        'base': '/workspaces/nodriver/debug_output',
        'csv': '/workspaces/nodriver/debug_output/csv_accounts/accounts.csv',
        'accounts': '/workspaces/nodriver/debug_output/accounts',
        'screenshots': '/workspaces/nodriver/debug_output/screenshots',
        'inbox_screenshots': '/workspaces/nodriver/debug_output/inbox_screenshots',
    }
    
    # 检查 .gitignore
    print_section("1. Git 安全性检查")
    gitignore_ok = check_gitignore()
    
    # 检查简化版本
    print_section("2. 简化版本检查")
    print(f"基础目录: {simple_version_paths['base']}\n")
    
    if os.path.exists(simple_version_paths['base']):
        csv_ok_simple = check_csv_file(simple_version_paths['csv'])
        print()
        json_ok_simple = check_json_files(simple_version_paths['accounts'])
        print()
        ss_ok_simple = check_screenshots(simple_version_paths['screenshots'])
        print()
        inbox_ok_simple = check_inbox_screenshots(simple_version_paths['inbox_screenshots'])
    else:
        print(f"ℹ️  简化版本还未运行过（目录不存在）")
        print(f"   运行命令: python example/register_outlook_simple.py")
        csv_ok_simple = json_ok_simple = ss_ok_simple = inbox_ok_simple = False
    
    # 检查完整版本
    print_section("3. 完整版本检查")
    print(f"基础目录: {full_version_paths['base']}\n")
    
    if os.path.exists(full_version_paths['base']):
        csv_ok_full = check_csv_file(full_version_paths['csv'])
        print()
        json_ok_full = check_json_files(full_version_paths['accounts'])
        print()
        ss_ok_full = check_screenshots(full_version_paths['screenshots'])
        print()
        inbox_ok_full = check_inbox_screenshots(full_version_paths['inbox_screenshots'])
    else:
        print(f"ℹ️  完整版本还未运行过（目录不存在）")
        print(f"   运行命令: python example/register_outlook_account.py")
        csv_ok_full = json_ok_full = ss_ok_full = inbox_ok_full = False
    
    # 总结
    print_section("📊 测试总结")
    
    print("功能检查结果:")
    print(f"  • Git 安全性 (.gitignore): {'✅ 通过' if gitignore_ok else '❌ 失败'}")
    print(f"  • CSV 导出 (简化版):      {'✅ 通过' if csv_ok_simple else '⏳ 未测试'}")
    print(f"  • CSV 导出 (完整版):      {'✅ 通过' if csv_ok_full else '⏳ 未测试'}")
    print(f"  • JSON 保存 (简化版):     {'✅ 通过' if json_ok_simple else '⏳ 未测试'}")
    print(f"  • JSON 保存 (完整版):     {'✅ 通过' if json_ok_full else '⏳ 未测试'}")
    print(f"  • 注册截图 (简化版):     {'✅ 通过' if ss_ok_simple else '⏳ 未测试'}")
    print(f"  • 注册截图 (完整版):     {'✅ 通过' if ss_ok_full else '⏳ 未测试'}")
    print(f"  • 邮箱截图 (简化版):     {'✅ 通过' if inbox_ok_simple else '⏳ 未测试' if inbox_ok_simple is None else '⚠️  登录失败'}")
    print(f"  • 邮箱截图 (完整版):     {'✅ 通过' if inbox_ok_full else '⏳ 未测试' if inbox_ok_full is None else '⚠️  登录失败'}")
    
    print("\n")
    print("📝 说明:")
    print("  • ✅ 通过: 功能已实现并产生了文件")
    print("  • ⏳ 未测试: 相应的脚本还未运行过")
    print("  • ⚠️  登录失败: 邮箱登录可能遇到问题（需要验证码等）")
    print("  • ℹ️  信息: 参考性提示")
    
    print("\n")
    print("🚀 快速开始:")
    print("  1. 运行简化版本:")
    print("     $ python example/register_outlook_simple.py")
    print()
    print("  2. 查看生成的 CSV:")
    print("     $ cat /tmp/outlook_registration/csv_accounts/accounts.csv")
    print()
    print("  3. 查看邮箱截图:")
    print("     $ ls /tmp/outlook_registration/inbox_screenshots/")
    print()
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
