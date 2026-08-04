import streamlit as st
import re
import random
import os
import io
import datetime

# 🚀 全域系統版本號
APP_VERSION = "v1.2.0 (Tribal Totem Edition)"

# --- 頁面配置 ---
st.set_page_config(page_title="朗讀訓練機", layout="wide", initial_sidebar_state="collapsed")

# --- 核心 CSS 樣式控制層 (少數民族圖騰風) ---
st.markdown("""
<style>
    /* 全域色彩與圖騰定義 */
    :root {
        --tribal-red: #C62828;   /* 傳統紅 */
        --tribal-black: #212121; /* 深邃黑 */
        --tribal-bg: #FAF0E6;    /* 大地米色 (Linen) */
        
        /* 利用 CSS 漸層繪製編織幾何圖騰 */
        --totem-pattern: repeating-linear-gradient(
            45deg,
            #C62828,
            #C62828 10px,
            #212121 10px,
            #212121 20px
        );
    }

    .stApp {
        background-color: var(--tribal-bg) !important;
        color: var(--tribal-black) !important;
    }

    /* 頂部控制台液態佈局 */
    .header-container {
        display: flex;
        flex-wrap: wrap; 
        align-items: center;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
        margin-top: 10px;
        border-bottom: 4px solid var(--tribal-black);
        padding-bottom: 15px;
        position: relative;
    }
    
    /* 標題下方的裝飾性圖騰橫幅 */
    .header-container::after {
        content: "";
        display: block;
        position: absolute;
        bottom: -12px;
        left: 0;
        height: 8px;
        width: 100%;
        background: var(--totem-pattern);
    }

    .title-wrapper {
        display: flex;
        flex-direction: column;
        gap: 5px;
        min-width: 250px;
    }
    
    .header-title {
        font-size: 2.4rem;
        font-weight: 900;
        margin: 0;
        line-height: 1.2;
        color: var(--tribal-red);
        letter-spacing: 2px;
    }

    .subtitle-text {
        color: gray;
        font-size: 1rem;
        font-weight: bold;
        letter-spacing: 1px;
        margin: 0;
    }

    /* 倒數計時框 (強烈對比) */
    .countdown-box {
        border: 3px solid var(--tribal-black);
        border-radius: 0px; /* 移除圓角，增加質樸感 */
        padding: 8px 24px;
        color: #FFFFFF; 
        font-size: 1.1rem;
        font-weight: bold;
        background-color: var(--tribal-red);
        letter-spacing: 2px;
        white-space: nowrap;
        box-shadow: 4px 4px 0px var(--tribal-black);
    }

    /* 詞卡樣式：帶有頂部圖騰與粗曠陰影 */
    .word-card {
        border: 3px solid var(--tribal-black);
        border-radius: 4px;
        padding: 35px 10px 20px 10px;
        text-align: center;
        background-color: #FFFFFF; 
        color: var(--tribal-black);
        box-shadow: 6px 6px 0px var(--tribal-red);
        margin-bottom: 25px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    
    /* 詞卡頂部圖騰裝飾 */
    .word-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 10px;
        background: var(--totem-pattern);
    }
    
    /* 按鈕樣式：粗黑框與色塊陰影互動 */
    .stButton > button {
        width: 100%;
        padding: 0.5rem 0.2rem !important;
        font-size: 0.95rem !important;
        border-radius: 4px;
        border: 2px solid var(--tribal-black) !important;
        color: var(--tribal-black) !important;
        background-color: #FFFFFF !important;
        font-weight: 800 !important;
        box-shadow: 3px 3px 0px var(--tribal-black);
        transition: all 0.1s ease-in-out;
    }
    .stButton > button:hover {
        background-color: var(--tribal-red) !important;
        color: #FFFFFF !important;
        box-shadow: 1px 1px 0px var(--tribal-black);
        transform: translate(2px, 2px); /* 點擊下壓效果 */
    }

    /* 中文翻譯文字框 */
    .cn-text-box {
        color: var(--tribal-black);
        background-color: #FFFFFF; 
        padding: 15px;
        border: 2px dashed var(--tribal-black);
        border-left: 6px solid var(--tribal-red);
        margin: 10px 0;
        line-height: 1.6;
        font-size: 1rem;
        font-weight: bold;
    }

    /* 資訊提示框 (st.info) */
    .stInfo {
        background-color: #FFFFFF !important; 
        color: var(--tribal-black) !important;
        border: 2px solid var(--tribal-black) !important;
        border-left: 6px solid var(--tribal-black) !important;
        box-shadow: 3px 3px 0px rgba(0,0,0,0.1);
    }

    /* 頁尾版權文字 */
    div[data-testid="stCaptionContainer"] p {
        color: var(--tribal-black) !important;
        font-weight: bold;
        text-align: center;
    }

    /* 手機版專屬視覺優化 */
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        .countdown-box {
            width: 100%;
            text-align: center;
            font-size: 1rem;
            padding: 8px 16px;
        }
        .word-card {
            padding: 30px 10px 15px 10px;
            min-height: 100px;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 數據動態加載模組 ---
def load_reading_text(read_id):
    data = {"translation_map": {}, "audio_index_map": {}, "sents": [], "sent_trans": [], "paragraphs": []}
    
    base_path = f"assets/text/reading_{read_id}"
    if not os.path.exists(base_path):
        return data

    w_path = os.path.join(base_path, "words.txt")
    if os.path.exists(w_path):
        valid_word_count = 1  
        with open(w_path, "r", encoding="utf-8") as f:
            for line in f:
                normalized_line = line.replace("：", ":") 
                if ":" in normalized_line:
                    k, v = normalized_line.strip().split(":", 1)
                    k_str = k.strip()
                    data["translation_map"][k_str] = v.strip()
                    data["audio_index_map"][k_str] = valid_word_count 
                    valid_word_count += 1

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
            data["paragraphs"] = [p.strip() for p in content.splitlines() if p.strip()]

    return data

# --- 智慧音訊路由器 ---
def get_audio(read_id, category, index, text):
    if category == "paragraphs":
        file_name = f"para_{index:02d}.mp3"
    elif category == "words":
        file_name = f"word_{index:02d}.mp3"
    elif category == "sentences":
        file_name = f"sent_{index:02d}.mp3"
    else:
        file_name = f"{category[:-1]}_{index:02d}.mp3"
        
    file_path = f"assets/audio/readings_{read_id}/{category}/{file_name}"
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return f.read()
    else:
        return None

# --- 🚀 優化：強制時區校準 (台北時間 UTC+8) ---
taipei_tz = datetime.timezone(datetime.timedelta(hours=8))
target_date = datetime.date(2026, 9, 19)
current_date = datetime.datetime.now(taipei_tz).date()
days_remaining = (target_date - current_date).days
display_days = max(days_remaining, 0) 

# --- 第一層：首頁頂部極簡控制台 ---
st.markdown(f"""
<div class="header-container">
    <div class="title-wrapper">
        <div class="header-title">朗讀訓練機</div>
        <div class="subtitle-text">115年海岸阿美語 國中組</div>
    </div>
    <div class="countdown-box">距離比賽還有 &nbsp;&nbsp;{display_days}&nbsp;&nbsp; 天</div>
</div>
""", unsafe_allow_html=True)

selected_reading = st.selectbox(
    "請選擇朗讀稿件：",
    ["請選擇", "1號朗讀稿", "2號朗讀稿", "3號朗讀稿", "4號朗讀稿"],
    index=0,
    label_visibility="collapsed"
)

st.divider()

if selected_reading == "請選擇":
    st.info("👆 從選單選擇朗讀稿，展開練習。sa'icelen！")
else:
    reading_id = "1" if "1" in selected_reading else "2" if "2" in selected_reading else "3" if "3" in selected_reading else "4"
    current_data = load_reading_text(reading_id)

    translation_map = current_data["translation_map"]
    audio_index_map = current_data["audio_index_map"] 
    sent_trans = current_data["sent_trans"]
    sents = current_data["sents"]
    paragraphs_list = current_data["paragraphs"]

    if f'word_list_{reading_id}' not in st.session_state:
        st.session_state[f'word_list_{reading_id}'] = list(translation_map.keys()) if translation_map else []
    if f'w_idx_{reading_id}' not in st.session_state: 
        st.session_state[f'w_idx_{reading_id}'] = 0
    if f'w_flip_{reading_id}' not in st.session_state: 
        st.session_state[f'w_flip_{reading_id}'] = False

    word_list = st.session_state[f'word_list_{reading_id}']

    if not word_list or not paragraphs_list:
        st.warning(f"⚠️ 偵測到【{selected_reading}】文字專區尚未配置數據，請於 assets/text/ 補齊對應文字檔。")
    else:
        tabs = st.tabs(["🎴 生詞詞卡", "📏 重要單句", "📄 段落練習"])

        with tabs[0]:
            w_idx = st.session_state[f'w_idx_{reading_id}']
            w_flip = st.session_state[f'w_flip_{reading_id}']
            
            curr_w = word_list[w_idx]
            display = translation_map[curr_w] if w_flip else curr_w
            
            original_audio_idx = audio_index_map[curr_w]
            
            st.markdown(f'<div class="word-card"><h2>{display}</h2><p style="color:gray; font-weight:bold;">{w_idx+1}/{len(word_list)}</p></div>', unsafe_allow_html=True)
            
            # 使用預設的流式排版，Streamlit 在手機版會自動將 column 垂直堆疊
            cols = st.columns([1, 1, 1, 1, 1.2]) 
            
            if cols[0].button("⬅️ 往前", key=f"prev_w_{reading_id}"):
                st.session_state[f'w_idx_{reading_id}'] = (w_idx - 1) % len(word_list)
                st.session_state[f'w_flip_{reading_id}'] = False
                st.rerun()
                
            if cols[1].button("🔊 發音", key=f"play_w_{reading_id}"):
                audio_bytes = get_audio(reading_id, "words", original_audio_idx, curr_w)
                if audio_bytes: 
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    
            if cols[2].button("➡️ 向後", key=f"next_w_{reading_id}"):
                st.session_state[f'w_idx_{reading_id}'] = (w_idx + 1) % len(word_list)
                st.session_state[f'w_flip_{reading_id}'] = False
                st.rerun()
                
            if cols[3].button("🔀 隨機", key=f"shuffle_w_{reading_id}"):
                random.shuffle(st.session_state[f'word_list_{reading_id}'])
                st.session_state[f'w_idx_{reading_id}'] = 0
                st.rerun()
                
            if cols[4].button("🔄 翻轉/中文", key=f"flip_w_{reading_id}"):
                st.session_state[f'w_flip_{reading_id}'] = not w_flip
                st.rerun()

        with tabs[1]:
            st.subheader("重要單句")
            for i, s in enumerate(sents):
                with st.container():
                    st.info(s)
                    
                    if st.session_state.get(f"s_cn_{reading_id}_{i}", False):
                        st.markdown(f'<div class="cn-text-box">{sent_trans[i] if i < len(sent_trans) else "（翻譯內容更新中）"}</div>', unsafe_allow_html=True)
                    
                    if st.button("顯示/隱藏中文翻譯", key=f"show_s_cn_{reading_id}_{i}"):
                        st.session_state[f"s_cn_{reading_id}_{i}"] = not st.session_state.get(f"s_cn_{reading_id}_{i}", False)
                        st.rerun()
                        
                    c1, c2 = st.columns([1, 2])
                    if c1.button("🔊 播放句子", key=f"play_s_{reading_id}_{i}"):
                        audio_bytes = get_audio(reading_id, "sentences", i + 1, s)
                        if audio_bytes: st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    c2.radio("評分", ["未通過", "待加強", "通過"], key=f"chk_s_{reading_id}_{i}", horizontal=True, label_visibility="collapsed")
                    st.divider()

        with tabs[2]:
            c_head, c_slider = st.columns([1, 2])
            with c_head:
                st.subheader("段落練習")
            with c_slider:
                font_scale = st.slider("📏 調整段落字體大小", min_value=1.0, max_value=3.0, value=1.2, step=0.1, key=f"font_slider_{reading_id}", label_visibility="collapsed")
                
            for i, p in enumerate(paragraphs_list):
                with st.expander(f"第 {i+1} 段", expanded=False):
                    st.markdown(f'<div style="font-size: {font_scale}rem; line-height: 1.8; padding: 10px 0;">{p}</div>', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 2])
                    if c1.button("🔊 播放全段", key=f"play_p_{reading_id}_{i}"):
                        audio_bytes = get_audio(reading_id, "paragraphs", i + 1, p)
                        if audio_bytes: st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                    c2.radio("段落評分", ["未通過", "待加強", "通過"], key=f"chk_p_{reading_id}_{i}", horizontal=True, label_visibility="collapsed")

# --- 頁尾版權宣告 ---
st.divider()
st.caption(f"© 2026 115朗讀練習機 singsi sawmAh ｜ 系統版本：**{APP_VERSION}**")
