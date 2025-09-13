"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# 1. ライブラリの読み込み
############################################################
# 「.env」ファイルから環境変数を読み込むための関数
from dotenv import load_dotenv
import streamlit as st
import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import textwrap
from html import escape
import streamlit.components.v1 as components
import time
import streamlit as st

load_dotenv()
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# **********************************************
# ログイン後のメイン画面
# **********************************************

# APIキー設定
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
openai.api_key = api_key

fine_tuned_model = "ft:gpt-4o-mini-2024-07-18:personal::CFElHbRh"


# 画像（ロゴ）を表示
# スクリプトの場所を基準に画像パスを作成
BASE_DIR = os.path.dirname(__file__)
logo_img_path = os.path.join(BASE_DIR, "data", "images", "logo.png")

# カラム比率1:2:1で作成
col1, col2 = st.columns([3,1])

with col2:
    # --- ここを修正: 幅を固定してスマホでも小さく表示 ---
    st.image(logo_img_path, width=150)  # use_container_width=True は外す

# **********************************************
# チュートリアル（１）
# **********************************************

# 初期化（まだキーがなければ False を設定）
if "greeted" not in st.session_state:
    st.session_state["greeted"] = False

if not st.session_state["greeted"]:
    st.session_state["greeted"] = False
    # スクリプトの場所を基準に画像パスを作成
    BASE_DIR = os.path.dirname(__file__)
    ai_img_path = os.path.join(BASE_DIR, "data", "images", "ai.png")

    # カラム比率1:2:1で作成
    col1, col2, col3 = st.columns([2,1,2])

    with col2:
        # --- ここを修正: 幅を固定してスマホでも小さく表示 ---
        st.image(ai_img_path, width=150)  # use_container_width=True は外す
        
    message = "こんにちは、私はあなたのセラピストです。どんなことでも構いませんので、気軽にお話しくださいね。\n\n以下に何か入力して、送信をしてみてください。"

    # プレースホルダー作成
    placeholder = st.empty()

    # 表示用文字列
    display_text = ""

    for char in message:
        display_text += char
        placeholder.info(display_text, icon=":material/info:")  # st.info をプレースホルダーで更新
        time.sleep(0.05)
    
    st.session_state["greeted"] = True

    # 空行で間隔を作る
    st.write("")


# **********************************************
# 入力、送信ボタン、会話履歴表示
# **********************************************

# --- ユーザー入力フォーム ---
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input("相談内容を入力してください。\n\n（例: 仕事のストレスについて相談したいです。）")
    submit_button = st.form_submit_button("送信")

# --- セッションステートの初期化 ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if submit_button and user_input:
    # # --- チュートリアル（２） ---
    # if "greeted2" not in st.session_state:
    #     st.session_state["greeted2"] = False

    # if not st.session_state["greeted2"]:
    #     message = "入力ありがとうございます！\n\nもう一度入力して、このまま会話を続けてみましょう!\n\n【会話をクリア】ボタンで会話をリセットもできますよ。"
    #     placeholder = st.empty()
    #     display_text = ""
    #     for char in message:
    #         display_text += char
    #         placeholder.info(display_text, icon=":material/info:")
    #         time.sleep(0.05)

    #     st.session_state["greeted2"] = True
    #     st.write("")

    # ✅ ユーザーの入力は必ず追加する
    st.session_state["messages"].append({"role": "user", "content": user_input})


if submit_button and user_input:
    with st.spinner("セラピストが考えています…"):
        time.sleep(0.5)

        if "messages" not in st.session_state:
            st.session_state["messages"] = []
        messages_for_llm = st.session_state["messages"].copy()

        # --- system メッセージで振る舞い方を指示 ---
        messages_for_llm.append({
            "role": "system",
            "content": """
            あなたは反射や要約、解釈などの技法を活用しながらクライエント中心療法で対話を行うセラピストです。
            クライエントの悩みや感情に寄り添い、共感的に対話をしてください。
            応答の際に「（セラピスト）」や「（クライエント）」のようなラベルは付けず、
            実際に温厚で優しい人が話しているような、自然な文章だけで返答してください。

            # 制約事項
            ・積極的な問題解決を促すのではなく、クライエントの感情に寄り添い、共感的に対応すること。
            ・クライエントに求められた時以外は、アドバイスや提案をしないこと。
            ・「～するべき」など断定的な言い方はしないこと。
            """
        })

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
    # 新しいセッションIDを生成
    st.session_state["session_id"] = datetime.now().strftime("%Y%m%d-%H%M%S")
    # メッセージ履歴を初期化（システムメッセージのみ）
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