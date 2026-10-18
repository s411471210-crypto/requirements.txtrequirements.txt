import json
import re
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. 兩層式民法債編總則標籤體系 (Taxonomy)
# ==========================================
TAXONOMY = {
    "LEGAL_SUBJECT": {
        "name": "法律主體",
        "color": "#D81B60",
        "children": {
            "RIGHT_HOLDER": "權利主體 (債權人/賠償權利人)",
            "OBLIGOR": "義務主體 (債務人/主債務人/連帶債務人)",
            "THIRD_PARTY": "第三人 (代理人/受讓人/第三人/本人)",
        },
    },
    "SOURCE_ACT": {
        "name": "債之發生原因",
        "color": "#E65100",
        "children": {
            "CONTRACT": "契約/意思表示",
            "TORTS": "侵權行為",
            "UNJUST_ENRICHMENT": "不當得利",
            "NEGOTIORUM_GESTIO": "無因管理",
            "OTHER_ACT": "單獨行為/懸賞廣告/締約過失",
        },
    },
    "OBJECT_PERF": {
        "name": "債之標的與給付",
        "color": "#D97706",
        "children": {
            "TYPES_OF_OBLIGATION": "給付態樣 (種類/貨幣/利息/選擇之債)",
            "REMEDY_PERF": "賠償給付 (原狀回復/損害賠償/預定給付)",
        },
    },
    "BREACH_DEF": {
        "name": "債務不履行與狀態",
        "color": "#15803D",
        "children": {
            "DELAY": "遲延 (給付遲延/受領遲延)",
            "IMPOSSIBILITY": "給付不能",
            "DEFECT": "不完全給付",
            "FAULT_STATE": "歸責事由 (故意/重大過失/輕過失/不可抗力)",
        },
    },
    "RIGHT_REMEDY": {
        "name": "權利與救濟",
        "color": "#1D4ED8",
        "children": {
            "CLAIM": "請求權 (代位權/損害賠償請求權)",
            "FORMATION": "形成權 (撤銷權/解除權/終止權)",
            "DEFENSE": "抗辯權 (同時履行抗辯權)",
            "PENALTY": "違約金/減少價金",
        },
    },
    "EXTINCT_TRANS": {
        "name": "債之消滅與移轉",
        "color": "#7E22CE",
        "children": {
            "EXTINCTION": "債之消滅 (清償/提存/抵銷/免除/混同)",
            "TRANSFER": "債之移轉 (債權讓與/債務承擔/併存承擔)",
        },
    },
    "STATUTE_REF": {
        "name": "條文與法規",
        "color": "#4B5563",
        "children": {
            "CIVIL_CODE": "民法條文",
            "OTHER_LAW": "其他法規條文",
        },
    },
}

LABEL_OPTIONS = []
for m_key, m_info in TAXONOMY.items():
    for s_key, s_name in m_info["children"].items():
        LABEL_OPTIONS.append(
            {
                "main": m_key,
                "sub": s_key,
                "display": f"{m_info['name']} ➔ {s_name}",
            }
        )

