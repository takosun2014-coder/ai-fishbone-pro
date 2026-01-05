import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="AI 專業要因分析工具", layout="wide")
st.title("🛡️ 深度要因分析圖系統 (高穩定版)")
st.write("本工具由 **AI 應用規劃師 坤生** 監製")

# 1. 初始化 API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 自動選擇可用模型
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(target_model)
        st.sidebar.success(f"系統已連線: {target_model}")
    except Exception as e:
        st.error(f"模型初始化失敗: {e}")
        st.stop()
else:
    st.error("❌ 請在 Secrets 設定 GEMINI_API_KEY")
    st.stop()

# 2. 輸入與分析
issue = st.text_input("輸入要分析的事件 (如：長照機構諾羅病毒群聚)", "")

if st.button("🚀 開始深度分析"):
    if not issue:
        st.warning("請輸入內容")
    else:
        with st.spinner("AI 顧問正在應用 6M 模型進行深度分析..."):
            try:
                prompt = f"你是一位 TPS 專家。請針對『{issue}』進行 6M 要因分析。請嚴格回傳 JSON 格式：{{'人': {{'二次要因A': ['三次要因A1', '三次要因A2']}}}}。不要說廢話。"
                response = model.generate_content(prompt)
                
                raw_text = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(raw_text)
                
                # 3. 繪製圖表 (使用 Graphviz 引擎)
                st.subheader("魚骨圖結構分析")
                
                # 構建 Graphviz 代碼
                dot_code = 'digraph G {\n'
                dot_code += '  rankdir=LR;\n' # 從左到右
                dot_code += '  node [fontname="Microsoft JhengHei", shape=box, style=filled, fillcolor="lightblue"];\n'
                dot_code += f'  "核心問題\\n({issue})" [shape=ellipse, fillcolor="orange"];\n'
                
                for m6, seconds in data.items():
                    # 6M 大類
                    dot_code += f'  "{m6}" -> "核心問題\\n({issue})";\n'
                    for second, thirds in seconds.items():
                        # 二次要因
                        dot_code += f'  "{second}" -> "{m6}";\n'
                        for third in thirds:
                            # 三次要因 (真因)
                            dot_code += f'  "{third}" -> "{second}";\n'
                
                dot_code += '}'
                
                # 強制顯示圖表
                st.graphviz_chart(dot_code)
                
                st.write("---")
                st.subheader("詳細數據清單")
                st.json(data)

            except Exception as e:
                st.error(f"分析失敗，建議稍後再試。錯誤訊息：{e}")
