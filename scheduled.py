import datetime
import subprocess
import time

while True:
    if datetime.datetime.now().strftime('%H:%M:%S') == '08:00:00':
        subprocess.Popen(["python", "get_news.py"])
        subprocess.Popen(["python", "get_weather.py"])
        time.sleep(5)
