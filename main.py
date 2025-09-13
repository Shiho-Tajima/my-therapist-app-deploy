"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# 1. ライブラリの読み込み
############################################################
from dotenv import load_dotenv
import streamlit as st
import openai
import os
import json
from datetime import datetime
from html import escape
import streamlit.components.v1 as components
import time

load_dotenv()
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# **********************************************
# ログイン後のメイン画面
# **********************************************

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
openai.api_key = api_key

fine_tuned_model = "ft:gpt-4o-mini-2024-07-18:personal::CFElHbRh"

BASE_DIR = os.path.dirname(__file__)
logo_img_path = os.path.join(BASE_DIR, "data", "images", "logo.png")

col1, col2 = st.columns([3,1])
with col2:
    st.image(logo_img_path, width=150)

# **********************************************
# チュートリアル（１）
# **********************************************

if "greeted" not in st.session_state:
    st.session_state["greeted"] = False

if not st.session_state["greeted"]:
    BASE_DIR = os.path.dirname(__file__)
    ai_img_path = os.path.join(BASE_DIR, "data", "images", "ai.png")
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        st.image(ai_img_path, width=150)
        
    message = "こんにちは、私はあなたのセラピストです。どんなことでも構いませんので、気軽にお話しくださいね。\n\n以下に何か入力して、送信をしてみてください。"
    placeholder = st.empty()
    display_text = ""
    for char in message:
        display_text += char
        placeholder.info(display_text, icon=":material/info:")
        time.sleep(0.05)
    
    st.session_state["greeted"] = True
    st.write("")

# **********************************************
# 入力、送信ボタン、会話履歴表示
# **********************************************

with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input(
        "相談内容を入力してください。\n\n（例: 仕事のストレスについて相談したいです。）"
    )
    submit_button = st.form_submit_button("送信")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if submit_button and user_input:
    # ✅ ユーザー入力を必ず追加
    st.session_state["messages"].append({"role": "user", "content": user_input})

if submit_button and user_input:
    with st.spinner("セラピストが考えています…"):
        time.sleep(0.5)

        # 過去会話から「重要情報のみ」を要約
        def summarize_important(messages):
            summary_prompt = "次の会話履歴から、家族歴、仕事、生育歴、性格、価値観、趣味、生活状況などカウンセリングに重要な情報だけを要約してください。文章で簡潔に出力してください。\n\n"
            conversation_text = "\n".join([m["content"] for m in messages if m["role"]=="user"])
            return conversation_text  # 後でLLMに渡して要約させる

        important_info = summarize_important(st.session_state["messages"][:-1])  # 直前入力以外

        # LLMに渡すメッセージ作成
        messages_for_llm = [
            {"role": "system", "content": """
            あなたは反射や要約、解釈などの技法を活用しながらクライエント中心療法で対話を行うセラピストです。
            クライエントの悩みや感情に寄り添い、共感的に対話してください。
            応答は必ずユーザー向けで、独り言や内省を文章化したものは絶対に出力しないこと。

            # 制約事項
            ・直近のユーザー発言と重要情報の要約のみを参照して返答すること
            ・アドバイスや提案はクライエントが求めた場合のみ行うこと
            ・断定的な表現（～すべき）やラベル付け（（セラピスト）など）は使用しないこと
            ・応答は必ず自然な文章で、共感や質問のみで構成すること
            """}
        ]

        # 直近ユーザー発言 + 重要情報を追加
        if important_info.strip():
            messages_for_llm.append({"role": "system", "content": f"過去の重要情報の要約:\n{important_info}"})
        messages_for_llm.append(st.session_state["messages"][-1])  # 直近発言

        # LLM呼び出し
        response = openai.chat.completions.create(
            model=fine_tuned_model,
            messages=messages_for_llm
        )
        assistant_reply = response.choices[0].message.content
        st.session_state["messages"].append({"role": "assistant", "content": assistant_reply})

# --- 会話履歴表示 ---
chat_container = st.container()
chat_html_parts = []

for msg in st.session_state["messages"]:
    if msg["role"] == "system":
        continue
    content = escape(msg["content"]).replace("\n", "<br>")
    if msg["role"] == "user":
        bubble = f"""
        <div style="text-align:right; margin:5px 0;">
        <div style="display:inline-block; background-color:#DCF8C6;
        padding:8px 12px; border-radius:15px 15px 0px 15px; max-width:70%;
        word-wrap: break-word;">{content}</div></div>
        """
    elif msg["role"] == "assistant":
        bubble = f"""
        <div style="text-align:left; margin:5px 0;">
        <div style="display:inline-block; background-color:#F1F0F0;
        padding:8px 12px; border-radius:15px 15px 15px 0px; max-width:70%;
        word-wrap: break-word;">{content}</div></div>
        """
    chat_html_parts.append(bubble)

chat_html = "".join(chat_html_parts)

components.html(
    f"""
    <div id="chat-container" style="max-height:150px; overflow-y:auto;
    border:1px solid #ddd; padding:10px; background-color:#E6F7FF;">
        {chat_html}
    </div>
    <script>
        var chatBox = document.getElementById("chat-container");
        if (chatBox) {{
            chatBox.scrollTop = chatBox.scrollHeight;
        }}
    </script>
    """,
    height=170,
)

# 会話クリアボタン
if st.button("会話をクリア", key="reset_button"):
    st.session_state["session_id"] = datetime.now().strftime("%Y%m%d-%H%M%S")
    st.session_state["messages"] = [
        {"role": "system", "content": "あなたは反射や要約、解釈などの技法を活用しながらクライエント中心療法で対話を行うセラピストです。クライエントの悩みや感情に寄り添い、共感的に対応してください。セラピスト自身が悩み相談をすることはしないでください。"}
    ]
    try:
        st.rerun()
    except AttributeError:
        pass

st.write("")
st.write("")
st.write("")
st.write("")
st.write("")