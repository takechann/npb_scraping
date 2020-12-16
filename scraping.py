import sys
import time
import os

# スクレイピング
import requests
from bs4 import BeautifulSoup

# SQL周り
import pandas as pd
from sqlalchemy import create_engine

# DB接続
DB_URL = os.environ["DATABASE_URL"]
engine = create_engine(DB_URL)


## 投手の場合 ##
# データ取得
url = "https://npb.jp/bis/2020/stats/idp1_s.html"
html = requests.get(url)
soup = BeautifulSoup(html.content, "html.parser")
players = soup.select('.ststats')

# テーブル削除
TABLE_NAME = "pitcher_player_table"
engine.execute('delete from ' + TABLE_NAME + ";")
print(TABLE_NAME + " has been deleted")

# 投手の挿入
for player in players:
    # 選手の成績
    players_stats = []

    # 選手名の取得 ＆ 空白文字を削除
    plyaer_name = player.find_all("td")[1].text.replace('\u3000', '')
    players_stats.append("'" + plyaer_name + "'")

    # 各成績（登板～打者）
    for element in player.find_all("td")[2:11]:
        players_stats.append(int(element.text))

    # 各成績（勝率）
    for element in player.find_all("td")[11:12]:
        players_stats.append(float(element.text))

    # 各成績（打者）
    for element in player.find_all("td")[12:13]:
        players_stats.append(int(element.text))

    # 各成績（投球回）
    count = 0.0
    for element in player.find_all("td")[13:15]:
        if element.text != '':
            count = float(element.text) + count
    players_stats.append(count)

    # 各成績（安打～自責点）
    for element in player.find_all("td")[15:25]:
        players_stats.append(int(element.text))

    # 各成績（防御率）
    for element in player.find_all("td")[25:]:
        players_stats.append(float(element.text))

    # INCERT用の文字列
    maped_list = map(str, players_stats)
    players_stats_str = ','.join(maped_list)
    INCERT_STR = "INSERT INTO "+ TABLE_NAME + " VALUES(" + players_stats_str + ");"
    print(INCERT_STR)

    # ここでINCERT
    engine.execute(INCERT_STR)

# 待機
time.sleep(2)

## 野手の場合 ##
# データ取得
url = "https://npb.jp/bis/2020/stats/idb1_s.html"
html = requests.get(url)
soup = BeautifulSoup(html.content, "html.parser")
players = soup.select('.ststats')

# テーブル削除
TABLE_NAME = "fielder_player_table"
engine.execute('delete from ' + TABLE_NAME + ";")
print(TABLE_NAME + " has been deleted")

# 野手の挿入
for player in players:
    # 選手の成績
    players_stats = []

    # 選手名の取得 ＆ 空白文字を削除
    plyaer_name = player.find_all("td")[1].text.replace('\u3000', '')
    players_stats.append("'" + plyaer_name + "'")

    # 各成績（試合～併殺打）
    for element in player.find_all("td")[2:21]:
        players_stats.append(int(element.text))

    # 各成績（打率～出塁率）
    for element in player.find_all("td")[21:]:
        players_stats.append(float(element.text))

    # OPS
    ops = float(player.find_all("td")[22].text) + float(player.find_all("td")[23].text)
    players_stats.append(round(ops,2))

    # INCERT用の文字列
    maped_list = map(str, players_stats)
    players_stats_str = ','.join(maped_list)
    INCERT_STR = "INSERT INTO "+ TABLE_NAME + " VALUES(" + players_stats_str + ");"
    print(INCERT_STR)

    # ここでINCERT
    engine.execute(INCERT_STR)

print("task has been conducted ")
sys.stdout.flush()
