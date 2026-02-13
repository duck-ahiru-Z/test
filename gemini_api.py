import os
import json
import google.generativeai as genai
import streamlit as st  # ★これを忘れずに！
from dotenv import load_dotenv

# 1. ローカル開発用に .env を読み込む
load_dotenv()

# 2. APIキーの取得（ここが修正ポイント！）
# クラウド(st.secrets)にあればそれを、なければローカル(os.getenv)を使う
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = os.getenv("GEMINI_API_KEY")
except FileNotFoundError:
    # ローカルでsecrets.tomlがない場合はos.getenvに頼る
    api_key = os.getenv("GEMINI_API_KEY")

# APIキーがない場合のエラーチェック
if not api_key:
    print("Warning: API Keyが見つかりません")
else:
    genai.configure(api_key=api_key)

# ★重要：モデルを安定版に戻す
# 'gemini-3' はまだ不安定で、クラウドだとフリーズする原因になります
model = genai.GenerativeModel('gemini-1.5-flash')

def call_judge_ai(prompt_text):
    """
    プロンプトを送信し、JSONとしてパースして返す関数
    """
    try:
        response = model.generate_content(
            prompt_text,
            generation_config={"response_mime_type": "application/json"}
        )
        # JSONクリーニング
        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_text)
    except Exception as e:
        return {
            "status": "error",
            "reason": f"通信エラー: {e}",
            "girl_reply": "（…聞こえないみたい）",
            "damage_score": 0
        }
