import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="AI 專業要因分析工具", layout="wide")
st.title("🛡️ 深度要因分析魚骨圖系統")
st.write("本工具由 **AI 應用規劃師 坤生** 監製")

# 1. 安全載入 API Key
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("❌ 找不到 API 金鑰，請檢查 Streamlit Secrets 設定。")
    st.stop()

# 2. 自動偵測可用模型 (解決 404 的核心邏輯)
@st.cache_resource
def get_best_model():
    try:
        # 列出所有可用的模型名稱
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 優先順序邏輯
        priority_list = [
            'models/gemini-1.5-flash', 
            'models/gemini-1.5-flash-latest',
            'models/gemini-pro'
        ]
        
        for p in priority_list:
            if p in models:
                return genai.GenerativeModel(p), p
        
        # 如果都不在清單中，就選第一個可用的
        if models:
            return genai.GenerativeModel(models[0]), models[0]
        return None, None
    except Exception as e:
        st.error(f"無法存取 Google 模型清單，請確認 API Key 是否有效。錯誤：{e}")
        return None, None

model, model_name = get_best_model()

if model:
    st.success(f"✅ 系統就緒！目前使用的模型大腦：{model_name}")
else:
    st.warning("⚠️ 無法偵測到可用模型，請確認您的 Google AI Studio 專案狀態。")

# 3. UI 介面
issue = st.text_input("輸入要分析的事件：", placeholder="例如：長照機構諾羅病毒群聚事件")

if st.button("🚀 開始深度真因分析"):
    if not issue:
        st.warning("請輸入分析主題")
    else:
        with st.spinner("AI 顧問正在進行 6M 與 5-Why 深度分析..."):
            try:
                prompt = f"""
                你是一位精通 TPS 真因分析的專家。請針對『{issue}』進行要因分析。
                要求：使用 6M 模型，每一類別包含二次與三次要因。
                請僅以 JSON 格式回傳：{{"類別": {{"二次要因": ["三次要因A", "三次要因B"]}}}}
                """
                # 強制使用最新的 API 呼叫方式
                response = model.generate_content(prompt)
                
                # 清理並解析 JSON
                res_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(res_text)

                # 繪製魚骨圖 (Mermaid 語法)
                mm_code = "graph LR\n"
                mm_code += f"    Problem(({issue}))\n"
                for i, (m6, seconds) in enumerate(data.items()):
                    m_id = f"M{i}"
                    mm_code += f"    {m_id}[{m6}] --> Problem\n"
                    for j, (second, thirds) in enumerate(seconds.items()):
                        s_id = f"{m_id}S{j}"
                        mm_code += f"    {s_id}[{second}] --> {m_id}\n"
                        for k, third in enumerate(thirds):
                            mm_code += f"    T{i}{j}{k}[{third}] --> {s_id}\n"

                st.markdown(f"### 魚骨圖視覺化\n```mermaid\n{mm_code}\n```")
                st.write("---")
                st.json(data)
                
            except Exception as e:
                st.error(f"分析過程中斷：{str(e)}")
                st.info("建議檢查：1. API Key 是否過期 2. Google AI Studio 帳號是否需重新驗證")
