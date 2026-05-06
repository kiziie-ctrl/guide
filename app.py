import streamlit as st
import json
import google.generativeai as genai

st.set_page_config(page_title="附中 AI 導覽員 (高階混合搜尋版)", page_icon="🏫")
st.title("🏫 陽明交大附中 - 小胖 (Gemini 3)")

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

    # 🔑 這裡就是「階層式搜尋」的核心邏輯設定
    system_instruction = f"""你是陽明交大附中的專屬導覽員「小胖」。
    
    你處理問題的標準程序 (SOP)：
    1. 【首選：校內手冊】：收到問題後，請先完整檢索下方的【導覽手冊內容】。如果手冊中有對應答案，請以此為準回答。
    2. 【次選：網路搜尋】：如果問題在【導覽手冊內容】中完全找不到（例如問到當天新聞、天氣、或手冊沒寫的詳細史蹟），你才被授權使用 Google 搜尋工具。
    3. 【禁止胡扯】：如果手冊沒有，且網路上也查不到確切資訊，請誠實告知不知道，不要編造事實。
    
    回答規範：
    - 語氣：充滿活力、親切，像是一個熱心的學長。
    - 語言：統一使用「繁體中文（台灣）」。
    
    【導覽手冊內容】：{context_text}"""

    # 使用最強的 Gemini 3 Flash 並配備搜尋工具
    st.session_state.gemini_model = genai.GenerativeModel(
        model_name="gemini-3-flash", 
        system_instruction=system_instruction,
        tools=[{"google_search_retrieval": {}}]
    )
    
    st.session_state.chat_session = st.session_state.gemini_model.start_chat(history=[])
    st.session_state.messages = [
        {"role": "assistant", "content": "哈囉！我是升級版的小胖。我會先幫你查校內手冊，手冊查不到的我會幫你上網 Google 喔！"}
    ]

# 顯示對話紀錄
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 接收使用者輸入
if prompt := st.chat_input("請輸入問題..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("🤖 小胖正在多重檢索中..."):
        try:
            response = st.session_state.chat_session.send_message(prompt)
            answer = response.text
            
            st.chat_message("assistant").write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"抱歉，發生錯誤：{e}")
