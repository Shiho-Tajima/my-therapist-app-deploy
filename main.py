import streamlit as st
import openai
import os

from dotenv import load_dotenv
load_dotenv()  # .env の内容を環境変数に反映

# APIキー設定
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
openai.api_key = api_key

fine_tuned_model = "ft:gpt-4o-mini-2024-07-18:personal::C9x8qBFQ:ckpt-step-73"

st.title("AIセラピスト")

# 会話履歴初期化
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "あなたはクライエント中心療法で対話するセラピストです。"}
    ]

# リセットボタン（キーを指定）
if st.button("会話をリセット", key="reset_button"):
    st.session_state["messages"] = [
        {"role": "system", "content": "あなたはクライエント中心療法で対話するセラピストです。"}
    ]
    st.experimental_rerun()  # ページを再描画してリセットを反映

# --- ユーザー入力をフォームにして送信後にクリア ---
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input("相談内容を入力してください:")
    submit_button = st.form_submit_button("送信")  # keyは不要

if submit_button and user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    response = openai.chat.completions.create(
        model=fine_tuned_model,
        messages=st.session_state["messages"]
    )
    
    assistant_reply = response.choices[0].message.content
    st.session_state["messages"].append({"role": "assistant", "content": assistant_reply})

# 会話履歴表示（スクロール可能にする）
chat_container = st.container()
chat_markdown = ""
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        chat_markdown += f"**あなた:** {msg['content']}\n\n"
    elif msg["role"] == "assistant":
        chat_markdown += f"**セラピスト:** {msg['content']}\n\n"

# 最大高さ500pxでスクロールバーを設置
chat_container.markdown(
    f'<div style="max-height:300px; overflow-y:auto; border:1px solid #ddd; padding:10px;">{chat_markdown}</div>',
    unsafe_allow_html=True
)
