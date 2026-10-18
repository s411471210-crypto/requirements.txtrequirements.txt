import streamlit as st
import docx
import io
import json
import re
import streamlit as st
import streamlit.components.v1 as components

# 載入 Word 檔案處理套件
try:
    from docx import Document
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls
    from docx.shared import Pt, RGBColor
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# ==========================================
# 1. 完整民法債編專有名詞字典庫 (Legal Dictionary)
# ==========================================
LEGAL_DICTIONARY = {
    "債務承擔": {
        "basis": "民法第 300 條、第 301 條",
        "category": "債之消滅與移轉 ➔ 債之移轉",
        "definition": "指不變更債務同一性，由第三人替代原債務人負擔其債務之契約。原債務人脫離債務關係（免責承擔）。",
        "elements": "1. 第三人與債權人訂立契約（§300，即生效）。\n2. 第三人與債務人訂立契約（§301，非經債權人承認不生效力）。",
        "example": "甲欠乙 100 萬，丙與乙簽約約定由丙替甲還款，甲之債務消滅。",
    },
    "併存之債務承擔": {
        "basis": "法理與民法第 305 條第 2 項參照",
        "category": "債之消滅與移轉 ➔ 債之移轉",
        "definition": "第三人加入債務關係，與原債務人連帶負擔債務，原債務人並未脫離債務關係。",
        "elements": "第三人與債權人或債務人約定，由第三人加入承擔連帶責任。",
        "example": "父向銀行貸款，子簽署併存債務承擔，父子二人對銀行負連帶清償責任。",
    },
    "概括承受": {
        "basis": "民法第 305 條、第 306 條",
        "category": "債之消滅與移轉 ➔ 債之移轉",
        "definition": "就他人之營業或財產，將其資產與負債一併承接。",
        "elements": "需對債權人為承受之通知或公告。原債務人於 2 年內負連帶責任。",
        "example": "A 公司併購 B 公司之營業並概括承受其所有資產與負債。",
    },
    "清償": {
        "basis": "民法第 309 條～第 325 條",
        "category": "債之消滅與移轉 ➔ 債之消滅",
        "definition": "依債務本旨，向債權人或其他有受領權人為給付，經其受領者，債之關係消滅。",
        "elements": "1. 須依債務本旨為之。\n2. 須向有受領權人為之。\n3. 經受領人受領。",
        "example": "買款屆期時，買受人將約定之金錢全額轉帳至出賣人帳戶。",
    },
    "債權之準占有人": {
        "basis": "民法第 310 條第 2 款",
        "category": "法律主體 ➔ 第三人",
        "definition": "雖無真實債權，但依社會通念客觀上顯示出權利外觀之人。",
        "elements": "債務人善意且無過失向其為清償者，仍生清償效力，原債權消滅。",
        "example": "持蓋有真正印章之存摺與印章向銀行提款者；或表見繼承人。",
    },
    "代位清償": {
        "basis": "民法第 312 條",
        "category": "債之消滅與移轉 ➔ 債之消滅",
        "definition": "就債之履行有利害關係之第三人（如保證人、物保人）代為清償後，於清償限度內承受債權人之權利。",
        "elements": "1. 須為有利害關係之第三人。\n2. 須已為清償。\n3. 不得有害於債權人利益。",
        "example": "人保（保證人）替主債務人還款給銀行後，得代位行使銀行對主債務人的求償權。",
    },
    "代物清償": {
        "basis": "民法第 319 條",
        "category": "債之消滅與移轉 ➔ 債之消滅",
        "definition": "債權人受領他種給付以代原定給付之要物契約，給付完成時債之關係消滅。",
        "elements": "1. 須有替換給付之合意。\n2. 須實行他種給付。\n3. 須債權人受領。",
        "example": "甲欠乙 50 萬金錢債務，經乙同意後，甲將名下一台中古車過戶給乙抵債。",
    },
    "新債清償": {
        "basis": "民法第 320 條",
        "category": "債之消滅與移轉 ➔ 債之消滅",
        "definition": "因清償舊債務而對債權人負擔新債務（又稱間接清償）。若新債務不履行時，舊債務仍不消滅。",
        "elements": "負擔新債務以清償舊債務，且無消滅舊債務之特別意思表示。",
        "example": "開立支票以支付房屋租金，若支票跳票，原本的房屋租金債務依然存在。",
    },
    "提存": {
        "basis": "民法第 326 條～第 333 條",
        "category": "債之消滅與移轉 ➔ 債之消滅",
        "definition": "債權人受領遲延，或不能確知孰為債權人時，清償人將給付物提存於法院提存所以消滅債務。",
        "elements": "1. 債權人受領遲延或客觀上難為給付。\n2. 向清償地法院提存所為之。",
        "example": "房東無故拒收房租，租客將房租提存於法院提存所，避免構成給付遲延。",
    },
    "抵銷": {
        "basis": "民法第 334 條～第 342 條",
        "category": "債之消滅與移轉 ➔ 債之消滅",
        "definition": "二人互負債務，且給付種類相同、均屆清償期，各自以其債務與他方之債務等額消滅之單獨行為。",
        "elements": "1. 雙方互負債務（抵銷適狀）。\n2. 給付種類相同。\n3. 均屆清償期。\n4. 無禁止抵銷之情形（如故意侵權行為之債§339）。",
        "example": "甲欠乙 10 萬，乙亦欠甲 10 萬，甲向乙表示抵銷後，雙方債權債務溯及消滅。",
    },
    "免除": {
        "basis": "民法第 343 條",
        "category": "債之消滅與移轉 ➔ 債之消滅",
        "definition": "債權人向債務人表示免除其債務之意思者，債之關係消滅（單獨行為）。",
        "elements": "債權人向債務人為免除之單方意思表示到達即可。",
        "example": "債權人出具債務免除同意書給債務人，聲明無須償還剩餘借款。",
    },
    "混同": {
        "basis": "民法第 344 條",
        "category": "債之消滅與移轉 ➔ 債之消滅",
        "definition": "債權與其債務同歸一人時，債之關係消滅。",
        "elements": "債權與債務集中於同一權利主體（法律另有規定或為他人權利標的者除外）。",
        "example": "子向父借款，父死亡後子為唯一繼承人，子對父之債務因混同而消滅。",
    },
    "侵權行為": {
        "basis": "民法第 184 條",
        "category": "債之發生原因 ➔ 侵權行為",
        "definition": "因故意或過失，不法侵害他人權利或利益，依法應負損害賠償責任之行為。",
        "elements": "1. 加害行為 2. 行為不法 3. 侵害權利 4. 故意或過失 5. 發生損害 6. 相當因果關係。",
        "example": "駕駛開車超速撞傷行人，應負侵權行為損害賠償責任。",
    },
    "不當得利": {
        "basis": "民法第 179 條",
        "category": "債之發生原因 ➔ 不當得利",
        "definition": "無法律上之原因而受利益，致他人受損害者，應返還其利益。",
        "elements": "1. 無法律上原因 2. 受有利益 3. 致他人受損害 4. 損益間具因果關係。",
        "example": "買陸匯款時誤將款項轉帳至陌生人帳戶，得依不當得利請求返還。",
    },
    "給付遲延": {
        "basis": "民法第 229 條",
        "category": "債務不履行與狀態 ➔ 遲延",
        "definition": "債務人給付可能，但屆期未為給付，且具有可歸責事由之狀態。",
        "elements": "1. 債務已屆清償期 2. 給付可能 3. 具有歸責事由 4. 尚未為給付。",
        "example": "賣方承諾 5 月 1 日交貨，無正當理由延至 6 月才交付。",
    },
    "受領遲延": {
        "basis": "民法第 234 條",
        "category": "債務不履行與狀態 ➔ 遲延",
        "definition": "債務人已依債務本旨提出給付，而債權人拒絕受領或不能受領之狀態。",
        "elements": "1. 債務人適法提出給付 2. 債權人拒絕或不能受領。",
        "example": "外送員已將餐點送達指定地點，買家拒不開門取餐。",
    },
    "損害賠償請求權": {
        "basis": "民法第 184 條、第 213 條",
        "category": "權利與救濟 ➔ 請求權",
        "definition": "因他人之侵權行為或債務不履行受有損害時，請求填補損害之權利。",
        "elements": "損害事故發生、具歸責事由與因果關係、賠償權利人依法行使。",
        "example": "車禍受害者請求加害者賠償醫療費與車輛修繕費。",
    },
}

