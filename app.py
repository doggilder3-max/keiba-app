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
    horse = str(row.get("馬名", "不明"))
    num = None
    try:
        num = int(float(row["馬番"]))  # float → int 変換
    except:
        return None

    prev = None
    try:
        prev = int(float(row["前走着順"]))
    except:
        pass

    # 誕生日処理
    birthday_raw = str(row.get("誕生日", "")).strip()
    birthday = birthday_raw.replace("月", "-").replace("日", "")
    month, day = None, None
    try:
        if "/" in birthday_raw:  # YYYY/MM/DD 形式
            parts = birthday_raw.split("/")
            month, day = int(parts[1]), int(parts[2])
        else:  # X月Y日 形式
            month, day = map(int, birthday.split("-"))
    except:
        return None  # 誕生日が解釈できない場合はスキップ

    matches = []

    # 馬番 = 前走着順
    if prev and num == prev:
        matches.append(f"前走着順と馬番が一致（{prev}）")

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
# 🔽 レースごとに表示（カード形式）
# -------------------------------
for race, group in df.groupby("レース名"):
    st.subheader(f"🏆 {race}")

    any_match = False
    for _, row in group.iterrows():
        results = check_match(row)
        if results:
            any_match = True
            horse_num = int(float(row["馬番"])) if not pd.isna(row["馬番"]) else "?"
            prev_num = int(float(row["前走着順"])) if not pd.isna(row["前走着順"]) else "?"

            with st.container():
                st.markdown(
                    f"""
                    <div style='padding:20px; margin:15px 0; border-radius:15px; background-color:#2c2c2c; box-shadow:0 3px 8px rgba(0,0,0,0.3)'>
                        <h3 style='color:#f8f8f8;'>🐴 {row['馬名']}</h3>
                        <p style='color:#bbbbbb;'>🔢 馬番: <b style='color:#ffffff;'>{horse_num}</b></p>
                        <p style='color:#bbbbbb;'>🏁 前走着順: <b style='color:#ffffff;'>{prev_num}</b></p>
                        <p style='color:#bbbbbb;'>🎂 誕生日: <b style='color:#ffffff;'>{row['誕生日']}</b></p>
                        <div style='margin-top:10px;'>
                            {''.join([f"<div style='padding:10px; margin:6px 0; border-radius:8px; background-color:#20603c; color:#e6ffe6; font-weight:bold;'>{m}</div>" for m in results])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    if not any_match:
        st.info("一致する馬は見つかりませんでした。")
