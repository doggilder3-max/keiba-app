import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="競馬アプリ", layout="wide")

st.title("🏇 競馬判定アプリ")

# ✅ GoogleスプレッドシートのCSV URL
sheet_url = "https://docs.google.com/spreadsheets/d/1zZRXYBtqMMw8vSPoRnstItUOXGEkIRa3Gt8eu89V4MU/export?format=csv"

# ✅ CSV読み込み
df = pd.read_csv(sheet_url)

# 判定結果を保存
all_results = []

# ✅ 判定処理
for idx, row in df.iterrows():
    try:
        race_name = str(row["レース名"]).strip()
        horse_name = str(row["馬名"]).strip()
        uma_num = str(row["馬番"]).replace(" ", "").replace("　", "")
        prev_rank = str(row["前走着順"]).replace(" ", "").replace("　", "")
        birthday_raw = str(row["誕生日"]).strip()

        if not uma_num.isdigit():
            continue

        uma_num = int(uma_num)

        # 誕生日処理
        birthday = None
        if birthday_raw and birthday_raw.lower() != "nan":
            try:
                birthday = pd.to_datetime(birthday_raw, errors="coerce")
            except:
                birthday = None

        # 一致条件チェック
        matches = []

        # ① 馬番 = 前走着順
        if prev_rank.isdigit() and uma_num == int(prev_rank):
            matches.append(f"前走着順と馬番が一致（{uma_num}）")

        if birthday is not None:
            m, d = birthday.month, birthday.day

            # ② 馬番 = 誕生日の月+日（桁ごと合計）
            digit_sum = sum(int(x) for x in str(m) + str(d))
            if uma_num == digit_sum:
                matches.append(f"誕生日の月+日と馬番が一致（{m}月{d}日 → {digit_sum}）")

            # ③ 馬番 = 誕生日の日
            if uma_num == d:
                matches.append(f"誕生日の日と馬番が一致（{m}月{d}日）")

            # ④ 馬番 = 誕生日の日の一桁
            if uma_num == (d % 10):
                matches.append(f"誕生日の日の一桁と馬番が一致（{m}月{d}日 → {d % 10}）")

        # ✅ 一致があれば保存
        if matches:
            all_results.append({
                "race": race_name,
                "horse": horse_name,
                "uma": uma_num,
                "results": " / ".join(matches)
            })

    except Exception as e:
        continue

# ✅ レースごとに区切って表示
if all_results:
    result_df = pd.DataFrame(all_results)

    for race in result_df["race"].unique():
        st.subheader(f"📌 {race}")
        race_df = result_df[result_df["race"] == race]

        for _, r in race_df.iterrows():
            st.markdown(f"""
            <div style="border:2px solid #4CAF50; padding:15px; margin:10px; border-radius:10px; background:#f9fff9;">
                <h3>🐴 {r['horse']}（馬番 {r['uma']}）</h3>
                <p style="font-size:18px; color:#333;">✅ {r['results']}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("⚠ 一致する判定結果はありませんでした。")
