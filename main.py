import streamlit as st
import json
import time
from prompts import get_judge_prompt
from gemini_api import call_judge_ai

# ページ設定
st.set_page_config(
    page_title="逆張りバレンタイン", 
    page_icon="🍫", 
    layout="centered"
)

# ==========================================
# ★ここを追加：サイドバーにルールを表示
# ==========================================
with st.sidebar:
    st.title("📋 ルール説明")
    st.info("モテすぎる男の宿命…\nそれは「チョコを受け取らずに」愛を保つこと。")
    
    st.markdown("""
    ### 🛑 勝利条件
    「チョコを受け取らず」かつ「相手を傷つけずに」断ること。
    
    ### 💀 ゲームオーバー条件
    1. **受け取ってしまう**
       - 「ありがとう」はNG！
       - 手に持つのもNG！
    2. **傷つける・怒らせる**
       - 「いらない」「嫌い」は論外
       - 無視するのもNG
    3. **好感度が下がる**
       - つまらない嘘はバレます
       
    ### 🏅 ランクについて
    最後にランクが…？
    """)
    
    st.write("---")
    st.caption("Created for @duck_ahiru_Z")

# ==========================================
# メイン画面
# ==========================================

# タイトル表示
st.title("🍫 逆張りバレンタイン")
st.write("〜チョコを受け取らずに、紳士的に断り続けろ！〜")

# --- セッション状態の初期化 ---
if "stage" not in st.session_state:
    st.session_state.stage = 0
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# 戦績管理用
if "stats" not in st.session_state:
    st.session_state.stats = {
        "one_shot_clears": 0,  # 一発クリア数
        "total_retries": 0,    # 総ミス回数
        "current_stage_miss": 0 # 現在のステージでのミス数
    }

# 履歴ログ
if "history" not in st.session_state:
    st.session_state.history = []

# JSON読み込み
try:
    with open('characters.json', 'r', encoding='utf-8') as f:
        girls = json.load(f)
except FileNotFoundError:
    st.error("エラー：characters.json が見つかりません。")
    st.stop()

# ==========================================
# リザルト画面
# ==========================================
if st.session_state.stage >= len(girls):
    
    if st.session_state.last_result is not None:
        st.balloons()
        time.sleep(1)
        st.snow()
        st.session_state.last_result = None

    # ランク判定
    total_stages = len(girls)
    one_shots = st.session_state.stats["one_shot_clears"]
    retries = st.session_state.stats["total_retries"]
    
    rank = "C"
    rank_title = "見習い回避者"
    color = "#808080"
    
    if one_shots == total_stages:
        rank = "SSS"
        rank_title = "難攻不落の鉄壁王"
        color = "#FFD700"
    elif one_shots >= total_stages * 0.8:
        rank = "S"
        rank_title = "完全無欠のジェントルマン"
        color = "#FF4500"
    elif retries <= 5:
        rank = "A"
        rank_title = "一流のガードマン"
        color = "#1E90FF"
    elif retries <= 15:
        rank = "B"
        rank_title = "一般男性"
        color = "#32CD32"

    st.markdown(f"""
    <style>
    .result-card {{
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #333;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .rank-val {{ font-size: 60px; font-weight: 900; color: {color}; text-shadow: 2px 2px 0px #fff; }}
    .rank-label {{ font-size: 24px; font-weight: bold; color: #333; }}
    </style>
    <div class="result-card">
        <h3>🏆 MISSION COMPLETE</h3>
        <div>あなたの回避ランク</div>
        <div class="rank-val">{rank}</div>
        <div class="rank-label">{rank_title}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("クリア人数", f"{total_stages}人")
    c2.metric("一発回避", f"{one_shots}回")
    c3.metric("総ミス回数", f"{retries}回")

    st.divider()

    st.subheader("📜 回避の軌跡")
    for log in st.session_state.history:
        with st.expander(f"vs {log['girl']}"):
            st.markdown(f"**あなた**: {log['user_input']}")
            st.markdown(f"**女子**: {log['reply']}")
            st.caption(f"勝因: {log['reason']}")

    st.divider()
    
    share_text = f"【逆張りバレンタイン】ランク{rank}「{rank_title}」でクリア！\n一発回避: {one_shots}回 / ミス: {retries}回\n#逆張りバレンタイン"
    st.text_area("SNSで自慢する", share_text)

    if st.button("🔄 タイトルに戻る", use_container_width=True):
        st.session_state.stage = 0
        st.session_state.last_result = None
        st.session_state.stats = {"one_shot_clears": 0, "total_retries": 0, "current_stage_miss": 0}
        st.session_state.history = []
        st.rerun()
        
    st.stop()

# ==========================================
# ゲーム本編
# ==========================================

current_girl = girls[st.session_state.stage]

progress = st.session_state.stage / len(girls)
st.progress(progress, text=f"Mission: {st.session_state.stage}/{len(girls)}")

st.header(f"Stage {st.session_state.stage + 1}: {current_girl['name']}")
st.markdown(f"**【性格・特徴】** {current_girl['setting']}")
st.info(f"女子「{current_girl['dialogue']}」")

user_input = st.text_input("どうやって断る？", key=f"input_{st.session_state.stage}")

if st.button("判定する", type="primary"):
    if not user_input:
        st.warning("無言は一番傷つきます！何か言ってください！")
    else:
        with st.spinner(f"{current_girl['name']} の反応を解析中..."):
            full_prompt = get_judge_prompt(current_girl['setting'], current_girl['dialogue'], user_input)
            result = call_judge_ai(full_prompt)
            st.session_state.last_result = result
            
            if result["status"] == "success":
                if st.session_state.stats["current_stage_miss"] == 0:
                    st.session_state.stats["one_shot_clears"] += 1
                
                st.session_state.history.append({
                    "girl": current_girl['name'],
                    "user_input": user_input,
                    "reply": result['girl_reply'],
                    "reason": result['reason']
                })
            else:
                st.session_state.stats["total_retries"] += 1
                st.session_state.stats["current_stage_miss"] += 1

if st.session_state.last_result is not None:
    res = st.session_state.last_result
    
    st.subheader("判定結果")
    
    if res.get("status") == "error":
         st.error(f"エラー: {res.get('reason')}")
    
    elif res["status"] == "success":
        st.success("✨ 回避成功！")
        st.markdown(f"**{current_girl['name']}**: 「{res['girl_reply']}」")
        st.write(f"**勝因**: {res['reason']}")
        
        btn_label = "🏆 結果を見る" if st.session_state.stage + 1 == len(girls) else "次の女子へ"
        if st.button(btn_label):
            st.session_state.stage += 1
            st.session_state.last_result = None
            st.session_state.stats["current_stage_miss"] = 0
            st.rerun()
            
    else: 
        st.error("💀 ゲームオーバー...")
        st.markdown(f"**{current_girl['name']}**: 「{res['girl_reply']}」")
        st.write(f"**敗因**: {res['reason']}")
        st.caption(f"この女子へのリトライ回数: {st.session_state.stats['current_stage_miss']}回")

        st.write(f"**精神ダメージ**: {res.get('damage_score', 100)}")
        if st.button("もう一度挑戦"):
            st.session_state.last_result = None

            st.rerun()

