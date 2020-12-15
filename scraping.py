import sys
import time
import os

# スクレイピング
import requests
from bs4 import BeautifulSoup

# SQL周り
import pandas as pd
from sqlalchemy import create_engine

# urlを代入
url = "https://npb.jp/bis/2020/stats/idb1_s.html"

# データ取得
html = requests.get(url)
soup = BeautifulSoup(html.content, "html.parser")
players = soup.select('.ststats')

# 待機
# time.sleep(5)

# DB接続
DB_URL = os.environ["DATABASE_URL"]
engine = create_engine(DB_URL)

# df = pd.read_sql(sql='SELECT * FROM pitcher_player_table;', con=engine)

# テーブル削除
engine.execute('delete from pitcher_player_table;')
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
    INCERT_STR = "INSERT INTO pitcher_player_table VALUES(" + players_stats_str + ");"

    # ここでINCERT
    engine.execute(INCERT_STR)

# INCERT
# engine.execute(str2)

print("task has been conducted ")
sys.stdout.flush()