# ==========================================
# 2. 兩層式民法債編標籤體系 (Taxonomy)
# ==========================================
TAXONOMY = {
    "LEGAL_SUBJECT": {
        "name": "法律主體",
        "color": "#D81B60",
        "children": {
            "RIGHT_HOLDER": "權利主體 (債權人/賠償權利人)",
            "OBLIGOR": "義務主體 (債務人/主債務人/連帶債務人)",
            "THIRD_PARTY": "第三人 (代理人/受讓人/第三人/債權之準占有人)",
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
            "TYPES_OF_OBLIGATION": "給付態樣 (種類/貨幣/利息/選擇之債/特定物)",
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
            "DEFENSE": "抗辯權 (同時履行抗辯權/時效抗辯)",
            "PENALTY": "違約金/減少價金",
        },
    },
    "EXTINCT_TRANS": {
        "name": "債之消滅與移轉",
        "color": "#7E22CE",
        "children": {
            "EXTINCTION": "債之消滅 (清償/提存/抵銷/免除/混同/代物清償)",
            "TRANSFER": "債之移轉 (債權讓與/債務承擔/併存承擔/概括承受)",
        },
    },
    "ELEMENT_FACT": {
        "name": "要件事實與條件",
        "color": "#0284C7",
        "children": {
            "DAMAGE": "損害要件 (財產上/精神慰撫金/所受損害)",
            "CAUSATION": "因果關係 (相當因果關係/責任成立因果)",
            "ILLEGALITY": "不法性與阻卻 (不法侵害/正當防衛/緊急避難)",
            "CONDITION_LIMIT": "附條件與期限 (停止條件/解除條件/期限)",
        },
    },
    "LEGAL_EFFECT": {
        "name": "法律效果與效力",
        "color": "#059669",
        "children": {
            "VALIDITY": "行為效力 (無效/得撤銷/效力未定/不成立)",
            "LIABILITY_TYPE": "責任型態 (連帶責任/補充責任/不真正連帶)",
            "DISCHARGE": "免責與釋放 (免責事由/特約免責)",
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
    ("第三人", "LEGAL_SUBJECT", "THIRD_PARTY"),
    ("債權之準占有人", "LEGAL_SUBJECT", "THIRD_PARTY"),
    ("契約", "SOURCE_ACT", "CONTRACT"),
    ("意思表示", "SOURCE_ACT", "CONTRACT"),
    ("侵權行為", "SOURCE_ACT", "TORTS"),
    ("不當得利", "SOURCE_ACT", "UNJUST_ENRICHMENT"),
    ("無因管理", "SOURCE_ACT", "NEGOTIORUM_GESTIO"),
    ("給付", "OBJECT_PERF", "TYPES_OF_OBLIGATION"),
    ("損害賠償", "OBJECT_PERF", "REMEDY_PERF"),
    ("給付遲延", "BREACH_DEF", "DELAY"),
    ("受領遲延", "BREACH_DEF", "DELAY"),
    ("給付不能", "BREACH_DEF", "IMPOSSIBILITY"),
    ("故意", "BREACH_DEF", "FAULT_STATE"),
    ("過失", "BREACH_DEF", "FAULT_STATE"),
    ("損害賠償請求權", "RIGHT_REMEDY", "CLAIM"),
    ("撤銷權", "RIGHT_REMEDY", "FORMATION"),
    ("清償", "EXTINCT_TRANS", "EXTINCTION"),
    ("提存", "EXTINCT_TRANS", "EXTINCTION"),
    ("抵銷", "EXTINCT_TRANS", "EXTINCTION"),
    ("免除", "EXTINCT_TRANS", "EXTINCTION"),
    ("混同", "EXTINCT_TRANS", "EXTINCTION"),
    ("代物清償", "EXTINCT_TRANS", "EXTINCTION"),
    ("新債清償", "EXTINCT_TRANS", "EXTINCTION"),
    ("債務承擔", "EXTINCT_TRANS", "TRANSFER"),
    ("併存之債務承擔", "EXTINCT_TRANS", "TRANSFER"),
    ("概括承受", "EXTINCT_TRANS", "TRANSFER"),
    ("代位清償", "EXTINCT_TRANS", "EXTINCTION"),
    ("損害", "ELEMENT_FACT", "DAMAGE"),
    ("精神慰撫金", "ELEMENT_FACT", "DAMAGE"),
    ("相當因果關係", "ELEMENT_FACT", "CAUSATION"),
    ("無效", "LEGAL_EFFECT", "VALIDITY"),
    ("連帶責任", "LEGAL_EFFECT", "LIABILITY_TYPE"),
    ("免責", "LEGAL_EFFECT", "DISCHARGE"),
]

STATUTE_PATTERN = re.compile(
    r"(?:《(?P<law>[^》]+)》|(?P<law_short>民法|刑法|民事訴訟法))?第(?P<article>\d+(?:-\d+)?)條(?:第(?P<paragraph>\d+)項)?"
)


# ==========================================
# 3. 核心處理與 Word 智慧生成
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
                    "is_negated": False,
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
                "is_negated": False,
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
        is_negated = ent.get("is_negated", False)

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
        if is_negated:
            tag_display += " (❌消極)"

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


def generate_docx_report(
    text: str, entities: list[dict], taxonomy: dict
) -> io.BytesIO:
    """生成包含高亮文章、統計表格與專有名詞小辭典的精美 Word 報告"""
    doc = Document()

    doc.add_heading("⚖️ 民法債編總則語意標註分析報告", level=1)

    # 一、 高亮文章
    doc.add_heading("一、 標註內文視覺化結果", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.6

    sorted_ents = sorted(entities, key=lambda x: x["start"])
    last_idx = 0

    for ent in sorted_ents:
        start, end = ent["start"], ent["end"]
        label = ent.get("label", "STATUTE_REF")
        sub_label = ent.get("sub_label", "")
        is_negated = ent.get("is_negated", False)

        p.add_run(text[last_idx:start])

        chunk = text[start:end]
        main_name = taxonomy.get(label, {}).get("name", label)
        color_hex = (
            taxonomy.get(label, {}).get("color", "#4B5563").replace("#", "")
        )

        sub_name = ""
        if label in taxonomy and "children" in taxonomy[label]:
            sub_name = taxonomy[label]["children"].get(sub_label, sub_label)

        tag_text = (
            f" [{main_name}➔{sub_name.split(' (')[0] if sub_name else ''}]"
        )
        if is_negated:
            tag_text += " (❌消極/否定)"

        run = p.add_run(f" {chunk}{tag_text} ")
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)

        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        run._r.get_or_add_rPr().append(shd)

        last_idx = end

    p.add_run(text[last_idx:])

    # 二、 標註清單表格
    doc.add_heading("二、 標註項目詳細統計表", level=2)
    table = doc.add_table(rows=1, cols=5)
    table.style = "Table Grid"

    hdr_cells = table.rows[0].cells
    hdr_titles = [
        "序號",
        "標註詞彙",
        "文字位置 (Start:End)",
        "階層類別 (上位 ➔ 下位)",
        "屬性態樣",
    ]
    for i, title in enumerate(hdr_titles):
        hdr_cells[i].text = title
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True

    for idx, ent in enumerate(sorted_ents, 1):
        row_cells = table.add_row().cells
        row_cells[0].text = str(idx)
        row_cells[1].text = ent["text"]
        row_cells[2].text = f"{ent['start']}:{ent['end']}"

        main_name = taxonomy.get(ent["label"], {}).get("name", ent["label"])
        sub_name = (
            taxonomy.get(ent["label"], {})
            .get("children", {})
            .get(ent.get("sub_label"), ent.get("sub_label", ""))
        )
        row_cells[3].text = f"{main_name} ➔ {sub_name}"
        row_cells[4].text = (
            "❌ 消極/否定" if ent.get("is_negated") else "✅ 肯定/一般"
        )

    # 三、 自動匹配並生成專有名詞小辭典
    doc.add_heading("三、 本文涉及法律名詞速查字典", level=2)

    unique_terms = set(e["text"] for e in sorted_ents)
    matched_dict_terms = [t for t in unique_terms if t in LEGAL_DICTIONARY]

    if matched_dict_terms:
        for term in matched_dict_terms:
            info = LEGAL_DICTIONARY[term]
            p_term = doc.add_paragraph()
            r_term = p_term.add_run(f"📌 {term}")
            r_term.font.bold = True
            r_term.font.size = Pt(12)

            doc.add_paragraph(
                f"• 條文依據：{info['basis']}\n"
                f"• 概念定義：{info['definition']}\n"
                f"• 成立要件：{info['elements']}\n"
                f"• 實務範例：{info['example']}"
            )
    else:
        doc.add_paragraph("（本文標註詞彙尚未涵蓋內建名詞字典庫項目）")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def render_mouse_annotator():
    taxonomy_js = json.dumps(
        [
            {
                "main": opt["main"],
                "sub": opt["sub"],
                "display": opt["display"],
                "color": TAXONOMY[opt["main"]]["color"],
            }
            for opt in LABEL_OPTIONS
        ],
        ensure_ascii=False,
    )

    html_code = f"""
    <div id="mouse-annotator-container" style="font-family: sans-serif;">
        <div style="font-size: 0.9em; color: #4B5563; margin-bottom: 8px; font-weight: bold;">
            🖱️ 滑鼠右鍵標註指南：請在下方「視覺標註預覽區」用滑鼠劃選文字，然後按【滑鼠右鍵】選擇標籤。
        </div>
        <div id="custom-context-menu" style="display: none; position: absolute; z-index: 9999; background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); padding: 6px 0; max-height: 300px; overflow-y: auto; min-width: 260px;">
            <div style="padding: 6px 12px; font-size: 0.8em; color: #6b7280; border-bottom: 1px solid #f3f4f6; font-weight: bold;">
                請選擇標籤（套用至選取文字）：
            </div>
            <div id="context-menu-items"></div>
        </div>
    </div>

    <script>
    const labelOptions = {taxonomy_js};
    const parentDoc = window.parent.document;
    
    function initMouseAnnotator() {{
        const targetView = parentDoc.getElementById("annotation-text-view");
        const contextMenu = document.getElementById("custom-context-menu");
        const menuItems = document.getElementById("context-menu-items");

        if (!targetView) return;

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
            item.onmouseout = () => item.style.backgroundColor = "transparent";
            
            item.onclick = (e) => {{
                e.stopPropagation();
                applyMouseAnnotation(opt.main, opt.sub);
                contextMenu.style.display = "none";
            }};
            
            menuItems.appendChild(item);
        }});

        targetView.addEventListener("contextmenu", function(e) {{
            const selection = window.parent.getSelection();
            const selectedText = selection ? selection.toString().trim() : "";

            if (selectedText.length > 0) {{
                e.preventDefault();
                contextMenu.style.left = e.clientX + "px";
                contextMenu.style.top = (e.clientY + 10) + "px";
                contextMenu.style.display = "block";
            }} else {{
                contextMenu.style.display = "none";
            }}
        }});

        parentDoc.addEventListener("click", () => {{
            contextMenu.style.display = "none";
        }});
    }}

    function applyMouseAnnotation(mainLabel, subLabel) {{
        const selection = window.parent.getSelection();
        if (!selection || selection.rangeCount === 0) return;
        const selectedText = selection.toString().trim();
        if (!selectedText) return;

        const textInput = parentDoc.querySelector("input[aria-label='要標註的名詞文字']");
        if (textInput) {{
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
st.title("⚖️ 民法債編總則語意標註輔助系統 (含法學字典版)")

if "text" not in st.session_state:
    st.session_state.text = "因故意或過失，不法侵害他人之權利者，負損害賠償責任。故意以背於善良風俗之方法，加損害於他人者亦同。依民法第184條第1項，債權人得請求損害賠償。"
if "entities" not in st.session_state:
    st.session_state.entities = auto_annotate(
        st.session_state.text, DEFAULT_VOCAB
    )

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
            st.success(f"已新增「{new_term}」至預標註字典")
            st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📝 視覺標註與右鍵標註",
        "✏️ 標註微調與校對",
        "💾 匯出資料報告 (Word/JSON)",
        "📚 民法專有名詞速查字典",
    ]
)

with tab1:
    st.subheader("📄 匯入文件或載入歷史進度")
    uploaded_file = st.file_uploader(
        "📂 上傳文字檔 (.txt) 或先前儲存的標註進度 (.json)",
        type=["txt", "json"],
    )

    if uploaded_file is not None:
        file_name = uploaded_file.name
        if file_name.endswith(".json"):
            try:
                progress_data = json.load(uploaded_file)
                if "text" in progress_data and "entities" in progress_data:
                    st.session_state.text = progress_data["text"]
                    st.session_state.entities = progress_data["entities"]
                    st.success(f"已成功載入歷史標註進度：{file_name}")
                    st.rerun()
            except Exception as e:
                st.error(f"無法讀取 JSON：{e}")
        elif file_name.endswith(".txt"):
            bytes_data = uploaded_file.getvalue()
            try:
                file_text = bytes_data.decode("utf-8")
            except UnicodeDecodeError:
                file_text = bytes_data.decode("big5", errors="ignore")

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
    html_code = render_html_annotation(
        st.session_state.text, st.session_state.entities
    )
    st.markdown(html_code, unsafe_allow_html=True)
    render_mouse_annotator()

with tab2:
    st.subheader("人工校對與新增標註清單")

    st.markdown("#### ➕ 快速新增標註（支援一鍵批次標註）")
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
        is_neg_check = st.checkbox("❌ 消極/否定屬性", key="m_is_neg")

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("確認單一新增"):
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
                            "is_negated": is_neg_check,
                        }
                    )
                    st.session_state.entities.sort(key=lambda x: x["start"])
                    st.success(f"已新增標註：「{manual_text}」")
                    st.rerun()
    with col_btn2:
        if st.button("⚡ 批次標註全文所有相同詞彙"):
            if manual_text:
                count = 0
                start = 0
                while True:
                    idx = st.session_state.text.find(manual_text, start)
                    if idx == -1:
                        break
                    if not any(
                        e["start"] == idx and e["end"] == idx + len(manual_text)
                        for e in st.session_state.entities
                    ):
                        st.session_state.entities.append(
                            {
                                "start": idx,
                                "end": idx + len(manual_text),
                                "text": manual_text,
                                "label": manual_label_opt["main"],
                                "sub_label": manual_label_opt["sub"],
                                "is_negated": is_neg_check,
                            }
                        )
                        count += 1
                    start = idx + len(manual_text)

                st.session_state.entities.sort(key=lambda x: x["start"])
                st.success(f"已為全文 {count} 處「{manual_text}」完成標註！")
                st.rerun()

    st.markdown("---")
    st.markdown("#### ✏️ 標註項目清單微調")

    updated_entities = []
    for i, ent in enumerate(st.session_state.entities):
        col1, col2, col3, col4 = st.columns([2, 4, 2, 1])

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
                "階層標籤",
                options=LABEL_OPTIONS,
                index=current_opt_index,
                format_func=lambda x: x["display"],
                key=f"label_pair_{i}",
            )
            ent["label"] = selected_option["main"]
            ent["sub_label"] = selected_option["sub"]
        with col3:
            ent["is_negated"] = st.checkbox(
                "❌ 消極態樣",
                value=ent.get("is_negated", False),
                key=f"neg_{i}",
            )
        with col4:
            if not st.checkbox("保留", value=True, key=f"keep_{i}"):
                continue
        updated_entities.append(ent)

    if st.button("更新校對結果"):
        st.session_state.entities = updated_entities
        st.success("標註結果已更新！")
        st.rerun()

with tab3:
    st.subheader("📄 標註數據與 Word 報告導出")

    st.markdown("### 1. 🎉 匯出排版好的 Word (.docx) 分析報告")
    st.caption("自動包含：彩色高亮內文、標註統計表格與文章涉及之專有名詞詳解小辭典！")

    if DOCX_AVAILABLE:
        docx_file = generate_docx_report(
            st.session_state.text, st.session_state.entities, TAXONOMY
        )
        st.download_button(
            label="📥 下載 Word 分析報告 (.docx)",
            data=docx_file,
            file_name="民法債編總則語意標註報告.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    else:
        st.warning(
            "請在 requirements.txt 中新增 python-docx 即可啟用 Word 下載功能。"
        )

    st.markdown("---")
    st.markdown("### 2. 💾 研讀與繼續標註備份檔 (JSON/JSONL)")

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

    col_j1, col_j2 = st.columns([1, 1])
    with col_j1:
        st.markdown("#### Standard JSON (可重新載入)")
        st.download_button(
            label="下載 Standard JSON",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name="civil_code_hierarchical_annotation.json",
            mime="application/json",
        )
    with col_j2:
        st.markdown("#### Doccano JSONL (模型訓練用)")
        st.download_button(
            label="下載 Doccano JSONL",
            data=json.dumps(doccano_data, ensure_ascii=False) + "\n",
            file_name="doccano_hierarchical_import.jsonl",
            mime="application/jsonl",
        )

# 新增 Tab 4：民法專有名詞速查字典
with tab4:
    st.subheader("📚 民法債編總則專有名詞速查字典")
    st.caption(
        "收錄債之發生、債務不履行、債之移轉與消滅等核心法律名詞之定義、成立要件與實務範例："
    )

    col_search, col_filter = st.columns([3, 2])
    with col_search:
        search_query = st.text_input(
            "🔍 搜尋名詞關鍵字（例如：清償、抵銷、承擔）", ""
        )
    with col_filter:
        categories = list(
            set(info["category"] for info in LEGAL_DICTIONARY.values())
        )
        selected_cat = st.selectbox("📂 依類別篩選", ["全部類別"] + categories)

    st.markdown("---")

    for term, info in LEGAL_DICTIONARY.items():
        # 搜尋條件過濾
        if search_query and search_query not in term and search_query not in info["definition"]:
            continue
        if selected_cat != "全部類別" and info["category"] != selected_cat:
            continue

        with st.expander(f"📌 **{term}**（{info['basis']}） — {info['category']}"):
            st.markdown(f"**【概念定義】**：{info['definition']}")
            st.markdown(f"**【成立要件 / 特徵】**：\n{info['elements']}")
            st.markdown(f"**【實務範例】**：{info['example']}")



