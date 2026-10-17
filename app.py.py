import json
import re
import streamlit as st

# ==========================================
# 1. 內建民法債編總則詞庫與鮮明標籤色系設定
# ==========================================
TAXONOMY = {
    "LEGAL_SUBJECT": {"name": "法律主體", "color": "#D81B60"},   # 鮮豔洋紅
    "SOURCE_ACT": {"name": "債之發生原因", "color": "#E65100"},  # 濃橘色
    "OBJECT_PERF": {"name": "債之標的/給付", "color": "#D97706"}, # 深琥珀金
    "BREACH_DEF": {"name": "債務不履行/狀態", "color": "#15803D"}, # 深森林綠
    "RIGHT_REMEDY": {"name": "權利與救濟", "color": "#1D4ED8"},  # 皇家藍
    "EXTINCT_TRANS": {"name": "消滅與移轉", "color": "#7E22CE"}, # 深靛紫
    "STATUTE_REF": {"name": "條文與法規", "color": "#4B5563"},   # 石墨灰
}

DEFAULT_VOCAB = {
    "LEGAL_SUBJECT": ["債權人", "債務人", "主債務人", "連帶債務人", "第三人", "受讓人", "賠償權利人", "賠償義務人", "代理人", "本人"],
    "SOURCE_ACT": ["契約", "無因管理", "不當得利", "侵權行為", "單獨行為", "意思表示", "懸賞廣告", "締約過失"],
    "OBJECT_PERF": ["給付", "種類之債", "貨幣之債", "利息之債", "選擇之債", "預定給付", "原狀回復", "損害賠償"],
    "BREACH_DEF": ["給付遲延", "給付不能", "不完全給付", "受領遲延", "歸責事由", "故意", "重大過失", "輕過失", "不可抗力"],
    "RIGHT_REMEDY": ["代位權", "撤銷權", "同時履行抗辯權", "解除權", "終止權", "損害賠償請求權", "違約金", "減少價金請求權"],
    "EXTINCT_TRANS": ["清償", "提存", "抵銷", "免除", "混同", "債權讓與", "債務承擔", "併存之債務承擔"],
}

STATUTE_PATTERN = re.compile(
    r'(?:《(?P<law>[^》]+)》|(?P<law_short>民法|刑法|民事訴訟法))?第(?P<article>\d+(?:-\d+)?)條(?:第(?P<paragraph>\d+)項)?'
)

# ==========================================
# 2. 自動預標註核心邏輯
# ==========================================
def auto_annotate(text: str, vocab: dict) -> list[dict]:
    entities = []

    # A. 字典比對 (自動標註名詞)
    for label, terms in vocab.items():
        for term in terms:
            start = 0
            while True:
                idx = text.find(term, start)
                if idx == -1:
                    break
                entities.append({
                    "start": idx,
                    "end": idx + len(term),
                    "text": term,
                    "label": label
                })
                start = idx + len(term)

    # B. 正則表達式比對 (自動標註法條)
    for match in STATUTE_PATTERN.finditer(text):
        entities.append({
            "start": match.start(),
            "end": match.end(),
            "text": match.group(0),
            "label": "STATUTE_REF"
        })

    # C. 重疊區段處理解決 (取長詞優先)
    entities.sort(key=lambda x: (x['start'], -(x['end'] - x['start'])))
    filtered_entities = []
    last_end = -1
    for ent in entities:
        if ent['start'] >= last_end:
            filtered_entities.append(ent)
            last_end = ent['end']

    return filtered_entities

def render_html_annotation(text: str, entities: list[dict]) -> str:
    """將文字與標註轉化為帶有顏色的標註呈現"""
    entities = sorted(entities, key=lambda x: x['start'])
    html = ""
    last_idx = 0

    for ent in entities:
        start, end, label = ent['start'], ent['end'], ent['label']
        color = TAXONOMY.get(label, {}).get("color", "#4B5563")
        label_name = TAXONOMY.get(label, {}).get("name", label)

        # 拼接未標註文字
        html += text[last_idx:start]
        # 拼接深色顯目標註色塊 (搭配白字)
        chunk = text[start:end]
        html += (
            f'<span style="background-color: {color}; color: #ffffff; padding: 3px 8px; border-radius: 5px; margin: 0 3px; font-weight: 500; display: inline-block;">'
            f'{chunk} <span style="font-size: 0.75em; background-color: rgba(255,255,255,0.25); padding: 1px 5px; border-radius: 3px; margin-left: 3px;">{label_name}</span>'
            f'</span>'
        )
        last_idx = end

    html += text[last_idx:]
    return f'<div style="line-height: 2.3; font-size: 1.1em; padding: 20px; border: 1px solid #d1d5db; border-radius: 8px; background-color: #f9fafb; color: #111827;">{html}</div>'

# ==========================================
# 3. Streamlit Web UI 介面設計
# ==========================================
st.set_page_config(page_title="民法債編總則標註系統", layout="wide")
st.title("⚖️ 民法債編總則語意標註輔助系統")

# 初始化 session state
if "text" not in st.session_state:
    st.session_state.text = "因故意或過失，不法侵害他人之權利者，負損害賠償責任。故意以背於善良風俗之方法，加損害於他人者亦同。依民法第184條第1項，債權人得請求損害賠償。"
