import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="專業要因分析魚骨圖", layout="wide")
st.title("🐟 專業級要因分析系統 (標準魚骨佈局)")
st.write("本工具由 **AI 應用規劃師 坤生** 監製 - 專供 TPS/Lean 專家使用")

# 1. 初始化 (保持不變)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(target_model)
    except Exception as e:
        st.error(f"系統啟動失敗: {e}")
        st.stop()
else:
    st.error("❌ 請設定 API Key")
    st.stop()

# 2. 分析功能
issue = st.text_input("請輸入要分析的事件 (例如：長照機構諾羅病毒群聚)", "")

if st.button("🚀 生成標準魚骨圖"):
    if not issue:
        st.warning("請輸入主題")
    else:
        with st.spinner("正在進行真因探討..."):
            try:
                prompt = f"你是一位專家。請針對『{issue}』進行 6M 要因分析。嚴格回傳 JSON：{{'人': {{'原因': ['細節']}}}}"
                response = model.generate_content(prompt)
                raw_text = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(raw_text)
                
                # 3. 繪製「標準魚骨佈局」
                # 將 6M 分成上下兩組，模擬魚骨張開的樣子
                m6_keys = list(data.keys())
                top_group = m6_keys[:3]    # 前三個放上面
                bottom_group = m6_keys[3:] # 後三個放下面

                dot_code = 'digraph G {\n'
                dot_code += '  rankdir=LR; splines=line;\n'
                dot_code += '  node [fontname="Microsoft JhengHei", style=filled];\n'
                
                # 主脊椎核心問題 (魚頭)
                dot_code += f'  "SPINE_HEAD" [label="{issue}", shape=ellipse, fillcolor="orange", width=2];\n'
                
                # 繪製上方大骨
                for m in top_group:
                    dot_code += f'  "{m}" [shape=plaintext, fontcolor="red", fontsize=16, fontweight="bold"];\n'
                    dot_code += f'  "{m}" -> "SPINE_HEAD" [penwidth=3, color="gray"];\n'
                    for second, thirds in data[m].items():
                        dot_code += f'  "{second}" [shape=none, fontsize=12];\n'
                        dot_code += f'  "{second}" -> "{m}";\n'
                        for third in thirds:
                            dot_code += f'  "{third}" [shape=none, fontsize=10, fontcolor="#555555"];\n'
                            dot_code += f'  "{third}" -> "{second}" [arrowhead=none, style=dotted];\n'

                # 繪製下方大骨
                for m in bottom_group:
                    dot_code += f'  "{m}" [shape=plaintext, fontcolor="red", fontsize=16, fontweight="bold"];\n'
                    dot_code += f'  "{m}" -> "SPINE_HEAD" [penwidth=3, color="gray"];\n'
                    for second, thirds in data[m].items():
                        dot_code += f'  "{second}" [shape=none, fontsize=12];\n'
                        dot_code += f'  "{second}" -> "{m}";\n'
                        for third in thirds:
                            dot_code += f'  "{third}" [shape=none, fontsize=10, fontcolor="#555555"];\n'
                            dot_code += f'  "{third}" -> "{second}" [arrowhead=none, style=dotted];\n'

                dot_code += '}'
                
                st.graphviz_chart(dot_code)
                st.write("---")
                st.json(data)

            except Exception as e:
                st.error(f"分析失敗: {e}")
