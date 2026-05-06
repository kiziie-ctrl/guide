import streamlit as st
import json
import google.generativeai as genai

st.set_page_config(page_title="附中 AI 導覽員 (終極連網版)", page_icon="🏫")
st.title("🏫 陽明交大附中 - 小胖 (Gemini 2.5)")

# 讀取 JSON 導覽手冊 (RAG 核心)
try:
    with open('tour.json', 'r', encoding='utf-8') as f:
        context_text = json.dumps(json.load(f), ensure_ascii=False)
except FileNotFoundError:
    st.error("🚨 找不到 tour.json！")
    st.stop()

# 初始化 Gemini API
if "gemini_model" not in st.session_state:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"] 
    genai.configure(api_key=GEMINI_API_KEY)

    # 混合搜尋策略指令
    system_instruction = f"""你是陽明交大附中的專屬導覽員「小胖」。
    
    你處理問題的標準程序 (SOP)：
    1. 【優先】：請先從下方的【導覽手冊內容】尋找答案。
    2. 【補充】：如果手冊沒有答案，請使用 Google 搜尋工具查閱最新資訊。
    3. 【規範】：使用「繁體中文（台灣）」，語氣親切有活力。
    
    【導覽手冊內容】：{context_text}"""

    # ✅ 關鍵修正：將 tools 改為簡單的字串清單 ["google_search"]
    st.session_state.gemini_model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=system_instruction,
        tools=["google_search"] # ✨ 這是 2026 年最穩定的字串宣告法
    )
    
    st.session_state.chat_session = st.session_state.gemini_model.start_chat(history=[])
    st.session_state.messages = [
        {"role": "assistant", "content": "哈囉！我是小胖。現在大腦設定終於調對了，我可以幫你查手冊也可以上網囉！"}
    ]

# 顯示對話紀錄
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 接收使用者輸入
if prompt := st.chat_input("請輸入問題..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("🤖 小胖正在檢索資料..."):
        try:
            response = st.session_state.chat_session.send_message(prompt)
            answer = response.text
            
            st.chat_message("assistant").write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"抱歉，發生錯誤：{e}")
