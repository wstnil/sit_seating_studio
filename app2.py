"""
🎓 SEATING STUDIO — Premium Examination Seating & Report Suite
"""

import os
import sys
import io
import re
import html
import importlib
import zipfile
import tempfile
import datetime as dt
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sit3
import qr
importlib.reload(qr)
importlib.reload(sit3)

st.set_page_config(
    page_title="Sit Seating Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════════
#  THEMES
# ════════════════════════════════════════════════════════════════════
THEMES = {
    "Aurora": {
        "a1": "#6366F1", "a2": "#A855F7", "a3": "#22D3EE",
        "palette": ["#818CF8", "#34D399", "#F472B6", "#FBBF24", "#60A5FA", "#A78BFA", "#F87171", "#2DD4BF", "#FDBA74", "#C084FC"],
    },
    "Sunset": {
        "a1": "#F97316", "a2": "#EF4444", "a3": "#FBBF24",
        "palette": ["#FB923C", "#F87171", "#FBBF24", "#F472B6", "#FDBA74", "#E879F9", "#FDE047", "#FB7185", "#F59E0B", "#FCA5A5"],
    },
    "Ocean": {
        "a1": "#0EA5E9", "a2": "#6366F1", "a3": "#14B8A6",
        "palette": ["#38BDF8", "#2DD4BF", "#818CF8", "#60A5FA", "#22D3EE", "#A5B4FC", "#34D399", "#93C5FD", "#5EEAD4", "#67E8F9"],
    },
}

def build_css(t, light_mode=False):
    mode = {
        "page": "#F3F6FA" if light_mode else "#0A0E1A",
        "text": "#172033" if light_mode else "#E5E7EB",
        "muted": "#536174" if light_mode else "#A3ADBC",
        "surface": "rgba(255,255,255,.88)" if light_mode else "rgba(255,255,255,.055)",
        "surface_alt": "rgba(255,255,255,.72)" if light_mode else "rgba(255,255,255,.025)",
        "border": "rgba(31,45,66,.16)" if light_mode else "rgba(255,255,255,.11)",
        "field": "#FFFFFF" if light_mode else "#111827",
        "field_border": "#9AA8BA" if light_mode else "#536174",
        "placeholder": "#657286" if light_mode else "#A3ADBC",
        "menu": "#FFFFFF" if light_mode else "#172033",
        "menu_hover": "#EAF0F7" if light_mode else "#263449",
        "hero_title": "#172033" if light_mode else "#FFFFFF",
    }
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

:root {{
    --a1:{t['a1']}; --a2:{t['a2']}; --a3:{t['a3']};
    --page:{mode['page']}; --text:{mode['text']}; --muted:{mode['muted']};
    --surface:{mode['surface']}; --surface-alt:{mode['surface_alt']}; --border:{mode['border']};
    --field:{mode['field']}; --field-border:{mode['field_border']}; --placeholder:{mode['placeholder']};
    --menu:{mode['menu']}; --menu-hover:{mode['menu_hover']}; --hero-title:{mode['hero_title']};
}}

.stApp {{
    background:
        radial-gradient(1200px 700px at 85% -10%, {t['a1']}18, transparent 60%),
        radial-gradient(1000px 600px at -10% 110%, {t['a2']}14, transparent 60%),
        radial-gradient(600px 400px at 50% 50%, {t['a3']}0A, transparent 70%),
        var(--page);
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
    color-scheme: {'light' if light_mode else 'dark'};
}}
#MainMenu, footer, header[data-testid="stHeader"], [data-testid="collapsedControl"] {{ display: none !important; }}

h1, h2, h3, .stTabs button span {{ font-family: 'Sora', 'Inter', sans-serif !important; }}
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] p,
[data-testid="stFileUploaderDropzone"] small {{ color: var(--muted) !important; }}

