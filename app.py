import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="競馬判定アプリ", layout="wide")

st.title("🏇 競馬判定アプリ")

# ====== 数字処理 ======
def calc_digits(birthday):
    try:
        date = datetime.strptime(birthday, "%Y/%m/%d")
    except:
        return None, None, None, None

    # 西暦は無視 → 月+日だけ
    md_str = f"{date.month}{date.day}"
    digits = [int(d) for d in md_str]
    total = sum(digits)

    # 一桁まで分解
    digit_sum = total
    while digit_sum >= 10:
        digit_sum = sum(int(d) for d in str(digit_sum))

    return total, digit_sum, date.day, date.month


# ====== 判定関数 ======
def check_match(row):
    try:
        num = int(float(row["馬番"]))  
    except:
        return None

    try:
        prev = int(row["前走着順"])
    except:
        prev = None

    total, digit_sum, day, month = calc_digits(row["誕生日"])
    if total is None:
        return None

    matches = []

    if prev and num == prev:
        matches.append(f"🏆 馬番と前走着順が一致（馬番={num}, 前走着順={prev}）")

    if num == total:
        matches.append(f"🎯 馬番と誕生日の合計が一致（馬番={num}, 月日合計={total}）")

    if num == digit_sum:
        matches.append(f"✨ 馬番と誕生日の数字合計が一致（馬番={num}, 一桁合計={digit_sum}）")

    if num == day:
        matches.append(f"📅 馬番と誕生日の日が一致（馬番={num}, 日={day}）")

    if num == (day % 10):
        matches.append(f"🔢 馬番と誕生日の日の一桁が一致（馬番={num}, 一桁={day % 10}）")

    return matches if matches else None


# ====== データ読み込み（GoogleスプレッドシートのCSV） ======
@st.cache_data(ttl=60)  # 60秒キャッシュ → 1分以内に自動更新
def load_data():
    url = "https://docs.google.com/spreadsheets/d/【スプレッドシートID】/gviz/tq?tqx=out:csv&sheet=【シート名】"
    return pd.read_csv(url)

df = load_data()


# ====== 表示部分 ======
for _, row in df.iterrows():
    matches = check_match(row)
    if matches:
        with st.container():
            st.markdown(
                f"""
                <div style='padding:20px; margin:15px 0; border-radius:15px; background-color:#2c2c2c; box-shadow:0 3px 8px rgba(0,0,0,0.3)'>
                    <h2 style='color:#f8f8f8; margin-bottom:5px;'>🐴 {row['馬名']}</h2>
                    <h4 style='color:#cccccc; margin-top:0;'>📍 {row['レース名']}</h4>
                    <p style='color:#bbbbbb;'>🔢 馬番: <b style='color:#ffffff;'>{int(row['馬番'])}</b></p>
                    <p style='color:#bbbbbb;'>🏁 前走着順: <b style='color:#ffffff;'>{row['前走着順']}</b></p>
                    <p style='color:#bbbbbb;'>🎂 誕生日: <b style='color:#ffffff;'>{row['誕生日']}</b></p>
                </div>
                """,
                unsafe_allow_html=True
            )

            for match in matches:
                st.markdown(
                    f"""
                    <div style='padding:12px; margin:6px 0; border-radius:10px; background-color:#20603c; color:#e6ffe6; font-weight:bold;'>
                        {match}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
