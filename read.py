import streamlit as st
import re
import random
import os
from gtts import gTTS
import io
import base64

# --- 頁面配置 ---
st.set_page_config(page_title="菁英朗讀訓練機", layout="wide", initial_sidebar_state="collapsed")

# --- 核心極簡 CSS 樣式控制層（去除所有雜亂元件，確保手機不變形） ---
st.markdown("""
<style>
    /* 全局背景與字體微調 */
    html, body, [data-testid="stAppViewContainer"] {
        max-width: 600px !important; /* 限制全局最大寬度，防止在大螢幕或手機上橫向溢出變形 */
        margin: 0 auto !important;
    }

    /* 詞卡：大面積、留白、極簡專業感 */
    .word-card-container {
        position: relative;
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 16px;
        padding: 40px 20px;
        text-align: center;
        background-color: var(--secondary-bg-color); 
        color: var(--text-color);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    /* HTML5 純前端發音按鈕：漂浮在詞卡右下角，完全不佔用下方控制列空間 */
    .native-play-icon {
        position: absolute;
        bottom: 15px;
        right: 20px;
        font-size: 28px;
        cursor: pointer;
        user-select: none;
        transition: transform 0.1s ease;
        -webkit-tap-highlight-color: transparent;
    }
    .native-play-icon:active {
        transform: scale(0.85); /* 手機按壓的物理縮放回饋 */
    }

    /* 底層控制按鈕：100% 寬度單列縱向堆疊，絕對不會因為螢幕窄而擠壓變形 */
    .stButton > button {
        width: 100% !important;
        padding: 0.6rem 0rem !important;
        font-size: 0.95rem !important;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.3);
        background-color: transparent;
        margin-bottom: 8px;
    }

    /* 單句原文與段落卡片優化 */
    .stInfo {
        background-color: rgba(30, 144, 255, 0.05) !important;
        color: var(--text-color) !important;
        border: 1px solid rgba(30, 144, 255, 0.15) !important;
        border-radius: 10px !important;
    }
    
    .cn-text-box {
        color: var(--text-color);
        background-color: rgba(76, 175, 80, 0.08); 
        padding: 14px;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin: 8px 0;
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

    w_path = os.path.join(base_path, "words.txt")
    if os.path.exists(w_path):
        with open(w_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    k, v = line.strip().split(":", 1)
                    data["translation_map"][k] = v

    s_path = os.path.join(base_path, "sentences.txt")
    if os.path.exists(s_path):
        with open(s_path, "r", encoding="utf-8") as f:
            data["sents"] = [line.strip() for line in f if line.strip()]

    st_path = os.path.join(base_path, "sent_trans.txt")
    if os.path.exists(st_path):
        with open(st_path, "r", encoding="utf-8") as f:
            data["sent_trans"] = [line.strip() for line in f if line.strip()]

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

# --- 主交互渲染層 ---
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
    tabs = st.tabs(["🎴 生詞詞卡", "📏 重要單句", "📄 段落練習"])

    # --- Tab 1: 生詞詞卡（極簡優雅、純前端零延遲秒播） ---
    with tabs[0]:
        w_idx = st.session_state[f'w_idx_{reading_id}']
        w_flip = st.session_state[f'w_flip_{reading_id}']
        
        curr_w = word_list[w_idx]
        display = translation_map[curr_w] if w_flip else curr_w
        
        # 預先讀取當前生詞的音訊，準備注入 HTML
        audio_bytes = get_audio(reading_id, "words", w_idx + 1, curr_w)
        b64_audio = base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else ""
        
        # 將「🔊發音圖示」直接整合進詞卡 HTML 內。點擊右下角喇叭，純前端立刻發聲，隨按隨發，絕不重繪頁面！
        card_html = f"""
        <div class="word-card-container">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 600;">{display}</h2>
            <p style="color:gray; margin: 10px 0 0 0; font-size: 0.9rem;">{w_idx+1} / {len(word_list)}</p>
            <div class="native-play-icon" onclick="document.getElementById('native-card-audio').currentTime=0; document.getElementById('native-card-audio').play();">🔊</div>
            <audio id="native-card-audio" style="display:none;">
                <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
            </audio>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        
        # 控制按鈕一律採取單列縱向平鋪（專業、高效、手機完美適配不變形）
        if st.button("➡️ 下一個生詞", key=f"next_w_{reading_id}"):
            st.session_state[f'w_idx_{reading_id}'] = (w_idx + 1) % len(word_list)
            st.session_state[f'w_flip_{reading_id}'] = False
            st.rerun()
            
        if st.button("🔄 翻轉卡片 / 檢視中文", key=f"flip_w_{reading_id}"):
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
                
                if st.button("🔊 播放單句音訊", key=f"play_s_{reading_id}_{i}"):
                    audio_bytes = get_audio(reading_id, "sentences", i + 1, s)
                    if audio_bytes: st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    
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
                
                if st.button("🔊 播放全段音訊", key=f"play_p_{reading_id}_{i}"):
                    audio_bytes = get_audio(reading_id, "paragraphs", i + 1, p)
                    if audio_bytes: st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    
                st.radio("段落評分", ["未通過", "待加強", "通過"], key=f"chk_p_{reading_id}_{i}", horizontal=True, label_visibility="collapsed")
