import streamlit as st
import google.generativeai as genai
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io

# --- 頁面設定 ---
st.set_page_config(page_title="專業標準魚骨圖工具", layout="wide")
st.title("🛡️ 專業級標準魚骨圖生成系統")
st.write("本工具由 **AI 應用規劃師 坤生** 監製 - 專供 TPS/Lean 專家使用")

# --- Matplotlib 中文顯示設定 (嘗試解決雲端中文亂碼問題) ---
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# --- 核心功能：繪製標準魚骨圖 ---
def draw_standard_fishbone(problem, data):
    # 1. 建立畫布
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off') # 關閉座標軸

    # 2. 繪製主脊椎 (Spine)
    spine_start = (1, 5)
    spine_end = (10, 5)
    ax.annotate("", xy=spine_end, xytext=spine_start,
                arrowprops=dict(arrowstyle="-|>", lw=3, color='navy'))

    # 3. 繪製魚頭 (核心問題)
    head_box = patches.FancyBboxPatch((spine_end[0] + 0.2, 4), 1.8, 2,
                                      boxstyle="round,pad=0.1", ec="navy", fc="orange", alpha=0.8)
    ax.add_patch(head_box)
    ax.text(spine_end[0] + 1.1, 5, problem, ha='center', va='center', fontsize=12, fontweight='bold', wrap=True)

    # 4. 繪製大骨與要因 (6M)
    m_keys = list(data.keys())
    # 設定大骨在脊椎上的連接點 (x座標)
    attach_points = [3, 5, 7, 3.5, 5.5, 7.5]
    
    for i, m_key in enumerate(m_keys):
        if i >= len(attach_points): break # 避免超過6個
        
        attach_x = attach_points[i]
        is_top = i < 3 # 前三個在上面，後三個在下面

        # 計算大骨的起始點和角度
        if is_top:
            bone_start = (attach_x - 1.5, 8.5)
            bone_end = (attach_x, 5.1) # 稍微高一點點避開主脊
            text_y = 8.8
            angle_deg = -60 # 用於文字旋轉參考
        else:
            bone_start = (attach_x - 1.5, 1.5)
            bone_end = (attach_x, 4.9) # 稍微低一點點
            text_y = 1.2
            angle_deg = 60

        # 畫大骨線條
        ax.annotate("", xy=bone_end, xytext=bone_start,
                    arrowprops=dict(arrowstyle="-", lw=2, color='darkred'))
        
        # 標示 6M 大類名稱
        ax.text(bone_start[0], text_y, m_key, ha='center', va='center', 
                fontsize=14, fontweight='bold', color='darkred',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="darkred", lw=1))

        # 繪製細項要因 (作為文字列表顯示在大骨旁邊，保持畫面整潔)
        sub_causes = []
        try:
            for second, thirds in data[m_key].items():
                sub_causes.append(f"• {second}")
                for third in thirds:
                    sub_causes.append(f"  - {third}")
        except: pass # 避免資料格式錯誤導致崩潰

        detail_text = "\n".join(sub_causes)
        if detail_text:
            text_x_offset = 0.2
            detail_y = bone_start[1] + (0.5 if not is_top else -0.5)
            ax.text(bone_start[0] + text_x_offset, detail_y, detail_text, 
                    ha='left', va=('top' if is_top else 'bottom'), fontsize=9,
                    bbox=dict(boxstyle="square,pad=0.5", fc="#f0f2f6", ec="none", alpha=0.7))

    plt.tight_layout()
    return fig

# --- API 初始化 ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(target_model)
        st.sidebar.success(f"✅ AI 就緒 ({target_model.split('/')[-1]})")
    except:
        st.sidebar.error("⚠️ AI 連線異常")
        model = None
else:
    st.error("❌ 請設定 API Key")
    st.stop()

# --- 主介面 ---
st.info("💡 提示：此模式將繪製具有標準斜角結構的專業魚骨圖。")
issue = st.text_input("請輸入要分析的事件：", placeholder="例如：長照機構諾羅病毒群聚事件")

if st.button("🚀 開始分析並繪圖"):
    if not issue or not model:
        st.warning("請輸入主題並確保 AI 連線正常")
    else:
        with st.spinner("AI 正在進行深度分析並構建幾何圖形..."):
            try:
                # Prompt 保持不變
                prompt = f"你是一位 TPS 專家。請針對『{issue}』進行 6M 要因分析。嚴格回傳 JSON：{{'人': {{'二次要因': ['三次要因']}}}}。確保包含 6M 的六個面向。"
                response = model.generate_content(prompt)
                raw_text = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(raw_text)
                
                # 呼叫繪圖函數
                fig = draw_standard_fishbone(issue, data)
                
                # 顯示圖表
                st.pyplot(fig)
                
                # --- 建立下載按鈕 ---
                # 將 Matplotlib 圖表轉存到記憶體中
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                
                st.download_button(
                    label="💾 下載標準魚骨圖 (PNG)",
                    data=img_buffer,
                    file_name=f"魚骨圖分析_{issue}.png",
                    mime="image/png"
                )
                
                with st.expander("查看原始分析數據"):
                    st.json(data)

            except Exception as e:
                st.error(f"繪圖失敗，請稍後再試。錯誤：{e}")