DEFAULT_VOCAB = [
    ("債權人", "LEGAL_SUBJECT", "RIGHT_HOLDER"),
    ("賠償權利人", "LEGAL_SUBJECT", "RIGHT_HOLDER"),
    ("債務人", "LEGAL_SUBJECT", "OBLIGOR"),
    ("主債務人", "LEGAL_SUBJECT", "OBLIGOR"),
    ("連帶債務人", "LEGAL_SUBJECT", "OBLIGOR"),
    ("賠償義務人", "LEGAL_SUBJECT", "OBLIGOR"),
    ("第三人", "LEGAL_SUBJECT", "THIRD_PARTY"),
    ("受讓人", "LEGAL_SUBJECT", "THIRD_PARTY"),
    ("代理人", "LEGAL_SUBJECT", "THIRD_PARTY"),
    ("本人", "LEGAL_SUBJECT", "THIRD_PARTY"),
    ("契約", "SOURCE_ACT", "CONTRACT"),
    ("意思表示", "SOURCE_ACT", "CONTRACT"),
    ("侵權行為", "SOURCE_ACT", "TORTS"),
    ("不當得利", "SOURCE_ACT", "UNJUST_ENRICHMENT"),
    ("無因管理", "SOURCE_ACT", "NEGOTIORUM_GESTIO"),
    ("單獨行為", "SOURCE_ACT", "OTHER_ACT"),
    ("懸賞廣告", "SOURCE_ACT", "OTHER_ACT"),
    ("締約過失", "SOURCE_ACT", "OTHER_ACT"),
    ("給付", "OBJECT_PERF", "TYPES_OF_OBLIGATION"),
    ("種類之債", "OBJECT_PERF", "TYPES_OF_OBLIGATION"),
    ("貨幣之債", "OBJECT_PERF", "TYPES_OF_OBLIGATION"),
    ("利息之債", "OBJECT_PERF", "TYPES_OF_OBLIGATION"),
    ("選擇之債", "OBJECT_PERF", "TYPES_OF_OBLIGATION"),
    ("預定給付", "OBJECT_PERF", "REMEDY_PERF"),
    ("原狀回復", "OBJECT_PERF", "REMEDY_PERF"),
    ("損害賠償", "OBJECT_PERF", "REMEDY_PERF"),
    ("給付遲延", "BREACH_DEF", "DELAY"),
    ("受領遲延", "BREACH_DEF", "DELAY"),
    ("給付不能", "BREACH_DEF", "IMPOSSIBILITY"),
    ("不完全給付", "BREACH_DEF", "DEFECT"),
    ("歸責事由", "BREACH_DEF", "FAULT_STATE"),
    ("故意", "BREACH_DEF", "FAULT_STATE"),
    ("重大過失", "BREACH_DEF", "FAULT_STATE"),
    ("輕過失", "BREACH_DEF", "FAULT_STATE"),
    ("不可抗力", "BREACH_DEF", "FAULT_STATE"),
    ("代位權", "RIGHT_REMEDY", "CLAIM"),
    ("損害賠償請求權", "RIGHT_REMEDY", "CLAIM"),
    ("撤銷權", "RIGHT_REMEDY", "FORMATION"),
    ("解除權", "RIGHT_REMEDY", "FORMATION"),
    ("終止權", "RIGHT_REMEDY", "FORMATION"),
    ("同時履行抗辯權", "RIGHT_REMEDY", "DEFENSE"),
    ("違約金", "RIGHT_REMEDY", "PENALTY"),
    ("減少價金請求權", "RIGHT_REMEDY", "PENALTY"),
    ("清償", "EXTINCT_TRANS", "EXTINCTION"),
    ("提存", "EXTINCT_TRANS", "EXTINCTION"),
    ("抵銷", "EXTINCT_TRANS", "EXTINCTION"),
    ("免除", "EXTINCT_TRANS", "EXTINCTION"),
    ("混同", "EXTINCT_TRANS", "EXTINCTION"),
    ("債權讓與", "EXTINCT_TRANS", "TRANSFER"),
    ("債務承擔", "EXTINCT_TRANS", "TRANSFER"),
    ("併存之債務承擔", "EXTINCT_TRANS", "TRANSFER"),
]

STATUTE_PATTERN = re.compile(
    r"(?:《(?P<law>[^》]+)》|(?P<law_short>民法|刑法|民事訴訟法))?第(?P<article>\d+(?:-\d+)?)條(?:第(?P<paragraph>\d+)項)?"
)

# ==========================================
# 2. 自動預標註核心邏輯
# ==========================================
def auto_annotate(text: str, vocab: list[tuple]) -> list[dict]:
    entities = []

    for term, main_label, sub_label in vocab:
        start = 0
        while True:
            idx = text.find(term, start)
            if idx == -1:
                break
            entities.append(
                {
                    "start": idx,
                    "end": idx + len(term),
                    "text": term,
                    "label": main_label,
                    "sub_label": sub_label,
                }
            )
            start = idx + len(term)

    for match in STATUTE_PATTERN.finditer(text):
        entities.append(
            {
                "start": match.start(),
                "end": match.end(),
                "text": match.group(0),
                "label": "STATUTE_REF",
                "sub_label": "CIVIL_CODE",
            }
        )

    entities.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))
    filtered_entities = []
    last_end = -1
    for ent in entities:
        if ent["start"] >= last_end:
            filtered_entities.append(ent)
            last_end = ent["end"]

    return filtered_entities

