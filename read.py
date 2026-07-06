import streamlit as st
import re
import random
import os
from gtts import gTTS
import io

# --- 頁面配置 ---
st.set_page_config(page_title="朗讀訓練機", layout="wide", initial_sidebar_state="collapsed")[cite: 1]

# --- 第一層：首頁頂部極簡控制台 (視覺縮放與選單) ---
st.title("朗讀訓練機")[cite: 1]

col_select, col_scale = st.columns([3, 1])
with col_select:
    selected_reading = st.selectbox(
        "請選擇朗讀稿件：",
        ["1號朗讀稿", "2號朗讀稿", "3號朗讀稿", "4號朗讀稿"],
        index=0,
        label_visibility="collapsed"
    )[cite: 1]
with col_scale:
    # 建立底層視覺映射的動態變數
    font_scale = st.slider("📏 字體與排版縮放", min_value=0.8, max_value=2.5, value=1.0, step=0.1, label_visibility="collapsed")

# --- 核心 CSS 樣式控制層 (純粹邏輯：變數連動引擎) ---
st.markdown(f"""
<style>
    /* 將滑桿數值注入為全局 CSS 變數 */
    :root {{
        --base-scale: {font_scale};
    }}

    /* 詞卡樣式：容器與字體全比例連動縮放 */
    .word-card {{
        border: 2px solid #4CAF50;
        border-radius: calc(15px * var(--base-scale));
        padding: calc(30px * var(--base-scale)) calc(10px * var(--base-scale));
        text-align: center;
        background-color: var(--secondary-bg-color); 
        color: var(--text-color);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: calc(20px * var(--base-scale));
        min-height: calc(120px * var(--base-scale));
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    
    .word-card h2 {{
        font-size: calc(2rem * var(--base-scale)) !important;
        margin: 0;
    }}
    
    .word-card p {{
        font-size: calc(1rem * var(--base-scale)) !important;
    }}
    
    /* 按鈕全局控頻：確保觸控精準度與回饋 */
    .stButton > button {{
        width: 100%;
        padding: calc(0.5rem * var(--base-scale)) calc(0.2rem * var(--base-scale)) !important;
        font-size: calc(0.9rem * var(--base-scale)) !important;
        border-radius: 8px;
    }}

    /* 中文翻譯對照框：等比例縮放邊距與字級 */
    .cn-text-box {{
        color: var(--text-color);
        background-color: rgba(76, 175, 80, 0.15); 
        padding: calc(15px * var(--base-scale));
        border-radius: calc(10px * var(--base-scale));
        border-left: calc(5px * var(--base-scale)) solid #4CAF50;
        margin: calc(10px * var(--base-scale)) 0;
        line-height: calc(1.6 * var(--base-scale));
        font-size: calc(0.95rem * var(--base-scale)) !important;
    }}

    /* 原文流動資訊框與 Streamlit 原生 Markdown 覆寫 */
    .stInfo {{
        background-color: rgba(30, 144, 255, 0.1) !important;
        color: var(--text-color) !important;
        padding: calc(15px * var(--base-scale)) !important;
    }}
    
    .stMarkdown p, .stInfo p, .streamlit-expanderContent p {{
        font-size: calc(1rem * var(--base-scale)) !important;
        line-height: calc(1.6 * var(--base-scale)) !important;
    }}
    
    /* 覆寫 Expander (段落練習) 的標題字體 */
    .streamlit-expanderHeader {{
        font-size: calc(1rem * var(--base-scale)) !important;
    }}
</style>
""", unsafe_allow_html=True)[cite: 1]

# 依據選擇動態計算路由 ID 並秒讀資料
reading_id = "1" if "1" in selected_reading else "2" if "2" in selected_reading else "3" if "3" in selected_reading else "4"[cite: 1]
# ... (接續你原本 load_reading_text 與 get_audio 的核心邏輯) ...
