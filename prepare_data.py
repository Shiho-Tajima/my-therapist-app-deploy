"""
このファイルは、fine_tune.pyでファインチューニングを実施するための事前処理が記述されたファイルです。
（学習データのcsvをjsonlに変換します。）
"""

import pandas as pd
import json

# 仮のトークン上限（モデルによって変更）
MAX_TOKENS = 16384

# 入力CSVと出力JSONLのパスを修正
input_csv = r"D:\therapist_app\data\input.csv"
output_jsonl = r"D:\therapist_app\data\output.jsonl"

# CSV読み込み
df = pd.read_csv(input_csv)

# =============================
# NaNをNoneに変換（JSON用にnullとして出力される）
df = df.where(pd.notnull(df), None)
# =============================

# JSONL用リスト
jsonl_data = []

# systemメッセージ
system_message = {
    "role": "system",
    "content": "あなたはクライエント中心療法を専門とする心理専門職として、悩み相談の対応をするアシスタントAIです。"
}

# sessionごとに処理
for session_id, session_df in df.groupby("session_id"):
    messages_history = [system_message.copy()]
    
    for i in range(len(session_df)):
        row = session_df.iloc[i]
        role = "user" if row["speaker"] == "client" else "assistant"
        
        messages_history.append({
            "role": role,
            "content": row["text"]
        })
        
        # トークン数の概算チェック（空白で分割）
        total_tokens = sum(len(msg["content"].split()) for msg in messages_history)
        if total_tokens > MAX_TOKENS:
            raise ValueError(f"セッションID {session_id} がトークン上限を超えています（概算 {total_tokens} トークン）")
        
        # 最新のアシスタント発言で1つの学習例を作成
        if role == "assistant" and i > 0:
            # そのまま messages 配列を Example として追加
            jsonl_data.append({
                "messages": messages_history.copy()  # copy で履歴を固定
            })

# JSONLとして書き込み
with open(output_jsonl, "w", encoding="utf-8") as f:
    for entry in jsonl_data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("JSONLファイルの生成が完了しました。")
