import streamlit as st
import pandas as pd
import re

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
# 🔽 判定ロジック
# -------------------------------
def check_match(row):
    horse = row["馬名"]

    # 馬番
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
    birthday = str(row["誕生日"]).replace("月", "-").replace("日", "").strip()
    try:
        # "2021/05/06" 形式
        year, month, day = map(int, birthday.split("/"))
    except:
        try:
            # "5-6" 形式
            month, day = map(int, birthday.split("-"))
        except:
            return None

    matches = []

    # 馬番 = 前走着順
    if prev and num == prev:
        matches.append(f"{horse} → ✅ 前走着順と馬番が一致（馬番={num}, 前走着順={prev}）")

    # 馬番 = 月+日（合計値）
    total = month + day
    if num == total:
        matches.append(f"{horse} → ✅ 誕生日の月+日と馬番が一致（{month}+{day}={total}）")

    # 馬番 = 誕生日の各桁合計（ただし月+日と同じ結果ならスキップ）
    digit_parts = [int(d) for d in str(month) + str(day)]
    digit_sum = sum(digit_parts)
    if num == digit_sum and num != total:
        parts_str = "＋".join(str(d) for d in digit_parts)
        matches.append(f"{horse} → ✅ 誕生日の数字合計と馬番が一致（{parts_str}={digit_sum}）")

    # 馬番 = 日そのもの
    if num == day:
        matches.append(f"{horse} → ✅ 誕生日の日と馬番が一致（馬番={num}, 日={day}）")

    # 馬番 = 日の一桁
    if num == (day % 10):
        matches.append(f"{horse} → ✅ 誕生日の日の一桁と馬番が一致（馬番={num}, 日の一桁={day % 10}）")

    return matches if matches else None

# -------------------------------
# 🔽 レース番号でソートするための関数
# -------------------------------
def extract_race_number(race_name):
    match = re.search(r"(\d+)R", str(race_name))
    return int(match.group(1)) if match else 999  # 数字が取れない場合は後ろ

# -------------------------------
# 🔽 レースごとに表示（番号順ソート）
# -------------------------------
for race in sorted(df["レース名"].dropna().unique(), key=extract_race_number):
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
                🔢 馬番: {int(float(row['馬番'])) if not pd.isna(row['馬番']) else '不明'}  
                🏁 前走着順: {int(float(row['前走着順'])) if not pd.isna(row['前走着順']) else '不明'}  
                🎂 誕生日: {row['誕生日']}  
                """
            )
            for line in result:
                st.success(line)

    if not any_match:
        st.info("一致する馬は見つかりませんでした。")
