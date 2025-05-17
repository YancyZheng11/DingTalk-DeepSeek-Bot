import requests
import json

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

apiUrl = 'http://v.juhe.cn/toutiao/index'  # 接口请求URL
apiKey = config["juhe_news_key"]

# 接口请求入参配置
requestParams = {
    'key': apiKey,
    'type': '',
    'page': '',
    'page_size': '5',
    'is_filter': '',
}

# 发起接口网络请求
response = requests.get(apiUrl, params=requestParams)

# 解析响应结果
if response.status_code == 200:
    responseResult = response.json()
    # 网络请求成功。可依据业务逻辑和接口文档说明自行处理。
    print(responseResult)
else:
    # 网络异常等因素，解析结果异常。可依据业务逻辑自行处理。
    print('请求异常')

def format_news_to_markdown(a):
    """将新闻数据格式化为Markdown"""
    markdown_output = []
    
    # 添加标题和基本信息
    markdown_output.append("# 每日新闻摘要")
    markdown_output.append(f"**更新时间**: {a['result']['data'][0]['date'][:10]}\n")
    
    # 遍历每条新闻
    for i, news in enumerate(a['result']['data'], 1):
        markdown_output.append(f"## {i}. {news['title']}")
        markdown_output.append(f"- **时间**: {news['date']}")
        markdown_output.append(f"- **来源**: {news['author_name']} ({news['category']})")
        
        # 如果有缩略图
        if news.get('thumbnail_pic_s'):
            if isinstance(news['thumbnail_pic_s'], list):
                for img in news['thumbnail_pic_s']:
                    if img:  # 确保图片URL不为空
                        markdown_output.append(f"![图片]({img})")
            elif news['thumbnail_pic_s']:  # 单个图片URL
                markdown_output.append(f"![图片]({news['thumbnail_pic_s']})")
        
        markdown_output.append(f"- [阅读原文]({news['url']})\n")
    
    # 添加页脚信息
    markdown_output.append(f"共 {len(a['result']['data'])} 条新闻 | 当前第 {a['result']['page']} 页")
    return "\n".join(markdown_output)

def send(a):
    webhook = config["webhook"]

    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "新闻",
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

# 生成Markdown
markdown_result = format_news_to_markdown(responseResult)

send(markdown_result)
