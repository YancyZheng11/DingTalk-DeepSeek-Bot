#!/usr/bin/env python

import argparse
import logging
import random
import subprocess
import sys
import os
import threading
import time
import platform
from dingtalk_stream import AckMessage
import dingtalk_stream
import json

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 游戏状态
game_active = True
current_board = [None] * 9
player_symbol = "⭕️"
ai_symbol = "❌"
current_turn = "player"  # 或 "ai"

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
    
    # 不再需要 --client_id 和 --client_secret 参数
    # 直接读取 config.json
    config_file = 'config.json'
    
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件 {config_file} 不存在！")
    
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

def print_board_markdown(board):
    return (
        f" {board[0] or '⬜️'} | {board[1] or '⬜️'} | {board[2] or '⬜️'} \n"
        "-----------\n"
        f" {board[3] or '⬜️'} | {board[4] or '⬜️'} | {board[5] or '⬜️'} \n"
        "-----------\n"
        f" {board[6] or '⬜️'} | {board[7] or '⬜️'} | {board[8] or '⬜️'} "
    )

def check_winner(board):
    win_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    
    for combo in win_combinations:
        if board[combo[0]] and board[combo[0]] == board[combo[1]] == board[combo[2]]:
            return board[combo[0]]
    return None

def is_board_full(board):
    return all(cell is not None for cell in board)

def get_ai_move():
    for i in range(9):
        if current_board[i] is None:
            current_board[i] = ai_symbol
            if check_winner(current_board) == ai_symbol:
                current_board[i] = None
                return i
            current_board[i] = None
    
    for i in range(9):
        if current_board[i] is None:
            current_board[i] = player_symbol
            if check_winner(current_board) == player_symbol:
                current_board[i] = None
                return i
            current_board[i] = None
    
    if current_board[4] is None:
        return 4
    
    corners = [0, 2, 6, 8]
    random.shuffle(corners)
    for i in corners:
        if current_board[i] is None:
            return i
    
    edges = [1, 3, 5, 7]
    random.shuffle(edges)
    for i in edges:
        if current_board[i] is None:
            return i

def make_ai_move():
    global game_active, current_turn
    
    position = get_ai_move()
    current_board[position] = ai_symbol
    current_turn = "player"
    
    winner = check_winner(current_board)
    if winner:
        game_active = False
        return f"AI选择了位置 {position+1}\n\n{print_board_markdown(current_board)}\n\n{winner} 获胜！游戏结束。"
    
    if is_board_full(current_board):
        game_active = False
        return f"AI选择了位置 {position+1}\n\n{print_board_markdown(current_board)}\n\n平局！游戏结束。"
    
    return f"AI选择了位置 {position+1}\n\n{print_board_markdown(current_board)}\n\n请选择你的下一步(1-9):"

def handle_player_move(position):
    global game_active, current_turn
    
    try:
        position = int(position) - 1
        if position < 0 or position > 8:
            return False, "请输入1-9之间的数字"
        
        if current_board[position] is not None:
            return False, "该位置已被占用"
        
        current_board[position] = player_symbol
        current_turn = "ai"
        
        winner = check_winner(current_board)
        if winner:
            game_active = False
            return True, f"{print_board_markdown(current_board)}\n\n{winner} 获胜！游戏结束。"
        
        if is_board_full(current_board):
            game_active = False
            return True, f"{print_board_markdown(current_board)}\n\n平局！游戏结束。"
        
        return True, None
    except ValueError:
        return False, "请输入有效的数字"

def init_game():
    global game_active, current_board, player_symbol, ai_symbol, current_turn
    
    game_active = True
    current_board = [None] * 9
    
    if random.random() < 0.5:
        player_symbol, ai_symbol = "⭕️", "❌"
        current_turn = "player"
    else:
        player_symbol, ai_symbol = "❌", "⭕️"
        current_turn = "ai"
    
    initial_message = (
        f"井字棋游戏开始！你是{player_symbol}，AI是{ai_symbol}\n"
        f"{'AI先手！' if current_turn == 'ai' else '你先手！'}\n\n"
    )
    
    if current_turn == "ai":
        ai_response = make_ai_move()
        return initial_message + ai_response
    else:
        return initial_message + print_board_markdown(current_board) + "\n\n请选择你的第一步(1-9):"

def run_another_program():
    """跨平台启动主程序并退出当前程序"""
    cmd = [
        sys.executable,  # 使用相同的Python解释器
        "./run.py",
        f"--client_id={config["client_id"]}",
        f"--client_secret={config["client_secret"]}"
    ]
    
    if platform.system() == 'Windows':
        # Windows平台
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        # Linux平台
        subprocess.Popen(cmd, 
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       start_new_session=True)
    
    # 确保消息发送完成
    time.sleep(1)
    os._exit(0)

class TicTacToeHandler(dingtalk_stream.ChatbotHandler):
    def __init__(self, logger: logging.Logger = None):
        super(dingtalk_stream.ChatbotHandler, self).__init__()
        self.logger = logger or logging.getLogger()
        self.initial_message_sent = False

    async def process(self, callback: dingtalk_stream.CallbackMessage):
        global game_active
        
        incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        text = incoming_message.text.content.strip()
        
        if not self.initial_message_sent:
            self.initial_message_sent = True
            response = init_game()
        else:
            if current_turn == "player":
                success, response = handle_player_move(text)
                if success and response is None:
                    response = make_ai_move()
            else:
                response = "请等待AI的回合..."
        
        self.reply_text(response, incoming_message)
        
        if not game_active:
            self.reply_text("返回对话模式中......", incoming_message)
            # 使用线程确保消息发送完成
            threading.Thread(target=run_another_program).start()
        
        return AckMessage.STATUS_OK, 'OK'

def main():
    logger = setup_logger()
    options = define_options()

    credential = dingtalk_stream.Credential(options.client_id, options.client_secret)
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, TicTacToeHandler(logger))
    client.start_forever()

if __name__ == '__main__':
    main()