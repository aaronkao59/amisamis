import streamlit as st
import re
import random
import os
from gtts import gTTS
import io
import base64

# --- 頁面配置：強制優化移動端視口 ---
st.set_page_config(page_title="菁英朗讀訓練機", layout="wide", initial_sidebar_state="collapsed")

# --- 核心 CSS 樣式控制層（全面適應移動端與多巴胺微交互） ---
st.markdown("""
<style>
    /* 詞卡樣式：主動適應深淺色主題變數 */
    .word-card {
        border: 2px solid #4CAF50;
        border-radius: 15px;
        padding: 30px 10px;
        text-align: center;
        background-color: var(--secondary-bg-color); 
        color: var(--text-color);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 15px;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    /* 按鈕移動端防誤觸與高度優化 */
    .stButton > button {
        width: 100%;
        padding: 0.7rem 0.3rem !important; /* 放大點擊熱區，符合 44x44 pt 胖手指防禦 */
        font-size: 1rem !important;
        border-radius: 10px;
        margin-bottom: 5px;
    }

    /* 獨立優化發音按鈕：極限視覺對比與觸控引導 */
    .play-btn-container > button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    
    .play-btn-container > button:active {
        transform: scale(0.98); /* 手機按壓微觀力學回饋 */
    }

    /* 中文翻譯對照框 */
    .cn-text-box {
        color: var(--text-color);
        background-color: rgba(76, 175, 80, 0.15); 
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }

    /* 隱藏原生音訊元件，防止撐開手機版面 */
    .hidden-audio {
        display: none !important;
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

    # 2. 單句原文
    s_path = os.path.join(base_path, "sentences.txt")
    if os.path.exists(s_path):
        with open(s_path, "r", encoding="utf-8") as f:
            data["sents"] = [line.strip() for line in f if line.strip()]

    # 3. 單句翻譯
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

# --- 第一層：首頁頂部極簡控制台 ---
st.title("菁英朗讀訓練機")

selected_reading = st.selectbox(
    "請選擇朗讀稿件：",
    ["1號朗讀稿", "2號朗讀稿", "3號朗讀稿", "4號朗讀稿"],
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
    st.warning(f"⚠️ 偵測到【{selected_reading}】文字專區尚未配置數據，請於 assets/text/ 補齊對應文字檔。")
else:
    # --- 第二層：多維核心訓練艙（手機版全面自適應 Tab 容器） ---
    tabs = st.tabs(["🎴 生詞詞卡", "📏 重要單句", "📄 段落練習"])

    # --- Tab 1: 生詞詞卡（手機單手操作最佳化佈局） ---
    with tabs[0]:
        w_idx = st.session_state[f'w_idx_{reading_id}']
        w_flip = st.session_state[f'w_flip_{reading_id}']
        
        curr_w = word_list[w_idx]
        display = translation_map[curr_w] if w_flip else curr_w
        
        # 渲染大詞卡
        st.markdown(f'<div class="word-card"><h2>{display}</h2><p style="color:gray;">{w_idx+1}/{len(word_list)}</p></div>', unsafe_allow_html=True)
        
        # 🚀 行動端黃金指配：核心發音大按鈕，單獨佔據第一排，解決高頻連續點擊
        st.markdown('<div class="play-btn-container">', unsafe_allow_html=True)
        if st.button("🔊 播放生詞發音", key=f"play_w_{reading_id}"):
            audio_bytes = get_audio(reading_id, "words", w_idx + 1, curr_w)
            if audio_bytes:
                # 注入 Base64 隱含純前端 JavaScript 零延遲秒播，支援連續多次快速點擊
                b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
                audio_tag = f"""
                <audio id="mobile-word-audio" autoplay class="hidden-audio">
                    <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById('mobile-word-audio');
                    audio.currentTime = 0;
                    audio.play();
                </script>
                """
                st.markdown(audio_tag, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 輔助控制按鈕：拆分為手機單手大拇指左右兩側熱區，2x2 矩陣排布
        c1, c2 = st.columns(2)
        if c1.button("⬅️ 上一個生詞", key=f"prev_w_{reading_id}"):
            st.session_state[f'w_idx_{reading_id}'] = (w_idx - 1) % len(word_list)
            st.session_state[f'w_flip_{reading_id}'] = False
            st.rerun()
        if c2.button("➡️ 下一個生詞", key=f"next_w_{reading_id}"):
            st.session_state[f'w_idx_{reading_id}'] = (w_idx + 1) % len(word_list)
            st.session_state[f'w_flip_{reading_id}'] = False
            st.rerun()
            
        c3, c4 = st.columns(2)
        if c3.button("🔄 翻轉卡片 / 中文", key=f"flip_w_{reading_id}"):
            st.session_state[f'w_flip_{reading_id}'] = not w_flip
            st.rerun()
        if c4.button("🔀 隨機亂序", key=f"shuffle_w_{reading_id}"):
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
                
                # 移動端寬度優化：改為垂直堆疊或 1:1 等寬列，適應窄螢幕
                cc1, cc2 = st.columns(2)
                if cc1.button("🔍 顯示/隱藏翻譯", key=f"show_s_cn_{reading_id}_{i}"):
                    st.session_state[f"s_cn_{reading_id}_{i}"] = not st.session_state.get(f"s_cn_{reading_id}_{i}", False)
                    st.rerun()
                if cc2.button("🔊 播放句子", key=f"play_s_{reading_id}_{i}"):
                    audio_bytes = get_audio(reading_id, "sentences", i + 1, s)
                    if audio_bytes: st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                
                st.radio("評分", ["未通過", "待加強", "通過"], key=f"chk_s_{reading_id}_{i}", horizontal=True, label_visibility="collapsed")
                st.divider()

    # --- Tab 3: 段落練習 ---
    with tabs[2]:
        st.subheader("段落練習")
        for i, p in enumerate(paragraphs_list):
            with st.expander(f"第 {i+1} 段", expanded=True):
                st.write(p)
                st.divider()
                
                # 手機直向視口排版最佳化
                ccc1, cc2 = st.columns([1, 1])
                if ccc1.button("🔊 播放全段", key=f"play_p_{reading_id}_{i}"):
                    audio_bytes = get_audio(reading_id, "paragraphs", i + 1, p)
                    if audio_bytes: st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                st.radio("段落評分", ["未通過", "待加強", "通過"], key=f"chk_p_{reading_id}_{i}", horizontal=True, label_visibility="collapsed")
