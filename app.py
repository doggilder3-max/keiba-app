import streamlit as st
import pandas as pd

st.set_page_config(page_title="競馬判定アプリ", layout="wide")

st.title("🏇 競馬判定アプリ")

# 🔽 公開済みスプレッドシートのCSVリンク
CSV_URL = "https://docs.google.com/spreadsheets/d/1zZRXYBtqMMw8vSPoRnstItUOXGEkIRa3Gt8eu89V4MU/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

# -------------------------------
# 判定ロジック
# -------------------------------
def check_match(row):
    matches = []
    horse = row["馬名"]

    try:
        num = int(row["馬番"])
    except:
        return None

    prev = None
    try:
        prev = int(row["前走着順"])
    except:
        pass

    # 誕生日処理
    birthday_raw = str(row["誕生日"]).strip()
    try:
        y, m, d = map(int, birthday_raw.split("/"))
        month, day = m, d
    except:
        return None

    # 判定条件
    if prev and num == prev:
        matches.append(f"馬番と前走着順が一致（馬番={num}, 前走着順={prev}）")

    total = month + day
    if num == total:
        matches.append(f"馬番と誕生日の合計が一致（馬番={num}, {month}+{day} → {total}）")

    digit_sum = sum(int(d) for d in str(month) + str(day))
    if num == digit_sum:
        matches.append(f"馬番と誕生日の数字合計が一致（馬番={num}, 合計={digit_sum}）")

    if num == day:
        matches.append(f"馬番と誕生日の日が一致（馬番={num}, 日={day}）")

    if num == (day % 10):
        matches.append(f"馬番と誕生日の日の一桁が一致（馬番={num}, 一桁={day % 10}）")

    return {
        "name": horse,
        "race": row["レース名"],
        "num": num,
        "rank": prev if prev else "不明",
        "birthday": f"{month}月{day}日 → 合計:{month+day}, 一桁:{day % 10}, 日:{day}",
        "reasons": matches
    } if matches else None


# -------------------------------
# 表示用カード
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
        ">
            <h3>🐎 {info['name']}</h3>
            <p>📍 レース: <b>{info['race']}</b></p>
            <p>🔢 馬番: <span style="color:#4169e1;"><b>{info['num']}</b></span></p>
            <p>🏁 前走着順: <span style="color:#8a2be2;"><b>{info['rank']}</b></span></p>
            <p>🎂 誕生日: <span style="color:#ff1493;"><b>{info['birthday']}</b></span></p>
            <hr>
            {"<br>".join([f"✅ {r}" for r in info['reasons']])}
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------------
# レースごとに表示
# -------------------------------
for race, group in df.groupby("レース名"):
    st.subheader(f"🏆 {race}")

    found = False
    for _, row in group.iterrows():
        result = check_match(row)
        if result:
            found = True
            render_horse_card(result)

    if not found:
        st.info("一致する馬は見つかりませんでした。")
