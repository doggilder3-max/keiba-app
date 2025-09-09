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
# 🔽 誕生日を分解する関数
# -------------------------------
def calc_digits(birthday):
    try:
        year, month, day = map(int, str(birthday).split("/"))
    except:
        return None, None, None

    total = month + day
    digit_sum = sum(int(d) for d in str(month) + str(day))
    return total, digit_sum, day


# -------------------------------
# 🔽 判定ロジック
# -------------------------------
def check_match(row):
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

    total, digit_sum, day = calc_digits(row["誕生日"])
    if total is None:
        return None

    matches = []

    # 馬番 = 前走着順
    if prev and num == prev:
        matches.append(f"馬番と前走着順が一致（馬番={num}, 前走着順={prev}）")

    # 馬番 = 月+日
    if num == total:
        matches.append(f"馬番と誕生日の合計が一致（馬番={num}, {month}月+{day}日→{total}）")

    # 馬番 = 誕生日の数字合計
    if num == digit_sum:
        matches.append(f"馬番と誕生日の数字合計が一致（馬番={num}, {month}{day}→{digit_sum}）")

    # 馬番 = 日
    if num == day:
        matches.append(f"馬番と誕生日の日が一致（馬番={num}, 日={day}）")

    # 馬番 = 日の一桁
    if num == (day % 10):
        matches.append(f"馬番と誕生日の日の一桁が一致（馬番={num}, 一桁={day % 10}）")

    return matches if matches else None


# -------------------------------
# 🔽 一致がある馬だけ表示
# -------------------------------
for _, row in df.iterrows():
    matches = check_match(row)
    if not matches:
        continue  # 一致がない馬はスキップ

    total, digit_sum, day = calc_digits(row["誕生日"])

    with st.container():
        st.markdown(f"## 🐴 {row['馬名']}")
        st.write(f"📍 レース名: {row['レース名']}")
        st.write(f"🔢 馬番: {row['馬番']}")
        st.write(f"🏁 前走着順: {row['前走着順']}")
        st.write(f"🎂 誕生日: {row['誕生日']} → 合計:{total}, 一桁:{digit_sum}, 日:{day}")

        for match in matches:
            st.success(match)
