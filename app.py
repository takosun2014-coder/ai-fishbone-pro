import streamlit as st
import google.generativeai as genai
import json

# 頁面基本設定
st.set_page_config(page_title="AI 要因分析工具", layout="wide")
st.title("🛡️ 深度要因分析魚骨圖")
st.write("---")

# 1. 檢查金鑰並初始化
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 自動抓取可用的模型
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(target_model)
        st.sidebar.success(f"系統就緒：{target_model}")
    except Exception as e:
        st.error(f"金鑰或模型初始化失敗: {e}")
        st.stop()
else:
    st.error("❌ 請在 Secrets 中設定 GEMINI_API_KEY")
    st.stop()

# 2. 使用者輸入
issue = st.text_input("輸入要分析的事件 (例如：長照機構諾羅病毒群聚)", "")

if st.button("開始分析"):
    if not issue:
        st.warning("請輸入內容")
    else:
        with st.spinner("AI 顧問正在分析中..."):
            try:
                # 簡化 Prompt，確保 AI 回傳標準格式
                prompt = f"你是一位 TPS 專家。請針對『{issue}』進行 6M 要因分析。請嚴格回傳 JSON 格式：{{'人': {{'原因1': ['細節1']}}}}。不要說廢話。"
                response = model.generate_content(prompt)
                
                # 處理回傳內容
                raw_text = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(raw_text)
                
                # 3. 建立 Mermaid 語法 (最穩定的 Markdown 寫法)
                mm_code = "graph LR\n"
                mm_code += f"    Problem(({issue}))\n"
                
                for m6, seconds in data.items():
                    m_id = m6
                    mm_code += f"    {m_id}[{m6}] --> Problem\n"
                    for second, thirds in seconds.items():
                        s_id = second.replace(" ", "")
                        mm_code += f"    {s_id}[{second}] --> {m_id}\n"
                        for t in thirds:
                            t_id = t.replace(" ", "")
                            mm_code += f"    {t_id}[{t}] --> {s_id}\n"

                # 顯示魚骨圖 (使用 Streamlit 最原生的方式)
                st.subheader("魚骨圖結果")
                st.markdown(f"```mermaid\n{mm_code}\n```")
                
                st.write("---")
                st.subheader("詳細數據清單")
                st.json(data)

            except Exception as e:
                st.error(f"發生錯誤：{e}")
                st.info("可能是 AI 回傳格式不正確，請再按一次分析試試。")