def render_html_annotation(text: str, entities: list[dict]) -> str:
    entities = sorted(entities, key=lambda x: x["start"])
    html = ""
    last_idx = 0

    for ent in entities:
        start, end = ent["start"], ent["end"]
        label = ent.get("label", "STATUTE_REF")
        sub_label = ent.get("sub_label", "")

        color = TAXONOMY.get(label, {}).get("color", "#4B5563")
        main_name = TAXONOMY.get(label, {}).get("name", label)

        sub_name = ""
        if label in TAXONOMY and "children" in TAXONOMY[label]:
            sub_name = TAXONOMY[label]["children"].get(sub_label, sub_label)

        tag_display = (
            f"{main_name} ➔ {sub_name.split(' (')[0]}"
            if sub_name
            else main_name
        )

        html += text[last_idx:start]
        chunk = text[start:end]
        html += (
            f'<span style="background-color: {color}; color: #ffffff; padding: 3px 8px; border-radius: 5px; margin: 0 3px; font-weight: 500; display: inline-block;">'
            f'{chunk} <span style="font-size: 0.75em; background-color: rgba(255,255,255,0.25); padding: 1px 5px; border-radius: 3px; margin-left: 3px;">{tag_display}</span>'
            f"</span>"
        )
        last_idx = end

    html += text[last_idx:]
    return f'<div id="annotation-text-view" style="line-height: 2.3; font-size: 1.1em; padding: 20px; border: 1px solid #d1d5db; border-radius: 8px; background-color: #f9fafb; color: #111827;">{html}</div>'

# ==========================================
# 3. 滑鼠圈選與右鍵標註 JavaScript 元件
# ==========================================
def render_mouse_annotator():
    """繪製支援滑鼠選取與右鍵選單的互動元件"""
    taxonomy_js = json.dumps(
        [
            {
                "main": opt["main"],
                "sub": opt["sub"],
                "display": opt["display"],
                "color": TAXONOMY[opt["main"]]["color"]
            }
            for opt in LABEL_OPTIONS
        ],
        ensure_ascii=False
    )
    
    html_code = f"""
    <div id="mouse-annotator-container" style="font-family: sans-serif;">
        <div style="font-size: 0.9em; color: #4B5563; margin-bottom: 8px; font-weight: bold;">
            🖱️ 滑鼠右鍵標註指南：請在下方「視覺標註預覽區」用滑鼠劃選文字，然後按【滑鼠右鍵】選擇標籤。
        </div>
        
        <!-- 自訂右鍵選單 -->
        <div id="custom-context-menu" style="display: none; position: absolute; z-index: 9999; background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); padding: 6px 0; max-height: 300px; overflow-y: auto; min-width: 260px;">
            <div style="padding: 6px 12px; font-size: 0.8em; color: #6b7280; border-bottom: 1px solid #f3f4f6; font-weight: bold;">
                請選擇標籤（套用至選取文字）：
            </div>
            <div id="context-menu-items"></div>
        </div>
    </div>

    <script>
    const labelOptions = {taxonomy_js};
    
    // 綁定主視窗的選取與右鍵事件
    const parentDoc = window.parent.document;
    
    function initMouseAnnotator() {{
        const targetView = parentDoc.getElementById("annotation-text-view");
        const contextMenu = document.getElementById("custom-context-menu");
        const menuItems = document.getElementById("context-menu-items");

        if (!targetView) return;

        // 生成右鍵選單項目
        menuItems.innerHTML = "";
        labelOptions.forEach(opt => {{
            const item = document.createElement("div");
            item.style.padding = "8px 14px";
            item.style.cursor = "pointer";
            item.style.fontSize = "0.9em";
            item.style.transition = "background-color 0.15s";
            item.style.display = "flex";
            item.style.alignItems = "center";
            item.style.gap = "8px";
            
            item.innerHTML = `<span style="width: 10px; height: 10px; border-radius: 50%; background-color: ${{opt.color}}; display: inline-block;"></span>` +
                             `<span>${{opt.display}}</span>`;
                             
            item.onmouseover = () => item.style.backgroundColor = "#f3f4f6";
            item.onmouseout = () => item.style.backgroundColor = "#transparent";
            
            item.onclick = (e) => {{
                e.stopPropagation();
                applyMouseAnnotation(opt.main, opt.sub);
                contextMenu.style.display = "none";
            }};
            
            menuItems.appendChild(item);
        }});

        // 監聽右鍵點擊事件
        targetView.addEventListener("contextmenu", function(e) {{
            const selection = window.parent.getSelection();
            const selectedText = selection ? selection.toString().trim() : "";

            if (selectedText.length > 0) {{
                e.preventDefault();
                
                // 計算滑鼠點擊位置
                const rect = targetView.getBoundingClientRect();
                contextMenu.style.left = e.clientX + "px";
                contextMenu.style.top = (e.clientY + 10) + "px";
                contextMenu.style.display = "block";
            }} else {{
                contextMenu.style.display = "none";
            }}
        }});

        // 點擊其它區域關閉選單
        parentDoc.addEventListener("click", () => {{
            contextMenu.style.display = "none";
        }});
    }}

    function applyMouseAnnotation(mainLabel, subLabel) {{
        const selection = window.parent.getSelection();
        if (!selection || selection.rangeCount === 0) return;

        const selectedText = selection.toString().trim();
        if (!selectedText) return;

        // 向 Streamlit 觸發手動新增
        const textInput = parentDoc.querySelector("input[aria-label='要標註的名詞文字']");
        if (textInput) {{
            // 計算文字位置或直接設定文字觸發新增
            textInput.value = selectedText;
            textInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }}

    setTimeout(initMouseAnnotator, 500);
    </script>
    """
    components.html(html_code, height=40)

