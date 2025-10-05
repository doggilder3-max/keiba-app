import streamlit as st
import pandas as pd
import re
import hashlib

# ===================================
# 🔐 管理者認証設定
# ===================================
ADMIN_PASS = "AdminPass2025!"
def make_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
ADMIN_HASH = make_hash(ADMIN_PASS)

def check_admin():
    """管理者認証（閲覧は誰でもOK）"""
    if "admin_mode" not in st.session_state:
        st.session_state["admin_mode"] = False

    if st.session_state["admin_mode"]:
        return True

    with st.expander("👑 管理者ログイン"):
        password = st.text_input("パスワードを入力", type="password")
        if st.button("ログイン"):
            if make_hash(password) == ADMIN_HASH:
                st.session_state["admin_mode"] = True
                st.success("✅ 管理者モード有効化されました")
            else:
                st.error("❌ パスワードが間違っています")
    return st.session_state["admin_mode"]


# ===================================
# 📊 データ読み込み
# ===================================
CSV_URL = "https://docs.google.com/spreadsheets/d/1zZRXYBtqMMw8vSPoRnstItUOXGEkIRa3Gt8eu89V4MU/export?format=csv"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(CSV_URL)

# ===================================
# 🏇 判定ロジック
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

    # 馬番と前走着順
    if prev and num == prev:
        matches.append(f"✅ 前走着順と馬番が一致（馬番={num}, 前走着順={prev}）")

    # 誕生日の月＋日
    total = month + day
    if num == total:
        matches.append(f"✅ 誕生日の月+日と馬番が一致（{month}+{day}={total}）")

    # 誕生日の数字合計
    digit_sum = sum(int(d) for d in str(month) + str(day))
    if num == digit_sum and num != total:
        matches.append(f"✅ 誕生日の数字合計と馬番が一致（{month}{day}→{digit_sum}）")

    # 日と一致
    if num == day:
        matches.append(f"✅ 誕生日の日と馬番が一致（馬番={num}, 日={day}）")

    return matches if matches else None

# ===================================
# 🔢 レース番号ソート用
# ===================================
def extract_race_number(race_name):
    match = re.search(r"(\d+)R", str(race_name))
    return int(match.group(1)) if match else 999

# ===================================
# 🖥️ メインアプリ
# ===================================
st.set_page_config(page_title="競馬ロジック＆予想アプリ", layout="wide")
st.title("🏇 競馬ロジック＆予想アプリ")

df = load_data()
is_admin = check_admin()

# ===================================
# 🔮 レース表示
# ===================================
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

            # 予想表示
            if "予想" in row and not pd.isna(row["予想"]):
                st.markdown(f"💬 **予想:** {row['予想']}")
            if "コメント" in row and not pd.isna(row["コメント"]):
                st.markdown(f"🗒️ {row['コメント']}")

    if not any_match:
        st.info("一致する馬は見つかりませんでした。")

# ===================================
# ✍️ 管理者専用：予想入力フォーム
# ===================================
if is_admin:
    st.divider()
    st.header("📝 管理者用予想入力フォーム")

    race_name = st.selectbox("レースを選択", sorted(df["レース名"].dropna().unique()))
    race_df = df[df["レース名"] == race_name]
    horse_name = st.selectbox("馬名を選択", race_df["馬名"])
    yoso = st.text_input("予想（例：◎ or ○ or △ など）")
    comment = st.text_area("コメント")

    st.info("※ 現時点ではGoogleスプレッドシートへの直接保存は未実装です。手動でシートに記入してください。")

    if st.button("プレビュー表示"):
        st.success(f"【{race_name}】{horse_name} → {yoso}\n\n{comment}")

