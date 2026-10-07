import os
import sys
import io
import time
import zipfile
import base64
import re
import importlib
from pathlib import Path
import pandas as pd
import streamlit as st

# Backend engine - force reload to ensure latest code is always active
import sit3
importlib.reload(sit3)

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="SIT Seating Arrangement Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# LUXURY MODERN DESIGN SYSTEM (CSS)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --primary: #3b82f6;
        --primary-dark: #1d4ed8;
        --primary-gradient: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
        --success-gradient: linear-gradient(135deg, #10b981 0%, #059669 100%);
        --card-bg: #ffffff;
        --border-color: #e2e8f0;
        --text-main: #0f172a;
        --text-muted: #64748b;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0f172a;
        background-color: #f8fafc;
    }

    h1, h2, h3, h4, .outfit-font {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }

    code, pre, .mono-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 4rem;
        max-width: 1240px;
    }

    /* Ambient Glow Background Effect */
    body {
        background: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.035) 0%, transparent 45%),
                    radial-gradient(circle at 85% 75%, rgba(14, 165, 233, 0.035) 0%, transparent 45%),
                    #f8fafc;
    }

    /* Floating Modern Brand Header */
    .brand-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 16px;
        padding: 16px 24px;
        margin-bottom: 22px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
    }

    .brand-title-wrap {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .brand-logo-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 1.4rem;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }

    .brand-title-text {
        font-family: 'Outfit', sans-serif;
        font-size: 1.35rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-subtitle-text {
        font-size: 0.8rem;
        color: #64748b;
        margin: 0;
        font-weight: 500;
    }

    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
    }

    .badge-pill.success {
        background: #f0fdf4;
        color: #15803d;
        border: 1px solid #bbf7d0;
    }

    .badge-pill.warning {
        background: #fff1f2;
        color: #be123c;
        border: 1px solid #fecdd3;
    }

    /* Modern Stepper Roadmap */
    .stepper-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 24px;
    }

    .step-card {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px 18px;
        display: flex;
        align-items: center;
        gap: 14px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .step-card.active {
        border-color: #2563eb;
        background: #f8faff;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.12);
    }

    .step-card.active::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
    }

    .step-card.completed {
        border-color: #10b981;
        background: #f0fdf4;
    }

    .step-avatar {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1rem;
        flex-shrink: 0;
        background: #f1f5f9;
        color: #64748b;
        transition: all 0.2s ease;
    }

    .step-card.active .step-avatar {
        background: linear-gradient(135deg, #2563eb, #4f46e5);
        color: #ffffff;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35);
    }

    .step-card.completed .step-avatar {
        background: #10b981;
        color: #ffffff;
    }

    .step-info-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 0.95rem;
        color: #0f172a;
        margin: 0;
    }

    .step-info-desc {
        font-size: 0.74rem;
        color: #64748b;
        margin: 2px 0 0 0;
    }

    /* Main Content Surface Card */
    .surface-card {
        background: #ffffff;
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 18px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.03);
    }

    .surface-header-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #eff6ff;
        color: #1d4ed8;
        font-weight: 800;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 4px 12px;
        border-radius: 6px;
        margin-bottom: 8px;
    }

    .surface-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.55rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }

    .surface-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 24px;
    }

    /* KPI Summary Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 14px;
        margin: 20px 0;
    }

    .kpi-tile {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 18px;
        position: relative;
        overflow: hidden;
    }

    .kpi-tile::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: #cbd5e1;
    }

    .kpi-tile.blue::before { background: #3b82f6; }
    .kpi-tile.emerald::before { background: #10b981; }
    .kpi-tile.amber::before { background: #f59e0b; }
    .kpi-tile.purple::before { background: #8b5cf6; }

    .kpi-tile-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .kpi-tile-value {
        font-family: 'Outfit', sans-serif;
        font-size: 1.55rem;
        font-weight: 800;
        color: #0f172a;
        margin-top: 4px;
    }

    .kpi-tile-sub {
        font-size: 0.74rem;
        color: #94a3b8;
        margin-top: 2px;
    }

    /* Realistic Paper Report Mockup Card */
    .paper-preview-card {
        background: #ffffff;
        border: 2px solid #cbd5e1;
        border-radius: 12px;
        padding: 22px 26px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.06), 0 4px 6px -2px rgba(0, 0, 0, 0.02);
        margin-top: 14px;
        position: relative;
        overflow: hidden;
    }

    .paper-preview-card::before {
        content: 'OFFICIAL REPORT PREVIEW';
        position: absolute;
        top: 8px;
        right: 12px;
        font-size: 0.65rem;
        font-weight: 800;
        color: #94a3b8;
        letter-spacing: 1px;
    }

    .paper-inst-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 800;
        color: #1e3a8a;
        text-align: center;
        letter-spacing: -0.01em;
    }

    .paper-inst-sub {
        font-size: 0.8rem;
        color: #475569;
        text-align: center;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .paper-heading-badge {
        display: inline-block;
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: #ffffff;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 0.98rem;
        padding: 8px 22px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        margin: 6px 0;
        letter-spacing: 0.2px;
    }

    .paper-notice {
        font-size: 0.75rem;
        color: #64748b;
        text-align: center;
        margin-top: 8px;
        font-style: italic;
    }

    /* Giant Download Banner */
    .download-hero {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #86efac;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 22px;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.08);
    }

    .download-hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.35rem;
        font-weight: 800;
        color: #14532d;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .download-hero-desc {
        font-size: 0.88rem;
        color: #166534;
        margin-top: 4px;
        line-height: 1.45;
    }

    /* Desk Cards */
    .desk-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        transition: all 0.15s ease;
    }

    .desk-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }

    .bench-pill {
        background: #eff6ff;
        color: #1d4ed8;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
    }

    .prn-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        color: #334155;
    }

    .student-title {
        font-size: 0.88rem;
        font-weight: 700;
        color: #0f172a;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 3px;
    }

    /* Streamlit Button Luxury Overrides */
    div[data-testid="stButton"] > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        padding: 10px 20px !important;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
        color: #ffffff !important;
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
    }

    div[data-testid="stDownloadButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        padding: 14px 28px !important;
    }

    div[data-testid="stDownloadButton"] > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# STATE INITIALIZATION
