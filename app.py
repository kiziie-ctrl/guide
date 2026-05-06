# 1. 安裝 Gemini 官方套件與 Streamlit
!pip install streamlit google-generativeai -q
!npm install -g localtunnel

# 2. 寫入外部知識庫 (tour.json)
%%writefile tour.json
{
  "生物醫學實驗班": "這是與陽明交大醫學院合作的特色班級，學習智慧醫療與生命科學。",
  "電機資訊實驗班": "結合 AI 與半導體課程，培育未來的護國群山科技人才。",
  "地理位置": "我們位於新竹縣竹北市，就在豆子埔溪畔，校舍環境優美。",
  "校歌": "竹北高中校歌由駱正榮先生作曲、連添財先生作詞。歌詞是：『豆子埔溪畔，可愛的校園，成長的搖籃；精誠博雅，紳士淑女的風範，為人處事的領綱。豆子埔溪畔，快樂的校園，三年的同窗；開闊胸襟，是我竹北的夥伴，是我學習的榜樣。溪畔搖籃令我回憶，溪畔搖籃令我難忘。』"
}

# 3. 寫入主程式 (app.py)
%%writefile app.py
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
    # ⚠️ 老師請注意：這裡要換成您剛剛申請的「AIza」開頭的密碼
    GEMINI_API_KEY = "AIzaSyDBfH7Wjeb9QZ6-8lShKO-CzrFxBGew9cY" 
    genai.configure(api_key=GEMINI_API_KEY)

    # 設定系統人設與規則
    system_instruction = f"""你是陽明交大附中的親切導覽員「小胖」。
    請嚴格根據以下提供的【導覽手冊內容】來回答問題。
    ⚠️ 重要指令：必須使用「繁體中文（台灣）」回答。手冊沒寫的請告知不知道。
    【導覽手冊內容】：{context_text}"""

    # 建立 Gemini 模型 (對應老師截圖中出現的模型)
    st.session_state.gemini_model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", # 使用免費額度支援的輕量模型
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

# 4. 挖隧道並顯示密碼
import urllib
print("👉 你的 Tunnel 密碼:", urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip())
!streamlit run app.py & npx localtunnel --port 8501