[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea, [data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {{
    background: var(--field) !important; border: 1px solid var(--field-border) !important;
    border-radius: 10px !important; color: var(--text) !important; caret-color: var(--a1);
}}
[data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {{
    color: var(--placeholder) !important; opacity: 1 !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {{
    background: var(--field) !important; border-color: var(--field-border) !important;
    border-radius: 10px !important; color: var(--text) !important;
}}
[data-testid="stSelectbox"] [role="group"],
[data-testid="stMultiSelect"] [role="group"] {{
    background: var(--field) !important; border: 1px solid var(--field-border) !important;
    border-radius: 10px !important;
}}
[data-testid="stSelectbox"] input[role="combobox"],
[data-testid="stMultiSelect"] input[role="combobox"] {{
    background: transparent !important; border: 0 !important; color: var(--text) !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] * {{ color: var(--text) !important; }}
[data-baseweb="popover"] > div, [role="listbox"] {{
    background: var(--menu) !important; color: var(--text) !important;
    border: 1px solid var(--border) !important;
}}
[role="option"] {{ color: var(--text) !important; }}
[role="option"]:hover, [aria-selected="true"][role="option"] {{ background: var(--menu-hover) !important; }}
[data-testid="stNumberInputContainer"] {{
    background: var(--field) !important; border: 1px solid var(--field-border) !important;
    border-radius: 10px !important; overflow: hidden;
}}
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] {{
    background: var(--field) !important; border: 0 !important;
    border-left: 1px solid var(--field-border) !important; color: var(--text) !important;
}}
[data-testid="stFileUploaderDropzone"] {{
    background: var(--surface-alt) !important; border: 1.5px dashed var(--field-border) !important;
    border-radius: 12px !important; padding: 12px !important; color: var(--text) !important;
}}
[data-testid="stFileUploaderDropzone"] button {{
    background: var(--field) !important; border: 1px solid var(--field-border) !important;
    color: var(--text) !important; box-shadow: none !important;
}}
.stButton>button {{
    background: linear-gradient(135deg, var(--a1), var(--a2)) !important; color: #fff !important;
    border: none !important; border-radius: 14px !important; font-weight: 800 !important;
    letter-spacing: .3px; padding: .65rem 1rem !important;
    box-shadow: 0 10px 28px {t['a1']}55 !important; transition: all .18s ease;
}}
.stButton>button:hover {{ transform: translateY(-2px); filter: brightness(1.1); }}

.stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: var(--surface-alt); padding: 6px; border-radius: 12px; border: 1px solid var(--border); }}
.stTabs [data-baseweb="tab"] {{ border-radius: 12px; padding: 6px 18px; }}
.stTabs [aria-selected="true"] {{ background: linear-gradient(135deg, {t['a1']}28, {t['a2']}28) !important; }}
.stTabs [aria-selected="true"] span {{ color: var(--text) !important; font-weight: 700; }}

[data-testid="stExpander"] {{ background: var(--surface-alt); border: 1px solid var(--border); border-radius: 12px; }}

.hero {{
    background: linear-gradient(135deg, {t['a1']}26, {t['a2']}1A 55%, {t['a3']}14);
    border: 1px solid var(--border); border-radius: 16px; padding: 24px 30px;
    position: relative; overflow: hidden; margin-bottom: 24px;
}}
.hero h1 {{ font-size: 2.2rem; margin: 0 0 4px; font-weight: 800; background: linear-gradient(90deg, var(--hero-title), {t['a3']}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.hero p {{ margin: 0; color: var(--muted); font-size: .95rem; font-weight: 500; }}

.metric {{
    background: var(--surface);
    border: 1px solid var(--border); border-radius: 12px; padding: 16px 20px; height: 100%; transition: all .2s ease;
}}
.metric:hover {{ transform: translateY(-2px); border-color: {t['a1']}66; box-shadow: 0 12px 28px {t['a1']}2E; }}
.metric .ic {{ font-size: 1.4rem; }}
.metric .v {{ font-family: 'Sora', sans-serif; font-size: 1.7rem; font-weight: 800; color: var(--text); line-height: 1.2; }}
.metric .l {{ font-size: .75rem; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: .5px; }}

.sect-title {{ font-family: 'Sora', sans-serif; font-weight: 800; font-size: 1.15rem; color: var(--text); margin: 10px 0 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}

.studio-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px 22px; height: 100%; }}
.bno {{ background: linear-gradient(135deg, var(--a1), var(--a2)); color: #fff; font-weight: 800; padding: 5px 14px; border-radius: 12px; font-size: .95rem; }}
.bsubj {{ font-weight: 700; color: var(--text); font-size: .92rem; margin-left:10px; }}
.bpill {{ float: right; background: var(--surface-alt); border: 1px solid var(--border); padding: 4px 12px; border-radius: 999px; color: var(--muted); font-size: .75rem; font-weight: 600; }}
.seatgrid {{ display: grid; grid-template-columns: repeat(var(--cols), 1fr); gap: 8px; margin-top:20px; }}
.seat {{ background: color-mix(in srgb, var(--c) 10%, var(--surface)); border: 1px solid color-mix(in srgb, var(--c) 30%, transparent); border-top: 3px solid var(--c); border-radius: 10px; padding: 7px 8px; min-height: 58px; overflow: hidden; }}
.seat .sn {{ font-weight: 800; color: var(--c); font-size: .62rem; text-transform: uppercase; }}
.seat .nm {{ font-size: .74rem; font-weight: 600; color: var(--text); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-thumb {{ background: {t['a1']}55; border-radius: 99px; }}
</style>
"""

# ════════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def read_csv_cached(raw_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(raw_bytes), dtype=str)

def find_default_column(columns, aliases: set[str]):
    for column in columns:
        normalized = (
            str(column).replace("\ufeff", "").strip().replace(".", "").replace(" ", "_")
        )
        if normalized.casefold() in aliases:
            return column
    return None

def date_sort_key(d: str):
    for fmt in ("%d-%m-%Y", "%d-%m-%Y %H:%M:%S"):
        try: return dt.datetime.strptime(str(d).split(" ")[0], fmt)
        except Exception: continue
    return dt.datetime.max

def block_num_key(b):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", str(b))]

def assign_subject_colors(blocks: list, palette: list) -> dict:
    mapping, i = {}, 0
    for b in blocks:
        for code in b["subjects"]:
            if code not in mapping:
                mapping[code] = palette[i % len(palette)]
                i += 1
    return mapping

def build_seating_arrangement(df: pd.DataFrame) -> dict:
    seating = {}
    for _, student in df.iterrows():
        institute_code = str(student.get("Exam_Center_Code", "000")).strip() or "000"
        block_number = str(student.get("Block_Number", "")).strip().split(".")[0]
        key = (
            str(student.get("Date", "")).strip(),
            str(student.get("Exam_Session", "")).strip(),
            institute_code,
            block_number,
        )
        program = sit3.extract_code(student.get("Program", ""))
        subject = sit3.extract_code(student.get("Subject", ""))
        seating.setdefault(key, []).append([
            None,
            f"{program[0]}{(' - ' + program[2]) if program[2] else ''}",
            f"{subject[0]}{(' - ' + subject[2]) if subject[2] else ''}",
            student.get("Seat_No", ""),
            student.get("PRN", ""),
            student.get("Name", ""),
        ])
    return seating

def make_zip_bytes(root: Path) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in root.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(root).as_posix())
    return buffer.getvalue()

# ════════════════════════════════════════════════════════════════════
#  STATE & CSS
# ════════════════════════════════════════════════════════════════════
theme_name = st.session_state.get("theme_sel", "Aurora")
theme = THEMES.get(theme_name, THEMES["Aurora"])
light_mode = st.session_state.get("light_mode", False)
st.markdown(build_css(theme, light_mode), unsafe_allow_html=True)

st.session_state.setdefault("plan", None)
st.session_state.setdefault("plan_config", None)

# ════════════════════════════════════════════════════════════════════
#  UPPER BAR (CONTROL PANEL)
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="hero"><h1>🎓 Sit Seating Studio</h1></div>', unsafe_allow_html=True)

top_col1, top_col2, top_col3 = st.columns([1.2, 1.2, 1])
df_raw = None

with top_col1:
    uploaded = st.file_uploader("📂 Upload Student CSV", type=["csv"], label_visibility="collapsed")
    if uploaded is not None:
        try: df_raw = read_csv_cached(uploaded.getvalue())
        except Exception: st.error("Invalid CSV")
        
    columns = list(df_raw.columns) if df_raw is not None else []
    qr_options = columns or ["—"]
    qr_idx = qr_options.index("PRN") if "PRN" in qr_options else 0
    qr_col = st.selectbox("🔲 QR Code Field", options=qr_options, index=qr_idx)
    st.session_state["qr_column"] = qr_col
    date_placeholder = "— Select date column —"
    session_placeholder = "— Select session column —"
    date_options = [date_placeholder, *columns]
    session_options = [session_placeholder, *columns]
    default_date = find_default_column(columns, {"date", "exam_date", "date_of_exam"})
    default_session = find_default_column(
        columns, {"exam_session", "session", "exam_time", "time", "time_of_exam"}
    )
    date_col = st.selectbox(
        "📅 Exam Date Column",
        options=date_options,
        index=date_options.index(default_date) if default_date is not None else 0,
        disabled=df_raw is None,
    )
    session_col = st.selectbox(
        "🕒 Exam Session Column",
        options=session_options,
        index=session_options.index(default_session) if default_session is not None else 0,
        disabled=df_raw is None,
    )

with top_col2:
    college = st.text_input("🏛️ College Heading", placeholder="Institute Name")
    exam_heading = st.text_input("📝 Exam Heading", placeholder="e.g. Mid Semester 2026")
    inst_code = st.text_input("🔢 Institute Code", placeholder="e.g. EN6317")

with top_col3:
    capacity = st.number_input("🪑 Block Capacity", min_value=10, max_value=150, value=30)
    theme_sel = st.selectbox("🎨 Theme", list(THEMES.keys()), key="theme_sel")
    st.toggle("Light mode", key="light_mode")
    st.write("")
    generate_btn = st.button("✨ Generate Plan", type="primary", use_container_width=True)

# ════════════════════════════════════════════════════════════════════
#  ADVANCED SETTINGS (EXPANDER)
# ════════════════════════════════════════════════════════════════════
with st.expander("⚙️ Advanced Setup"):
    adv1, adv2, adv3 = st.columns(3)
    with adv1:
        logo_file = st.file_uploader("🏫 Logo (PNG)", type=["png", "jpg"])
        logo_path = None
        if logo_file:
            logo_path = os.path.join(tempfile.gettempdir(), f"studio_logo.png")
            with open(logo_path, "wb") as f: f.write(logo_file.getvalue())
    with adv2:
        per_block = st.text_input("Block Override", placeholder="e.g. 1=30, 2=45")
        seats_per_row = st.number_input("Seats per row", value=6)
    with adv3:
        show_prn = st.checkbox("Show PRN on seats", value=True)
        show_seatno = st.checkbox("Show Seat No.", value=False)

st.write("")

# ════════════════════════════════════════════════════════════════════
#  PLAN GENERATION
# ════════════════════════════════════════════════════════════════════
if generate_btn:
    if df_raw is None:
        st.error("⚠️ Upload student CSV first.")
    elif date_col == date_placeholder or session_col == session_placeholder:
        st.error("⚠️ Select the CSV columns for exam date and exam session.")
    elif date_col == session_col:
        st.error("⚠️ Exam date and exam session must use different columns.")
    else:
        with st.spinner("🏗️ Architecting plan…"):
            override = capacity
            if per_block and "=" in per_block:
                override = {b.split("=")[0].strip(): int(b.split("=")[1].strip()) for b in per_block.split(",")}

            plan_df = df_raw.copy()
            plan_df["Date"] = plan_df[date_col]
            plan_df["Exam_Session"] = plan_df[session_col]
            code_column = next((
                column for column in plan_df.columns
                if re.sub(r"\s+", "_", str(column).strip().replace(".", "")) == "Exam_Center_Code"
            ), None)
            if inst_code and code_column is not None:
                plan_df[code_column] = inst_code

            with tempfile.TemporaryDirectory(prefix="seating_plan_") as plan_dir:
                result = sit3.create_directories_and_pdfs(
                    plan_df,
                    parent_dir=plan_dir,
                    custom_institute_name=college,
                    block_capacity_override=override,
                    exam_heading=exam_heading,
                )
            updated_df = result["updated_df"]
            st.session_state["plan"] = {
                "plan": {"seating_arrangement_dict": build_seating_arrangement(updated_df)},
                "total_students": len(updated_df),
                "institute_name": result["institute_name"],
                "exam_heading": exam_heading or sit3.DEFAULT_EXAM_HEADING,
                "institute_code": inst_code,
                "updated_df": updated_df,
                "input_df": plan_df,
            }
            st.session_state["plan_config"] = {
                "capacity": capacity, "seats_per_row": seats_per_row,
                "show_prn": show_prn, "show_seatno": show_seatno, "override": override,
            }
        st.success("✅ Plan generated successfully!")

# ════════════════════════════════════════════════════════════════════
#  MAIN TABS
# ════════════════════════════════════════════════════════════════════
if st.session_state.get("plan") is None:
    st.stop()

plan = st.session_state["plan"]
cfg = st.session_state["plan_config"]

blocks = []
for (d, s, inst, bno), rows in plan["plan"]["seating_arrangement_dict"].items():
    subjs = {}
    for r in rows:
        c = (str(r[2]).split(" - ")[0] if " - " in str(r[2]) else str(r[2])).strip()
        if c: subjs[c] = subjs.get(c, 0) + 1
    blocks.append({
        "date": str(d), "session": str(s), "block": str(bno),
        "rows": rows, "subjects": list(subjs), "count": len(rows)
    })
blocks.sort(key=lambda b: (date_sort_key(b["date"]), b["session"], block_num_key(b["block"])))
cmap = assign_subject_colors(blocks, theme["palette"])

tab_over, tab_map, tab_rep, tab_data = st.tabs(["📊 Overview", "🪑 Seat Map", "📥 Export PDFs", "🗂️ Dataset"])

with tab_over:
    m = st.columns(5)
    m[0].markdown(f"""<div class="metric"><div class="ic">👥</div><div class="v">{plan['total_students']}</div><div class="l">Students</div></div>""", unsafe_allow_html=True)
    m[1].markdown(f"""<div class="metric"><div class="ic">🧱</div><div class="v">{len(blocks)}</div><div class="l">Blocks</div></div>""", unsafe_allow_html=True)
    m[2].markdown(f"""<div class="metric"><div class="ic">📚</div><div class="v">{len({c for b in blocks for c in b['subjects']})}</div><div class="l">Subjects</div></div>""", unsafe_allow_html=True)
    m[3].markdown(f"""<div class="metric"><div class="ic">📅</div><div class="v">{len({b['date'] for b in blocks})}</div><div class="l">Days</div></div>""", unsafe_allow_html=True)
    m[4].markdown(f"""<div class="metric"><div class="ic">🪑</div><div class="v">{cfg['capacity']}</div><div class="l">Capacity</div></div>""", unsafe_allow_html=True)
    
    st.write("")
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<p class="sect-title">🗓️ Schedule</p>', unsafe_allow_html=True)
        sched = []
        for d in sorted({b["date"] for b in blocks}, key=date_sort_key):
            for s in sorted({b["session"] for b in blocks if b["date"]==d}):
                bb = [b for b in blocks if b["date"]==d and b["session"]==s]
                sched.append({"Date": d, "Session": sit3.format_session_label(s), "Students": sum(b["count"] for b in bb), "Blocks": len(bb)})
        st.dataframe(pd.DataFrame(sched), width="stretch", hide_index=True)
    with c2:
        st.markdown('<p class="sect-title">🧱 Utilisation</p>', unsafe_allow_html=True)
        st.bar_chart(pd.Series({f"B{b['block']} ({b['date']})": b["count"] for b in blocks}), height=250, color=theme["a3"])

with tab_map:
    st.markdown('<p class="sect-title">🗺️ Interactive Seat Map</p>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1.5, 1.5, 3])
    d_sel = f1.selectbox("Exam Date", sorted({b["date"] for b in blocks}, key=date_sort_key))
    s_sel = f2.selectbox("Session", sorted({b["session"] for b in blocks if b["date"]==d_sel}))
    b_opts = [b for b in blocks if b["date"]==d_sel and b["session"]==s_sel]
    b_lbls = [f"Block {b['block']} ({b['count']})" for b in b_opts]
    chosen = f3.multiselect("Select Blocks", b_lbls, default=b_lbls[:2] if b_lbls else None)
    
    selected_blocks = [b for b, lbl in zip(b_opts, b_lbls) if lbl in chosen]
    for i in range(0, len(selected_blocks), 2):
        pair = selected_blocks[i:i+2]
        cols = st.columns(2)
        for col, b in zip(cols, pair):
            with col:
                parts = []
                for idx, row in enumerate(b["rows"]):
                    _, _, subj, sno, prn, nm = (list(row) + [""]*6)[:6]
                    c = cmap.get((str(subj).split(" - ")[0] if " - " in str(subj) else str(subj)).strip(), "#94A3B8")
                    p_str = f'<div class="pr">{prn}</div>' if cfg["show_prn"] else ""
                    parts.append(f'<div class="seat" style="--c:{c}"><div class="sn">Seat {idx+1:02d}</div><div class="nm">{nm}</div>{p_str}</div>')
                
                st.markdown(f"""
                <div class="studio-card">
                    <div class="bno">🪑 Block {b['block']}</div><span class="bsubj">{', '.join(b['subjects'])}</span>
                    <span class="bpill">{b['count']} Seats</span>
                    <div class="seatgrid" style="--cols:{cfg['seats_per_row']};">{''.join(parts)}</div>
                </div>""", unsafe_allow_html=True)

with tab_rep:
    st.markdown('<p class="sect-title">📥 Generate PDF Reports & QR Labels</p>', unsafe_allow_html=True)
    export_btn = st.button("🎬 Generate Everything", type="primary")

    if export_btn:
        out_dir = tempfile.mkdtemp(prefix="seating_reports_")
        prog = st.progress(0.0, text="⚙️ Generating PDFs...")
        
        try:
            sit3.create_directories_and_pdfs(
                plan["input_df"], parent_dir=out_dir, custom_institute_name=plan["institute_name"],
                block_capacity_override=cfg["override"], exam_heading=plan["exam_heading"]
            )
            if "qr_column" in st.session_state:
                qr.generate_all_qrs(df_raw.copy(), out_dir, st.session_state["qr_column"])
                
            prog.progress(1.0, text="✅ All PDFs ready!")
            zip_bytes = make_zip_bytes(Path(out_dir))
            
            st.download_button("⬇️ Download All Files (ZIP)", data=zip_bytes, file_name="seating_reports.zip", mime="application/zip", width="stretch")
        except Exception as e:
            st.error(f"❌ Error: {e}")

with tab_data:
    st.markdown('<p class="sect-title">🗂️ Dataset</p>', unsafe_allow_html=True)
    st.dataframe(plan["updated_df"], width="stretch", height=400)