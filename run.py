#!/usr/bin/env python

from urllib.parse import urlparse, unquote
from dingtalk_stream import AckMessage # type: ignore
from openai import OpenAI # type: ignore
import subprocess
import dingtalk_stream # type: ignore
import argparse
import logging
import asyncio
import json
import os
import threading
import time
import sys
import platform
import subprocess

subprocess.Popen(["python", "scheduled.py"])

# 读取 config.json 文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

client = OpenAI(api_key=config["deepseek_key"], base_url="https://api.deepseek.com")

if os.path.exists('memory.json'):
    with open('memory.json', 'r', encoding='utf-8') as file:
        memory = json.load(file)
else:
    memory = [{"role": "system", "content": "You are a helpful assistant."}]



def talk(ask):
    memory.append({"role": "user", "content": ask})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=memory,
        stream=False
    )
    
    answer = response.choices[0].message.content
    memory.append({"role": "assistant", "content": answer})
    save()

    return answer

def save():
    with open('memory.json', 'w', encoding='utf-8') as file:
        json.dump(memory, file, ensure_ascii=False, indent=4)

def setup_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

def define_options():
    parser = argparse.ArgumentParser(description="从 config.json 读取配置")

    config_file = 'config.json'
    
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件 {config_file} 不存在")
    
    # 读取 JSON 配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 检查必需的字段
    required_keys = ['client_id', 'client_secret']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"配置文件中缺少必需的字段: {key}")
    
    # 返回一个类似 argparse.Namespace 的对象，保持兼容性
    class Options:
        def __init__(self, config_dict):
            self.client_id = config_dict['client_id']
            self.client_secret = config_dict['client_secret']
    
    return Options(config)

def start_new_program(program_name, *args):
    """跨平台启动新程序并退出当前程序"""
    if platform.system() == 'Windows':
        # Windows平台使用CREATE_NEW_CONSOLE
        creationflags = subprocess.CREATE_NEW_CONSOLE
        subprocess.Popen([sys.executable, program_name] + list(args), 
                        creationflags=creationflags)
    else:
        # Linux/Mac平台使用nohup和重定向
        cmd = ['nohup', sys.executable, program_name] + list(args)
        subprocess.Popen(cmd, 
                       stdout=open(os.devnull, 'w'),
                       stderr=subprocess.STDOUT,
                       preexec_fn=os.setpgrp)
    
    # 确保消息发送后退出
    time.sleep(1)
    os._exit(0)

class EchoTextHandler(dingtalk_stream.ChatbotHandler):
    def __init__(self, logger: logging.Logger = None):
        super(dingtalk_stream.ChatbotHandler, self).__init__()
        if logger:
            self.logger = logger

    async def process(self, callback: dingtalk_stream.CallbackMessage):
        incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        text = incoming_message.text.content.strip()

        if text.startswith('生成图像'):
            self.reply_markdown("生成中......", "生成中......", incoming_message)
            proc = await asyncio.create_subprocess_exec(
                "python", "text_to_image.py", "--prompt", text[4:].strip()
            )
            await proc.wait()
            return AckMessage.STATUS_OK, 'OK'
        
        elif text == '新闻':
            self.reply_markdown("生成中......", "生成中......", incoming_message)
            proc = await asyncio.create_subprocess_exec(
                "python", "get_news.py"
            )
            await proc.wait()
            return AckMessage.STATUS_OK, 'OK'
        
        elif text == '天气':
            self.reply_markdown("生成中......", "生成中......", incoming_message)
            proc = await asyncio.create_subprocess_exec(
                "python", "get_weather.py"
            )
            await proc.wait()
            return AckMessage.STATUS_OK, 'OK'
        
        elif text == '井字棋':
            self.reply_markdown("启动中......", "游戏启动中，请稍候...", incoming_message)
            
            # 启动新程序并退出
            threading.Thread(target=start_new_program, 
                           args=('./tic_tac_toe.py', 
                                f'--client_id={config["client_id"]}',
                                f'--client_secret={config["client_secret"]}')).start()
            
            return AckMessage.STATUS_OK, 'OK'

        else:
            answer = '\n'.join(['%s'%i for i in talk(text).split('\n')])
            self.reply_markdown(answer.replace('*', ''), answer, incoming_message)
            return AckMessage.STATUS_OK, 'OK'

def main():
    logger = setup_logger()
    options = define_options()

    credential = dingtalk_stream.Credential(options.client_id, options.client_secret)
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, EchoTextHandler(logger))
    client.start_forever()

if __name__ == '__main__':
    main()