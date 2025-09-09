import streamlit as st
import pandas as pd

st.set_page_config(page_title="競馬判定アプリ", layout="wide")

st.title("🏇 競馬判定アプリ")

# 🔽 公開済みスプレッドシートのCSVリンク
CSV_URL = "https://docs.google.com/spreadsheets/d/1zZRXYBtqMMw8vSPoRnstItUOXGEkIRa3Gt8eu89V4MU/export?format=csv"

# スプレッドシート読み込み
@st.cache_data(ttl=60)  # 60秒ごとに更新
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

# -------------------------------
# 🔽 判定ロジック
# -------------------------------
def check_match(row):
    horse = row["馬名"]

    # 馬番（空欄ならスキップ）
    try:
        num = int(float(row["馬番"]))
    except:
        return None

    # 前走着順
    try:
        prev = int(float(row["前走着順"]))
    except:
        prev = None

    # 誕生日処理
    try:
        birthday = str(row["誕生日"]).replace("月", "-").replace("日", "").strip()
        if "/" in birthday:
            _, month, day = birthday.split("/")
        else:
            month, day = birthday.split("-")
        month, day = int(month), int(day)
    except:
        return None  # 誕生日形式が不正ならスキップ

    matches = []

    # 馬番 = 前走着順
    if prev and num == prev:
        matches.append(f"前走着順と馬番が一致（馬番={num}, 前走着順={prev}）")

    # 馬番 = 月+日（合計値）
    total = month + day
    match_month_day = None
    if num == total:
        match_month_day = f"誕生日の月+日と馬番が一致（{month}+{day}={total}）"

    # 馬番 = 誕生日の各桁合計（計算式表示付き）
    digit_parts = [int(d) for d in str(month) + str(day)]
    digit_sum = sum(digit_parts)
    match_digit_sum = None
    if num == digit_sum:
        parts_str = "＋".join(str(d) for d in digit_parts)
        match_digit_sum = f"誕生日の数字合計と馬番が一致（{parts_str}={digit_sum}）"

    # 👉 ここで重複チェック
    if match_month_day and match_digit_sum and match_month_day.split("（")[1] == match_digit_sum.split("（")[1]:
        matches.append(match_month_day)  # 片方だけ残す
    else:
        if match_month_day:
            matches.append(match_month_day)
        if match_digit_sum:
            matches.append(match_digit_sum)

    # 馬番 = 日そのもの
    if num == day:
        matches.append(f"誕生日の日と馬番が一致（日={day}）")

    # 馬番 = 日の一桁
    if num == (day % 10):
        matches.append(f"誕生日の日の一桁と馬番が一致（日の一桁={day % 10}）")

    return matches if matches else None

# -------------------------------
# 🔽 レースごとに表示（番号順）
# -------------------------------
def extract_race_number(race_name):
    import re
    match = re.search(r'(\d+)R', str(race_name))
    return int(match.group(1)) if match else 9999

for race, group in sorted(df.groupby("レース名"), key=lambda x: extract_race_number(x[0])):
    st.subheader(f"🏆 {race}")

    any_match = False
    for _, row in group.iterrows():
        result = check_match(row)
        if result:
            any_match = True
            st.markdown(f"""
                ### 🐴 {row['馬名']}
                🔢 馬番: {int(float(row['馬番'])) if pd.notna(row['馬番']) else '不明'}  
                🏁 前走着順: {int(float(row['前走着順'])) if pd.notna(row['前走着順']) else '不明'}  
                🎂 誕生日: {row['誕生日']}
            """)
            for line in result:
                st.success(line)

    if not any_match:
        st.info("一致する馬は見つかりませんでした。")
