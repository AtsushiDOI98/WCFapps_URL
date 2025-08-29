import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Google Sheets 認証
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
gc = gspread.authorize(credentials)

# スプレッドシートを開く（名前 or ID）
spreadsheet = gc.open("Group_Assignments")
worksheet = spreadsheet.sheet1

# グループとURL
groups = {
    "Model": "https://l2-writing-platform-model.streamlit.app/",
    "AI": "https://l2-writing-platform.streamlit.app/",
    "Control": "https://l2-writing-platform-control.streamlit.app/"
}

# 既存データを取得
data = worksheet.get_all_records()
df = pd.DataFrame(data) if data else pd.DataFrame(columns=["Name", "Group", "Timestamp"])

st.markdown(
    "名前を入力してください。  \n"
    "入力すると、あなたのリンクが表示されます。  \n"
    "そちらをクリックして始めてください。"
)

name = st.text_input("名前:", "")


if st.button("スタート"):
    if name in df["Name"].values:
        # 既に割り当て済みの場合は同じグループに誘導
        group = df.loc[df["Name"] == name, "Group"].values[0]
    else:
        # 各グループの人数を数えて最小のところに振り分け
        counts = df["Group"].value_counts().to_dict()
        group = min(groups.keys(), key=lambda g: counts.get(g, 0))
        new_row = {
            "Name": name,
            "Group": group,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        worksheet.append_row(list(new_row.values()))
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    st.success(f"{group} グループに割り当てられました。")
    st.markdown(f"[ここをクリックして開始する]({groups[group]})")
