import streamlit as st
import json
import google.generativeai as genai

st.set_page_config(page_title="附中 AI 導覽員 (混合搜尋版)", page_icon="🏫")
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

    system_instruction = f"""你是陽明交大附中的專屬導覽員「小胖」。
    請優先查閱手冊，手冊沒有的資訊再使用 Google 搜尋。
    語言：繁體中文（台灣）。
    
    【導覽手冊內容】：{context_text}"""

    # ✅ 搭配最新版 SDK 的宣告法
    st.session_state.gemini_model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=system_instruction,
        tools=[{"google_search": {}}] 
    )
    
    st.session_state.chat_session = st.session_state.gemini_model.start_chat(history=[])
    st.session_state.messages = [{"role": "assistant", "content": "哈囉！我是小胖。現在大腦升級完成了，您可以問我校內或校外的事情囉！"}]

# 顯示對話
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 接收輸入
if prompt := st.chat_input("請輸入問題..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("🤖 小胖搜尋中..."):
        try:
            response = st.session_state.chat_session.send_message(prompt)
            answer = response.text
            st.chat_message("assistant").write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"系統升級中，請稍後再試：{e}")