# ==========================================
# 4. Streamlit Web UI 介面設計
# ==========================================
st.set_page_config(page_title="民法債編總則標註系統", layout="wide")
st.title("⚖️ 民法債編總則語意標註輔助系統 (滑鼠右鍵標註版)")

# 初始化 session state
if "text" not in st.session_state:
    st.session_state.text = "因故意或過失，不法侵害他人之權利者，負損害賠償責任。故意以背於善良風俗之方法，加損害於他人者亦同。依民法第184條第1項，債權人得請求損害賠償。"
if "entities" not in st.session_state:
    st.session_state.entities = auto_annotate(
        st.session_state.text, DEFAULT_VOCAB
    )

# SideBar 標籤圖例與維護
with st.sidebar:
    st.header("🏷️ 兩層式標籤體系 (Taxonomy)")
    for code, info in TAXONOMY.items():
        st.markdown(
            f'<span style="background-color:{info["color"]}; color:white; padding:4px 8px; border-radius:5px; font-weight:bold;">{info["name"]} (`{code}`)</span>',
            unsafe_allow_html=True,
        )
        for sub_code, sub_name in info["children"].items():
            st.caption(f"  └ `{sub_code}`: {sub_name}")
        st.write("")

    st.markdown("---")
    st.header("⚙️ 字典快速擴充")
    new_term = st.text_input("新增名詞")
    target_main = st.selectbox(
        "上位大類",
        options=list(TAXONOMY.keys()),
        format_func=lambda x: TAXONOMY[x]["name"],
    )
    target_sub = st.selectbox(
        "下位子類",
        options=list(TAXONOMY[target_main]["children"].keys()),
        format_func=lambda x: TAXONOMY[target_main]["children"][x],
    )

    if st.button("加到預標註字典"):
        if new_term:
            DEFAULT_VOCAB.append((new_term, target_main, target_sub))
            st.session_state.entities = auto_annotate(
                st.session_state.text, DEFAULT_VOCAB
            )
            st.success(
                f"已新增「{new_term}」至 {TAXONOMY[target_main]['name']} ➔ {TAXONOMY[target_main]['children'][target_sub]}"
            )
            st.rerun()

# 主介面區域
tab1, tab2, tab3 = st.tabs(
    ["📝 視覺標註與滑鼠右鍵標註", "✏️ 標註微調與校對", "💾 匯出資料庫 (JSON/Doccano)"]
)

