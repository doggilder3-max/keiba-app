import streamlit as st
import pandas as pd
import re
import hashlib

# ===================================
# 🔑 パスワード用ハッシュ生成関数（確認用）
# ===================================
def make_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ここは初回確認用。実行するとターミナル/ログにハッシュが出ます。
# AdminPass2025! と ViewerPass2025! のハッシュを確認して、
# st.secrets["auth"] に保存されているものと一致するか確認してください。
print("管理者(AdminPass2025!):", make_hash("AdminPass2025!"))
print("閲覧者(ViewerPass2025!):", make_hash("ViewerPass2025!"))

# ===================================
# 🔐 パスワード認証
# ===================================
def check_password():
    """ログインフォームを表示し、正しいパスワードか確認"""
    def password_entered():
        pwd = st.session_state["password"]
        hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()

        if hashed_pwd == st.secrets["auth"]["admin_hash"]:
            st.session_state["role"] = "admin"
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        elif hashed_pwd == st.secrets["auth"]["viewer_hash"]:
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
def check_match(row):
    horse = row["馬名"]

    # 馬番
    try:
        num = int(float(row["馬番"]))
    except:
        return None

    # 前走着順
    try:
        prev = int(float(row["前走着順"]))
    except:
        prev = None

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

    # 馬番 = 月+日
    total = month + day
    if num == total:
        matches.append(f"{horse} → ✅ 誕生日の月+日と馬番が一致（{month}+{day}={total}）")

    # 馬番 = 誕生日の数字合計（桁ごと）
    digit_parts = [int(d) for d in str(month) + str(day)]
    digit_sum = sum(digit_parts)
    if num == digit_sum and num != total:
        parts_str = "＋".join(str(d) for d in digit_parts)
        matches.append(f"{horse} → ✅ 誕生日の数字合計と馬番が一致（{parts_str}={digit_sum}）")

    # 馬番 = 日そのもの
    if num == day:
        matches.append(f"{horse} → ✅ 誕生日の日と馬番が一致（馬番={num}, 日={day}）")

    # 馬番 = 日の一桁（ただし28→8のような一致は除外、実際に日が一桁のときのみ）
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
                    🐴 **{row['馬名']}**  
                    🔢 馬番: {int(float(row['馬番'])) if not pd.isna(row['馬番']) else '不明'}  
                    🏁 前走着順: {int(float(row['前走着順'])) if not pd.isna(row['前走着順']) else '不明'}  
                    🎂 誕生日: {row['誕生日']}  
                    """
                )
                for line in result:
                    st.success(line)

        if not any_match:
            st.info("一致する馬は見つかりませんでした。")

    # ログアウトボタン
    if st.button("🚪 ログアウト"):
        st.session_state.clear()
        st.experimental_rerun()
