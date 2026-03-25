import streamlit as st
import re
import random
from gtts import gTTS
import io

# --- 初始設定 ---
st.set_page_config(page_title="朗讀訓練機", layout="wide")
st.title("🎙️ 朗讀訓練機")

# --- 文本資料 ---
article_title = "Dadaya no niyaro’"
raw_text = """
Mahakakerem ko romi’ad, matengil to ko soni no tanikay, satapang saho sa afesa’ sa makaleng ko soni, matenes to mato mafana’ay a misalof to soni, safangcal sato a matengil. Yo madodem to ko kakarayan masadak to ko fo’is, mato sonol sanay to ko soni, sa fangcal sato a tengilen.

O malingaday a maemin, sadak saho ko cidal lomowad to talakatayalan, tangasa sa micelem ko cidal ta minokay a pahanhan, deng to no romi’ad sa, mi’orongto to pitaw malalitemoh i rihi’ no facal sedi sa matatawa a malalicay, masasipalemed, ko nanay makadofah ko kinaira toni a mihecaan ato pali’ayaw to saki no dafak a tatayalen. Tada masinanotay, damsayay, fangcalay a niyaro’ koni.

Masadak to ko folad, seriw seriw sa ko fali, nengneng han ko lawac no lalan macelak to ko hana. Mato maemin masafaeloh masanek ko fali nona pala, seriw seriw sa nai rengorengosan. Tengil han to ko soni no tanikay ngalengalef saan mato pasenengay, masinanot mato pahinoker sanay to tona palapalaan a masoni.

Sacikacikay sa i pawalian to panay a malawla ko wawa, o mato’asay sa maro’ i falaw mahaholol, pakimad. O fafahiyan sa i, mitapid to macicihay a riko’, roma i, miparpar to pinawali a padaka. Talacowa caay ka samaan ko ’orip i niyaro’, nika nengneng han ko tamdaw maemin lipahak lihaday makadofah ko ’orip.

Mato caho katenes ko ’aro, kafahalan sa o tenok to no lafii, tengil han cecacecay to ko soni, lahedaw sato ko soni no tanikay, o folad mamicelem to, polong no hekal maemin to awa to ko ades’es no soni. talalemed to ko tamdamdaw a mafoti’, patedi han no folad ko widawidan no panay, seriw seriw han no fali sa matiya sa o tapelik no riyar a manengneng.

Caho ka taengad ko romi’ad, mi’orong to to sakatayal mililis to rihi’ no omah ko malingaday, misatapang to malingad a matayal. Caho caho katenes conihal to ko wali masadak to ko matiyaay o lamal a cidal patedi to hekal, sa maliemi sato ko o’ol i rengorengosan ato i papah no kilang a manengneng. Satapang to rarawraw ko tamdaw no niyaro’, o mitiliday sa matatawatawa to i lalan talapitilidan, o satapangan to no niyaro’ koni a romi’ad.
"""

# --- 工具函數 ---
def count_syllables(word):
    # 簡單音節計算：計算母音出現次數 (a, e, i, o, u)
    word = word.lower()
    return len(re.findall(r'[aeiou]', word))

def speak(text):
    # 使用 gTTS 生成音檔
    # 註：阿美語並非 gTTS 官方支援，這裡暫用 'id' (印尼語) 或 'it' (義大利語) 模擬語音邏輯
    tts = gTTS(text=text, lang='it') 
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 資料處理 ---
# 提取 3 音節以上詞彙
words_list = sorted(list(set(re.findall(r'\b\w+’?\b', raw_text))))
long_words = [w for w in words_list if count_syllables(w) >= 3]

# 模擬中文對照表（實際應用時需補完）
translation_map = {w: "（中文意思預留位）" for w in long_words}

# --- Session State 初始化 ---
if 'word_idx' not in st.session_state:
    st.session_state.word_idx = 0
if 'shuffled_words' not in st.session_state:
    st.session_state.shuffled_words = long_words.copy()
if 'flip_card' not in st.session_state:
    st.session_state.flip_card = False

# --- App 導航 ---
tabs = st.tabs(["🎴 多音節詞卡測試", "📏 單句練習", "📄 段落練習"])

# --- 第一部分：詞卡測試 ---
with tabs[0]:
    st.header("多音節詞卡")
    
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("⬅️ 上一個"):
        st.session_state.word_idx = (st.session_state.word_idx - 1) % len(st.session_state.shuffled_words)
        st.session_state.flip_card = False
    if col2.button("➡️ 下一個"):
        st.session_state.word_idx = (st.session_state.word_idx + 1) % len(st.session_state.shuffled_words)
        st.session_state.flip_card = False
    if col3.button("🔀 打亂順序"):
        random.shuffle(st.session_state.shuffled_words)
        st.session_state.word_idx = 0
    if col4.button("🔄 翻轉/顯示原文"):
        st.session_state.flip_card = not st.session_state.flip_card

    # 詞卡顯示
    current_word = st.session_state.shuffled_words[st.session_state.word_idx]
    
    st.markdown(f"""
    <div style="border:2px solid #4CAF50; border-radius: 15px; padding: 50px; text-align: center; background-color: #f9f9f9;">
        <h1 style="color: #2E7D32;">{"🔍 " + translation_map[current_word] if st.session_state.flip_card else current_word}</h1>
        <p style="color: gray;">進度：{st.session_state.word_idx + 1} / {len(st.session_state.shuffled_words)}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔊 播放發音"):
        audio_fp = speak(current_word)
        st.audio(audio_fp, format='audio/mp3')

# --- 第二部分：單句練習 ---
with tabs[1]:
    st.header("單句練習")
    # 使用正則表達式切分句子，保留標點
    sentences = re.split(r'(?<=[,.])\s*', raw_text.strip())
    
    for i, sent in enumerate(sentences):
        if sent.strip():
            with st.container():
                c1, c2, c3 = st.columns([0.6, 0.2, 0.2])
                c1.write(f"**{i+1}.** {sent}")
                if c2.button("🔊 播放", key=f"sent_btn_{i}"):
                    st.audio(speak(sent), format='audio/mp3')
                c3.radio("狀態", ["尚未選擇", "通過", "待加強", "未通過"], key=f"check_sent_{i}", label_visibility="collapsed")
                st.divider()

# --- 第三部分：段落練習 ---
with tabs[2]:
    st.header("段落練習")
    paragraphs = [p.strip() for p in raw_text.split('\n\n') if p.strip()]
    
    for i, para in enumerate(paragraphs):
        with st.expander(f"第 {i+1} 段", expanded=True):
            st.write(para)
            col_a, col_b = st.columns([0.2, 0.8])
            if col_a.button("🔊 播放全段", key=f"para_btn_{i}"):
                st.audio(speak(para), format='audio/mp3')
            col_b.radio("評分", ["尚未選擇", "通過", "待加強", "未通過"], key=f"check_para_{i}", horizontal=True)

# --- 側邊欄資訊 ---
with st.sidebar:
    st.subheader("統計數據")
    st.write(f"總詞彙數：{len(words_list)}")
    st.write(f"多音節詞（>=3）：{len(long_words)}")
    st.info("提示：詞卡模式可點擊「翻轉」查看中文意思（範例已預留欄位）。")
