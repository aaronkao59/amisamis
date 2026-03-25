import streamlit as st
import random

# 1. 數據解構：將詞彙定義為不可分割的字典單元
WORDS_DATA = [
    {"amis": "Mahakakerem", "zh": "黎明 / 清晨"}, {"amis": "Tanikay", "zh": "蟬 / 鳴叫聲"},
    {"amis": "Afesa’", "zh": "嘶嘶聲"}, {"amis": "Kakarayan", "zh": "天空"},
    {"amis": "Fo’is", "zh": "星星"}, {"amis": "Cidal", "zh": "太陽"},
    {"amis": "Micelem", "zh": "沉沒 / 落山"}, {"amis": "Pahanhan", "zh": "休息"},
    {"amis": "Mi’orong", "zh": "肩扛"}, {"amis": "Kinaira", "zh": "收穫"},
    {"amis": "Niyaro’", "zh": "部落"}, {"amis": "Folad", "zh": "月亮"},
    {"amis": "Fali", "zh": "風"}, {"amis": "Rengorengosan", "zh": "草叢"},
    {"amis": "Pahinoker", "zh": "靜謐"}, {"amis": "Pawalian", "zh": "曬穀場"},
    {"amis": "Panay", "zh": "水稻"}, {"amis": "Mato’asay", "zh": "長者"},
    {"amis": "Pakimad", "zh": "敘事"}, {"amis": "Fafahiyan", "zh": "女性"},
    {"amis": "Lipahak", "zh": "快樂"}, {"amis": "Lihaday", "zh": "悠閒"},
    {"amis": "Mafoti’", "zh": "睡覺"}, {"amis": "Tapelik", "zh": "海浪"},
    {"amis": "Riyar", "zh": "海洋"}, {"amis": "Omah", "zh": "田地"},
    {"amis": "Lamal", "zh": "火"}, {"amis": "O’ol", "zh": "雲霧"},
    {"amis": "Mitiliday", "zh": "學生"}, {"amis": "Satapang", "zh": "開始"}
]

# 2. 初始化應用狀態 (Session State)
if 'index_list' not in st.session_state:
    st.session_state.index_list = list(range(len(WORDS_DATA)))
    random.shuffle(st.session_state.index_list)
    st.session_state.current_ptr = 0
    st.session_state.show_answer = False

# 3. UI 構建：重建純粹的測試框架
st.set_page_config(page_title="阿美語誦讀測試", layout="centered")
st.title("🏹 原理級：阿美語詞彙誦讀測試")
st.markdown("---")

# 計算進度
progress = (st.session_state.current_ptr + 1) / len(WORDS_DATA)
st.progress(progress)
st.write(f"進度：{st.session_state.current_ptr + 1} / {len(WORDS_DATA)}")

# 獲取當前詞彙
current_idx = st.session_state.index_list[st.session_state.current_ptr]
word = WORDS_DATA[current_idx]

# 4. 核心視覺區域
with st.container():
    # 使用大型字體呈現阿美語，強調視覺識別
    st.markdown(f"""
        <div style="text-align: center; padding: 50px; border: 2px solid #4CAF50; border-radius: 15px; background-color: #f9f9f9;">
            <h1 style="font-size: 64px; color: #2E7D32; margin-bottom: 0;">{word['amis']}</h1>
        </div>
    """, unsafe_allow_html=True)

    st.write("\n")
    
    # 顯示答案邏輯
    if st.session_state.show_answer:
        st.info(f"💡 中文含義：{word['zh']}")
    else:
        st.write(" ")

# 5. 控制邏輯 (Logic Reconstruction)
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("顯示答案", use_container_width=True):
        st.session_state.show_answer = True
        st.rerun()

with col2:
    if st.button("下一個 (Next)", type="primary", use_container_width=True):
        if st.session_state.current_ptr < len(WORDS_DATA) - 1:
            st.session_state.current_ptr += 1
        else:
            st.success("🎉 全部詞彙測試完成！重新打亂中...")
            random.shuffle(st.session_state.index_list)
            st.session_state.current_ptr = 0
        st.session_state.show_answer = False
        st.rerun()

with col3:
    if st.button("打亂重來", use_container_width=True):
        random.shuffle(st.session_state.index_list)
        st.session_state.current_ptr = 0
        st.session_state.show_answer = False
        st.rerun()

st.markdown("---")
st.caption("第一性原理提醒：誦讀的本質是口腔肌肉對拼音符號的物理反應，請專注於每一個 `'` 符號的停頓。")
