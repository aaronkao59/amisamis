import streamlit as st
import re
import random
from gtts import gTTS
import io

# --- 頁面配置 ---
st.set_page_config(page_title="朗讀訓練機", layout="wide", initial_sidebar_state="collapsed")

# 自定義 CSS
st.markdown("""
<style>
    .word-card {
        border: 2px solid #4CAF50;
        border-radius: 15px;
        padding: 30px 10px;
        text-align: center;
        background-color: #ffffff;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .stButton > button {
        width: 100%;
        padding: 0.4rem 0.2rem !important;
        font-size: 0.85rem !important;
    }
    [data-testid="column"] {
        padding: 0 2px !important;
    }
    .cn-text-box {
        color: #2E7D32;
        background-color: #f1f8e9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    .amis-text {
        font-size: 1.1rem;
        font-weight: 500;
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

# --- 數據定義 ---
translation_map = {
    "Mahakakerem": "傍晚/天快黑時", "matengil": "聽見/聽到", "tanikay": "蟬", "satapang": "開始", 
    "afesa’": "響亮/嘶鳴", "makaleng": "清亮/嘹亮", "matenes": "很久", "mafana’ay": "會/明白", 
    "misalof": "修理/修正", "safangcal": "變美/變好", "madodem": "變暗/陰暗", "kakarayan": "天空", 
    "masadak": "出現/出來", "tengilen": "聽", "malingaday": "耕作的人/農夫", "lomowad": "起床/出發", 
    "talakatayalan": "工作的地方", "tangasa": "到達", "micelem": "沒入/落山", "minokay": "回家", 
    "pahanhan": "休息", "mi’orongto": "扛著", "malalitemoh": "相遇/遇見", "malalicay": "交談/聊天", 
    "masasipalemed": "互相祝福", "makadofah": "豐富/豐收", "kinaira": "產量/獲收", "mihecaan": "年度/年", 
    "pali’ayaw": "預備/準備", "tatayalen": "要做的工作", "masinanotay": "整潔的", "damsayay": "溫暖/親切", 
    "fangcalay": "美麗的/好的", "niyaro’": "部落", "macelak": "盛開/綻放", "masafaeloh": "全新的/變新", 
    "masanek": "氣味/聞起來", "rengorengosan": "草叢", "ngalengalef": "更加/越發", "pasenengay": "誇耀/自豪", 
    "masinanot": "整潔/有條理", "pahinoker": "平靜/安靜", "palapalaan": "大地/荒野", "sacikacikay": "跑來跑去", 
    "pawalian": "曬穀場", "malawla": "嬉戲/玩耍", "mato’asay": "長者/老人", "mahaholol": "聊天/聚談", 
    "pakimad": "講故事", "fafahiyan": "女性/婦女", "mitapid": "縫補/編織", "macicihay": "破舊的", 
    "miparpar": "鋪開/攤開", "pinawali": "曝曬", "lipahak": "快樂", "lihaday": "安詳/自在", 
    "katenes": "很久", "kafahalan": "突然/深夜", "cecacecay": "一個接一個", "lahedaw": "消失/不見", 
    "ades’es": "吵雜/喧鬧", "talalemed": "入夢/幸運", "mafoti’": "睡覺", "widawidan": "稻穗", 
    "manengneng": "看見/看到", "taengad": "天亮/黎明", "sakatayal": "工具/器具", "mililis": "沿著邊緣", 
    "misatapang": "開始(做)", "conihal": "放晴/太陽出來", "matiyaay": "像是...一樣", "rarawraw": "喧嘩/吵鬧", 
    "mitiliday": "學生/讀書的人", "talapitilidan": "學校", "satapangan": "開始/起頭"
}

# 完整補回 25 句單句翻譯
sent_trans = [
    "傍晚時分，聽見了蟬鳴聲，", "起初聲音斷斷續續，", "久了似乎熟練了鳴叫，變得悅耳。", 
    "當天空變暗星星出現，", "聲音像是順流而下般好聽。",
    "耕作的人，太陽剛出來就起床去工作，", "直到夕陽西下才回家休息，",
    "整天辛苦工作，扛著鋤頭在田埂邊相遇，說笑聊天，", "互相祝福，希望今年產量豐收，也為明天的工作預備。", "這是一個整潔、溫馨、美麗的部落。",
    "月亮出來了，涼風徐徐，", "看那路邊花朵盛開。", "大地似乎充滿了清新的氣息，從草叢中傳來陣陣涼風。",
    "聽那蟬鳴聲更加響亮，彷彿在誇耀，", "像是讓這片大地平靜下來般鳴叫著。",
    "孩子們在曬穀場跑來跑去玩耍，", "長者坐在走廊聊天、講故事。", "婦女們在縫補破舊的衣服，或者在整理曝曬的乾菜。",
    "雖然部落生活簡單，", "但看每個人都過得快樂安詳、生活充實。",
    "坐沒多久，突然到了深夜，", "聽見聲音一個個消失，蟬鳴聲不見了，", "月亮要下山了，全世界靜悄悄。",
    "人們進入夢鄉，月光照在稻穗上，", "微風吹過像海浪波動。",
    "天還沒亮，農夫扛著工具沿著田邊出發工作。沒多久太陽出來照耀大地，萬物甦醒，這是部落一天的開始。"
]

raw_text_content = """（Mahakakerem ko romi’ad, matengil to ko soni no tanikay,）（ satapang saho sa afesa’ sa makaleng ko soni, ）（matenes to mato mafana’ay a misalof to soni,safangcal sato a matengil. ）（Yo madodem to ko kakarayan masadak to ko fo’is,）（ mato sonol sanay to ko soni, sa fangcal sato a tengilen.）

（O malingaday a maemin, sadak saho ko cidal lomowad to talakatayalan, ）（tangasa sa micelem ko cidal ta minokay a pahanhan, ）（deng to no romi’ad sa, mi’orongto to pitaw malalitemoh i rihi’ no facal sedi sa matatawa a malalicay,）（ masasipalemed, ko nanay makadofah ko kinaira toni a mihecaan ato pali’ayaw to saki no dafak a tatayalen. ）（Tada masinanotay, damsayay, fangcalay a niyaro’ koni.）

（Masadak to ko folad, seriw seriw sa ko fali,）（ nengneng han ko lawac no lalan macelak to ko hana. ）（Mato maemin masafaeloh masanek ko fali nona pala, seriw seriw sa nai rengorengosan. ）（Tengil han to ko soni no tanikay ngalengalef saan mato pasenengay, ）（masinanot mato pahinoker sanay to tona palapalaan a masoni.）

（Sacikacikay sa i pawalian to panay a malawla ko wawa, ）（o mato’asay sa maro’ i falaw mahaholol, pakimad. ）（O fafahiyan sa i, mitapid to macicihay a riko’, roma i, miparpar to pinawali a padaka. ）（Talacowa caay ka samaan ko ’orip i niyaro’,）（ nika nengneng han ko tamdaw maemin lipahak lihaday makadofah ko ’orip.）

（Mato caho katenes ko ’aro, kafahalan sa o tenok to no lafii, ）（tengil han cecacecay to ko soni, lahedaw sato ko soni no tanikay, ）（o folad mamicelem to, polong no hekal maemin to awa to ko ades’es no soni. ）（talalemed to ko tamdamdaw a mafoti’, patedi han no folad ko widawidan no panay,）（ seriw seriw han no fali sa matiya sa o tapelik no riyar a manengneng.）

（Caho ka taengad ko romi’ad, mi’orong to to sakatayal mililis to rihi’ no omah ko malingaday, ）（misatapang to malingad a matayal. ）（Caho caho katenes conihal to ko wali masadak to ko matiyaay o lamal a cidal patedi to hekal, ）（sa maliemi sato ko o’ol i rengorengosan ato i papah no kilang a manengneng. ）（Satapang to rarawraw ko tamdaw no niyaro’, ）（o mitiliday sa matatawatawa to i lalan talapitilidan,）（ o satapangan to no niyaro’ koni a romi’ad.）"""

# --- 工具函數 ---
def speak(text):
    try:
        tts = gTTS(text=text, lang='it')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except: return None

# --- Session State 初始化 ---
if 'word_list' not in st.session_state:
    st.session_state.word_list = sorted(list(translation_map.keys()))
if 'w_idx' not in st.session_state: st.session_state.w_idx = 0
if 'w_flip' not in st.session_state: st.session_state.w_flip = False

# --- App 介面 ---
st.title("菁英朗讀訓練機")
tabs = st.tabs(["🎴 生詞詞卡", "📏 單句朗讀訓練", "📄 段落練習"])

# --- Tab 1: 生詞詞卡 ---
with tabs[0]:
    curr_w = st.session_state.word_list[st.session_state.w_idx]
    display = translation_map[curr_w] if st.session_state.w_flip else curr_w
    st.markdown(f'<div class="word-card"><h2>{display}</h2><p style="color:gray;">{st.session_state.w_idx+1}/{len(st.session_state.word_list)}</p></div>', unsafe_allow_html=True)
    
    cols = st.columns([1, 1, 1, 1, 1.2]) 
    if cols[0].button("⬅️ 往前", key="prev_w"):
        st.session_state.w_idx = (st.session_state.w_idx - 1) % len(st.session_state.word_list)
        st.session_state.w_flip = False
        st.rerun()
    if cols[1].button("🔊 發音", key="play_w"):
        audio = speak(curr_w)
        if audio: st.audio(audio)
    if cols[2].button("➡️ 向後", key="next_w"):
        st.session_state.w_idx = (st.session_state.w_idx + 1) % len(st.session_state.word_list)
        st.session_state.w_flip = False
        st.rerun()
    if cols[3].button("🔀 隨機", key="shuffle_w"):
        random.shuffle(st.session_state.word_list)
        st.session_state.w_idx = 0
        st.rerun()
    if cols[4].button("🔄 翻轉/中文", key="flip_w"):
        st.session_state.w_flip = not st.session_state.w_flip
        st.rerun()

# --- Tab 2: 單句朗讀訓練 (順序修正) ---
with tabs[1]:
    st.subheader("單句朗讀訓練")
    sents = re.findall(r'（(.*?)）', raw_text_content, re.DOTALL)
    for i, s in enumerate(sents):
        s = s.strip()
        with st.container():
            # 1. 阿美語原文
            st.info(s)
            
            # 2. 中文翻譯框 (展開時)
            if st.session_state.get(f"s_cn_{i}", False):
                st.markdown(f'<div class="cn-text-box">{sent_trans[i] if i < len(sent_trans) else "（翻譯內容更新中）"}</div>', unsafe_allow_html=True)
            
            # 3. 顯示中文按鈕 (位於中文翻譯框下方)
            if st.button("顯示/隱藏中文翻譯", key=f"show_s_cn_{i}"):
                st.session_state[f"s_cn_{i}"] = not st.session_state.get(f"s_cn_{i}", False)
                st.rerun()
                
            # 4. 播放與評分列
            c1, c2 = st.columns([1, 2])
            if c1.button("🔊 播放句子", key=f"play_s_{i}"):
                audio = speak(s)
                if audio: st.audio(audio)
            c2.radio("評分", ["未通過", "待加強", "通過"], key=f"chk_s_{i}", horizontal=True, label_visibility="collapsed")
            st.divider()

# --- Tab 3: 段落練習 (移除顯示中文按鈕) ---
with tabs[2]:
    st.subheader("段落練習 (共 6 段)")
    paras_list = [p.strip() for p in raw_text_content.split('\n\n') if p.strip()]
    
    for i, p in enumerate(paras_list):
        clean_p = re.sub(r'[（）]', '', p)
        with st.expander(f"第 {i+1} 段", expanded=True):
            # 1. 阿美語原文
            st.write(clean_p)
            
            # 2. 播放與評分列 (此處不再顯示中文按鈕)
            c1, c2 = st.columns([1, 2])
            if c1.button("🔊 播放全段", key=f"play_p_{i}"):
                audio = speak(clean_p)
                if audio: st.audio(audio)
            c2.radio("段落評分", ["未通過", "待加強", "通過"], key=f"chk_p_{i}", horizontal=True, label_visibility="collapsed")
