import streamlit as st
import pandas as pd
import re

# ===================================
# データ読み込み（GoogleスプレッドシートCSV形式）
# ===================================
SHEET_URL = "スプレッドシートCSV公開URL"  # GoogleスプレッドシートをCSV公開したURL
MAIN_SHEET_NAME = "Sheet1"  # 元データシート名
PREDICT_SHEET_NAME = "Sheet2"  # 予想・結果シート名

@st.cache_data(ttl=60)
def load_sheet(sheet_url, sheet_name, predict=False):
    try:
        url = f"{sheet_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(url)
        # Sheet2が空の場合は列だけ定義して空DataFrameにする
        if predict and df.empty:
            df = pd.DataFrame(columns=["レース名", "馬名", "予想印", "コメント", "結果"])
        return df
    except Exception as e:
        st.warning(f"{sheet_name} 読み込み失敗: {e}")
        if predict:
            return pd.DataFrame(columns=["レース名", "馬名", "予想印", "コメント", "結果"])
        return pd.DataFrame()

df_main = load_sheet(SHEET_URL, MAIN_SHEET_NAME)
df_predict = load_sheet(SHEET_URL, PREDICT_SHEET_NAME, predict=True)

# ===================================
# 判定ロジック
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

    birthday = str(row["誕生日"]).replace("月", "-").replace("日", "").strip()
    try:
        year, month, day = map(int, birthday.split("/"))
    except:
        try:
            month, day = map(int, birthday.split("-"))
        except:
            return None

    matches = []

    if prev and num == prev:
        matches.append(f"{horse} - 前走着順と馬番が一致 (馬番={num}, 前走着順={prev})")

    total = month + day
    if num == total:
        matches.append(f"{horse} - 誕生日の月+日と馬番が一致 ({month}+{day}={total})")

    digit_parts = [int(d) for d in str(month) + str(day)]
    digit_sum = sum(digit_parts)
    if num == digit_sum and num != total:
        parts_str = "＋".join(str(d) for d in digit_parts)
        matches.append(f"{horse} - 誕生日の数字合計と馬番が一致 ({parts_str}={digit_sum})")

    if num == day:
        matches.append(f"{horse} - 誕生日の日と馬番が一致 (馬番={num}, 日={day})")

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
# Streamlit表示
# ===================================
st.set_page_config(page_title="競馬判定＆予想アプリ", layout="wide")
st.title("競馬判定＆予想アプリ")

if df_main.empty:
    st.warning("元データが読み込めません。")
    st.stop()

# 検索・フィルター
search_horse = st.text_input("馬名検索 (部分一致可)")
race_filter = st.selectbox("レースを選択", ["全レース"] + sorted(df_main['レース名'].dropna().unique(), key=extract_race_number))

df_filtered = df_main.copy()
if race_filter != "全レース":
    df_filtered = df_filtered[df_filtered['レース名'] == race_filter]
if search_horse:
    df_filtered = df_filtered[df_filtered['馬名'].str.contains(search_horse, case=False, na=False)]

# 判定ロジック適用
df_filtered['一致'] = df_filtered.apply(lambda row: check_match(row) is not None, axis=1)
df_matched = df_filtered[df_filtered['一致']]

# 予想・結果シートと結合
df_display = df_matched.merge(df_predict, on=["レース名", "馬名"], how="left")

# レースごとのアコーディオン表示
for race in sorted(df_display['レース名'].dropna().unique(), key=extract_race_number):
    group = df_display[df_display['レース名'] == race]

    with st.expander(f"{race} の詳細"):
        if group.empty:
            st.info("一致する馬は見つかりませんでした。")
            continue

        for _, row in group.iterrows():
            st.markdown(
                f"**馬名:** {row['馬名']}  |  **馬番:** {int(float(row['馬番'])) if not pd.isna(row['馬番']) else '不明'}  |  "
                f"**前走着順:** {int(float(row['前走着順'])) if not pd.isna(row['前走着順']) else '不明'}  |  **誕生日:** {row['誕生日']}"
            )

            # 判定一致内容
            matches = check_match(row)
            if matches:
                for line in matches:
                    st.success(line)

            # 予想・コメント・結果（Sheet2が空でもエラーにならない）
            st.markdown(
                f"**予想印:** {row.get('予想印', '')}  |  **コメント:** {row.get('コメント', '')}  |  **結果:** {row.get('結果', '')}"
            )

# データ再読み込みボタン
if st.button("データ再読み込み"):
    st.cache_data.clear()
    st.experimental_rerun()