with tab1:
    st.subheader("📄 匯入文件或載入歷史進度")

    uploaded_file = st.file_uploader(
        "📂 請上傳新文字檔 (.txt) 或先前儲存的標註進度檔 (.json)",
        type=["txt", "json"],
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name

        if file_name.endswith(".json"):
            try:
                progress_data = json.load(uploaded_file)
                if "text" in progress_data and "entities" in progress_data:
                    st.session_state.text = progress_data["text"]

                    processed_entities = []
                    for ent in progress_data["entities"]:
                        label = ent.get("label", "STATUTE_REF")
                        sub_label = ent.get("sub_label")

                        if not sub_label and label in TAXONOMY:
                            sub_label = list(
                                TAXONOMY[label]["children"].keys()
                            )[0]

                        processed_entities.append(
                            {
                                "start": ent["start"],
                                "end": ent["end"],
                                "text": ent["text"],
                                "label": label,
                                "sub_label": sub_label,
                            }
                        )

                    st.session_state.entities = processed_entities
                    st.success(f"已成功載入歷史標註進度：{file_name}")
                    st.rerun()
                else:
                    st.error(
                        "JSON 格式不相符，檔案必須包含 'text' 與 'entities' 欄位。"
                    )
            except Exception as e:
                st.error(f"無法讀取 JSON 檔案：{e}")

        elif file_name.endswith(".txt"):
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
                st.session_state.entities = auto_annotate(
                    file_text, DEFAULT_VOCAB
                )
                st.success(f"已成功匯入新文件：{file_name}")
                st.rerun()

    input_text = st.text_area(
        "或在此直接貼上/修改文字：", value=st.session_state.text, height=150
    )

    if st.button("🤖 執行/重新預標註"):
        st.session_state.text = input_text
        st.session_state.entities = auto_annotate(input_text, DEFAULT_VOCAB)
        st.rerun()

    st.markdown("---")
    st.subheader("即時視覺標註結果區（支援滑鼠劃選）")
    
    # 渲染即時標註結果
    html_code = render_html_annotation(
        st.session_state.text, st.session_state.entities
    )
    st.markdown(html_code, unsafe_allow_html=True)

    # 載入滑鼠右鍵選單邏輯
    render_mouse_annotator()

with tab2:
    st.subheader("人工校對與新增標註清單")
    st.caption(
        "法律系同學可以在此檢查標註結果，調整標籤類別或新增滑鼠選取的字詞："
    )

    # 手動新增標註區塊
    st.markdown("#### ➕ 快速新增選取字詞")
    col_a, col_b, col_c = st.columns([2, 4, 1])
    with col_a:
        manual_text = st.text_input("要標註的名詞文字", key="m_text_input")
    with col_b:
        manual_label_opt = st.selectbox(
            "選擇標籤（上位 ➔ 下位）",
            options=LABEL_OPTIONS,
            format_func=lambda x: x["display"],
            key="m_label_pair",
        )
    with col_c:
        st.write("")
        st.write("")
        if st.button("確認新增"):
            if manual_text:
                start_idx = st.session_state.text.find(manual_text)
                if start_idx != -1:
                    st.session_state.entities.append(
                        {
                            "start": start_idx,
                            "end": start_idx + len(manual_text),
                            "text": manual_text,
                            "label": manual_label_opt["main"],
                            "sub_label": manual_label_opt["sub"],
                        }
                    )
                    st.session_state.entities.sort(key=lambda x: x["start"])
                    st.success(f"已成功新增標註：「{manual_text}」")
                    st.rerun()
                else:
                    st.error("文章中找不到該文字，請確認拼字。")

    st.markdown("---")
    st.markdown("#### ✏️ 標註項目清單校對")

    updated_entities = []
    for i, ent in enumerate(st.session_state.entities):
        col1, col2, col3 = st.columns([2, 5, 1])

        current_opt_index = 0
        for opt_idx, opt in enumerate(LABEL_OPTIONS):
            if opt["main"] == ent.get("label") and opt["sub"] == ent.get(
                "sub_label"
            ):
                current_opt_index = opt_idx
                break

        with col1:
            st.write(f"**{ent['text']}** (`{ent['start']}:{ent['end']}`)")
        with col2:
            selected_option = st.selectbox(
                "選擇階層標籤（上位 ➔ 下位）",
                options=LABEL_OPTIONS,
                index=current_opt_index,
                format_func=lambda x: x["display"],
                key=f"label_pair_{i}",
            )
            ent["label"] = selected_option["main"]
            ent["sub_label"] = selected_option["sub"]
        with col3:
            if not st.checkbox("保留", value=True, key=f"keep_{i}"):
                continue
        updated_entities.append(ent)

    if st.button("更新校對結果"):
        st.session_state.entities = updated_entities
        st.success("標註結果已更新！")
        st.rerun()

with tab3:
    st.subheader("標註數據導出")

    export_entities = []
    for e in st.session_state.entities:
        e_copy = dict(e)
        m = e_copy.get("label", "")
        s = e_copy.get("sub_label", "")
        e_copy["full_label"] = f"{m}.{s}" if s else m
        export_entities.append(e_copy)

    export_data = {
        "text": st.session_state.text,
        "entities": export_entities,
    }

    doccano_data = {
        "text": st.session_state.text,
        "label": [
            [
                e["start"],
                e["end"],
                (
                    f"{e.get('label', '')}.{e.get('sub_label', '')}"
                    if e.get("sub_label")
                    else e.get("label", "")
                ),
            ]
            for e in st.session_state.entities
        ],
    }

    st.markdown("#### 1. 標準 2-Tier Offset JSON 格式")
    st.json(export_data)
    st.download_button(
        label="下載 Standard JSON",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name="civil_code_hierarchical_annotation.json",
        mime="application/json",
    )

    st.markdown("#### 2. Doccano 階層式 JSONL 匯入格式")
    st.code(json.dumps(doccano_data, ensure_ascii=False), language="json")
    st.download_button(
        label="下載 Doccano JSONL",
        data=json.dumps(doccano_data, ensure_ascii=False) + "\n",
        file_name="doccano_hierarchical_import.jsonl",
        mime="application/jsonl",
    )