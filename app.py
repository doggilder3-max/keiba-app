import streamlit as st
import pandas as pd
import re
import hashlib
import math

# ===================================
# 🔐 パスワード認証
# ===================================
ADMIN_PASS = "AdminPass2025!"
VIEWER_PASS = "ViewerPass2025!"

def make_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

ADMIN_HASH = make_hash(ADMIN_PASS)
VIEWER_HASH = make_hash(VIEWER_PASS)

def check_password():
    def password_entered():
        pwd = st.session_state["password"]
        hashed_pwd = make_hash(pwd)
        if hashed_pwd == ADMIN_HASH:
            st.session_state["role"] = "admin"
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        elif hashed_pwd == VIEWER_HASH:
            st.session_state["role"] = "viewer"
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔑 パスワードを入力してください:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔑 パスワードを入力してください:", type="password", on_change=password_entered, key="password")
        st.error("❌ パスワードが間違っています")
        return False
    else:
        return True

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
def to_int_safe(value):
    """NaNや空白を安全に整数化"""
    try:
        if pd.isna(value):
            return None
        f = float(value)
        if math.isnan(f):
            return None
        return int(f)
    except:
        return None

def check_match(row):
    horse = row.get("馬名", "")

    num = to_int_safe(row.get("馬番"))
    prev = to_int_safe(row.get("前走着順"))

    birthday = str(row.get("誕生日", "")).replace("月", "-").replace("日", "").strip()
    month = day = None
    try:
        if "/" in birthday:
            parts = birthday.split("/")
            if len(parts) == 3:
                year, month, day = map(int, parts)
            elif len(parts) == 2:
                month, day = map(int, parts)
        elif "-" in birthday:
            parts = birthday.split("-")
            month, day = map(int, parts)
    except:
        month = day = None

    if num is None:
        return None

    matches = []

    # 前走着順と馬番一致
    if prev is not None and num == prev:
        matches.append(f"{horse} → ✅ 前走着順と馬番が一致（馬番={num}, 前走着順={prev}）")

    if month is not None and day is not None:
        # 誕生日の月+日と馬番一致
        total = month + day
        if num == total:
            matches.append(f"{horse} → ✅ 誕生日の月+日と馬番が一致（{month}+{day}={total}）")

        # 誕生日の数字合計と馬番一致（ただし月+日とは別）
        digit_sum = sum(int(d) for d in f"{month}{day}")
        if num == digit_sum and num != total:
            parts_str = "＋".join(str(d) for d in f"{month}{day}")
            matches.append(f"{horse} → ✅ 誕生日の数字合計と馬番が一致（{parts_str}={digit_sum}）")

        # 誕生日の日と馬番一致
        if num == day:
            matches.append(f"{horse} → ✅ 誕生日の日と馬番が一致（馬番={num}, 日={day}）")

        # 一桁の日と馬番一致（重複判定も可）
        if day < 10 and num == day:
            matches.append(f"{horse} → ✅ 誕生日が一桁の日と馬番が一致（馬番={num}, 日={day}）")

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
st.set_page_config(page_title="競馬判定アプリ", layout="wide")

if check_password():
    role = st.session_state["role"]

    if role == "admin":
        st.title("👑 管理者ページ - 競馬判定アプリ")
    else:
        st.title("👥 閲覧者ページ - 競馬判定アプリ")

    df = load_data()

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
                    🐴 **{row.get('馬名', '')}**  
                    🔢 馬番: {to_int_safe(row.get('馬番')) or '不明'}  
                    🏁 前走着順: {to_int_safe(row.get('前走着順')) or '不明'}  
                    🎂 誕生日: {row.get('誕生日', '')}  
                    """
                )
                for line in result:
                    st.success(line)

        if not any_match:
            st.info("一致する馬は見つかりませんでした。")

    if st.button("🚪 ログアウト"):
        st.session_state.clear()
