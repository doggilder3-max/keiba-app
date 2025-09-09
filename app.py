import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="競馬判定アプリ", layout="wide")

st.title("🏇 競馬判定アプリ")

# ====== 数字処理 ======
def calc_digits(birthday):
    try:
        date = datetime.strptime(birthday, "%Y/%m/%d")
    except:
        return None, None, None, None, None

    # 西暦は無視 → 月+日だけ
    md_str = f"{date.month}{date.day}"
    digits = [int(d) for d in md_str]
    total = sum(digits)

    # 途中式（例: 1+2+7）
    formula = "+".join(str(d) for d in digits)

    # 一桁になるまで分解
    digit_sum = total
    steps = []
    while digit_sum >= 10:
        steps.append("+".join(str(d) for d in str(digit_sum)))
        digit_sum = sum(int(d) for d in str(digit_sum))

    return total, digit_sum, date.day, date.month, formula, steps


# ====== 判定関数 ======
def check_match(row):
    try:
        num = int(float(row["馬番"]))  
    except:
        return None

    try:
        prev = int(row["前走着順"])
    except:
        prev = None

    total, digit_sum, day, month, formula, steps = calc_digits(row["誕生日"])
    if total is None:
        return None

    matches = []

    if prev and num == prev:
        matches.append(f"🏆 馬番と前走着順が一致（馬番={num}, 前走着順={prev}）")

    if num == total:
        matches.append(f"🎯 馬番と誕生日の合計が一致（馬番={num}, {formula}={total}）")

    if num == digit_sum:
        if steps:
            matches.append(f"✨ 馬番と誕生日の数字合計が一致（馬番={num}, {formula}={total} → {' → '.join(steps)} → {digit_sum}）")
        else:
            matches.append(f"✨ 馬番と誕生日の数字合計が一致（馬番={num}, {formula}={digit_sum}）")

    if num == day:
        matches.append(f"📅 馬番と誕生日の日が一致（馬番={num}, 日={day}）")

    if num == (day % 10):
        matches.append(f"🔢 馬番と誕生日の日の一桁が一致（馬番={num}, 一桁={day % 10}）")

    return matches if matches else None


# ====== データ読み込み（サンプル: CSVやGoogleスプレッドシートから取得可） ======
data = [
    {"馬名": "アルマーザアミール", "レース名": "中山4R", "馬番": 10, "前走着順": 10, "誕生日": "2021/01/27"},
    {"馬名": "エコロマーベリック", "レース名": "中山4R", "馬番": 12, "前走着順": 12, "誕生日": "2020/03/24"},
]

df = pd.DataFrame(data)

# ====== 表示部分 ======
for _, row in df.iterrows():
    matches = check_match(row)
    if matches:
        with st.container():
            st.markdown(
                f"""
                <div style='padding:15px; margin:10px 0; border-radius:12px; background-color:#1e1e1e; box-shadow:0 2px 5px rgba(0,0,0,0.2)'>
                    <h2 style='color:#f8f8f8'>🐴 {row['馬名']}</h2>
                    <p>📍 レース名: <b>{row['レース名']}</b></p>
                    <p>🔢 馬番: <b>{int(row['馬番'])}</b></p>
                    <p>🏁 前走着順: <b>{row['前走着順']}</b></p>
                    <p>🎂 誕生日: <b>{row['誕生日']}</b></p>
                </div>
                """,
                unsafe_allow_html=True
            )

            for match in matches:
                st.markdown(
                    f"""
                    <div style='padding:10px; margin:5px 0; border-radius:10px; background-color:#204d38; color:#e6ffe6; font-weight:bold'>
                        {match}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
