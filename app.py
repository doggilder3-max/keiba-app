import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="競馬判定アプリ", layout="wide")
st.title("🏇 競馬判定アプリ")

# ======================
# 🔽 公開済みスプレッドシートのCSVリンク
# ======================
CSV_URL = "https://docs.google.com/spreadsheets/d/1zZRXYBtqMMw8vSPoRnstItUOXGEkIRa3Gt8eu89V4MU/export?format=csv"

# ======================
# 🔽 スプレッドシート読み込み
# ======================
@st.cache_data(ttl=60)  # 60秒ごとに更新
def load_data():
    return pd.read_csv(CSV_URL)

df = load_data()
df.columns = df.columns.str.strip()  # カラム名の前後の空白を削除
st.write("📋 データのカラム名:", df.columns.tolist())  # デバッグ用

# ======================
# 🔽 判定ロジック
# ======================
def check_match(row):
    try:
        num = int(float(row["馬番"]))
    except:
        return None

    prev = None
    try:
        prev = int(float(row["前走着順"]))
    except:
        pass

    # 誕生日処理（形式: YYYY/MM/DD）
    try:
        birthday = datetime.strptime(str(row["誕生日"]), "%Y/%m/%d")
        month, day = birthday.month, birthday.day
    except:
        return None

    matches = []

    # 馬番 = 前走着順
    if prev and num == prev:
        matches.append(f"{row['馬名']} → ✅ 前走着順と馬番が一致（馬番={num}, 前走着順={prev}）")

    # 馬番 = 月+日（合計値）
    total = month + day
    if num == total:
        matches.append(f"{row['馬名']} → ✅ 誕生日の月+日と馬番が一致（{month}+{day}={total}）")

    # 馬番 = 誕生日の各桁合計
    digit_sum = sum(int(d) for d in str(month) + str(day))
    if num == digit_sum:
        matches.append(f"{row['馬名']} → ✅ 誕生日の数字合計と馬番が一致（{'＋'.join(list(str(month) + str(day)))}={digit_sum}）")

    # 馬番 = 日そのもの
    if num == day:
        matches.append(f"{row['馬名']} → ✅ 誕生日の日と馬番が一致（馬番={num}, 日={day}）")

    # 馬番 = 日の一桁
    if num == (day % 10):
        matches.append(f"{row['馬名']} → ✅ 誕生日の日の一桁と馬番が一致（馬番={num}, 日の一桁={day % 10}）")

    return matches if matches else None


# ======================
# 🔽 レース選択（セレクトボックス）
# ======================
if "レース名" in df.columns:
    races = sorted(df["レース名"].dropna().unique())
    selected_race = st.selectbox("📌 レースを選択してください", races)

    race_data = df[df["レース名"] == selected_race]

    st.subheader(f"🏆 {selected_race}")

    any_match = False
    for _, row in race_data.iterrows():
        result = check_match(row)
        if result:
            any_match = True
            st.markdown(f"""
            🐴 **{row['馬名']}**
            🔢 馬番: {int(float(row['馬番'])) if pd.notna(row['馬番']) else '-'}
            🏁 前走着順: {row['前走着順'] if pd.notna(row['前走着順']) else '-'}
            🎂 誕生日: {row['誕生日']}
            """)
            for line in result:
                st.success(line)

    if not any_match:
        st.info("一致する馬は見つかりませんでした。")

else:
    st.error("❌ データに『レース名』カラムが存在しません。")

if not any_match:
    st.info("一致する馬は見つかりませんでした。")