# ==============================================================================
if "active_df" not in st.session_state:
    if os.path.exists("sem7sl.csv"):
        st.session_state["active_df"] = pd.read_csv("sem7sl.csv", dtype=str)
        st.session_state["active_filename"] = "sem7sl.csv (Default Sample)"
    elif os.path.exists("sl1.csv"):
        st.session_state["active_df"] = pd.read_csv("sl1.csv", dtype=str)
        st.session_state["active_filename"] = "sl1.csv (Default Sample)"
    else:
        st.session_state["active_df"] = None
        st.session_state["active_filename"] = None

if "custom_institute_name" not in st.session_state:
    st.session_state["custom_institute_name"] = "Sharad Institute of Technology College of Engineering"

if "custom_exam_heading" not in st.session_state:
    st.session_state["custom_exam_heading"] = "Winter Semester Examination 2026 Final Year B.Tech (sem - VII )"

if "global_capacity" not in st.session_state:
    st.session_state["global_capacity"] = 30

if "generation_result" not in st.session_state:
    st.session_state["generation_result"] = None

# Always start at Step 1 for transparent, clear navigation
if "active_step" not in st.session_state:
    st.session_state["active_step"] = 1

# ==============================================================================
# HELPER UTILITIES
# ==============================================================================
def create_zip_archive(source_dir):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                archive_name = os.path.relpath(file_path, source_dir)
                zip_file.write(file_path, archive_name)
    zip_buffer.seek(0)
    return zip_buffer


def render_pdf_preview(pdf_path):
    if not os.path.exists(pdf_path):
        st.warning("Selected PDF report file does not exist on disk.")
        return
    try:
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        st.markdown(f'''
        <div style="border: 2px solid #cbd5e1; border-radius: 14px; overflow: hidden; margin-top: 14px; box-shadow: 0 8px 24px rgba(0,0,0,0.06);">
            <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="750" type="application/pdf" style="border:none;"></iframe>
        </div>
        ''', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not render PDF preview: {e}")


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]


# ==============================================================================
# BRAND NAVBAR & WORKSPACE STATUS
# ==============================================================================
df_current = st.session_state.get("active_df")
has_data = df_current is not None and not df_current.empty
file_label = st.session_state.get("active_filename", "Custom Upload")
record_count_str = f"{len(df_current):,} Candidates" if has_data else "No CSV Loaded"

