import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# APIキーがない場合のエラーチェック
if not api_key:
    # エラーが出ても画面が落ちないようにダミーを設定（本番はエラー推奨）
    print("Warning: API Keyが見つかりません")
else:
    genai.configure(api_key=api_key)

# 動作を軽くするため Flash モデルを使用
model = genai.GenerativeModel('gemini-3-flash-preview')

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