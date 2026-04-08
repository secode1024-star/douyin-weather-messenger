#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音天气私信 - 主发送脚本
自动获取天气并通过抖音发送私信
"""

import argparse
import io
import sys

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 获取脚本目录
SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_DIR = SCRIPT_DIR.parent / 'config'

def load_friends():
    """加载好友列表"""
    config_file = CONFIG_DIR / 'friends.json'
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return None
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_account():
    """加载账号配置"""
    config_file = CONFIG_DIR / 'account.json'
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return None
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_weather(city: str) -> dict:
    """获取天气信息"""
    sys.path.insert(0, str(SCRIPT_DIR))
    from get_weather import get_weather as _get_weather
    return _get_weather(city, 'openmeteo')

def get_clothing_and_tips(weather: dict) -> tuple:
    """根据天气生成穿衣建议和注意事项"""
    clothing = []
    tips = []
    
    condition = weather.get('condition', '')
    temp = weather.get('temperature', 0)
    low = weather.get('low', 0)
    high = weather.get('high', 0)
    wind = weather.get('wind_speed', 0)
    uv = weather.get('uv_index', 0)
    humidity = weather.get('humidity', 0)
    
    # === 穿衣建议 ===
    # 根据最高温度和最低温度综合判断
    avg_temp = (low + high) / 2
    
    if high >= 30:
        clothing.append("穿短袖短裤，轻薄透气 🩳")
    elif high >= 25:
        clothing.append("穿短袖或薄长袖，舒适为主 👕")
    elif high >= 20:
        if low < 15:
            clothing.append("早晚温差大，带件薄外套 🧥")
        else:
            clothing.append("穿长袖或薄外套，温度适中 👔")
    elif high >= 15:
        if low < 10:
            clothing.append("早晚较凉，穿外套刚刚好 🧥")
        else:
            clothing.append("穿外套或卫衣，温度适中 🧥")
    elif high >= 10:
        clothing.append("穿厚外套或毛衣，注意保暖 🧥")
    elif high >= 5:
        clothing.append("穿棉衣或羽绒服，注意保暖 🧥")
    else:
        clothing.append("穿厚羽绒服，做好保暖措施 🧥")
    
    # === 注意事项 ===
    # 天气状况
    if '雨' in condition or '小雨' in condition:
        tips.append("出门记得带伞 🌂")
    elif '中雨' in condition or '大雨' in condition or '暴雨' in condition:
        tips.append("雨势较大，出门带伞注意安全 🌂")
    elif '雪' in condition:
        tips.append("路面可能湿滑，注意出行安全 ❄️")
    elif '雾' in condition or '霾' in condition:
        tips.append("能见度低，出行注意安全 🌫️")
    
    # 紫外线
    if uv >= 8:
        tips.append("紫外线很强，做好防晒措施 🧴")
    elif uv >= 6:
        tips.append("紫外线较强，注意防晒 🧴")
    elif uv >= 3:
        tips.append("紫外线中等，适当防晒")
    
    # 风力
    if wind >= 30:
        tips.append("风力很大，注意防风 🌬️")
    elif wind >= 20:
        tips.append("风力较大，出门注意防风 💨")
    
    # 温度相关
    if high >= 35:
        tips.append("高温天气，注意防暑降温 🍦")
    elif low <= 0:
        tips.append("气温很低，注意防寒保暖 ⛄")
    
    # 湿度
    if humidity < 30:
        tips.append("空气干燥，多喝水 💧")
    elif humidity > 85:
        tips.append("空气潮湿，体感可能闷热")
    
    # 空气质量提示（如果有雾霾）
    if '霾' in condition:
        tips.append("空气质量差，建议戴口罩 😷")
    
    return clothing, tips

def format_message(weather: dict) -> str:
    """格式化私信内容（新模板 - 简洁版）"""
    
    clothing, tips = get_clothing_and_tips(weather)
    
    # 获取天气图标
    condition = weather.get('condition', '')
    if '雨' in condition:
        weather_icon = '🌧️'
    elif '雪' in condition:
        weather_icon = '❄️'
    elif '晴' in condition:
        weather_icon = '☀️'
    elif '多云' in condition or '阴' in condition:
        weather_icon = '⛅'
    elif '雾' in condition or '霾' in condition:
        weather_icon = '🌫️'
    else:
        weather_icon = '🌤️'
    
    # 构建消息
    lines = [
        f"{weather_icon} 今天{weather['city']}{weather['condition']}，温度{weather['low']}°C-{weather['high']}°C，阳光不错，心情也要美美的！",
        "",
        f"🌡️ 全天温度：{weather['low']}°C - {weather['high']}°C",
        f"💨 风力：{weather['wind_speed']} km/h",
        f"💧 湿度：{weather['humidity']}%",
        ""
    ]
    
    # 添加穿衣建议
    if clothing:
        lines.append(f"👕 穿衣建议：{clothing[0]}")
    
    # 添加注意事项
    if tips:
        lines.append("")
        lines.append("⚠️ 注意事项：")
        for tip in tips[:3]:  # 最多3条
            lines.append(f"  • {tip}")
    
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='抖音天气私信发送')
    parser.add_argument('--dry-run', action='store_true', help='仅打印消息，不实际发送')
    parser.add_argument('--friend', '-f', help='仅处理指定好友（姓名或抖音号）')
    parser.add_argument('--interval', '-i', type=int, default=5, help='发送间隔（秒）')
    parser.add_argument('--source', '-s', choices=['wttr', 'openmeteo'], default='openmeteo', help='天气数据源')
    args = parser.parse_args()
    
    # 加载配置
    friends_config = load_friends()
    account_config = load_account()
    
    if not friends_config or not account_config:
        sys.exit(1)
    
    friends = friends_config.get('friends', [])
    
    # 筛选指定好友
    if args.friend:
        friends = [f for f in friends if f['name'] == args.friend or f['douyin_id'] == args.friend]
        if not friends:
            print(f"❌ 未找到好友: {args.friend}")
            sys.exit(1)
    
    print(f"📋 抖音账号: {account_config['username']} (@{account_config['douyin_id']})")
    print(f"📋 待处理好友: {len(friends)} 位")
    print("-" * 50)
    
    results = []
    
    for i, friend in enumerate(friends, 1):
        print(f"\n[{i}/{len(friends)}] 处理: {friend['name']} (@{friend['douyin_id']})")
        
        # 获取天气
        print(f"  🌤️ 获取 {friend['city']} 天气...")
        
        sys.path.insert(0, str(SCRIPT_DIR))
        from get_weather import get_weather as _get_weather
        weather = _get_weather(friend['city'], args.source)
        
        if not weather.get('success'):
            print(f"  ❌ 天气获取失败: {weather.get('error')}")
            results.append({
                'friend': friend,
                'weather': None,
                'status': 'failed',
                'error': weather.get('error')
            })
            continue
        
        print(f"  ✅ 天气: {weather['temperature']}°C {weather['condition']}")
        
        # 格式化消息
        message = format_message(weather)
        print(f"\n  📝 私信内容:")
        for line in message.split('\n'):
            print(f"     {line}")
        
        if args.dry_run:
            print(f"\n  ⏭️ [DRY RUN] 跳过发送")
            results.append({
                'friend': friend,
                'weather': weather,
                'status': 'skipped'
            })
        else:
            # TODO: 实际发送逻辑（需要 browser-cdp）
            print(f"\n  📤 发送私信...")
            print(f"  ⚠️ 实际发送需要浏览器自动化，请使用 browser-cdp 技能")
            results.append({
                'friend': friend,
                'weather': weather,
                'status': 'pending'
            })
        
        # 发送间隔
        if i < len(friends) and not args.dry_run:
            print(f"\n  ⏳ 等待 {args.interval} 秒...")
            time.sleep(args.interval)
    
    # 输出报告
    print("\n" + "=" * 50)
    print("📊 发送报告")
    print("=" * 50)
    
    success = sum(1 for r in results if r['status'] == 'pending')
    failed = sum(1 for r in results if r['status'] == 'failed')
    skipped = sum(1 for r in results if r['status'] == 'skipped')
    
    print(f"总计: {len(results)} 位好友")
    print(f"成功: {success} 位")
    print(f"失败: {failed} 位")
    print(f"跳过: {skipped} 位")

if __name__ == '__main__':
    main()
