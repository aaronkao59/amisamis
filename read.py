import streamlit as st
import re
import random
import os
from gtts import gTTS
import io

# --- 頁面配置：維持 wide 配置，透過 CSS 控制手機視覺核心 ---
st.set_page_config(page_title="菁英朗讀訓練機", layout="wide", initial_sidebar_state="collapsed")

# --- 核心 CSS 更新：力求簡潔、效率、專業（手機直向最佳化） ---
st.markdown("""
<style>
    /* 限制全局最大寬度，確保在手機上單手操作時不變形，視覺高度專業 */
    [data-testid="stAppViewContainer"] > .main > .block-container {
        max-width: 500px !important;
        margin: 0 auto !important;
        padding-top: 2rem !important;
    }

    /* 詞卡：乾淨、標準格線 */
    .word-card {
        border: 2px solid #4CAF50;
        border-radius: 15px;
        padding: 35px 10px;
        text-align: center;
        background-color: var(--secondary-bg-color); 
        color: var(--text-color);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    /* 常規控制按鈕：100% 寬度單列平鋪，符合行動端胖手指防禦 */
    .stButton > button {
        width: 100% !important;
        padding: 0.6rem 0rem !important;
        font-size: 0.95rem !important;
        border-radius: 8px;
        margin-bottom: 5px;
    }

    /* 原生音訊組件優化：100% 寬度，確保持續點擊發音不閃退、不卡頓 */
    .stAudio {
        width: 100% !important;
        margin-bottom: 15px;
    }

    /* 翻譯框與原文框保持專業極簡 */
    .cn-text-box {
        color: var(--text-color);
        background-color: rgba(76, 175, 80, 0.1); 
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 數據動態加載模組 ---
def load_reading_text(read_id):
    base_path = f"assets/text/reading_{read_id}"
    data = {"translation_map": {}, "sents": [], "sent_trans": [], "paragraphs": []}
    
    if not os.path.exists(base_path):
        return data

    # 1. 生詞
    w_path = os.path.join(base_path, "words.txt")
    if os.path.exists(w_path):
        with open(w_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    k, v = line.strip().split(":", 1)
                    data["translation_map"][k] = v

    # 2. 單句
    s_path = os.path.join(base_path, "sentences.txt")
    if os.path.exists(s_path):
        with open(s_path, "r", encoding="utf-8") as f:
            data["sents"] = [line.strip() for line in f if line.strip()]

    # 3. 翻譯
    st_path = os.path.join(base_path, "sent_trans.txt")
    if os.path.exists(st_path):
        with open(st_path, "r", encoding="utf-8") as f:
            data["sent_trans"] = [line.strip() for line in f if line.strip()]

    # 4. 段落
    p_path = os.path.join(base_path, "paragraphs.txt")
    if os.path.exists(p_path):
        with open(p_path, "r", encoding="utf-8") as f:
            content = f.read()
            data["paragraphs"] = [p.strip() for p in content.split("\n\n") if p.strip()]

    return data

# --- 智慧音訊路由器 ---
def get_audio(read_id, category, index, text):
    if category == "paragraphs":
        file_name = f"para_{index:02d}.mp3"
    else:
        file_name = f"{category[:-1]}_{index}.mp3"
        
    file_path = f"assets/audio/readings_{read_id}/{category}/{file_name}"
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return f.read()
    else:
        try:
            tts = gTTS(text=text, lang='it')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            return fp.getvalue()
        except:
            return None

# --- 第一層：主導航控制列 ---
st.title("菁英朗讀訓練機")

selected_reading = st.selectbox(
    "請選擇朗讀稿件：",
    ["1號朗讀稿", "2號朗讀稿", "3號朗讀稿", "4號朗隔稿"],
    index=0,
    label_visibility="collapsed"
)

reading_id = "1" if "1" in selected_reading else "2" if "2" in selected_reading else "3" if "3" in selected_reading else "4"
current_data = load_reading_text(reading_id)

translation_map = current_data["translation_map"]
sent_trans = current_data["sent_trans"]
sents = current_data["sents"]
paragraphs_list = current_data["paragraphs"]

if f'word_list_{reading_id}' not in st.session_state:
    st.session_state[f'word_list_{reading_id}'] = sorted(list(translation_map.keys())) if translation_map else []
if f'w_idx_{reading_id}' not in st.session_state: 
    st.session_state[f'w_idx_{reading_id}'] = 0
if f'w_flip_{reading_id}' not in st.session_state: 
    st.session_state[f'w_flip_{reading_id}'] = False

word_list = st.session_state[f'word_list_{reading_id}']

st.divider()

if not word_list or not paragraphs_list:
    st.warning(f"⚠️ 偵測到【{selected_reading}】文本數據尚未配置，請先於 assets/text/ 內補齊文字檔。")
else:
    # --- 第二層：多維分頁艙 ---
    tabs = st.tabs(["🎴 生詞詞卡", "📏 重要單句", "📄 段落練習"])

    # --- Tab 1: 生詞詞卡（回歸標準原生，支援手機端不重繪連續按壓） ---
    with tabs[0]:
        w_idx = st.session_state[f'w_idx_{reading_id}']
        w_flip = st.session_state[f'w_flip_{reading_id}']
        
        curr_w = word_list[w_idx]
        display = translation_map[curr_w] if w_flip else curr_w
        
        # 詞卡顯示
        st.markdown(f'<div class="word-card"><h2>{display}</h2><p style="color:gray;">{w_idx+1}/{len(word_list)}</p></div>', unsafe_allow_html=True)
        
        # 🟢 解決發音：直接加載原生音訊播放器。
        # 由於此組件完全由瀏覽器本端接管，使用者可以「任意次數、持續反覆點擊」圖示上的播放，絕對不會引發 Streamlit 頁面重繪卡頓
        audio_bytes = get_audio(reading_id, "words", w_idx + 1, curr_w)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
            
        # 標準化垂直平鋪按鈕（手機不變形、專業極簡）
        if st.button("➡️ 下一個生詞", key=f"next_w_{reading_id}"):
            st.session_state[f'w_idx_{reading_id}'] = (w_idx + 1) % len(word_list)
            st.session_state[f'w_flip_{reading_id}'] = False
            st.rerun()
            
        if st.button("🔄 翻轉卡片 / 中文對照", key=f"flip_w_{reading_id}"):
            st.session_state[f'w_flip_{reading_id}'] = not w_flip
            st.rerun()
            
        if st.button("⬅️ 上一個生詞", key=f"prev_w_{reading_id}"):
            st.session_state[f'w_idx_{reading_id}'] = (w_idx - 1) % len(word_list)
            st.session_state[f'w_flip_{reading_id}'] = False
            st.rerun()
            
        if st.button("🔀 隨機亂序排序", key=f"shuffle_w_{reading_id}"):
            random.shuffle(st.session_state[f'word_list_{reading_id}'])
            st.session_state[f'w_idx_{reading_id}'] = 0
            st.rerun()

    # --- Tab 2: 重要單句 ---
    with tabs[1]:
        st.subheader("重要單句")
        for i, s in enumerate(sents):
            with st.container():
                st.info(s)
                
                if st.session_state.get(f"s_cn_{reading_id}_{i}", False):
                    st.markdown(f'<div class="cn-text-box">{sent_trans[i] if i < len(sent_trans) else "（翻譯內容更新中）"}</div>', unsafe_allow_html=True)
                
                # 單句音訊同樣改為原生直接載入，手機流暢度極大化
                audio_bytes = get_audio(reading_id, "sentences", i + 1, s)
                if audio_bytes: st.audio(audio_bytes, format="audio/mp3")
                    
                if st.button("🔍 顯示 / 隱藏中文翻譯", key=f"show_s_cn_{reading_id}_{i}"):
                    st.session_state[f"s_cn_{reading_id}_{i}"] = not st.session_state.get(f"s_cn_{reading_id}_{i}", False)
                    st.rerun()
                
                st.radio("評分", ["未通過", "待加強", "通過"], key=f"chk_s_{reading_id}_{i}", horizontal=True, label_visibility="collapsed")
                st.divider()

    # --- Tab 3: 段落練習 ---
    with tabs[2]:
        st.subheader("段落練習")
        for i, p in enumerate(paragraphs_list):
            with st.expander(f"第 {i+1} 段", expanded=True):
                st.write(p)
                st.divider()
                
                audio_bytes = get_audio(reading_id, "paragraphs", i + 1, p)
                if audio_bytes: st.audio(audio_bytes, format="audio/mp3")
                    
                st.radio("段落評分", ["未通過", "待加強", "通過"], key=f"chk_p_{reading_id}_{i}", horizontal=True, label_visibility="collapsed")
