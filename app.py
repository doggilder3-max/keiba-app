import streamlit as st
import pandas as pd
import re

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
    try:
        num = int(row["馬番"])
    except:
        return None

    try:
        prev = int(row["前走着順"]) if not pd.isna(row["前走着順"]) else None
    except:
        prev = None

    birthday = str(row["誕生日"]).strip()
    try:
        year, month, day = map(int, birthday.split("/"))
    except:
        return None  # 形式が違う場合スキップ

    matches = []

    # 馬番 = 前走着順
    if prev and num == prev:
        matches.append("前走着順と馬番が一致")

    # 馬番 = 月+日（合計値）
    total = month + day
    if num == total:
        matches.append(f"誕生日の月+日と馬番が一致（{month}+{day}={total}）")

    # 馬番 = 誕生日の各桁合計
    digit_sum = sum(int(d) for d in str(month) + str(day))
    if num == digit_sum:
        matches.append(f"誕生日の数字合計と馬番が一致（合計={digit_sum}）")

    # 馬番 = 日そのもの
    if num == day:
        matches.append(f"誕生日の日と馬番が一致（日={day}）")

    # 馬番 = 日の一桁
    if num == (day % 10):
        matches.append(f"誕生日の日の一桁と馬番が一致（日の一桁={day % 10}）")

    return matches if matches else None

# -------------------------------
# 🔽 レース番号を数字順にソート
# -------------------------------
def extract_race_number(race_name):
    match = re.search(r"(\d+)R", str(race_name))
    return int(match.group(1)) if match else 999

# -------------------------------
# 🔽 レースごとに表示
# -------------------------------
for race in sorted(df["レース名"].unique(), key=extract_race_number):
    group = df[df["レース名"] == race]

    st.subheader(f"🏆 {race}")

    any_match = False
    for _, row in group.iterrows():
        result = check_match(row)
        if result:
            any_match = True
            st.markdown(
                f"""
                🐴 **{row['馬名']}**  
                🔢 馬番: {int(row['馬番']) if not pd.isna(row['馬番']) else '不明'}  
                🏁 前走着順: {int(row['前走着順']) if not pd.isna(row['前走着順']) else '不明'}  
                🎂 誕生日: {row['誕生日']}  
                """
            )
            for line in result:
                st.success(line)

    if not any_match:
        st.info("一致する馬は見つかりませんでした。")
