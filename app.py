import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="競馬判定アプリ", layout="wide")
st.title("🏇 競馬判定アプリ")

# 🔽 公開済みスプレッドシートのCSVリンク
CSV_URL = "https://docs.google.com/spreadsheets/d/1zZRXYBtqMMw8vSPoRnstItUOXGEkIRa3Gt8eu89V4MU/export?format=csv"

# スプレッドシート読み込み
@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

# -------------------------------
# 🔽 判定ロジック
# -------------------------------
def check_match(row):
    horse = str(row["馬名"])
    race = str(row["レース名"])

    # 数値処理
    try:
        num = int(row["馬番"])
    except:
        return None
    prev = None
    try:
        prev = int(row["前走着順"])
    except:
        pass

    # 誕生日処理（例: 2021/01/27）
    try:
        birthday_str = str(row["誕生日"]).strip()
        birthday = datetime.strptime(birthday_str, "%Y/%m/%d")
        month, day = birthday.month, birthday.day
    except:
        return None

    matches = []

    # 馬番 = 前走着順
    if prev and num == prev:
        matches.append(f"馬番と前走着順が一致（馬番={num}, 前走着順={prev}）")

    # 馬番 = 月+日
    total = month + day
    if num == total:
        matches.append(f"馬番と誕生日の合計が一致（馬番={num}, {month}月{day}日 → {total}）")

    # 馬番 = 誕生日の数字合計
    digit_sum = sum(int(d) for d in f"{month}{day}")
    if num == digit_sum:
        matches.append(f"馬番と誕生日の数字合計が一致（馬番={num}, {month}{day} → {digit_sum}）")

    # 馬番 = 日
    if num == day:
        matches.append(f"馬番と誕生日の日が一致（馬番={num}, 日={day}）")

    # 馬番 = 日の一桁
    if num == (day % 10):
        matches.append(f"馬番と誕生日の日の一桁が一致（馬番={num}, 一桁={day % 10}）")

    if matches:
        return {
            "name": horse,
            "race": race,
            "num": num,
            "rank": prev if prev else "不明",
            "birthday": f"{birthday.month}月{birthday.day}日 → 合計:{month+day}, 一桁:{day % 10}, 日:{day}",
            "reasons": matches
        }
    return None

# -------------------------------
# 🔽 UI カード表示関数
# -------------------------------
def render_horse_card(info):
    st.markdown(
        f"""
        <div style="
            background-color:#f5fff5;
            border:2px solid #228B22;
            border-radius:10px;
            padding:15px;
            margin-bottom:15px;
            color:#000000;
        ">
            <h3 style="color:#000000;">🐎 {info['name']}</h3>
            <p style="color:#000000;">📍 レース: <b>{info['race']}</b></p>
            <p style="color:#000000;">🔢 馬番: <span style="color:#4169e1;"><b>{info['num']}</b></span></p>
            <p style="color:#000000;">🏁 前走着順: <span style="color:#8a2be2;"><b>{info['rank']}</b></span></p>
            <p style="color:#000000;">🎂 誕生日: <span style="color:#ff1493;"><b>{info['birthday']}</b></span></p>
            <hr>
            <div style="color:#000000;">
                {" / ".join([f"✅ {r}" for r in info['reasons']])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# 🔽 レースごとに一致した馬だけ表示
# -------------------------------
for race, group in df.groupby("レース名"):
    matches = []
    for _, row in group.iterrows():
        result = check_match(row)
        if result:
            matches.append(result)

    if matches:
        st.subheader(f"🏆 {race}")
        for horse_info in matches:
            render_horse_card(horse_info)
