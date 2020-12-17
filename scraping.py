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

# チームのイニシャル
team_initial_list = [
    "s", #ヤクルト
    "d", #ドラゴンズ
    "c", #カープ
    "g", #ジャイアンツ
    "t", #タイガース
    "db", #ベイスターズ
    "l", #ライオンズ
    "h", #ホークス
    "e", #イーグルス
    "m", #マリーンズ
    "f", #ファイターズ
    "b" #バファローズ
]

## 投手の場合 ##
TABLE_NAME = "pitcher_player_table"

# 投手の挿入を行う
def incert_pitcher(team_initial):
    url = "https://npb.jp/bis/2020/stats/idp1_"+ team_initial +".html"
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    players = soup.select('.ststats')

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
            if element.text == '+':
                count = 0.0
            elif element.text != '':
                count = float(element.text) + count
        players_stats.append(count)

        # 各成績（安打～自責点）
        for element in player.find_all("td")[15:25]:
            players_stats.append(int(element.text))

        # 各成績（防御率）
        for element in player.find_all("td")[25:26]:
            if element.text == '----':
                players_stats.append(99.99)
            else :
                players_stats.append(float(element.text))

        # チーム名_イニシャル
        players_stats.append("'" + team_initial + "'")

        # INCERT用の文字列
        maped_list = map(str, players_stats)
        players_stats_str = ','.join(maped_list)
        INCERT_STR = "INSERT INTO "+ TABLE_NAME + " VALUES(" + players_stats_str + ");"
        print(INCERT_STR)

        # ここでINCERT
        engine.execute(INCERT_STR)

    # 待機
    time.sleep(2)

# 全データ削除
engine.execute('delete from ' + TABLE_NAME + ";")
print(TABLE_NAME + " has been deleted")

# 投手挿入の実行
for initial in team_initial_list:
    incert_pitcher(initial)

### 野手の場合 ###
TABLE_NAME = "fielder_player_table"

# 野手の挿入を行う
def incert_fielder(team_initial):
    url = "https://npb.jp/bis/2020/stats/idb1_"+ team_initial +".html"
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    players = soup.select('.ststats')
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

        # チーム名_イニシャル
        players_stats.append("'" + team_initial + "'")

        # INCERT用の文字列
        maped_list = map(str, players_stats)
        players_stats_str = ','.join(maped_list)
        INCERT_STR = "INSERT INTO "+ TABLE_NAME + " VALUES(" + players_stats_str + ");"
        print(INCERT_STR)

        # ここでINCERT
        engine.execute(INCERT_STR)

# 全データ削除
engine.execute('delete from ' + TABLE_NAME + ";")
print(TABLE_NAME + " has been deleted")

# 野手挿入の実行
for initial in team_initial_list:
    incert_fielder(initial)

print("task has been conducted ")
sys.stdout.flush()
