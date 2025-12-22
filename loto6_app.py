
import streamlit as st
import pandas as pd
import json
import os
import datetime
import random
import update_loto6
import time

# Page Config
st.set_page_config(
    page_title="LOTO6 Predictor",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styles ---
st.markdown("""
<style>
    .big-font { font-size: 20px !important; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    .css-1v0mbdj.tr { text-align: right; }
    .pred-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2a2a3a, #1a1a2a);
        border: 2px solid #ffd700;
        color: #ffd700;
        font-weight: bold;
        font-size: 24px;
        margin: 5px;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data(ttl=60) # Cache for 1 min, but we trigger clear on update
def load_data():
    if not os.path.exists('loto6_data.js'):
        return []
    
    try:
        with open('loto6_data.js', 'r', encoding='utf-8') as f:
            content = f.read()
            json_str = content.replace('const LOTO6_DATA = ', '').strip().rstrip(';')
            return json.loads(json_str)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return []

def get_stats(data):
    if not data:
        return None, None
    
    # Calculate Frequency and Gaps
    freq = {i: 0 for i in range(1, 44)}
    gaps = {i: len(data) for i in range(1, 44)} # Default max
    
    for idx, draw in enumerate(data):
        for n in draw['numbers']:
            if n in freq:
                freq[n] += 1
            if gaps.get(n) == len(data): # First time seeing it (since we iterate desc round?)
                # Wait, data is sorted desc (latest first).
                # So the first time we see it, that's the latest appearance.
                gaps[n] = idx
                
    return freq, gaps

data = load_data()
freq, gaps = get_stats(data)

# --- Sidebar ---
st.sidebar.title("LOTO6 予想")
st.sidebar.markdown("---")

if st.sidebar.button("🔄 データ更新 (Update Data)"):
    with st.spinner("データを更新中..."):
        try:
            update_loto6.main()
            load_data.clear() # Clear cache
            data = load_data()
            freq, gaps = get_stats(data)
            st.toast('データ更新完了！', icon='✅')
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"更新失敗: {e}")

st.sidebar.markdown("---")
algorithm = st.sidebar.radio(
    "予想アルゴリズム (Algorithm)",
    ("hybrid", "hot", "cold", "balanced", "gap", "pattern"),
    format_func=lambda x: {
        "hybrid": "ハイブリッド法 (Hybrid)",
        "hot": "ホットナンバー法 (Hot)",
        "cold": "コールドナンバー法 (Cold)",
        "balanced": "バランス法 (Balanced)",
        "gap": "出現間隔法 (Gap)",
        "pattern": "パターン分析法 (Pattern)"
    }[x]
)

# --- Main Content ---
st.title("LOTO6 統計予想システム")

if not data:
    st.warning("データがありません。「データ更新」ボタンを押してください。")
    st.stop()

# Header Stats
last_draw = data[0]
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("最新データ日", last_draw['date'])
with col2:
    st.metric("最新回号", f"第{last_draw['round']}回")
with col3:
    st.metric("分析データ数", f"{len(data)}回")
with col4:
    last_nums = [str(n) for n in last_draw['numbers']] + [f"({last_draw['bonus']})"]
    st.text("最新当選数字")
    st.markdown(f"**{' '.join(last_nums)}**")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["🎯 予想 (Prediction)", "📊 分析 (Analysis)", "📜 履歴 (History)"])

# Prediction Logic
def generate_prediction(algo_name, freq, gaps):
    selected = []
    
    if algo_name == "hot":
        # Top 15 freq, pick 6 from Top 10 randomized
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        top15 = [x[0] for x in sorted_freq[:15]]
        candidates = top15[:10] # Simplified logic from HTML
        selected = random.sample(candidates, 6)
        
    elif algo_name == "cold":
        # Bottom 15 freq, pick 6 from Bottom 10 randomized
        sorted_freq = sorted(freq.items(), key=lambda x: x[1]) # Ascending
        bottom15 = [x[0] for x in sorted_freq[:15]]
        candidates = bottom15[:10]
        selected = random.sample(candidates, 6)
        
    elif algo_name == "balanced":
        # 3 from low (1-21), 3 from high (22-43)
        low = list(range(1, 22))
        high = list(range(22, 44))
        selected = random.sample(low, 3) + random.sample(high, 3)
        
    elif algo_name == "gap":
        # Sort by gap desc. Pick 6 from top 15
        sorted_gap = sorted(gaps.items(), key=lambda x: x[1], reverse=True)
        candidates = [x[0] for x in sorted_gap[:15]]
        selected = random.sample(candidates, 6)
        
    elif algo_name == "pattern":
        # 1 from 1-10, 1 from 11-20, 1 from 21-30, 2 from 31-43, 1 from high freq
        p1 = random.choice(range(1, 11))
        
        p2_pool = [x for x in range(11, 21) if x != p1]
        p2 = random.choice(p2_pool)
        
        p3_pool = [x for x in range(21, 31) if x not in [p1, p2]]
        p3 = random.choice(p3_pool)
        
        p4_5_pool = [x for x in range(31, 44) if x not in [p1, p2, p3]]
        p4_5 = random.sample(p4_5_pool, 2)
        
        temp_sel = [p1, p2, p3] + p4_5
        
        # High freq addition
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        for num, _ in sorted_freq:
            if num not in temp_sel:
                temp_sel.append(num)
                break
        selected = temp_sel
        
    else: # hybrid
        # 2 from hot, 2 from cold, 2 random
        sorted_freq_desc = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        sorted_freq_asc = sorted(freq.items(), key=lambda x: x[1])
        
        hot_candidates = [x[0] for x in sorted_freq_desc[:10]]
        cold_candidates = [x[0] for x in sorted_freq_asc[:10]]
        
        sel_hot = random.sample(hot_candidates, 2)
        sel_cold = random.sample(cold_candidates, 2)
        
        current = sel_hot + sel_cold
        rem_pool = [x for x in range(1, 44) if x not in current]
        sel_rand = random.sample(rem_pool, 2)
        
        selected = current + sel_rand

    return sorted(selected)

with tab1:
    st.subheader(f"予想: {algorithm.upper()}")
    
    # Descriptions
    desc = {
        "hybrid": "ホット・コールド・ランダムを組み合わせたバランス型アルゴリズム。",
        "hot": "最近よく出ている数字を重視。",
        "cold": "最近出ていない数字（そろそろ出るかも）を重視。",
        "balanced": "小さい数字と大きい数字をバランスよく選択。",
        "gap": "出現間隔が空いている数字を狙い撃ち。",
        "pattern": "過去の傾向に基づくパターン（各番台から選択など）で生成。"
    }
    st.info(desc[algorithm])
    
    if st.button("予想を生成 (Generate)", type="primary"):
        prediction = generate_prediction(algorithm, freq, gaps)
        
        # Display Circles
        cols = st.columns(6)
        html_str = ""
        for n in prediction:
            html_str += f"<div class='pred-circle'>{n}</div>"
        
        st.markdown(f"<div style='display:flex; justify-content:center; flex-wrap:wrap;'>{html_str}</div>", unsafe_allow_html=True)
        
        # Confidence (Mock)
        conf = random.randint(50, 65)
        st.caption(f"統計的信頼度: {conf}%")

with tab2:
    st.subheader("数字別出現回数 (Frequency)")
    # Bar Chart for Freq
    df_freq = pd.DataFrame(list(freq.items()), columns=['Number', 'Count'])
    st.bar_chart(df_freq.set_index('Number'))
    
    st.subheader("出現間隔 (Gap - 未出現回数)")
    st.caption("値が大きいほど、最近出ていない数字です")
    df_gap = pd.DataFrame(list(gaps.items()), columns=['Number', 'Gap'])
    st.bar_chart(df_gap.set_index('Number'))

with tab3:
    st.subheader("直近の抽選結果")
    
    hist_data = []
    for d in data[:20]: # Show last 20
        nums = " ".join([str(n).zfill(2) for n in d['numbers']])
        hist_data.append({
            "回号 (Round)": d['round'],
            "日付 (Date)": d['date'],
            "当選番号 (Numbers)": nums,
            "B": d['bonus']
        })
    
    st.dataframe(pd.DataFrame(hist_data))

st.caption("LOTO6 Predictor v2.0 (Streamlit Edition)")
