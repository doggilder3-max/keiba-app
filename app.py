import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="競馬判定アプリ", layout="wide")

st.title("🏇 競馬判定アプリ")

# 🔽 公開済みスプレッドシートのCSVリンク
CSV_URL = "https://docs.google.com/spreadsheets/d/1zZRXYBtqMMw8vSPoRnstItUOXGEkIRa3Gt8eu89V4MU/export?format=csv"

# -------------------------------
# 🔽 データ読み込み
# -------------------------------
@st.cache_data(ttl=60)  # 60秒ごとに更新
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()

# -------------------------------
# 🔽 ヘルパー関数
# -------------------------------
def safe_int(value):
    """数値に変換できれば int を返し、できなければ None"""
    try:
        return int(float(str(value).strip()))
    except:
        return None

# -------------------------------
# 🔽 判定ロジック
# -------------------------------
def check_match(row):
    horse = row["馬名"]

    # 馬番
    num = safe_int(row["馬番"])
    if num is None:
        return None

    # 前走着順
    prev = safe_int(row["前走着順"])

    # 誕生日処理
    birthday = str(row["誕生日"]).strip()
    month, day = None, None
    try:
        # 例: 2021/01/27
        dt = datetime.datetime.strptime(birthday, "%Y/%m/%d")
        month, day = dt.month, dt.day
    except:
        try:
            # 例: 1月27日
            birthday = birthday.replace("月", "-").replace("日", "")
            month, day = map(int, birthday.split("-"))
        except:
            return None  # 誕生日が解釈できない場合はスキップ

    matches = []

    # 馬番 = 前走着順
    if prev and num == prev:
        matches.append(f"{horse} → ✅ 前走着順と馬番が一致（馬番={num}, 前走着順={prev}）")

    # 馬番 = 月+日（合計値）
    total = month + day
    if num == total:
        matches.append(f"{horse} → ✅ 誕生日の月+日と馬番が一致（馬番={num}, {month}+{day}={total}）")

    # 馬番 = 誕生日の各桁合計
    digit_sum = sum(int(d) for d in str(month) + str(day))
    if num == digit_sum:
        matches.append(f"{horse} → ✅ 誕生日の数字合計と馬番が一致（馬番={num}, 合計={digit_sum}）")

    # 馬番 = 日そのもの
    if num == day:
        matches.append(f"{horse} → ✅ 誕生日の日と馬番が一致（馬番={num}, 日={day}）")

    # 馬番 = 日の一桁
    if num == (day % 10):
        matches.append(f"{horse} → ✅ 誕生日の日の一桁と馬番が一致（馬番={num}, 一桁={day % 10}）")

    return matches if matches else None

# -------------------------------
# 🔽 レースごとに表示
# -------------------------------
for race, group in df.groupby("レース名"):
    st.subheader(f"🏆 {race}")

    any_match = False
    for _, row in group.iterrows():
        result = check_match(row)
        if result:
            any_match = True
            for line in result:
                st.success(line)

    if not any_match:
        st.info("一致する馬は見つかりませんでした。")