status_pill = f'''
<div class="badge-pill success">
    <span style="font-size: 0.65rem;">🟢</span>
    <span>Ready: {file_label} ({record_count_str})</span>
</div>
''' if has_data else '''
<div class="badge-pill warning">
    <span style="font-size: 0.65rem;">🔴</span>
    <span>Step 1 Required: Upload Student CSV</span>
</div>
'''

st.markdown(f'''
<div class="brand-navbar">
    <div class="brand-title-wrap">
        <div class="brand-logo-icon">🏛️</div>
        <div>
            <div class="brand-title-text">
                <span>SIT Seating Arrangement Studio</span>
                <span style="font-size: 0.72rem; font-weight: 700; background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; padding: 2px 8px; border-radius: 6px; letter-spacing: 0.5px;">PRO V3</span>
            </div>
            <div class="brand-subtitle-text">Autonomous Examination Deliverables & Attendance Generation Suite</div>
        </div>
    </div>
    <div>{status_pill}</div>
</div>
''', unsafe_allow_html=True)

# ==============================================================================
# 3-STEP PIPELINE NAVIGATION (CLICKABLE STEPPERS)
# ==============================================================================
has_generated = st.session_state.get("generation_result") is not None or os.path.exists("Seating arrangement deliverables")

col_n1, col_n2, col_n3 = st.columns(3)

with col_n1:
    btn_s1_label = f"① Upload Data {'✅' if has_data else '⏳'}"
    if st.button(btn_s1_label, width="stretch", type="primary" if st.session_state["active_step"] == 1 else "secondary"):
        st.session_state["active_step"] = 1
        st.rerun()

with col_n2:
    btn_s2_label = f"② Configure & Generate {'✅' if has_generated else '⏳'}"
    if st.button(btn_s2_label, width="stretch", type="primary" if st.session_state["active_step"] == 2 else "secondary"):
        st.session_state["active_step"] = 2
        st.rerun()

