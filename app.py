import streamlit as st
import pandas as pd
import re
import hashlib

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
    """ログインフォームを表示し、正しいパスワードか確認"""
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
    df = pd.read_csv(CSV_URL)
    # 馬番・前走着順を必ず数値型に変換（空白や文字列はNaNに変換）
    df["馬番"] = pd.to_numeric(df["馬番"], errors="coerce")
    df["前走着順"] = pd.to_numeric(df["前走着順"], errors="coerce")
    return df

# ===================================
# 🏇 判定ロジック
# ===================================
def check_match(row):
    horse = row.get("馬名", "")
    num = row.get("馬番")
    prev = row.get("前走着順")
    birthday = str(row.get("誕生日", "")).replace("月", "-").replace("日", "").strip()

    if pd.isna(num):
        return None  # 馬番がない場合は判定不可

    # 誕生日のパース
    try:
        year, month, day = map(int, birthday.split("/"))
    except:
        try:
            month, day = map(int, birthday.split("-"))
        except:
            month, day = None, None

    if month is None or day is None:
        return None

    matches = []

    # 前走着順と馬番
    if not pd.isna(prev) and int(num) == int(prev):
        matches.append(f"{horse} → ✅ 前走着順と馬番が一致（馬番={int(num)}, 前走着順={int(prev)}）")

    # 誕生日の月+日
    total = month + day
    if int(num) == total:
        matches.append(f"{horse} → ✅ 誕生日の月+日と馬番が一致（{month}+{day}={total}）")

    # 誕生日の数字合計
    digit_parts = [int(d) for d in str(month) + str(day)]
    digit_sum = sum(digit_parts)
    if int(num) == digit_sum and int(num) != total:
        parts_str = "＋".join(str(d) for d in digit_parts)
        matches.append(f"{horse} → ✅ 誕生日の数字合計と馬番が一致（{parts_str}={digit_sum}）")

    # 誕生日の日と馬番
    if int(num) == day:
        matches.append(f"{horse} → ✅ 誕生日の日と馬番が一致（馬番={int(num)}, 日={day}）")

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

    st.title("👑 管理者ページ - 競馬判定アプリ" if role=="admin" else "👥 閲覧者ページ - 競馬判定アプリ")

    df = load_data()

    for race in sorted(df["レース名"].dropna().unique(), key=extract_race_number):
        group = df[df["レース名"] == race]

        st.subheader(f"🏆 {race}")

        any_match = False
        for _, row in group.iterrows():
            result = check_match(row)
            if result:  # リストが返ってきた場合に必ず表示
                any_match = True
                st.markdown(
                    f"""
                    🐴 **{row['馬名']}**  
                    🔢 馬番: {int(row['馬番']) if not pd.isna(row['馬番']) else '不明'}  
                    🏁 前走着順: {int(row['前走着順']) if not pd.isna(row['前走着順']) else '不明'}  
                    🎂 誕生日: {row['誕生日']}  
                    """
                )
                for line in result:
                    st.success(line)

        if not any_match:
            st.info("一致する馬は見つかりませんでした。")

    if st.button("🚪 ログアウト"):
        st.session_state.clear()
