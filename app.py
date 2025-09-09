import streamlit as st
import pandas as pd

st.set_page_config(page_title="競馬判定アプリ", layout="wide")

st.title("🏇 競馬判定アプリ")

# 🔽 公開済みスプレッドシートのCSVリンク
CSV_URL = "https://docs.google.com/spreadsheets/d/1zZRXYBtqMMw8vSPoRnstItUOXGEkIRa3Gt8eu89V4MU/export?format=csv"

# スプレッドシート読み込み
@st.cache_data(ttl=60)  # 60秒ごとに更新
def load_data():
    df = pd.read_csv(CSV_URL)

    # レース番号を抽出（例: "中山4R" → 4）
    df["レース番号"] = (
        df["レース名"].str.extract(r"(\d+)R")[0]
        .fillna(0)
        .astype(int)
    )
    return df

df = load_data()

# -------------------------------
# 🔽 判定ロジック
# -------------------------------
def check_match(row):
    horse = row["馬名"]
    try:
        num = int(float(row["馬番"])) if pd.notna(row["馬番"]) else None
    except:
        return None
    prev = int(float(row["前走着順"])) if pd.notna(row["前走着順"]) else None

    # 誕生日処理
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
# 🔽 レースごとに表示（競馬場ごと＋レース番号昇順）
# -------------------------------
for place, group_place in df.groupby(df["レース名"].str.replace(r"\d+R", "", regex=True)):
    st.header(f"🏟 {place.strip()}")

    # レース番号順にソート
    for race, group in group_place.sort_values("レース番号").groupby("レース名"):
        st.subheader(f"🏆 {race}")

        any_match = False
        for _, row in group.iterrows():
            result = check_match(row)
            if result:
                any_match = True
                st.markdown(f"**🐴 {row['馬名']}**")
                st.write(f"🔢 馬番: {int(float(row['馬番']))}")
                st.write(f"🏁 前走着順: {row['前走着順']}")
                st.write(f"🎂 誕生日: {row['誕生日']}")
                for line in result:
                    st.success(line)
                st.markdown("---")

        if not any_match:
            st.info("一致する馬は見つかりませんでした。")
