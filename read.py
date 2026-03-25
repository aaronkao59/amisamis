import streamlit as st
import re

# 第一性原理：數據底層定義
TEXT = """
Mahakakerem ko romi’ad, matengil to ko soni no tanikay, satapang saho sa afesa’ sa makaleng ko soni, matenes to mato mafana’ay a misalof to soni, safangcal sato a matengil. Yo madodem to ko kakarayan masadak to ko fo’is, mato sonol sanay to ko soni, sa fangcal sato a tengilen.

O malingaday a maemin, sadak saho ko cidal lomowad to talakatayalan, tangasa sa micelem ko cidal ta minokay a pahanhan, deng to no romi’ad sa, mi’orongto to pitaw malalitemoh i rihi’ no facal sedi sa matatawa a malalicay, masasipalemed, ko nanay makadofah ko kinaira toni a mihecaan ato pali’ayaw to saki no dafak a tatayalen. Tada masinanotay, damsayay, fangcalay a niyaro’ koni.

Masadak to ko folad, seriw seriw sa ko fali, nengneng han ko lawac no lalan macelak to ko hana. Mato maemin masafaeloh masanek ko fali nona pala, seriw seriw sa nai rengorengosan. Tengil han to ko soni no tanikay ngalengalef saan mato pasenengay, masinanot mato pahinoker sanay to tona palapalaan a masoni.

Sacikacikay sa i pawalian to panay a malawla ko wawa, o mato’asay sa maro’ i falaw mahaholol, pakimad. O fafahiyan sa i, mitapid to macicihay a riko’, roma i, miparpar to pinawali a padaka. Talacowa caay ka samaan ko ’orip i niyaro’, nika nengneng han ko tamdaw maemin lipahak lihaday makadofah ko ’orip.

Mato caho katenes ko ’aro, kafahalan sa o tenok to no lafii, tengil han cecacecay to ko soni, lahedaw sato ko soni no tanikay, o folad mamicelem to, polong no hekal maemin to awa to ko ades’es no soni. talalemed to ko tamdamdaw a mafoti’, patedi han no folad ko widawidan no panay, seriw seriw han no fali sa matiya sa o tapelik no riyar a manengneng.

Caho ka taengad ko romi’ad, mi’orong to to sakatayal mililis to rihi’ no omah ko malingaday, misatapang to malingad a matayal. Caho caho katenes conihal to ko wali masadak to ko matiyaay o lamal a cidal patedi to hekal, sa maliemi sato ko o’ol i rengorengosan ato i papah no kilang a manengneng. Satapang to rarawraw ko tamdaw no niyaro’, o mitiliday sa matatawatawa to i lalan talapitilidan, o satapangan to no niyaro’ koni a romi’ad.
"""

def count_syllables(word):
    # 阿美語音節邏輯：元音 (a, e, i, o, u) 以及喉塞音 (') 作為發音單位
    # 這裡以元音字母作為判斷基礎
    vowels = "aeiouAEIOU"
    return len([char for char in word if char in vowels])

def get_multisyllabic_words(text):
    # 移除非字母字符並拆解單詞
    clean_text = re.sub(r'[^\w\s\u02bc\u0027]', '', text)
    words = list(set(clean_text.split())) # 去重
    return [w for w in words if count_syllables(w) >= 3]

# --- Streamlit UI 設置 ---
st.set_page_config(page_title="朗讀訓練機", layout="centered")
st.title("🎙️ 朗讀訓練機 (Dadaya no niyaro’)")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🧩 音節詞卡 (發音練習)", "📏 單句訓練 (氣息控制)", "📖 段落訓練 (語境流動)"])

# 第一部分：多音節詞卡
with tab1:
    st.header("多音節（3+）單詞挑戰")
    words_list = get_multisyllabic_words(TEXT)
    
    if 'word_index' not in st.session_state:
        st.session_state.word_index = 0

    current_word = words_list[st.session_state.word_index]
    
    st.info("目標：精準發出每一個音節，注意舌頭位置。")
    st.markdown(f"""
    <div style="text-align: center; padding: 50px; border: 2px solid #4CAF50; border-radius: 15px; background-color: #f9f9f9;">
        <h1 style="color: #2E7D32; font-size: 60px;">{current_word}</h1>
        <p style="color: #666;">音節數: {count_syllables(current_word)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ 上一個", use_container_width=True):
            st.session_state.word_index = (st.session_state.word_index - 1) % len(words_list)
            st.rerun()
    with col2:
        if st.button("下一個 ➡️", use_container_width=True):
            st.session_state.word_index = (st.session_state.word_index + 1) % len(words_list)
            st.rerun()
    
    st.caption(f"目前進度：{st.session_state.word_index + 1} / {len(words_list)}")

# 第二部分：單句練習
with tab2:
    st.header("單句呼吸法練習")
    # 使用正則表達式根據 , 和 . 拆分單句
    sentences = re.split(r'[,.]', TEXT)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    
    st.write("在標點符號處完整停頓，並重新吸氣。")
    for i, sen in enumerate(sentences):
        with st.expander(f"句子 {i+1}"):
            st.markdown(f"### {sen}")
            st.button(f"標記為已練習 #{i}", key=f"btn_{i}")

# 第三部分：段落練習
with tab3:
    st.header("全段落邏輯流動")
    paragraphs = TEXT.strip().split("\n\n")
    
    for i, para in enumerate(paragraphs):
        st.subheader(f"段落 {i+1}")
        st.write(para)
        st.divider()

st.sidebar.markdown("""
### 訓練說明
1. **音節詞卡**：針對肌肉記憶，解決「舌頭打結」問題。
2. **單句訓練**：針對「肺活量配速」，確保讀完一句才換氣。
3. **段落練習**：針對「長時間專注度」。
""")
