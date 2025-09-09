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
    try:
        num = int(float(row["馬番"]))
    except:
        return None
    try:
        prev = int(float(row["前走着順"])) if not pd.isna(row["前走着順"]) else None
    except:
        prev = None

    # 誕生日処理
    birthday = str(row["誕生日"]).strip()
    if "/" not in birthday:
        return None
    try:
        _, month, day = map(int, birthday.split("/"))
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

    # 馬番 = 日そのもの
    if num == day:
        matches.append(f"{horse} → ✅ 誕生日の日と馬番が一致（日={day}）")

    # 馬番 = 日の一桁
    if num == (day % 10):
        matches.append(f"{horse} → ✅ 誕生日の日の一桁と馬番が一致（日の一桁={day % 10}）")

    return matches if matches else None


# -------------------------------
# 🔽 レースごとの切り替え（セレクトボックス）
# -------------------------------
races = sorted(df["レース名"].unique())
selected_race = st.selectbox("レースを選択してください", races)

st.subheader(f"🏆 {selected_race}")
group = df[df["レース名"] == selected_race]

any_match = False
for _, row in group.iterrows():
    result = check_match(row)
    if result:
        any_match = True
        st.write(f"🐴 {row['馬名']}")
        st.write(f"🔢 馬番: {int(float(row['馬番']))}")
        if not pd.isna(row['前走着順']):
            st.write(f"🏁 前走着順: {int(float(row['前走着順']))}")
        st.write(f"🎂 誕生日: {row['誕生日']}")
        for line in result:
            st.success(line)
        st.markdown("---")

if not any_match:
    st.info("一致する馬は見つかりませんでした。")
