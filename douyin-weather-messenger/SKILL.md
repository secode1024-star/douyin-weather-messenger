---
name: douyin-weather-messenger
description: |
  抖音天气私信技能。自动获取好友所在城市的天气信息，通过抖音网页版向好友发送天气私信。
  支持智能位置检测：自动识别好友最近消息中提到的位置变化，发送对应城市天气。
  触发词：抖音天气、douyin weather、天气私信、抖音私信天气、发送天气、查天气发私信。
metadata:
  openclaw:
    emoji: "🌤️"
---

# 抖音天气私信技能

## ⚠️ 核心规定（必须遵守）

### 规定一：使用抖音号搜索好友
搜索好友时**必须使用抖音号（douyin_id）**，不能使用昵称。
- ✅ 正确：搜索框输入 `zhanglinyuan1`、`nxx_0430end`
- ❌ 错误：搜索框输入 `张琳媛`、`朱涛`
- 原因：昵称可能重复，抖音号唯一

### 规定二：位置检测后替换发送城市
检测到好友位置变化后，**立即替换配置中的城市**：
- 配置城市：青岛胶州
- 检测到位置：济南（好友说"我现在在济南"）
- **实际发送：济南天气** ✅

### 规定三：每次执行前检查好友位置
**每次发送前都要检查好友最近消息**，确认当前位置：
1. 打开好友聊天窗口
2. 读取最近 24 小时消息
3. 检测位置关键词
4. 确定发送城市后获取天气

---

## 功能概述

自动为抖音好友发送天气私信：
1. 获取每位好友所在城市的实时天气
2. 智能检测好友位置变化（从聊天记录中识别）
3. 打开抖音网页版（复用登录态）
4. 进入好友私信页面
5. 发送天气信息私信

---

## 核心流程

### Step 1：读取好友配置
```python
# 从 config/friends.json 读取
friend = {
    "name": "张琳媛",
    "douyin_id": "zhanglinyuan1",  # 用于搜索
    "city": "青岛胶州"              # 默认城市，可能被位置检测替换
}
```

### Step 2：搜索好友（必须用抖音号）
```python
# 在搜索框输入抖音号（不是昵称！）
browser(action="type", ref="搜索框", text="zhanglinyuan1")
browser(action="press", key="Enter")
```

### Step 3：进入聊天并检查位置
```python
# 点击搜索结果进入好友主页或聊天
browser(action="click", selector="text=zhanglinyuan1")

# 检查最近消息中的位置关键词
# 例如："我现在在济南"、"来杭州出差了"
detected_city = check_friend_location()
```

### Step 4：确定发送城市
```python
# 优先使用检测到的位置
if detected_city:
    send_city = detected_city  # 规定二：替换
else:
    send_city = friend["city"]  # 使用配置中的默认城市
```

### Step 5：获取天气并发送
```python
weather = get_weather(send_city)
message = format_message(weather)
browser(action="type", ref="输入框", text=message)
browser(action="press", key="Enter")
```

---

## 智能位置检测

### 检测模式（正则表达式）

```python
LOCATION_PATTERNS = [
    r"我现在在(.+?)(?:了|呢|，|。|$)",
    r"我在(.+?)(?:了|呢|，|。|$)",
    r"来(.+?)(?:了|出差|旅游|玩)",
    r"去(.+?)(?:了|出差|旅游|玩)",
    r"坐标[：:]\s*(.+?)(?:，|。|$)",
    r"已到(.+?)(?:了|，|。|$)",
    r"目前[在]?(.+?)(?:，|。|$)",
]

def detect_location(messages: list) -> dict:
    """
    检测好友最近消息中的位置变化
    
    返回: {
        "detected": True/False,
        "city": "济南",
        "matched_text": "我现在在济南",
        "confidence": 0.95
    }
    """
    pass
```

### 置信度规则
- 精确匹配（"我现在在XX"）：置信度 0.95
- 模糊匹配（"去XX了"）：置信度 0.80
- 置信度 > 0.7：切换城市

### 城市名标准化
```python
# 常见城市别名映射
CITY_ALIASES = {
    "济南": ["济南", "济南市"],
    "青岛": ["青岛", "青岛市", "胶州", "青岛胶州"],
    "临沂": ["临沂", "临沂市", "兰陵", "临沂兰陵"],
    "杭州": ["杭州", "杭州市"],
    "菏泽": ["菏泽", "菏泽市"],
}
```

---

## 私信模板

### 标准模板

```
🌤️ {城市}今日天气 ({日期})

当前: {温度}°C {天气状况}
体感温度: {体感温度}°C
湿度: {湿度}%
风速: {风速} km/h
紫外线指数: {紫外线}

今日气温: {最低温}°C - {最高温}°C

温馨提示：
1. {提示1}
2. {提示2}
3. {提示3}

祝你今天开心！😊
```

### 天气图标映射