with col_n3:
    btn_s3_label = f"③ Download Deliverables {'📥' if has_generated else '⚪'}"
    if st.button(btn_s3_label, width="stretch", type="primary" if st.session_state["active_step"] == 3 else "secondary"):
        st.session_state["active_step"] = 3
        st.rerun()

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# STEP 1: UPLOAD DATA
# ==============================================================================
if st.session_state["active_step"] == 1:
    st.markdown('''
    <div class="surface-card">
        <span class="surface-header-tag">Step 1 of 3 • Input Source</span>
        <div class="surface-title">📁 Choose or Upload Student Portal CSV</div>
        <div class="surface-subtitle">Select a pre-verified examination dataset or upload your own student list CSV directly from your computer.</div>
    ''', unsafe_allow_html=True)

    col_u1, col_u2 = st.columns([1, 1], gap="large")
    
    with col_u1:
        st.markdown("#### ⚡ 1-Click Sample Datasets")
        st.caption("Instantly test the seating engine without having to search for a file:")
        
        btn_sample1, btn_sample2 = st.columns(2)
        with btn_sample1:
            if st.button("🚀 Load sem7sl.csv\n(3,928 Students)", width="stretch", type="primary" if not has_data else "secondary"):
                if os.path.exists("sem7sl.csv"):
                    st.session_state["active_df"] = pd.read_csv("sem7sl.csv", dtype=str)
                    st.session_state["active_filename"] = "sem7sl.csv"
                    st.toast("Loaded sem7sl.csv (3,928 candidates)!", icon="✅")
                    st.rerun()
                else:
                    st.error("sem7sl.csv not found in workspace.")
                    
        with btn_sample2:
            if st.button("📄 Load sl1.csv\n(1,276 Students)", width="stretch"):
                if os.path.exists("sl1.csv"):
                    st.session_state["active_df"] = pd.read_csv("sl1.csv", dtype=str)
                    st.session_state["active_filename"] = "sl1.csv"
                    st.toast("Loaded sl1.csv (1,276 candidates)!", icon="✅")
                    st.rerun()
                else:
                    st.error("sl1.csv not found in workspace.")

    with col_u2:
        st.markdown("#### 📤 Upload Your Own Student CSV")
        st.caption("Upload any CSV containing Date, Session, Subject, PRN, and Block Number:")
        
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
        if uploaded_file is not None:
            try:
                st.session_state["active_df"] = pd.read_csv(uploaded_file, dtype=str)
                st.session_state["active_filename"] = uploaded_file.name
                st.toast(f"Uploaded {uploaded_file.name} successfully!", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

    # Dataset Status Deck
    if has_data:
        df_norm = df_current.copy()
        df_norm.columns = df_norm.columns.str.strip().str.replace(r'\.', '', regex=True).str.replace(" ", "_")
        
        n_dates = df_norm["Date"].dropna().nunique() if "Date" in df_norm.columns else 0
        n_sess = df_norm["Exam_Session"].dropna().nunique() if "Exam_Session" in df_norm.columns else 0
        n_subj = df_norm["Subject"].dropna().nunique() if "Subject" in df_norm.columns else 0
        
        st.markdown("<hr style='margin: 22px 0;'/>", unsafe_allow_html=True)
        st.markdown(f"#### 📊 Active Dataset Metrics: `{st.session_state.get('active_filename')}`")
        
        st.markdown(f'''
        <div class="kpi-grid">
            <div class="kpi-tile blue">
                <div class="kpi-tile-label">Total Candidates</div>
                <div class="kpi-tile-value">{len(df_current):,}</div>
                <div class="kpi-tile-sub">Eligible student rows</div>
            </div>
            <div class="kpi-tile emerald">
                <div class="kpi-tile-label">Examination Dates</div>
                <div class="kpi-tile-value">{n_dates}</div>
                <div class="kpi-tile-sub">Unique exam days</div>
            </div>
            <div class="kpi-tile amber">
                <div class="kpi-tile-label">Time Slots</div>
                <div class="kpi-tile-value">{n_sess}</div>
                <div class="kpi-tile-sub">Daily sessions</div>
            </div>
            <div class="kpi-tile purple">
                <div class="kpi-tile-label">Subjects Mapped</div>
                <div class="kpi-tile-value">{n_subj}</div>
                <div class="kpi-tile-sub">Course codes</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        col_act1, col_act2 = st.columns([2, 1])
        with col_act1:
            if st.button("👉 Proceed to Step 2: Configure Exam & Heading ➔", type="primary", width="stretch"):
                st.session_state["active_step"] = 2
                st.rerun()
        with col_act2:
            if st.button("🔄 Clear Active File", width="stretch"):
                st.session_state["active_df"] = None
                st.session_state["active_filename"] = None
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# STEP 2: SETTINGS & GENERATE
# ==============================================================================
elif st.session_state["active_step"] == 2:
    st.markdown('''
    <div class="surface-card">
        <span class="surface-header-tag">Step 2 of 3 • Configuration & Execution</span>
        <div class="surface-title">⚙️ Select Examination Heading & Room Capacity</div>
        <div class="surface-subtitle">Select or type the official examination title that appears on all 8 report deliverables, then launch the seating generator.</div>
    ''', unsafe_allow_html=True)

    if not has_data:
        st.warning("⚠️ No student data loaded. Please return to Step 1 to select or upload a CSV.")
        if st.button("⬅️ Back to Step 1: Upload Student CSV", type="primary"):
            st.session_state["active_step"] = 1
            st.rerun()
    else:
        col_cfg1, col_cfg2 = st.columns([1, 1], gap="large")
        
        with col_cfg1:
            st.markdown("#### 📝 1. Select Official Examination Heading")
            st.caption("Choose from standard semester presets or type your own custom title:")
            
            heading_presets = [
                "Winter Semester Examination 2026 Final Year B.Tech (sem - VII )",
                "End Semester Examination (ESE) Winter 2026",
                "Mid Semester Examination (MSE) 2026",
                "Winter Re-Semester Examination (ESE) 2026",
                "In-Semester Assessment Examination 2026",
                "Continuous Assessment Examination (CA-1 / CA-2) 2026",
                "✏️ Type Custom Heading..."
            ]

            curr_hd = st.session_state.get("custom_exam_heading", heading_presets[0])
            p_idx = heading_presets.index(curr_hd) if curr_hd in heading_presets else len(heading_presets) - 1

            chosen_preset = st.selectbox("Exam Heading Preset:", heading_presets, index=p_idx)
            
            if chosen_preset != "✏️ Type Custom Heading...":
                typed_hd = st.text_input("Review or Edit Heading Text:", value=chosen_preset)
            else:
                typed_hd = st.text_input(
                    "Enter Custom Examination Heading:",
                    value=curr_hd if curr_hd not in heading_presets[:-1] else "",
                    placeholder="e.g. End Semester Examination 2026 Final Year B.Tech..."
                )
                
            if typed_hd and typed_hd.strip():
                st.session_state["custom_exam_heading"] = typed_hd.strip()

        with col_cfg2:
            st.markdown("#### 🪑 2. Room Allocation & Block Capacity")
            st.caption("Enforce maximum student count per block and verify college title:")
            
            st.markdown("<label style='font-size: 0.82rem; font-weight: 700; color: #334155; text-transform: uppercase; letter-spacing: 0.5px;'>Quick Capacity Presets:</label>", unsafe_allow_html=True)
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                if st.button("20 Seats / Hall", type="primary" if st.session_state.get("global_capacity") == 20 else "secondary", width="stretch"):
                    st.session_state["global_capacity"] = 20
                    st.rerun()
            with col_p2:
                if st.button("25 Seats / Hall", type="primary" if st.session_state.get("global_capacity") == 25 else "secondary", width="stretch"):
                    st.session_state["global_capacity"] = 25
                    st.rerun()
            with col_p3:
                if st.button("30 Seats / Hall", type="primary" if st.session_state.get("global_capacity", 30) == 30 else "secondary", width="stretch"):
                    st.session_state["global_capacity"] = 30
                    st.rerun()

            c_cap, c_inst = st.columns([1, 2])
            with c_cap:
                curr_cap = int(st.session_state.get("global_capacity", 30))
                new_cap = st.number_input(
                    "Seats per Hall:",
                    min_value=5,
                    max_value=150,
                    value=curr_cap,
                    step=5,
                    key="num_cap_input"
                )
                if new_cap != curr_cap:
                    st.session_state["global_capacity"] = int(new_cap)
                    st.rerun()

            with c_inst:
                inst_val = st.text_input(
                    "College / Institute Name:",
                    value=st.session_state.get("custom_institute_name", "Sharad Institute of Technology College of Engineering"),
                    key="inst_name_input"
                )
                st.session_state["custom_institute_name"] = inst_val.strip()

            active_cap = int(st.session_state.get("global_capacity", 30))
            st.markdown(f'''
            <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 10px 14px; margin-top: 6px; font-size: 0.82rem; color: #1e40af;">
                <span style="font-weight: 800;">⚙️ Capacity Rule:</span> Each examination block is strictly capped at <strong>{active_cap} students</strong>. 
                The student list (SL) data will be overridden with clean sequential blocks (Block 1, Block 2, Block 3...).
            </div>
            ''', unsafe_allow_html=True)

        # Realistic Official Report Sheet Preview Mockup
        st.markdown(f'''
        <div class="paper-preview-card">
            <div class="paper-inst-title">{st.session_state.get("custom_institute_name")}</div>
            <div class="paper-inst-sub">(An Autonomous Institute)</div>
            <div style="text-align: center;">
                <div class="paper-heading-badge">{st.session_state.get("custom_exam_heading")}</div>
            </div>
            <div class="paper-notice">
                ✓ Verified: This heading and {st.session_state.get("global_capacity", 30)}-seat capacity are printed uniformly across all 8 deliverable report types
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("<hr style='margin: 26px 0;'/>", unsafe_allow_html=True)

        col_act1, col_act2 = st.columns([2, 1])
        with col_act1:
            run_btn = st.button("⚡ GENERATE COMPLETE SEATING DELIVERABLES (ALL 8 REPORTS)", type="primary", width="stretch")
        with col_act2:
            if st.button("⬅️ Change Dataset in Step 1", width="stretch"):
                st.session_state["active_step"] = 1
                st.rerun()

        if run_btn:
            progress_bar = st.progress(0)
            status_box = st.empty()
            
            def on_progress(current, total, msg):
                pct = int((current / max(1, total)) * 100)
                progress_bar.progress(min(100, pct))
                status_box.markdown(f"**Generating ({pct}%):** {msg}")
                
            t_start = time.time()
            try:
                output_dir = "Seating arrangement deliverables"
                with st.spinner("Processing seating arrangement and generating deliverable PDFs..."):
                    res = sit3.create_directories_and_pdfs(
                        student_list_csv=df_current,
                        parent_dir=output_dir,
                        progress_callback=on_progress,
                        custom_institute_name=st.session_state.get("custom_institute_name"),
                        block_capacity_override=st.session_state.get("global_capacity", 30),
                        exam_heading=st.session_state.get("custom_exam_heading")
                    )
                elapsed = time.time() - t_start
                progress_bar.progress(100)
                status_box.empty()
                
                # CRITICAL: Overwrite the active student list with newly allocated block numbers!
                updated_df = res.get("updated_df")
                if updated_df is not None and not updated_df.empty:
                    st.session_state["active_df"] = updated_df

                st.session_state["generation_result"] = {
                    "status": "success",
                    "parent_dir": output_dir,
                    "total_blocks": res.get("total_blocks", 0),
                    "elapsed_time": round(elapsed, 2),
                    "updated_csv_path": res.get("updated_csv_path"),
                    "block_capacity": res.get("block_capacity", st.session_state.get("global_capacity", 30))
                }
                
                # Automatically transition to Step 3 for instant download!
                st.session_state["active_step"] = 3
                st.toast(f"All 8 report deliverables generated successfully ({res.get('total_blocks', 0)} blocks)!", icon="🎉")
                st.rerun()
            except Exception as e:
                st.error(f"Error during execution: {e}")
                import traceback
                st.code(traceback.format_exc())

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# STEP 3: DOWNLOAD & VIEW DELIVERABLES
# ==============================================================================
elif st.session_state["active_step"] == 3:
    st.markdown('''
    <div class="surface-card">
        <span class="surface-header-tag">Step 3 of 3 • Deliverables Hub</span>
        <div class="surface-title">📥 Download Deliverables & Preview PDF Reports</div>
        <div class="surface-subtitle">Download the complete ZIP package containing all print-ready reports or inspect individual PDF documents directly in your browser.</div>
    ''', unsafe_allow_html=True)

    parent_dir = "Seating arrangement deliverables"
    
    if not os.path.exists(parent_dir):
        st.warning("⚠️ No deliverables found. Please return to Step 2 to generate reports.")
        if st.button("⬅️ Go to Step 2: Select Exam & Generate", type="primary"):
            st.session_state["active_step"] = 2
            st.rerun()
    else:
        # Collect all generated PDFs
        all_pdfs = []
        for root, _, files in os.walk(parent_dir):
            for file in files:
                if file.endswith(".pdf"):
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, parent_dir)
                    all_pdfs.append((rel_p, full_p))
                    
        all_pdfs.sort(key=lambda x: natural_sort_key(x[0]))
        
        if not all_pdfs:
            st.warning("⚠️ No PDF reports found in deliverables folder. Please return to Step 2 and click Generate.")
            if st.button("⬅️ Return to Step 2"):
                st.session_state["active_step"] = 2
                st.rerun()
        else:
            # HERO DOWNLOAD BANNER
            st.markdown(f"""
            <div class="download-hero">
                <div class="download-hero-title">
                    <span>🎉</span>
                    <span>All Deliverables Generated & Ready for Download!</span>
                </div>
                <div class="download-hero-desc">
                    Generated <strong>{len(all_pdfs)} total PDF reports</strong> across all exam blocks and sessions with heading:<br/>
                    <strong style="color: #15803d; font-size: 0.95rem;">"{st.session_state.get('custom_exam_heading')}"</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            gen_res = st.session_state.get("generation_result") or {}
            active_cap = gen_res.get("block_capacity", st.session_state.get("global_capacity", 30))

            # Capacity Enforcement Banner
            st.markdown(f"""
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 14px 20px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div style="font-weight: 800; font-size: 1rem; color: #15803d; display: flex; align-items: center; gap: 8px;">
                        <span>🛡️</span>
                        <span>Block Capacity Enforced: {active_cap} Students / Room</span>
                    </div>
                    <div style="font-size: 0.83rem; color: #166534; margin-top: 4px;">
                        Student List (SL) data was automatically overridden with clean sequential block numbers (Block 1, 2, 3...) strictly capped at {active_cap} seats per hall.
                    </div>
                </div>
                <div style="background: #dcfce7; border: 1px solid #86efac; color: #15803d; font-weight: 700; font-size: 0.8rem; padding: 6px 14px; border-radius: 20px; letter-spacing: 0.5px;">
                    MAX {active_cap} SEATS / ROOM
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Read updated CSV data for download
            updated_csv_path = os.path.join(parent_dir, "updated_student_list_with_blocks.csv")
            csv_bytes = b""
            if os.path.exists(updated_csv_path):
                with open(updated_csv_path, "rb") as f_csv:
                    csv_bytes = f_csv.read()
            elif st.session_state.get("active_df") is not None and not st.session_state["active_df"].empty:
                csv_bytes = st.session_state["active_df"].to_csv(index=False).encode("utf-8")

            zip_buffer = create_zip_archive(parent_dir)

            col_dl1, col_dl2 = st.columns(2, gap="medium")
            with col_dl1:
                st.download_button(
                    label="📦 DOWNLOAD COMPLETE DELIVERABLES (.ZIP)\n(All 8 PDF reports + updated SL CSV)",
                    data=zip_buffer,
                    file_name=f"SIT_Seating_Deliverables_{time.strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    type="primary",
                    width="stretch"
                )
            with col_dl2:
                st.download_button(
                    label="📄 DOWNLOAD UPDATED STUDENT LIST (.CSV)\n(Overridden with allocated Block Numbers)",
                    data=csv_bytes,
                    file_name="updated_student_list_with_blocks.csv",
                    mime="text/csv",
                    width="stretch"
                )

            st.caption("💡 The ZIP archive includes Attendance Sheets, College Block Reports, Supervision Summaries, Junior Supervisor Reports, Answer Book Collections, Seat Number Summaries & the updated student list CSV.")

            st.markdown("<hr style='margin: 28px 0;'/>", unsafe_allow_html=True)

            # INTERACTIVE PDF VIEWER & SINGLE DOWNLOAD
            st.markdown("#### 📑 Preview & Download Individual PDF Reports")
            st.caption("Select any individual report from the dropdown to preview it on screen or download it separately:")

            # Report Category Quick Filter
            categories = [
                "All Reports",
                "Attendance Sheets",
                "College Block Reports",
                "Supervision Summaries",
                "Junior Supervisor Reports",
                "Answer Book Collections",
                "Group Summaries"
            ]
            chosen_cat = st.selectbox("Filter by Report Category:", categories)

            filtered_pdfs = all_pdfs
            if chosen_cat == "Attendance Sheets":
                filtered_pdfs = [p for p in all_pdfs if "attendance" in p[0].lower()]
            elif chosen_cat == "College Block Reports":
                filtered_pdfs = [p for p in all_pdfs if "college_block" in p[0].lower()]
            elif chosen_cat == "Supervision Summaries":
                filtered_pdfs = [p for p in all_pdfs if "summary_supervision" in p[0].lower()]
            elif chosen_cat == "Junior Supervisor Reports":
                filtered_pdfs = [p for p in all_pdfs if "supervisor_report" in p[0].lower()]
            elif chosen_cat == "Answer Book Collections":
                filtered_pdfs = [p for p in all_pdfs if "ansbkcol" in p[0].lower()]
            elif chosen_cat == "Group Summaries":
                filtered_pdfs = [p for p in all_pdfs if "summary" in p[0].lower()]

            if not filtered_pdfs:
                filtered_pdfs = all_pdfs

            col_sel1, col_sel2 = st.columns([3, 1])
            with col_sel1:
                pdf_names = [p for p, _ in filtered_pdfs]
                selected_pdf_rel = st.selectbox("Select PDF to inspect:", pdf_names)
            with col_sel2:
                selected_pdf_abs = next(abs_p for rel_p, abs_p in filtered_pdfs if rel_p == selected_pdf_rel)
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                with open(selected_pdf_abs, "rb") as f:
                    st.download_button(
                        label="⬇️ Download This PDF",
                        data=f.read(),
                        file_name=os.path.basename(selected_pdf_abs),
                        mime="application/pdf",
                        width="stretch"
                    )

            render_pdf_preview(selected_pdf_abs)

            # CLASSROOM DESK MAP & STUDENT SEARCH
            st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
            with st.expander("🪑 Optional: Classroom Desk Layout Visualizer & Hall Pass Search", expanded=False):
                col_tab_m, col_tab_s = st.columns(2, gap="large")
                
                with col_tab_m:
                    st.markdown("##### 🏛️ Classroom Desk Layout")
                    if has_data:
                        df_map = st.session_state.get("active_df", df_current).copy()
                        df_map.columns = df_map.columns.str.strip().str.replace(r'\.', '', regex=True).str.replace(" ", "_")
                        
                        m_d, m_s, m_b = st.columns(3)
                        with m_d:
                            dates = sorted(df_map["Date"].dropna().unique().astype(str), key=natural_sort_key) if "Date" in df_map.columns else []
                            sel_d = st.selectbox("Date:", dates, key="m_d_sel")
                        with m_s:
                            sessions = sorted(df_map[df_map["Date"].astype(str) == sel_d]["Exam_Session"].dropna().unique().astype(str)) if "Exam_Session" in df_map.columns else []
                            sel_s = st.selectbox("Session:", sessions, key="m_s_sel")
                        with m_b:
                            blocks = sorted(df_map[(df_map["Date"].astype(str) == sel_d) & (df_map["Exam_Session"].astype(str) == sel_s)]["Block_Number"].dropna().unique().astype(str), key=natural_sort_key) if "Block_Number" in df_map.columns else []
                            sel_b = st.selectbox("Block:", blocks, key="m_b_sel")

                        students_in_block = df_map[
                            (df_map["Date"].astype(str) == str(sel_d)) &
                            (df_map["Exam_Session"].astype(str) == str(sel_s)) &
                            (df_map["Block_Number"].astype(str) == str(sel_b))
                        ].sort_values(by="PRN")

                        st.caption(f"Allocated: {len(students_in_block)} candidates in Block {sel_b}.")
                        
                        cols_desk = st.columns(3)
                        for d_idx, (_, row_s) in enumerate(students_in_block.iterrows()):
                            c_col = cols_desk[d_idx % 3]
                            s_name = str(row_s.get("Name", row_s.get("Student_Name", "Candidate"))).strip()
                            with c_col:
                                c_col.markdown(f'''
                                <div class="desk-card">
                                    <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                                        <span class="bench-pill">Desk #{d_idx + 1}</span>
                                        <span class="prn-pill">{row_s.get("PRN", "")}</span>
                                    </div>
                                    <div class="student-title">{s_name}</div>
                                    <div style="font-size:0.72rem; color:#64748b; margin-top:2px;">{str(row_s.get("Subject", ""))[:28]}</div>
                                </div>
                                ''', unsafe_allow_html=True)

                with col_tab_s:
                    st.markdown("##### 🔍 Student Hall Pass Search")
                    if has_data:
                        search_prn = st.text_input("Search Candidate PRN or Name:", placeholder="e.g. 23140134 or Name...")
                        if search_prn.strip():
                            srch = search_prn.strip().lower()
                            name_col = next((c for c in ["Student_Name", "Name", "Student_name"] if c in df_map.columns), None)
                            if name_col:
                                mask = (
                                    df_map["PRN"].astype(str).str.lower().str.contains(srch, na=False) |
                                    df_map[name_col].astype(str).str.lower().str.contains(srch, na=False)
                                )
                                cols_show = [c for c in ["PRN", name_col, "Date", "Exam_Session", "Block_Number", "Subject"] if c in df_map.columns]
                            else:
                                mask = df_map["PRN"].astype(str).str.lower().str.contains(srch, na=False)
                                cols_show = [c for c in ["PRN", "Date", "Exam_Session", "Block_Number", "Subject"] if c in df_map.columns]
                            
                            found_df = df_map[mask]
                            st.write(f"Found {len(found_df)} record(s):")
                            st.dataframe(found_df[cols_show], hide_index=True)
                        else:
                            st.caption("Enter a PRN or student name to look up their assigned hall and block.")

            st.markdown("<hr style='margin: 24px 0;'/>", unsafe_allow_html=True)
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("⬅️ Back to Step 2: Configure Another Exam", width="stretch"):
                    st.session_state["active_step"] = 2
                    st.rerun()
            with col_b2:
                if st.button("🔄 Back to Step 1: Upload New Student CSV", width="stretch"):
                    st.session_state["active_step"] = 1
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
