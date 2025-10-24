import streamlit as st
import pandas as pd
import re

# ===================================
# 📊 データ読み込み
# ===================================
CSV_URL = "https://docs.google.com/spreadsheets/d/1zZRXYBtqMMw8vSPoRnstItUOXGEkIRa3Gt8eu89V4MU/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        return pd.read_csv(CSV_URL)
    except Exception as e:
        st.error(f"データ読み込み失敗: {e}")
        return pd.DataFrame()

# ===================================
# 判定ロジック（誕生日表記ゆれ対応版）
# ===================================
def check_match(row):
    horse = row["馬名"]

    try:
        num = int(float(row["馬番"]))
    except:
        return None

    try:
        prev = int(float(row["前走着順"]))
    except:
        prev = None

    # 誕生日整形（例： '3月12日' → '3-12' → month=3, day=12）
    birthday = str(row["誕生日"])
    birthday_clean = re.sub(r"[^0-9/-]", "", birthday)  # 数字と「/」「-」以外削除

    # スラッシュ・ハイフン両対応
    if "/" in birthday_clean:
        parts = birthday_clean.split("/")
    elif "-" in birthday_clean:
        parts = birthday_clean.split("-")
    else:
        return None

    # 年が入っていたら無視（3つある場合は後ろ2つだけ使う）
    if len(parts) == 3:
        parts = parts[1:]

    try:
        month = int(parts[0])
        day = int(parts[1])
    except:
        return None

    matches = []

    # 1️⃣ 前走着順と馬番が一致
    if prev and num == prev:
        matches.append(f"{horse} - 前走着順と馬番が一致 (馬番={num}, 前走着順={prev})")

    # 2️⃣ 月＋日 が馬番と一致
    total = month + day
    if num == total:
        matches.append(f"{horse} - 誕生日の月+日と馬番が一致 ({month}+{day}={total})")

    # 3️⃣ 各数字の合計が馬番と一致
    digits_only = re.sub(r"[^0-9]", "", str(month) + str(day))
    digit_parts = [int(d) for d in digits_only] if digits_only else []
    digit_sum = sum(digit_parts)

    if digit_parts and num == digit_sum and num != total:
        parts_str = "＋".join(str(d) for d in digit_parts)
        matches.append(f"{horse} - 誕生日の数字合計と馬番が一致 ({parts_str}={digit_sum})")

    # 4️⃣ 日付が馬番と一致
    if num == day:
        matches.append(f"{horse} - 誕生日の日と馬番が一致 (馬番={num}, 日={day})")

    # 5️⃣ 日付が一桁かつ馬番が一致
    if day < 10 and num == day:
        matches.append(f"{horse} - 誕生日が一桁の日と馬番が一致 (馬番={num}, 日={day})")

    return matches if matches else None

# ===================================
# レース番号ソート用
# ===================================
def extract_race_number(race_name):
    match = re.search(r"(\d+)R", str(race_name))
    return int(match.group(1)) if match else 999

# ===================================
# メインアプリ
# ===================================
st.set_page_config(page_title="競馬判定アプリ", layout="wide")
st.title("競馬判定アプリ")

# データ読み込み
df = load_data()
if df.empty:
    st.stop()

# 検索・フィルター
search_horse = st.text_input("馬名検索 (部分一致可)")
race_filter = st.selectbox("レースを選択", ["全レース"] + sorted(df["レース名"].dropna().unique(), key=extract_race_number))

if race_filter != "全レース":
    df = df[df["レース名"] == race_filter]
if search_horse:
    df = df[df["馬名"].str.contains(search_horse, case=False, na=False)]

# レースごとのアコーディオン表示
for race in sorted(df["レース名"].dropna().unique(), key=extract_race_number):
    group = df[df["レース名"] == race]

    with st.expander(f"{race} の詳細"):
        any_match = False
        for _, row in group.iterrows():
            result = check_match(row)
            if result:
                any_match = True
                st.markdown(
                    f"""
                    **馬名:** {row['馬名']}  |  
                    **馬番:** {int(float(row['馬番'])) if not pd.isna(row['馬番']) else '不明'}  |  
                    **前走着順:** {int(float(row['前走着順'])) if not pd.isna(row['前走着順']) else '不明'}  |  
                    **誕生日:** {row['誕生日']}
                    """
                )
                for line in result:
                    st.success(line)
        if not any_match:
            st.info("一致する馬は見つかりませんでした。")

# データ再読み込みボタン
if st.button("データ再読み込み"):
    st.cache_data.clear()
    st.rerun()
