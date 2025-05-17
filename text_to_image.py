from dashscope import ImageSynthesis
from openai import OpenAI
from pathlib import PurePosixPath
from http import HTTPStatus
import requests
import argparse
import json


with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

parser = argparse.ArgumentParser(description="通义万相生成图片并通过钉钉机器人发送")
parser.add_argument("--prompt", type=str, help="对需生成的图像的描述", required=True)
args = parser.parse_args()

client = OpenAI(api_key=config["deepseek_key"], base_url="https://api.deepseek.com")

memory=[{"role": "system", "content": "接下来，用户会描述一张图片，你需要根据描述生成这张图片的prompt，以供文生图模型使用。记住，只要输出prompt，别的什么都不要输出。"},{"role": "user", "content":args.prompt}]

def deepseek_talk():

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=memory,
        stream=False
    )

    reply = response.choices[0].message.content

    memory.append({"role": "assistant", "content": reply})

    return reply

def gen_image(prompt):

    global url

    rsp = ImageSynthesis.call(api_key=config["ali_key"],
                            model="wanx2.1-t2i-turbo",
                            prompt=prompt,
                            n=1,
                            size='1024*1024')

    print('response: %s' % rsp)
    if rsp.status_code == HTTPStatus.OK:

        for result in rsp.output.results:
            url = result.url
            print(url)
            send_image()

    else:
        print('sync_call Failed, status_code: %s, code: %s, message: %s' %
            (rsp.status_code, rsp.code, rsp.message))

def send_image():
    webhook = config["webhook"]

    data = {
        "msgtype": "image",
        "image": {
            "picURL": url
        }
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook, headers=headers, data=json.dumps(data))
    print(response.text)

gen_image(deepseek_talk())
