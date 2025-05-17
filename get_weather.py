import requests
import json

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

def send(a):
    webhook = config["webhook"]

    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "天气",
            "text": a
        },
        "at": {
            "atMobiles": [],
            "isAtAll": False
        }
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook, headers=headers, data=json.dumps(data))
    print(response.text)

def format_weather_markdown(data):
    """将天气数据转换为Markdown格式"""
    if data.get('error_code') != 0:
        return f"**获取天气数据失败**: {data.get('reason', '未知错误')}"
    
    result = data['result']
    city = result['city']
    realtime = result['realtime']
    future = result['future']
    
    markdown = [
        f"# {city}天气预报",
        "",
        "## 实时天气",
        f"- **天气状况**: {realtime['info']}",
        f"- **温度**: {realtime['temperature']}℃",
        f"- **风向/风力**: {realtime['direct']} {realtime['power']}",
        f"- **湿度**: {realtime['humidity']}%",
        f"- **空气质量指数(AQI)**: {realtime['aqi']}",
        "",
        "## 未来五天预报",
        "| 日期 | 白天/夜间 | 天气 | 温度 | 风向 |",
        "|------|----------|------|------|------|"
    ]
    
    for day in future:
        markdown.append(
            f"| {day['date']} | "
            f"白天: {day['weather'].split('转')[0]} / 夜间: {day['weather'].split('转')[-1]} | "
            f"{day['weather']} | "
            f"{day['temperature']} | "
            f"{day['direct']} |"
        )
    
    markdown.extend([
        "",
        f"*数据更新时间: {day['date']}*",
        "[查看更多天气详情](https://www.weather.com.cn)"
    ])
    
    return "\n".join(markdown)

# 1213-根据城市查询天气 - 代码参考（根据实际业务情况修改）

# 基本参数配置
apiUrl = 'http://apis.juhe.cn/simpleWeather/query'  # 接口请求URL
apiKey = config["juhe_weather_key"]

# 接口请求入参配置
requestParams = {
    'key': apiKey,
    'city': '上海',
}

# 发起接口网络请求
response = requests.get(apiUrl, params=requestParams)

# 解析响应结果
if response.status_code == 200:
    responseResult = response.json()

    weather_markdown = format_weather_markdown(responseResult)

    send(weather_markdown)
else:
    # 网络异常等因素，解析结果异常。可依据业务逻辑自行处理。
    print('请求异常')
    