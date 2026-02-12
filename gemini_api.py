import os
import json
import google.generativeai as genai
import streamlit as st # ★追加：Streamlitの機能を使う
from dotenv import load_dotenv

# ---------------------------------------------------------
# APIキーの読み込み（ローカル・クラウド両対応版）
# ---------------------------------------------------------

# 1. まずローカルの .env を読み込む（ローカル開発用）
load_dotenv()

# 2. APIキーを取得するロジック
# Streamlit Cloud上なら st.secrets から、ローカルなら os.getenv から取る
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = os.getenv("GEMINI_API_KEY")
except FileNotFoundError:
    # ローカルでsecrets.tomlがない場合は.envに頼る
    api_key = os.getenv("GEMINI_API_KEY")

# ---------------------------------------------------------
# 以下は変更なし（ただしモデル設定などはそのまま）
# ---------------------------------------------------------

# APIキーがない場合のエラーチェック
if not api_key:
    # エラーが出ても画面が落ちないようにダミーを設定（本番はエラー推奨）
    print("Warning: API Keyが見つかりません")
else:
    genai.configure(api_key=api_key)

# 動作を軽くするため Flash モデルを使用
# ※注意: gemini-3系がまだ安定していない場合は gemini-1.5-flash に戻してください
model = genai.GenerativeModel('gemini-1.5-flash') 

def call_judge_ai(prompt_text):
    """
    プロンプトを送信し、JSONとしてパースして返す関数
    """
    try:
        response = model.generate_content(prompt_text)
        # JSONの前後に ```json ... ``` がつくことがあるので削除
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_text)
    except Exception as e:
        # エラー時のフォールバック（開発用）
        return {
            "status": "error",
            "reason": f"AI通信エラー: {e}",
            "girl_reply": "（通信エラーにより聞こえない…）",
            "damage_score": 0
        }
