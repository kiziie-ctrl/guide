import streamlit as st
import json
import google.generativeai as genai

st.set_page_config(page_title="附中 AI 導覽員", page_icon="🏫")
st.title("🏫 陽明交大附中 - 小胖 (Gemini 大腦)")

# 讀取 JSON 導覽手冊
try:
    with open('tour.json', 'r', encoding='utf-8') as f:
        context_text = json.dumps(json.load(f), ensure_ascii=False)
except FileNotFoundError:
    st.error("🚨 找不到 tour.json！")
    st.stop()

# 初始化 Gemini API
if "gemini_model" not in st.session_state:
    # 🛡️ 安全寫法：改成去 Streamlit 的保險箱 (Secrets) 拿密碼
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"] 
    genai.configure(api_key=GEMINI_API_KEY)

    # 設定系統人設與規則
    system_instruction = f"""你是陽明交大附中的親切導覽員「小胖」。
    請嚴格根據以下提供的【導覽手冊內容】來回答問題。
    ⚠️ 重要指令：必須使用「繁體中文（台灣）」回答。手冊沒寫的請告知不知道。
    【導覽手冊內容】：{context_text}"""

    # 建立 Gemini 模型
    st.session_state.gemini_model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=system_instruction
    )
    
    # 啟動 Gemini 專屬的記憶聊天室
    st.session_state.chat_session = st.session_state.gemini_model.start_chat(history=[])
    
    # 建立畫面上顯示的第一句話
    st.session_state.messages = [
        {"role": "assistant", "content": "哈囉！我是換上 Gemini 大腦的小胖，想聽我唱校歌嗎？"}
    ]

# 在畫面上印出對話紀錄
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 接收使用者輸入
if prompt := st.chat_input("想問關於附中的什麼？"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("🤖 Gemini 小胖查閱中..."):
        try:
            # 將問題丟給 Gemini 聊天室
            response = st.session_state.chat_session.send_message(prompt)
            answer = response.text
            
            st.chat_message("assistant").write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"抱歉，發生錯誤：{e}")
