import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="AI 專業要因分析工具", layout="wide")
st.title("🛡️ 深度要因分析魚骨圖系統")
st.write("本工具由 **AI 應用規劃師 坤生** 監製")

# 設定 API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 【自動偵測模型邏輯】
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 優先順序：1.5 Flash -> 1.5 Pro -> Pro
        if 'models/gemini-1.5-flash' in available_models:
            model_name = 'gemini-1.5-flash'
        elif 'models/gemini-1.5-pro' in available_models:
            model_name = 'gemini-1.5-pro'
        else:
            model_name = 'gemini-pro'
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        st.error(f"偵測模型失敗：{e}")
else:
    st.error("請在 Secrets 中設定 GEMINI_API_KEY")

issue = st.text_input("輸入要分析的事件 (如：長照機構諾羅病毒群聚)", placeholder="請輸入...")

if st.button("開始深度分析"):
    if not issue:
        st.warning("請先輸入主題")
    else:
        with st.spinner(f"正在使用模型 {model_name} 分析中..."):
            try:
                prompt = f"你是一位精通 TPS 的專家。請針對『{issue}』進行要因分析。使用 6M 模型，每一類別包含二次與三次要因。請僅以 JSON 格式回傳：{{'類別': {{'二次要因': ['三次要因A']}}}}"
                response = model.generate_content(prompt)
                
                # 清理並解析 JSON
                res_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(res_text)

                # 繪製魚骨圖語法
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

                st.success(f"分析完成！(使用模型: {model_name})")
                st.markdown(f"```mermaid\n{mm_code}\n```")
                st.json(data)
            except Exception as e:
                st.error(f"分析失敗：{e}")
