#!/usr/bin/env python3
"""
抖音天气私信 - 天气获取脚本
获取指定城市的天气信息（增强版）
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime

def get_weather_wttr(city: str) -> dict:
    """通过 wttr.in 获取天气信息（完整数据）"""
    try:
        # wttr.in API - 获取完整数据
        url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1&lang=zh"
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        current = data.get('current_condition', [{}])[0]
        weather = data.get('weather', [{}])[0]
        
        # 获取天气状况
        condition = current.get('lang_zh', [{}])[0].get('value', 
                   current.get('weatherDesc', [{}])[0].get('value', '未知'))
        
        # 紫外线指数
        uv_index = current.get('uvIndex', 'N/A')
        
        # 体感温度
        feels_like = current.get('FeelsLikeC', current.get('temp_C', 'N/A'))
        
        # 能见度
        visibility = current.get('visibility', 'N/A')
        
        # 气压
        pressure = current.get('pressure', 'N/A')
        
        # 风向
        wind_dir = current.get('winddir16Point', 'N/A')
        
        return {
            'city': city,
            'date': datetime.now().strftime('%m月%d日'),
            'temperature': int(current.get('temp_C', 0)),
            'condition': condition,
            'feels_like': int(feels_like) if feels_like != 'N/A' else 'N/A',
            'high': int(weather.get('maxtempC', 0)),
            'low': int(weather.get('mintempC', 0)),
            'humidity': int(current.get('humidity', 0)),
            'wind_speed': int(current.get('windspeedKmph', 0)),
            'wind_dir': wind_dir,
            'uv_index': uv_index,
            'visibility': visibility,
            'pressure': pressure,
            'success': True
        }
    except Exception as e:
        return {
            'city': city,
            'error': str(e),
            'success': False
        }

def get_weather_openmeteo(city: str) -> dict:
    """通过 Open-Meteo 获取天气（需要城市坐标）"""
    # 常用城市坐标
    city_coords = {
        '杭州': (30.04, 120.20),
        '青岛': (36.07, 120.38),
        '胶州': (36.26, 120.00),
        '临沂': (35.10, 118.35),
        '兰陵': (34.85, 118.08),
        '菏泽': (35.24, 115.48),
        '北京': (39.90, 116.41),
        '上海': (31.23, 121.47),
        '广州': (23.13, 113.26),
        '深圳': (22.54, 114.06),
        '济南': (36.65, 117.12),
        '烟台': (37.54, 121.39),
        '威海': (37.51, 122.12),
        '潍坊': (36.71, 119.10),
        '淄博': (36.81, 118.05),
        '济宁': (35.41, 116.59),
        '德州': (37.45, 116.31),
        '聊城': (36.45, 115.99),
        '滨州': (37.38, 118.02),
        '东营': (37.46, 118.49),
        '泰安': (36.19, 117.12),
        '枣庄': (34.81, 117.56),
        '日照': (35.42, 119.46),
        '莱芜': (36.21, 117.68),
        '南京': (32.06, 118.80),
        '苏州': (31.30, 120.62),
        '无锡': (31.49, 120.32),
        '常州': (31.81, 119.97),
        '宁波': (29.87, 121.55),
        '温州': (28.00, 120.67),
        '嘉兴': (30.75, 120.76),
        '湖州': (30.87, 120.09),
        '绍兴': (30.00, 120.83),
        '金华': (29.08, 119.65),
        '衢州': (28.97, 118.88),
        '舟山': (30.01, 122.21),
        '台州': (28.66, 121.43),
        '丽水': (28.45, 119.92),
    }
    
    # 尝试匹配城市名
    coords = None
    matched_city = None
    for name, c in city_coords.items():
        if name in city:
            coords = c
            matched_city = name
            break
    
    if not coords:
        return {
            'city': city,
            'error': f'未找到城市坐标: {city}',
            'success': False
        }
    
    try:
        # 请求完整数据
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={coords[0]}&longitude={coords[1]}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m"
            f"&daily=temperature_2m_max,temperature_2m_min,uv_index_max"
            f"&timezone=Asia/Shanghai"
        )
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        current = data.get('current', {})
        daily = data.get('daily', {})
        
        # 天气代码映射
        weather_codes = {
            0: '晴', 1: '少云', 2: '部分多云', 3: '多云',
            45: '雾', 48: '雾凇',
            51: '毛毛雨', 53: '毛毛雨', 55: '毛毛雨',
            56: '冻雨', 57: '冻雨',
            61: '小雨', 63: '中雨', 65: '大雨',
            66: '冻雨', 67: '冻雨',
            71: '小雪', 73: '中雪', 75: '大雪',
            77: '雪粒',
            80: '阵雨', 81: '阵雨', 82: '暴雨',
            85: '阵雪', 86: '阵雪',
            95: '雷暴', 96: '雷暴冰雹', 99: '强雷暴'
        }
        
        code = current.get('weather_code', 0)
        condition = weather_codes.get(code, '未知')
        
        # 风向转换
        wind_deg = current.get('wind_direction_10m', 0)
        wind_dirs = ['北', '东北', '东', '东南', '南', '西南', '西', '西北']
        wind_dir = wind_dirs[int((wind_deg + 22.5) % 360 / 45)]
        
        return {
            'city': matched_city or city,
            'date': datetime.now().strftime('%m月%d日'),
            'temperature': int(current.get('temperature_2m', 0)),
            'condition': condition,
            'feels_like': int(current.get('apparent_temperature', 0)),
            'high': int(daily.get('temperature_2m_max', [0])[0]),
            'low': int(daily.get('temperature_2m_min', [0])[0]),
            'humidity': int(current.get('relative_humidity_2m', 0)),
            'wind_speed': int(current.get('wind_speed_10m', 0)),
            'wind_dir': wind_dir,
            'uv_index': int(daily.get('uv_index_max', [0])[0]),
            'success': True
        }
    except Exception as e:
        return {
            'city': city,
            'error': str(e),
            'success': False
        }

def get_weather(city: str, source: str = 'openmeteo') -> dict:
    """获取天气信息（统一入口）"""
    if source == 'wttr':
        return get_weather_wttr(city)
    else:
        return get_weather_openmeteo(city)

def main():
    parser = argparse.ArgumentParser(description='获取城市天气信息')
    parser.add_argument('--city', '-c', required=True, help='城市名称')
    parser.add_argument('--source', '-s', choices=['wttr', 'openmeteo'], default='openmeteo', help='天气数据源')
    parser.add_argument('--output', '-o', choices=['json', 'text'], default='json', help='输出格式')
    args = parser.parse_args()
    
    weather = get_weather(args.city, args.source)
    
    if args.output == 'json':
        print(json.dumps(weather, ensure_ascii=False, indent=2))
    else:
        if not weather.get('success'):
            print(f"❌ 获取失败: {weather.get('error')}")
            return
        
        print(f"🌤️ {weather['city']}今日天气 ({weather['date']})")
        print()
        print(f"当前: {weather['temperature']}°C {weather['condition']}")
        print(f"体感温度: {weather['feels_like']}°C")
        print(f"湿度: {weather['humidity']}%")
        print(f"风速: {weather['wind_speed']} km/h")
        print(f"紫外线指数: {weather['uv_index']}")
        print()
        print(f"今日气温: {weather['low']}°C - {weather['high']}°C")

if __name__ == '__main__':
    main()
