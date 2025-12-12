import streamlit as st
import datetime
import random
import time
from dataclasses import dataclass, field

# ==========================================
# 1. 系統設定與核心參數 (System Config)
# ==========================================
st.set_page_config(
    page_title="Project Huizhen v0.1",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 模擬 2025 年的資料庫
CURRENT_YEAR = 2025
HUIZHEN_BIRTH_YEAR = 1982

# 角色設定
PROFILE = {
    "name": "惠貞",
    "age": CURRENT_YEAR - HUIZHEN_BIRTH_YEAR,  # 43歲
    "job": "資深社工",
    "mbti": "INFJ", # 內向、直覺、情感、判斷
    "hobbies": ["村上春樹", "健走", "老歌", "烹飪"],
    "bio": "1982年生，社工系畢業。經歷過921地震，對聲音敏感。外表冷靜，內心柔軟。"
}

# 預設新聞庫 (模擬 RAG 檢索結果)
NEWS_DATABASE = [
    "【社會】2025年台灣邁入超高齡社會，長照據點人力荒，社工負荷瀕臨極限。",
    "【藝文】台北市立美術館《2025 台北雙年展：地平線上的低吟》本週開幕。",
    "【生活】氣象署發布大雨特報，信義區今晚降雨機率 80%。",
    "【健康】換季過敏族群激增，醫師建議減少戶外運動。",
    "【懷舊】滾石唱片推出「千禧年情歌」復刻黑膠，引發七年級生搶購熱潮。"
]

# ==========================================
# 2. 狀態管理 (Session State)
# ==========================================
if 'affection' not in st.session_state:
    st.session_state.affection = 50  # 初始好感度
if 'chat_history' not in st.session_state:
    st.session_state.chat_history =
if 'user_images' not in st.session_state:
    st.session_state.user_images =
if 'current_mood' not in st.session_state:
    st.session_state.current_mood = "neutral"  # neutral, happy, tired, annoyed, shy

# ==========================================
# 3. 核心邏輯函數 (Core Logic)
# ==========================================

def get_time_context():
    """核對使用者時區與惠貞的作息"""
    now = datetime.datetime.now()
    hour = now.hour
    
    # 定義作息表
    if 0 <= hour < 7:
        return "sleeping", "惠貞已就寢 (離線)"
    elif 7 <= hour < 8:
        return "commuting", "通勤中"
    elif 8 <= hour < 12:
        return "working_high", "工作中 (忙碌)"
    elif 12 <= hour < 13:
        return "lunch", "午休時間"
    elif 13 <= hour < 18:
        return "working_out", "外訪/開會中"
    elif 18 <= hour < 20:
        return "resting", "下班休息 (能量低)"
    elif 20 <= hour < 23:
        return "free", "空閒 (黃金交流期)"
    else:
        return "sleeping", "準備就寢"

def calculate_affection_delta(user_input, time_status):
    """
    計算好感度增減
    邏輯：工作時打擾扣分，提及興趣加分，展現共情加分
    """
    delta = 0
    feedback = ""
    
    # 關鍵字分析
    keywords_positive = ["辛苦", "聽你說", "村上", "展覽", "吃飯", "休息"]
    keywords_negative = ["快回", "照片", "見面", "為什麼不理我"]
    
    # 1. 作息影響
    if time_status in ["working_high", "working_out", "sleeping"]:
        if len(user_input) > 10: # 簡單問候還好，長篇大論會扣分
            delta -= 2
            feedback = "(她在忙，你的訊息造成了壓力)"
    
    # 2. 內容影響
    for k in keywords_positive:
        if k in user_input:
            delta += random.randint(1, 3)
            feedback = "(她覺得被理解)"
            
    for k in keywords_negative:
        if k in user_input:
            delta -= random.randint(2, 5)
            feedback = "(她感到不悅)"

    # 3. 內向者加成
    if st.session_state.affection < 40 and "見面" in user_input:
        delta -= 5 # 熟度不夠就約見面，大扣分
        feedback = "(嚇到她了)"

    return delta, feedback

def generate_response(user_input, time_status, delta):
    """
    模擬 LLM 生成回應
    """
    response = ""
    mood = "neutral"
    
    # 狀態攔截
    if time_status == "sleeping":
        return "[系統] 對方已開啟勿擾模式，將在明早回覆。", "neutral"
    
    if time_status in ["working_high", "working_out"]:
        responses = ["稍等，我在忙個案...", "現在有點忙，晚點回你。", "（已讀）"]
        return random.choice(responses), "annoyed"

    # 一般對話邏輯
    if delta > 0:
        if "村上" in user_input:
            response = "你也讀村上春樹嗎？那段關於『挪威的森林』的描寫，我一直記得很清楚..."
            mood = "happy"
        elif "辛苦" in user_input:
            response = "謝謝...今天處理了一個安置個案，真的心很累。有你這句話好多了。"
            mood = "shy"
        else:
            news = random.choice(NEWS_DATABASE)
            response = f"剛好看到新聞說「{news[:15]}...」，覺得這社會變動好快。你怎麼看？"
            mood = "happy"
            
    elif delta < 0:
        response = "我現在真的沒力氣討論這個..."
        mood = "annoyed"
    else:
        # 閒聊
        response = "嗯，我知道了。今天是週末，你有什麼打算嗎？"
        mood = "neutral"
        
    # 好感度極高時的特殊回應
    if st.session_state.affection > 80:
        response = f"其實...{response} (她看著你的眼神變溫柔了)"
        mood = "love"
        
    return response, mood

# ==========================================
# 4. 前端介面 (UI Layout)
# ==========================================

# CSS 黑魔法：強制分割畫面 60% / 40%
st.markdown("""
<style>
   .main.block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    /* 上半部影像區 */
   .image-area {
        height: 60vh;
        width: 100%;
        background-color: #2b2b2b;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 1rem;
        position: relative;
    }
    /* 下半部對話區 */
   .chat-area {
        height: 35vh;
        overflow-y: auto;
        background-color: #f0f2f6;
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid #ddd;
    }
   .stTextInput {
        position: fixed;
        bottom: 0;
        width: 100%;
        background: white;
        padding: 10px;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Sidebar: 初始設定與狀態監控
# ----------------------------
with st.sidebar:
    st.header("🔧 遊戲初始化")
    
    # 功能 1: 上傳三張圖片
    uploaded_files = st.file_uploader("上傳 3 張人物參考圖 (Front/Side/Expression)", 
                                    accept_multiple_files=True, type=['jpg', 'png'])
    
    if uploaded_files and len(uploaded_files) >= 1:
        st.success(f"已載入 {len(uploaded_files)} 張圖片，神經渲染模型 Ready。")
        st.session_state.user_images = uploaded_files
    else:
        st.warning("請上傳圖片以生成「惠貞」")

    st.divider()
    st.subheader("📊 系統狀態 (Debug)")
    time_status, time_desc = get_time_context()
    st.write(f"目前時間: {datetime.datetime.now().strftime('%H:%M')}")
    st.write(f"作息狀態: {time_desc}")
    
    # 顯示好感度條
    st.write(f"好感度: {st.session_state.affection}/100")
    st.progress(st.session_state.affection / 100)
    
    if st.session_state.affection < 30:
        st.error("狀態: 厭惡")
    elif st.session_state.affection > 90:
        st.balloons()
        st.success("狀態: 男女朋友")
    elif st.session_state.affection > 70:
        st.info("狀態: 好感")

# ----------------------------
# Main Area: 60% 影像
# ----------------------------
mood_emoji = {
    "neutral": "😐",
    "happy": "😊",
    "tired": "😪",
    "annoyed": "😒",
    "shy": "😳",
    "love": "😍"
}

st.markdown('<div class="image-area">', unsafe_allow_html=True)

# 這裡模擬 "根據對話內容改變表情"
# 實際上這裡會連接 NeRF/SadTalker 模型，將 st.session_state.current_mood 轉為驅動參數
display_text = f"<h1>{mood_emoji[st.session_state.current_mood]}</h1>"

if st.session_state.user_images:
    # 如果有上傳圖片，顯示第一張並加上情緒濾鏡(模擬)
    st.image(st.session_state.user_images, caption=f"惠貞 ({st.session_state.current_mood})", use_column_width=True)
else:
    # 預設佔位符
    st.markdown(f"<div style='text-align:center; color:white;'>{display_text}<br>等待圖片生成中...</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Main Area: 40% 對話
# ----------------------------
st.markdown('<div class="chat-area">', unsafe_allow_html=True)

# 顯示歷史對話
for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**You:** {text}")
    else:
        st.markdown(f"**惠貞:** {text}")

st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Input Area
# ----------------------------
# 使用 form 避免每次輸入都重新整理整個頁面導致體驗不佳
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input("輸入對話...", placeholder="試著聊聊 921、社工工作或村上春樹...")
    submit_button = st.form_submit_button("發送")

if submit_button and user_input:
    # 1. 計算好感度
    delta, feedback = calculate_affection_delta(user_input, time_status)
    new_score = st.session_state.affection + delta
    st.session_state.affection = max(0, min(100, new_score)) # 限制在 0-100
    
    # 2. 生成回應
    response, new_mood = generate_response(user_input, time_status, delta)
    st.session_state.current_mood = new_mood
    
    # 3. 更新歷史
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", response))
    
    # 4. 強制刷新以更新 UI
    st.rerun()

# 模擬新聞自動推播 (冷啟動邏輯)
if len(st.session_state.chat_history) == 0:
    intro_news = random.choice(NEWS_DATABASE)
    st.session_state.chat_history.append(("bot", f"早安。剛看到這個新聞...{intro_news}，讓人有點在意。"))
    st.rerun()
