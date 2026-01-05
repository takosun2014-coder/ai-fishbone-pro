import streamlit as st
import google.generativeai as genai
import json

# 頁面配置：設定為寬螢幕模式
st.set_page_config(page_title="AI 專業要因分析工具", layout="wide")
st.title("🛡️ 深度要因分析魚骨圖系統")
st.write("本工具由 **AI 應用規劃師 坤生** 監製，專為 TPS/Lean 管理優化設計。")

# 讀取 API Key (這部分等一下會在 Streamlit Cloud 設定)
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("⚠️ 尚未偵測到 API 金鑰，請在 Streamlit Secrets 中設定 GEMINI_API_KEY")

# 使用者輸入區
st.info("💡 提示：輸入具體事件，如『長照機構為何發生諾羅病毒群聚』，AI 將自動進行 3 層真因探討。")
issue = st.text_input("請輸入要分析的事件名稱：", placeholder="例如：產品表面刮痕比率過高")

if st.button("🚀 開始深度真因分析"):
    if not issue:
        st.warning("請先輸入分析主題")
    else:
        with st.spinner("AI 顧問正在應用 6M 模型與 5-Why 邏輯分析中..."):
            try:
                # 設定專業的 Prompt 邏輯
                prompt = f"""
                你是一位精通 TPS (豐田生產方式) 的專家。請針對『{issue}』進行要因分析。
                請嚴格遵守以下格式：
                1. 使用 6M 分類：人(Man), 機(Machine), 料(Material), 法(Method), 測(Measurement), 環(Environment)。
                2. 每個 6M 類別下必須包含『二次要因』，每個二次要因下必須包含『三次要因(真因)』。
                3. 只回傳 JSON 格式數據，結構如下：
                {{ "人": {{ "二次要因名稱": ["三次要因A", "三次要因B"] }} }}
                """
                response = model.generate_content(prompt)
                
                # 清理並解析 JSON 數據
                res_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(res_text)

                # 建立 Mermaid 魚骨圖語法
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

                # 呈現結果
                st.success("🎉 分析完成！")
                st.markdown(f"### 魚骨圖視覺化 (深度分析)\n```mermaid\n{mm_code}\n```")
                
                st.write("---")
                with st.expander("📂 查看結構化要因清單"):
                    st.json(data)
                    
            except Exception as e:
                st.error(f"分析過程發生錯誤：{str(e)}")
                st.info("可能是 API 連線問題，請檢查金鑰設定。")
