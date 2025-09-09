import streamlit as st
import pandas as pd

st.set_page_config(page_title="競馬判定アプリ", layout="wide")
st.title("🏇 競馬判定アプリ")

# 🔽 公開済みスプレッドシートのCSVリンク
CSV_URL = "https://docs.google.com/spreadsheets/d/1zZRXYBtqMMw8vSPoRnstItUOXGEkIRa3Gt8eu89V4MU/export?format=csv"

# データ読み込み
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(CSV_URL)

    # 競馬場とレース番号を分ける
    df["競馬場"] = df["レース名"].str.extract(r"([^\d]+)")
    df["レース番号"] = df["レース名"].str.extract(r"(\d+)R").astype(int)
    return df

df = load_data()

# -------------------------------
# 🔽 判定ロジック
# -------------------------------
def check_match(row):
    horse = row["馬名"]

    try:
        num = int(float(row["馬番"]))
    except:
        return None

    prev = None
    try:
        if not pd.isna(row["前走着順"]):
            prev = int(float(row["前走着順"]))
    except:
        pass

    # 誕生日処理
    birthday = str(row["誕生日"]).replace("月", "-").replace("日", "").strip()
    if "-" not in birthday:
        return None

    try:
        if "/" in birthday:  # 2021/05/06 の形式
            _, month, day = map(int, birthday.split("/"))
        else:
            month, day = map(int, birthday.split("-"))
    except:
        return None

    matches = []

    # 馬番 = 前走着順
    if prev and num == prev:
        matches.append(f"{horse} → ✅ 前走着順と馬番が一致（馬番={num}, 前走着順={prev}）")

    # 馬番 = 月+日
    total = month + day
    if num == total:
        matches.append(f"{horse} → ✅ 誕生日の月+日と馬番が一致（{month}+{day}={total}）")

    # 馬番 = 数字合計（例: 1/26 → 1+2+6=9）
    digit_sum = sum(int(d) for d in str(month) + str(day))
    if num == digit_sum and num != total:  # 重複回避
        digits = "＋".join(list(str(month) + str(day)))
        matches.append(f"{horse} → ✅ 誕生日の数字合計と馬番が一致（{digits}={digit_sum}）")

    # 馬番 = 日そのもの
    if num == day:
        matches.append(f"{horse} → ✅ 誕生日の日と馬番が一致（日={day}）")

    # 馬番 = 日の一桁
    if num == (day % 10):
        matches.append(f"{horse} → ✅ 誕生日の日の一桁と馬番が一致（日の一桁={day % 10}）")

    return matches if matches else None

# -------------------------------
# 🔽 競馬場 → レース番号 選択
# -------------------------------
venues = sorted(df["競馬場"].unique())
selected_venue = st.selectbox("🏟 競馬場を選択してください", venues)

venue_races = df[df["競馬場"] == selected_venue]
race_numbers = sorted(venue_races["レース番号"].unique())
selected_race_num = st.selectbox("📌 レースを選択してください", race_numbers)

selected_race = f"{selected_venue}{selected_race_num}R"
st.subheader(f"🏆 {selected_race}")

# -------------------------------
# 🔽 レースデータの表示
# -------------------------------
race_data = df[df["レース名"] == selected_race]

any_match = False
for _, row in race_data.iterrows():
    result = check_match(row)
    if result:
        any_match = True
        st.markdown(f"""
        🐴 {row['馬名']}  
        🔢 馬番: {int(float(row['馬番'])) if pd.notna(row['馬番']) else '不明'}  
        🏁 前走着順: {int(float(row['前走着順'])) if pd.notna(row['前走着順']) else '不明'}  
        🎂 誕生日: {row['誕生日']}  
        """)
        for line in result:
            st.success(line)

if not any_match:
    st.info("一致する馬は見つかりませんでした。")