| 天气 | 图标 |
|------|------|
| 晴 | ☀️ |
| 少云/多云 | 🌤️ |
| 阴 | ☁️ |
| 小雨 | 🌧️ |
| 中雨/大雨 | ⛈️ |
| 雪 | ❄️ |
| 雾/霾 | 🌫️ |

---

## 完整执行示例

```python
# 1. 读取好友配置
friend = {"name": "张琳媛", "douyin_id": "zhanglinyuan1", "city": "青岛胶州"}

# 2. 搜索好友（用抖音号！）
browser(action="type", ref="搜索框", text="zhanglinyuan1")  # ✅ 正确
# browser(action="type", ref="搜索框", text="张琳媛")       # ❌ 错误

# 3. 进入聊天检查位置
# 好友最近消息："我现在在济南"
detected = detect_location(recent_messages)
# detected = {"detected": True, "city": "济南", "confidence": 0.95}

# 4. 确定发送城市
if detected["detected"] and detected["confidence"] > 0.7:
    send_city = detected["city"]  # "济南" - 替换配置中的"青岛胶州"
else:
    send_city = friend["city"]

# 5. 获取天气并发送
weather = get_weather(send_city)  # 济南天气
message = format_message(weather)
browser(action="type", ref="输入框", text=message)
browser(action="press", key="Enter")
```

---

## 配置文件

### 好友列表 (`config/friends.json`)

```json
{
  "friends": [
    {
      "name": "张琳媛",
      "douyin_id": "zhanglinyuan1",
      "city": "青岛胶州"
    },
    {
      "name": "朱涛",
      "douyin_id": "nxx_0430end",
      "city": "临沂兰陵"
    },
    {
      "name": "王懋荣",
      "douyin_id": "0226WMR",
      "city": "临沂兰陵"
    },
    {
      "name": "王国蕊",
      "douyin_id": "ysvsghdbsxakg",
      "city": "杭州"
    },
    {
      "name": "赵子鸣",
      "douyin_id": "shenghuozhu8",
      "city": "菏泽"
    }
  ]
}
```

### 抖音账号 (`config/account.json`)

```json
{
  "douyin_id": "secode1024",
  "username": "955"
}
```

---

## 浏览器操作要点

### 搜索好友（关键步骤）
```python
# 步骤1：点击搜索框
browser(action="click", ref="搜索框")

# 步骤2：输入抖音号（不是昵称！）
browser(action="type", text="zhanglinyuan1")  # ✅

# 步骤3：按回车搜索
browser(action="press", key="Enter")

# 步骤4：点击搜索结果中的用户
browser(action="click", selector="text=zhanglinyuan1")
```

### 获取元素 ref
```python
snapshot = browser(action="snapshot", refs="aria")
# 从快照中找到元素的 ref
```

---

## 天气数据源

### wttr.in（推荐）
```bash
curl "https://wttr.in/济南?format=j1"
```

### Open-Meteo
```bash
curl "https://api.open-meteo.com/v1/forecast?latitude=36.65&longitude=117.12&current=temperature_2m"
```

---

## 输出报告

```markdown
# 📤 抖音天气私信发送报告

**执行时间**: 2026-04-08 18:02

## 发送结果

| 好友 | 配置城市 | 检测位置 | 实际发送 | 状态 |
|------|----------|----------|----------|------|
| 张琳媛 | 青岛胶州 | 济南 | 济南 | ✅ 已发送 |
| 朱涛 | 临沂兰陵 | - | 临沂兰陵 | ✅ 已发送 |
| 王懋荣 | 临沂兰陵 | - | 临沂兰陵 | ✅ 已发送 |
| 王国蕊 | 杭州 | - | 杭州 | ✅ 已发送 |
| 赵子鸣 | 菏泽 | - | 菏泽 | ✅ 已发送 |

## 位置检测详情
- 张琳媛: 检测到 "我现在在济南" → 替换为济南天气

## 统计
- 总计：5 位好友
- 已发送：5 位
- 位置替换：1 位
```

---

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 搜索不到好友 | 用昵称搜索 | 使用抖音号搜索 |
| 发错城市天气 | 未检查位置 | 每次发送前检查最近消息 |
| 元素定位失败 | 页面刷新后 ref 变化 | 重新获取快照 |
| 私信发送失败 | 未关注/被限制 | 确认好友关系 |

---

## 文件结构

```
douyin-weather-messenger/
├── SKILL.md                 # 本文件
├── config/
│   ├── friends.json         # 好友列表（含抖音号）
│   └── account.json         # 账号配置
└── scripts/
    ├── get_weather.py       # 天气获取
    ├── send_message.py      # 主发送脚本
    └── location_parser.py   # 位置检测
```

---

## 依赖技能

- `browser` — 浏览器自动化（OpenClaw 内置）
- `weather-advisor` — 天气查询（可选）
