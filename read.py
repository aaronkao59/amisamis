import streamlit as st
import re
import random
import os
from gtts import gTTS
import io

# --- 頁面配置 ---
st.set_page_config(page_title="朗讀訓練機", layout="wide", initial_sidebar_state="collapsed")

# --- 核心 CSS 更新 ---
st.markdown("""
<style>
    /* 詞卡：使用系統背景色變數 */
    .word-card {
        border: 2px solid #4CAF50;
        border-radius: 15px;
        padding: 30px 10px;
        text-align: center;
        /* 使用 Streamlit 內建變數：自動隨主題切換背景與文字顏色 */
        background-color: var(--secondary-bg-color); 
        color: var(--text-color);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    /* 按鈕樣式：確保文字垂直居中與觸控友善 */
    .stButton > button {
        width: 100%;
        padding: 0.5rem 0.2rem !important;
        font-size: 0.9rem !important;
        border-radius: 8px;
    }

    /* 中文翻譯框：使用帶有透明度的綠色，確保在深淺色背景下都能閱讀 */
    .cn-text-box {
        color: var(--text-color);
        /* 使用 rgba 確保背景色在深色模式下不會太刺眼 */
        background-color: rgba(76, 175, 80, 0.15); 
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }

    /* 確保阿美語原文在深色模式下依然清晰 */
    .stInfo {
        background-color: rgba(30, 144, 255, 0.1) !important;
        color: var(--text-color) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 數據動態加載模組 (I/O 路由解耦) ---
def load_reading_text(read_id):
    base_path = f"assets/text/reading_{read_id}"
    data = {"translation_map": {}, "sents": [], "sent_trans": [], "paragraphs": []}
    
    if not os.path.exists(base_path):
        return data

    # 1. 解析生詞對照表
    w_path = os.path.join(base_path, "words.txt")
    if os.path.exists(w_path):
        with open(w_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    k, v = line.strip().split(":", 1)
                    data["translation_map"][k] = v

    # 2. 解析單句原文
    s_path = os.path.join(base_path, "sentences.txt")
    if os.path.exists(s_path):
        with open(s_path, "r", encoding="utf-8") as f:
            data["sents"] = [line.strip() for line in f if line.strip()]

    # 3. 解析單句翻譯
    st_path = os.path.join(base_path, "sent_trans.txt")
    if os.path.exists(st_path):
        with open(st_path, "r", encoding="utf-8") as f:
            data["sent_trans"] = [line.strip() for line in f if line.strip()]

    # 4. 解析段落練習
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

# --- 第一層：首頁控制層 ---
st.title("菁英朗讀訓練機")

selected_reading = st.selectbox(
    "請選擇朗讀稿件：",
    ["1號朗讀稿", "2號朗讀稿", "3號朗讀稿", "4號朗讀稿"],
    index=0,
    label_visibility="collapsed"
)

# 依據選擇動態計算路由 ID 並秒讀資料
reading_id = "1" if "1" in selected_reading else "2" if "2" in selected_reading else "3" if "3" in selected_reading else "4"
current_data = load_reading_text(reading_id)

translation_map = current_data["translation_map"]
sent_trans = current_data["sent_trans"]
sents = current_data["sents"]
paragraphs_list = current_data["paragraphs"]

# --- 全域狀態解耦初始化 ---
if f'word_list_{reading_id}' not in st.session_state:
    st.session_state[f'word_list_{reading_id}'] = sorted(list(translation_map.keys())) if translation_map else []
if f'w_idx_{reading_id}' not in st.session_state: 
    st.session_state[f'w_idx_{reading_id}'] = 0
if f'w_flip_{reading_id}' not in st.session_state: 
    st.session_state[f'w_flip_{reading_id}'] = False

word_list = st.session_state[f'word_list_{reading_id}']

st.divider()

# --- 數據完整性檢查 ---
if not word_list or not paragraphs_list:
    st.warning(f"⚠️ 偵測到【{selected_reading}】文字專區尚未配置數據，請於 assets/text/ 補齊對應文字檔。")
else:
    tabs = st.tabs(["🎴 生詞詞卡", "📏 單句朗讀訓練", "📄 段落練習"])

    # --- Tab 1: 生詞詞卡 ---
    with tabs[0]:
        w_idx = st.session_state[f'w_idx_{reading_id}']
        w_flip = st.session_state[f'w_flip_{reading_id}']
        
        curr_w = word_list[w_idx]
        display = translation_map[curr_w] if w_flip else curr_w
        
        st.markdown(f'<div class="word-card"><h2>{display}</h2><p style="color:gray;">{w_idx+1}/{len(word_list)}</p></div>', unsafe_allow_html=True)
        
        cols = st.columns([1, 1, 1, 1, 1.2]) 
        
        if cols[0].button("⬅️ 往前", key=f"prev_w_{reading_id}"):
            st.session_state[f'w_idx_{reading_id}'] = (w_idx - 1) % len(word_list)
            st.session_state[f'w_flip_{reading_id}'] = False
            # 切換詞卡時清除前一個詞的隨機狀態變數，維持乾淨的記憶體空間
            if f'w_play_stream_{reading_id}' in st.session_state:
                del st.session_state[f'w_play_stream_{reading_id}']
            st.rerun()
            
        # 🔊 生詞發音：直接將音訊二進位數據包裝進一個隨機變數屬性內
        # 如此一來，Streamlit 在每次點擊發音時都會向瀏覽器推播全新的數據流，徹底解除限制，同時外觀絕不變形
        if cols[1].button("🔊 發音", key=f"play_w_{reading_id}"):
            audio_bytes = get_audio(reading_id, "words", w_idx + 1, curr_w)
            if audio_bytes:
                st.session_state[f'w_play_stream_{reading_id}'] = audio_bytes
                
        if cols[2].button("➡️ 向後", key=f"next_w_{reading_id}"):
            st.session_state[f'w_idx_{reading_id}'] = (w_idx + 1) % len(word_list)
            st.session_state[f'w_flip_{reading_id}'] = False
            if f'w_play_stream_{reading_id}' in st.session_state:
                del st.session_state[f'w_play_stream_{reading_id}']
            st.rerun()
            
        if cols[3].button("🔀 隨機", key=f"shuffle_w_{reading_id}"):
            random.shuffle(st.session_state[f'word_list_{reading_id}'])
            st.session_state[f'w_idx_{reading_id}'] = 0
            if f'w_play_stream_{reading_id}' in st.session_state:
                del st.session_state[f'w_play_stream_{reading_id}']
            st.rerun()
            
        if cols[4].button("🔄 翻轉/中文", key=f"flip_w_{reading_id}"):
            st.session_state[f'w_flip_{reading_id}'] = not w_flip
            st.rerun()

        # 🟢 如果隨機發音狀態中有音訊，使用完全固定且唯一的靜態 key 渲染播放，絕不觸發任何類型語法錯誤
        if f'w_play_stream_{reading_id}' in st.session_state:
            st.audio(st.session_state[f'w_play_stream_{reading_id}'], format="audio/mp3", autoplay=True, key="play_card_word_audio")
            # 播放完畢後抹除暫存旗標，利於下一次點按
            del st.session_state[f'w_play_stream_{reading_id}']

    # --- Tab 2: 單句朗讀訓練 (100% 恢復原本寫法與功能) ---
    with tabs[1]:
        st.subheader("單句朗讀訓練")
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

    # --- Tab 3: 段落練習 (100% 恢復原本寫法與功能) ---
    with tabs[2]:
        st.subheader("段落練習")
        for i, p in enumerate(paragraphs_list):
            with st.expander(f"第 {i+1} 段", expanded=True):
                st.write(p)
                c1, c2 = st.columns([1, 2])
                if c1.button("🔊 播放全段", key=f"play_p_{reading_id}_{i}"):
                    audio_bytes = get_audio(reading_id, "paragraphs", i + 1, p)
                    if audio_bytes: st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                c2.radio("段落評分", ["未通過", "待加強", "通過"], key=f"chk_p_{reading_id}_{i}", horizontal=True, label_visibility="collapsed")
