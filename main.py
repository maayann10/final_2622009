import sqlite3
import time
from bs4 import BeautifulSoup
import requests

# 1. スクレイピングするURL（1ページ目〜2ページ目を取得する例）
base_url = "https://github.com/orgs/google/repositories"
headers = {"User-Agent": "Mozilla/5.0"}

repo_list = []

for page in range(1, 3):  # 1ページ目と2ページ目を取得
  url = f"{base_url}?page={page}"
  print(f"{page}ページ目を取得中...")

  response = requests.get(url, headers=headers)
  soup = BeautifulSoup(response.text, "html.parser")

  # 各リポジトリのタイトル部分を探す
  title_containers = soup.select(
      "div[data-listview-item-title-container='true']"
  )

  for title_div in title_containers:
    # ① リポジトリ名
    name_tag = title_div.find("a")
    repo_name = name_tag.text.strip() if name_tag else "不明"

    # リポジトリ1件全体の親要素を取得
    item = title_div.parent

    # ② 主要な言語
    lang_tag = item.select_one("div[class*='LanguageLabelContainer']")
    language = lang_tag.text.strip() if lang_tag else "なし"

    # ③ スターの数
    star_tag = item.select_one("a[href$='/stargazers']")
    stars = star_tag.text.strip() if star_tag else "0"

    repo_list.append((repo_name, language, stars))

  # 【重要】課題の必須条件：サーバー負荷軽減のため1秒待機
  time.sleep(1)

# 2. データベース（SQLite）の作成とデータ保存
conn = sqlite3.connect("google_repos.db")
cur = conn.cursor()

# テーブル作成（すでに存在する場合は一度消して作り直す）
cur.execute("DROP TABLE IF EXISTS repositories")
cur.execute("""
    CREATE TABLE repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        language TEXT,
        stars TEXT
    )
""")

# データをまとめて保存
cur.executemany(
    "INSERT INTO repositories (name, language, stars) VALUES (?, ?, ?)",
    repo_list,
)
conn.commit()

# 3. 保存したデータをSELECT文で表示する
print("\n--- データベースに保存されたデータ ---")
cur.execute("SELECT * FROM repositories")
rows = cur.fetchall()

for row in rows:
  print(row)

conn.close()