if "entities" not in st.session_state:
    st.session_state.entities = auto_annotate(st.session_state.text, DEFAULT_VOCAB)

# SideBar 標籤圖例與維護
with st.sidebar:
    st.header("🏷️ 標籤圖例 (Taxonomy)")
    for code, info in TAXONOMY.items():
        st.markdown(f'<span style="background-color:{info["color"]}; color:white; padding:5px 10px; border-radius:5px; font-weight:bold;">{info["name"]} (`{code}`)</span>', unsafe_allow_html=True)
        st.write("")

    st.markdown("---")
    st.header("⚙️ 字典快速擴充")
    new_term = st.text_input("新增名詞")
    target_label = st.selectbox("歸屬標籤", options=list(TAXONOMY.keys()), format_func=lambda x: TAXONOMY[x]["name"])
    if st.button("加到預標註字典"):
        if new_term:
            DEFAULT_VOCAB[target_label].append(new_term)
            st.session_state.entities = auto_annotate(st.session_state.text, DEFAULT_VOCAB)
            st.success(f"已新增「{new_term}」至 {TAXONOMY[target_label]['name']}")
            st.rerun()

# 主介面區域
tab1, tab2, tab3 = st.tabs(["📝 視覺標註預覽", "✏️ 標註微調與校對", "💾 匯出資料庫 (JSON/Doccano)"])

with tab1:
    st.subheader("📄 匯入或貼上文件")
    
    # 檔案上傳區塊
    uploaded_file = st.file_uploader("📂 請上傳文字檔 (.txt)", type=["txt"])
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        try:
            file_text = bytes_data.decode("utf-8")
        except UnicodeDecodeError:
            try:
                file_text = bytes_data.decode("big5")
            except UnicodeDecodeError:
                file_text = bytes_data.decode("utf-8-sig", errors="ignore")
        
        if file_text != st.session_state.text:
            st.session_state.text = file_text
            st.session_state.entities = auto_annotate(file_text, DEFAULT_VOCAB)
            st.success(f"已成功匯入檔案：{uploaded_file.name}")
            st.rerun()

    # 文字編輯/貼上區塊
    input_text = st.text_area("或在此直接貼上/修改文字：", value=st.session_state.text, height=150)
    
    if st.button("🤖 執行/重新預標註"):
        st.session_state.text = input_text
        st.session_state.entities = auto_annotate(input_text, DEFAULT_VOCAB)
        st.rerun()

    st.subheader("即時視覺標註結果")
    html_code = render_html_annotation(st.session_state.text, st.session_state.entities)
    st.markdown(html_code, unsafe_allow_html=True)

with tab2:
    st.subheader("人工校對清單")
    st.caption("法律系同學可以在此檢查預標註結果，刪除誤標或修改標籤類型：")

    updated_entities = []
    for i, ent in enumerate(st.session_state.entities):
        col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
        with col1:
            st.write(f"**{ent['text']}** (`{ent['start']}:{ent['end']}`)")
        with col2:
            new_label = st.selectbox(
                "標籤選擇",
                options=list(TAXONOMY.keys()),
                index=list(TAXONOMY.keys()).index(ent["label"]),
                format_func=lambda x: TAXONOMY[x]["name"],
                key=f"label_{i}"
            )
            ent["label"] = new_label
        with col3:
            st.write(f"類別: `{new_label}`")
        with col4:
            if not st.checkbox("保留", value=True, key=f"keep_{i}"):
                continue
        updated_entities.append(ent)

    if st.button("更新校對結果"):
        st.session_state.entities = updated_entities
        st.success("標註結果已更新！")
        st.rerun()

    st.markdown("---")
    st.subheader("➕ 手動新增遺漏標註")
    col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
    with col_a:
        manual_text = st.text_input("要標註的名詞文字")
    with col_b:
        manual_start = st.number_input("起始位置 (Start Index)", min_value=0, value=0)
    with col_c:
        manual_end = st.number_input("結束位置 (End Index)", min_value=0, value=0)
    with col_d:
        manual_label = st.selectbox("標籤", options=list(TAXONOMY.keys()), format_func=lambda x: TAXONOMY[x]["name"], key="m_label")

    if st.button("手動添加實體"):
        if manual_text and manual_end > manual_start:
            st.session_state.entities.append({
                "start": int(manual_start),
                "end": int(manual_end),
                "text": manual_text,
                "label": manual_label
            })
            st.session_state.entities.sort(key=lambda x: x["start"])
            st.rerun()

with tab3:
    st.subheader("標註數據導出")
    export_data = {
        "text": st.session_state.text,
        "entities": st.session_state.entities
    }
    
    doccano_data = {
        "text": st.session_state.text,
        "label": [[e["start"], e["end"], e["label"]] for e in st.session_state.entities]
    }

    st.markdown("#### 1. 標準 Offset JSON 格式 (spaCy / 自訂訓練)")
    st.json(export_data)
    st.download_button(
        label="下載 Standard JSON",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name="civil_code_annotation.json",
        mime="application/json"
    )

    st.markdown("#### 2. Doccano JSONL 匯入格式")
    st.code(json.dumps(doccano_data, ensure_ascii=False), language="json")
    st.download_button(
        label="下載 Doccano JSONL",
        data=json.dumps(doccano_data, ensure_ascii=False) + "\n",
        file_name="doccano_import.jsonl",
        mime="application/jsonl"
    )