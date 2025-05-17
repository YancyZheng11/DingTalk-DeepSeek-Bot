# DingTalk DeepSeek Bot 项目文档

## 项目概述

**dingtalk_deepseek** 是一个将钉钉机器人连接到 DeepSeek AI 和其他服务的集成项目，提供智能对话、天气查询、新闻摘要、井字棋游戏和AI图像生成功能，并具备对话历史记忆能力。

## 文件结构

```
dingtalk_deepseek/
├── config.json          # 配置文件（存储所有API密钥）
├── get_news.py         # 新闻获取模块
├── get_weather.py      # 天气获取模块
├── memory.json         # 对话历史存储（自动生成）
├── requirements.txt    # Python依赖库
├── run.py              # 主程序入口
├── scheduled.py        # 定时任务模块
├── text_to_image.py    # 图像生成模块
└── tic_tac_toe.py      # 井字棋游戏模块
```

## 配置说明

编辑 `config.json` 文件：

```json
{
    "webhook": "https://oapi.dingtalk.com/robot/send?access_token=your_dingtalk_token_here",
    "deepseek_key": "your_deepseek_api_key_here",
    "juhe_weather_key": "your_juhe_weather_api_key_here",
    "juhe_news_key": "your_juhe_news_api_key_here",
    "client_id": "your_dingtalk_client_id_here",
    "client_secret": "your_dingtalk_client_secret_here",
    "ali_key": "your_aliyun_api_key_here"
}
```

## 安装与运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python run.py
```

## 功能使用说明

### 基本命令

| 命令 | 功能 | 示例 |
|------|------|------|
| (任意消息) | 与DeepSeek AI对话 | "你好" |
| 天气 | 查询天气预报 | "天气" |
| 新闻 | 获取新闻摘要 | "新闻" |
| 井字棋 | 开始井字棋游戏 | "井字棋" |
| 生成图片 [描述] | AI生成图像 | "生成图片 日落海滩" |
| 帮助 | 查看帮助信息 | "帮助" |

### 定时推送
- 每天早上8点自动推送当日天气和新闻摘要
- 通过 `scheduled.py` 管理定时任务

### 对话记忆
- 所有对话历史自动保存在 `memory.json`
- 支持上下文理解和连续对话

## 技术说明

1. **运行机制**：
   - `run.py` 作为主控制器处理所有消息路由
   - 各功能模块独立实现，通过主程序调用
   - 对话状态和游戏状态由内存维护

2. **API服务**：
   - DeepSeek: 智能对话
   - 聚合数据: 天气和新闻
   - 通义万相: 图像生成

3. **安全特性**：
   - 所有API调用都有错误处理和重试机制
   - 敏感信息仅存储在config.json中

## 常见问题解答

❓ **如何重置对话历史？**
   - 删除 `memory.json` 文件后重启程序

❓ **为什么我的定时任务不工作？**
   - 确保服务器时间设置正确
   - 检查程序是否持续运行

❓ **如何添加新的API服务？**
   1. 创建新的Python模块
   2. 在 `run.py` 中添加命令处理器
   3. 更新 `config.json` 添加新配置项

## 项目维护

- 首次运行会自动创建 `memory.json`
- 图片生成默认分辨率为512x512

> 注意：请妥善保管您的config.json文件，不要分享其中的API密钥信息。