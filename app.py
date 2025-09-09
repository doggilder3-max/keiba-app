import streamlit as st
import pandas as pd

# -------------------------------
# 🔽 データ読み込み
# -------------------------------
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTOFgL4669h-1mjHREgNm5izTPL_nl0t786YKH-igsSjCSPXbguBxCex_5dTapuTXFusvC3avQfjiCo/pub?output=csv"
    df = pd.read_csv(url)
    return df

df = load_data()

# -------------------------------
# 🔽 安全な数値変換
# -------------------------------
def safe_int(value):
    """数値に変換できれば int, できなければ None"""
    try:
        return int(float(value))
    except:
        return None

# -------------------------------
# 🔽 判定ロジック
# -------------------------------
def check_match(row):
    horse = row["馬名"]
    num = safe_int(row["馬番"])
    prev = safe_int(row["前走着順"])

    # 誕生日の整形
    birthday = str(row["誕生日"]).replace("月", "-").replace("日", "").strip()
    try:
        year, month, day = map(int, birthday.split("/"))
    except:
        try:
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

    # 馬番 = 日そのもの
    if num == day:
        matches.append(f"{horse} → ✅ 誕生日の日と馬番が一致（日={day}）")

    # 馬番 = 日の一桁
    if num == (day % 10):
        matches.append(f"{horse} → ✅ 誕生日の日の一桁と馬番が一致（日の一桁={day % 10}）")

    return matches if matches else None

# -------------------------------
# 🔽 表示処理
# -------------------------------
st.title("🏇 ロジック一致チェック")

for race_name, group in df.groupby("レース名"):
    st.subheader(f"🏆 {race_name}")

    found = False
    for _, row in group.iterrows():
        result = check_match(row)
        if result:
            found = True
            st.write(f"🐴 {row['馬名']}")
            st.write(f"🔢 馬番: {safe_int(row['馬番'])}")
            st.write(f"🏁 前走着順: {row['前走着順']}")
            st.write(f"🎂 誕生日: {row['誕生日']}")
            st.write("")  # 改行
            for r in result:
                st.write(r)
            st.write("---")

    if not found:
        st.write("一致する馬は見つかりませんでした。")
