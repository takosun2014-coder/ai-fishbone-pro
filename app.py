import streamlit as st
import google.generativeai as genai
import json
import streamlit.components.v1 as components # 引入組件功能

# ... (前面的 API 設定與模型偵測保持不變) ...

# 在顯示結果的地方，將原本的 st.markdown(f"```mermaid...```") 替換為以下：

def render_mermaid(code):
    # 這段 HTML 會強迫瀏覽器去下載繪圖引擎並畫出圖案
    fmt_code = f"""
    <div class="mermaid">
        {code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    """
    components.html(fmt_code, height=600, scrolling=True)

# ... (在分析成功後的邏輯中) ...
if st.button("🚀 開始深度真因分析"):
    # ... (前面的 AI 請求邏輯) ...
    
    # [繪製魚骨圖語法]
    mm_code = "graph LR\n"
    mm_code += f"    Problem(({issue}))\n"
    for i, (m6, seconds) in enumerate(data.items()):
        m_id = f"M{i}"
        mm_code += f"    {m_id}[{m6}] --> Problem\n"
        for j, (second, thirds) in enumerate(seconds.items()):
            s_id = f"{m_id}S{j}"
            mm_code += f"    {s_id}[{second.replace('(', '').replace(')', '')}] --> {m_id}\n"
            for k, third in enumerate(thirds):
                t_id = f"T{i}{j}{k}"
                mm_code += f"    {t_id}[{third.replace('(', '').replace(')', '')}] --> {s_id}\n"

    st.success("🎉 分析完成！")
    st.write("### 魚骨圖視覺化")
    render_mermaid(mm_code) # 使用我們新寫的強制繪圖函數
    
    st.write("---")
    with st.expander("📂 查看結構化資料"):
        st.json(data)
