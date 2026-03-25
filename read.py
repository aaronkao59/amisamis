import streamlit as st
import re
import random
from gtts import gTTS
import io

# --- 頁面配置 ---
st.set_page_config(page_title="朗讀訓練機", layout="wide", initial_sidebar_state="collapsed")

# 自定義 CSS 以優化移動端體驗與詞卡樣式
st.markdown("""
<style>
    .word-card {
        border: 2px solid #4CAF50;
        border-radius: 20px;
        padding: 60px 20px;
        text-align: center;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 原始文章內容 ---
article_text = """
文章名稱：[Dadaya no niyaro’]		
（Mahakakerem ko romi’ad, matengil to ko soni no tanikay,）（ satapang saho sa afesa’ sa makaleng ko soni, ）（matenes to mato mafana’ay a misalof to soni,safangcal sato a matengil. ）（Yo madodem to ko kakarayan masadak to ko fo’is,）（ mato sonol sanay to ko soni, sa fangcal sato a tengilen.）

（O malingaday a maemin, sadak saho ko cidal lomowad to talakatayalan, ）（tangasa sa micelem ko cidal ta minokay a pahanhan, ）（deng to no romi’ad sa, mi’orongto to pitaw malalitemoh i rihi’ no facal sedi sa matatawa a malalicay,）（ masasipalemed, ko nanay makadofah ko kinaira toni a mihecaan ato pali’ayaw to saki no dafak a tatayalen. ）（Tada masinanotay, damsayay, fangcalay a niyaro’ koni.）

（Masadak to ko folad, seriw seriw sa ko fali,）（ nengneng han ko lawac no lalan macelak to ko hana. ）（Mato maemin masafaeloh masanek ko fali nona pala, seriw seriw sa nai rengorengosan. ）（Tengil han to ko soni no tanikay ngalengalef saan mato pasenengay, ）（masinanot mato pahinoker sanay to tona palapalaan a masoni.）

（Sacikacikay sa i pawalian to panay a malawla ko wawa, ）（o mato’asay sa maro’ i falaw mahaholol, pakimad. ）（O fafahiyan sa i, mitapid to macicihay a riko’, roma i, miparpar to pinawali a padaka. ）（Talacowa caay ka samaan ko ’orip i niyaro’,）（ nika nengneng han ko tamdaw maemin lipahak lihaday makadofah ko ’orip.）

（Mato caho katenes ko ’aro, kafahalan sa o tenok to no lafii, ）（tengil han cecacecay to ko soni, lahedaw sato ko soni no tanikay, ）（o folad mamicelem to, polong no hekal maemin to awa to ko ades’es no soni. ）（talalemed to ko tamdamdaw a mafoti’, patedi han no folad ko widawidan no panay,）（ seriw seriw han no fali sa matiya sa o tapelik no riyar a manengneng.）
			
（Caho ka taengad ko romi’ad, mi’orong to to sakatayal mililis to rihi’ no omah ko malingaday, ）（misatapang to malingad a matayal. ）（Caho caho katenes conihal to ko wali masadak to ko matiyaay o lamal a cidal patedi to hekal, ）（sa maliemi sato ko o’ol i rengorengosan ato i papah no kilang a manengneng. ）（Satapang to rarawraw ko tamdaw no niyaro’, ）（o mitiliday sa matatawatawa to i lalan talapitilidan, o satapangan to no niyaro’ koni a romi’ad.）
"""

# --- 資料處理函數 ---
def get_long_words(text):
    clean_text = re.sub(r'[（）]', '', text)
    words = re.findall(r'\b\w+’?\b', clean_text)
    vowels = 'aeiouAEIOU'
    # 計算音節：計算母音出現次數
    long_words = [w for w in set(words) if sum(1 for char in w if char in vowels) >= 3]
    return sorted(long_words)

def play_audio(text):
    try:
        tts = gTTS(text=text, lang='it') # 阿美語暫以義大利語引擎模擬發音效果較佳
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    except:
        st.error("語音生成失敗，請檢查網路連接。")

# --- 初始化狀態 ---
if 'words' not in st.session_state:
    st.session_state.words = get_long_words(article_text)
if 'word_idx' not in st.session_state:
    st.session_state.word_idx = 0
if 'show_chinese' not in st.session_state:
    st.session_state.show_chinese = False

# --- App 標題 ---
st.title("🎙️ 朗讀訓練機")

tab1, tab2, tab3 = st.tabs(["🎴 多音節詞卡", "📏 單句練習", "📄 段落練習"])

# --- 第一部分：詞卡功能 ---
with tab1:
    current_word = st.session_state.words[st.session_state.word_idx]
    
    # 詞卡顯示區
    display_content = f"（中文意思預留）" if st.session_state.show_chinese else current_word
    st.markdown(f'<div class="word-card"><h1>{display_content}</h1></div>', unsafe_allow_html=True)
    
    # 按鈕區 (放置於詞卡下方)
    c1, c2, c3 = st.columns(3)
    if c1.button("⬅️ 上一個"):
        st.session_state.word_idx = (st.session_state.word_idx - 1) % len(st.session_state.words)
        st.session_state.show_chinese = False
        st.rerun()
    if c2.button("🔊 發音"):
        play_audio(current_word)
    if c3.button("➡️ 下一個"):
        st.session_state.word_idx = (st.session_state.word_idx + 1) % len(st.session_state.words)
        st.session_state.show_chinese = False
        st.rerun()
        
    c4, c5 = st.columns(2)
    if c4.button("🔀 打亂順序"):
        random.shuffle(st.session_state.words)
        st.session_state.word_idx = 0
        st.rerun()
    if c5.button("🔄 翻轉/顯示中文"):
        st.session_state.show_chinese = not st.session_state.show_chinese
        st.rerun()
    
    st.caption(f"進度: {st.session_state.word_idx + 1} / {len(st.session_state.words)}")

# --- 第二部分：單句練習 ---
with tab2:
    st.subheader("以（）區分的單句訓練")
    # 提取括號內的內容
    sentences = re.findall(r'（(.*?)）', article_text, re.DOTALL)
    
    for i, sent in enumerate(sentences):
        sent = sent.strip()
        if sent:
            with st.container():
                st.write(f"**Sentence {i+1}:**")
                st.info(sent)
                col_audio, col_check = st.columns([1, 2])
                with col_audio:
                    if st.button(f"🔊 聆聽", key=f"audio_s_{i}"):
                        play_audio(sent)
                with col_check:
                    st.radio("練習狀態", ["未通過", "待加強", "通過"], key=f"check_s_{i}", horizontal=True, label_visibility="collapsed")
                st.markdown("---")

# --- 第三部分：段落練習 ---
with tab3:
    st.subheader("全文段落訓練")
    # 先按換行切分段落
    raw_paragraphs = [p.strip() for p in article_text.split('\n\n') if "文章名稱" not in p and p.strip()]
    
    for i, para in enumerate(raw_paragraphs):
        # 刪除括號
        clean_para = re.sub(r'[（）]', '', para)
        with st.expander(f"第 {i+1} 段", expanded=True):
            st.write(clean_para)
            col_a, col_b = st.columns([1, 2])
            with col_a:
                if st.button(f"🔊 聆聽全段", key=f"audio_p_{i}"):
                    play_audio(clean_para)
            with col_b:
                st.radio("評分", ["未通過", "待加強", "通過"], key=f"check_p_{i}", horizontal=True, label_visibility="collapsed")
