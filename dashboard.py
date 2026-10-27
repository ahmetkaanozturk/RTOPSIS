import sys
import html
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Proje kök dizinini ekle
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.rcz_topsis.core import RCZTOPSIS
from src.rcz_topsis.types import (
    AlternativeStatus,
    Context,
    CritType,
    RCZConfig,
    RCZExplanation,
)
from src.rcz_topsis.mcdm_comparisons import (
    run_classic_topsis,
    run_mean_imputation_topsis,
    run_vikor,
    run_promethee_ii,
    run_saw,
    MCDM_METHOD_DOSSIERS,
)
from src.rcz_topsis.schema import (
    CriterionDef,
    AlternativeDef,
    DecisionDataset,
    IntegrityReceipt,
    ProfileType,
    hash_config,
)
from src.rcz_topsis.profiles.tender import (
    TenderProfile,
    TenderCommissionAuth,
)
from src.rcz_topsis.profiles.military_advisory import (
    MilitaryAdvisoryProfile,
    AUTONOMOUS_ENGAGEMENT_ALLOWED,
)
from src.rcz_topsis.system_catalog import render_system_overview_page, get_faq_items
from src.rcz_topsis.landing_page import render_landing_intro_page
from src.rcz_topsis.glossary import render_glossary_component, get_glossary_terms
from src.rcz_topsis.external_data import SOURCE_SPECS


def safe_text(s: object) -> str:
    """XSS ve HTML enjeksiyonlarına karşı dinamik metinleri sanitize eder."""
    return html.escape(str(s))


st.set_page_config(
    page_title="R-CZ-TOPSIS: Eksik Verili Çok Kriterli Karar Verme Araştırma Prototipi",
    page_icon="🛡️",
    layout="wide",
)

# Kullanıcı tercihi oturum boyunca korunur; tema değişimi Streamlit'in doğal
# yeniden çizim davranışıyla tüm sayfaya uygulanır.
dark_mode = st.sidebar.toggle(
    "🌙 Gece modu",
    value=st.session_state.get("dark_mode", False),
    key="dark_mode",
    help="Düşük ışıklı ortamlarda daha rahat okuma için koyu arayüzü etkinleştirir.",
)

# ==============================================================================
# MODERN PREMIUM UI/UX TEMA & ÖZEL STİL KATMANI (SAAS & RESEARH LAB DİZAYNI)
# ==============================================================================
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    :root {
        --rcz-ink: #0f172a;
        --rcz-muted: #64748b;
        --rcz-line: #e2e8f0;
        --rcz-blue: #2563eb;
        --rcz-blue-dark: #1e3a8a;
        --rcz-surface: #ffffff;
        --rcz-soft: #f8fafc;
    }

    body {
        background: #f8fafc;
    }

    /* Streamlit canvas: subtle app-shell hierarchy without hiding native controls */
    .stApp {
        background:
            radial-gradient(circle at 88% 0%, rgba(219, 234, 254, 0.55), transparent 28rem),
            #f8fafc;
        color: var(--rcz-ink);
    }
    
    /* Modern Arka Plan Vurgusu */
    .main .block-container {
        padding-top: 1.35rem;
        padding-bottom: 3.5rem;
        max-width: 1480px;
    }

    .main h1, .main h2, .main h3, .main h4 {
        color: var(--rcz-ink);
        letter-spacing: -0.025em;
    }

    .main h2 {
        margin-top: 1.25rem;
        margin-bottom: 0.65rem;
    }

    .main h3 {
        margin-top: 1rem;
        margin-bottom: 0.55rem;
    }

    .main p, .main li {
        color: #334155;
        line-height: 1.58;
    }

    /* Consistent separators keep long analytical pages scannable */
    hr {
        border: 0 !important;
        border-top: 1px solid var(--rcz-line) !important;
        margin: 1.15rem 0 !important;
    }
    
    /* Hero Header Banner (Dengeli ve Kompakt) */
    .hero-banner {
        background:
            radial-gradient(circle at 92% 10%, rgba(96, 165, 250, 0.25), transparent 18rem),
            linear-gradient(135deg, #0b1329 0%, #111e38 52%, #1e40af 100%);
        border: 1px solid rgba(147, 197, 253, 0.25);
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 12px 30px -16px rgba(15, 23, 42, 0.65);
        position: relative;
        overflow: hidden;
        color: #ffffff;
    }
    .hero-title {
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #ffffff;
    }
    .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.74rem;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 6px;
        background: rgba(255, 255, 255, 0.09);
        border: 1px solid rgba(255, 255, 255, 0.16);
        color: #e0f2fe;
    }

    .hero-banner::after {
        content: "";
        position: absolute;
        right: -5rem;
        bottom: -6rem;
        width: 16rem;
        height: 16rem;
        border: 1px solid rgba(191, 219, 254, 0.22);
        border-radius: 50%;
        box-shadow: 0 0 0 1.2rem rgba(191, 219, 254, 0.06), 0 0 0 2.4rem rgba(191, 219, 254, 0.04);
        pointer-events: none;
    }
    .hero-badge-gold {
        background: rgba(245, 158, 11, 0.18);
        border-color: rgba(245, 158, 11, 0.4);
        color: #fde68a;
    }
    
    /* Modern KPI Metrik Kartları */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 13px 15px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.74rem !important;
        font-weight: 700 !important;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.42rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        line-height: 1.25 !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.76rem !important;
        font-weight: 600 !important;
    }

    /* Native containers become quiet, elevated analytical cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--rcz-line) !important;
        border-radius: 12px !important;
        box-shadow: 0 5px 16px -14px rgba(15, 23, 42, 0.55);
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--rcz-line) !important;
        border-radius: 11px !important;
        background: rgba(255, 255, 255, 0.74);
        overflow: hidden;
    }

    [data-testid="stExpander"] summary {
        font-weight: 700;
        color: var(--rcz-ink);
    }

    /* Tabs are used for dense mathematics and profile detail views */
    [data-baseweb="tab-list"] {
        gap: 0.35rem;
        border-bottom: 1px solid var(--rcz-line);
    }

    [data-baseweb="tab"] {
        color: var(--rcz-muted);
        font-weight: 650;
        padding: 0.65rem 0.9rem;
        border-radius: 8px 8px 0 0;
    }

    [aria-selected="true"][data-baseweb="tab"] {
        color: var(--rcz-blue-dark);
        background: #eff6ff;
    }

    /* Tables: more readable headers and compact numeric rows */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--rcz-line);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 14px -14px rgba(15, 23, 42, 0.55);
    }

    [data-testid="stDataFrame"] canvas {
        outline: none;
    }

    /* Markdown tabloları: hücreler arasında net görsel sınırlar */
    .rcz-comparison-wrap {
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        overflow-x: auto;
        background: #ffffff;
        box-shadow: 0 5px 16px -14px rgba(15, 23, 42, 0.6);
        margin: 0.65rem 0 1rem;
    }

    table.rcz-comparison {
        width: 100%;
        min-width: 780px;
        border-collapse: separate;
        border-spacing: 0;
        color: #334155;
        font-size: 0.88rem;
    }

    table.rcz-comparison th {
        background: linear-gradient(135deg, #172554, #1d4ed8);
        color: #ffffff;
        text-align: left;
        font-size: 0.78rem;
        letter-spacing: 0.02em;
        padding: 12px 13px;
        border-right: 1px solid rgba(255,255,255,0.22);
        vertical-align: top;
    }

    table.rcz-comparison td {
        padding: 12px 13px;
        line-height: 1.5;
        vertical-align: top;
        border-top: 2px solid #cbd5e1;
        border-right: 2px solid #cbd5e1;
        border-bottom: 0;
    }

    table.rcz-comparison th:last-child,
    table.rcz-comparison td:last-child {
        border-right: 0;
    }

    table.rcz-comparison tbody tr:nth-child(even) td {
        background: #f8fafc;
    }

    table.rcz-comparison tbody tr:hover td {
        background: #eff6ff;
    }

    table.rcz-comparison td:first-child {
        width: 18%;
        color: #1e3a8a;
        font-weight: 750;
        background: #f1f5f9;
        box-shadow: inset -1px 0 0 #94a3b8;
    }

    /* Buttons and download actions share one visual language */
    .stButton > button, .stDownloadButton > button {
        border-radius: 8px;
        border: 1px solid #bfdbfe;
        font-weight: 700;
        transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 12px -7px rgba(37, 99, 235, 0.7);
        border-color: #60a5fa;
    }

    .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
        color: #ffffff;
    }

    /* Alerts should read as status blocks, not floating text */
    [data-testid="stAlert"] {
        border-radius: 10px;
        border-left-width: 4px;
        box-shadow: 0 4px 12px -12px rgba(15, 23, 42, 0.6);
    }

    /* Streamlit üst çubuğu temayla bütünleşsin; içerik alanını örtmesin. */
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stToolbar"] {
        background: rgba(248, 250, 252, 0.86);
        border-radius: 0 0 0 10px;
        padding: 0.2rem 0.35rem;
    }

    /* Uzun başlıklar, formüller ve kart metinleri dar alanlarda taşmasın. */
    .main h1, .main h2, .main h3, .main h4,
    .main p, .main li, .main code,
    .rcz-card-title, .rcz-card-subtitle, .rcz-card-body {
        overflow-wrap: anywhere;
        word-break: normal;
    }

    .main [data-testid="stHorizontalBlock"] {
        align-items: stretch;
        gap: 1rem;
    }

    .main [data-testid="stColumn"] {
        min-width: 0;
    }

    .main [data-testid="stPlotlyChart"] {
        width: 100%;
        overflow: hidden;
        border-radius: 10px;
    }

    /* Kartların sabit minimum yüksekliği içerik uzunluğunda çakışma üretmesin. */
    .rcz-card {
        min-height: 0;
        height: auto;
    }

    @media (max-width: 900px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-title {
            display: block;
            line-height: 1.25;
        }

        .hero-title span + span {
            display: block;
            margin: 6px 0 0 !important;
            font-size: 0.82rem !important;
        }

        .main h2 {
            font-size: 1.35rem;
        }

        .main h3 {
            font-size: 1.12rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.12rem !important;
        }

        .rcz-card {
            padding: 13px;
        }

        .rcz-comparison-wrap {
            -webkit-overflow-scrolling: touch;
        }
    }

    @media (max-width: 640px) {
        .main .block-container {
            padding-top: 0.9rem;
            padding-left: 0.7rem;
            padding-right: 0.7rem;
        }

        .hero-banner {
            padding: 15px;
            border-radius: 12px;
        }

        .hero-badge {
            font-size: 0.68rem;
            padding: 4px 7px;
        }

        .main [data-testid="stHorizontalBlock"] {
            gap: 0.55rem;
        }

        section[data-testid="stSidebar"] .block-container {
            padding-left: 0.55rem !important;
            padding-right: 0.55rem !important;
        }

        .sidebar-brand-subtitle {
            font-size: 0.64rem;
        }
    }
    
    /* Şampiyonluk Kürsüsü Kartları (Dengeli Yükseklik & Orantılı Yazı) */
    .podium-gold {
        background: linear-gradient(145deg, #fffbeb 0%, #fef3c7 60%, #fde68a 100%);
        border: 1.5px solid #f59e0b;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);
        color: #78350f;
    }
    .podium-silver {
        background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 60%, #e2e8f0 100%);
        border: 1.5px solid #94a3b8;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 4px 12px rgba(148, 163, 184, 0.15);
        color: #334155;
    }
    .podium-bronze {
        background: linear-gradient(145deg, #fff7ed 0%, #ffedd5 60%, #fed7aa 100%);
        border: 1.5px solid #f97316;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.15);
        color: #7c2d12;
    }
    
    /* Pratik Durum ve Doktrin Kartları (Kompakt ve Orantılı) */
    .real-life-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 13px 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        border-left: 4px solid #2563eb;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .real-life-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px -2px rgba(0, 0, 0, 0.06);
    }

    /* Standart RCZ Kartları - Hem Light Hem Dark Mod Uyumlu */
    .rcz-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        color: #0f172a;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 290px;
        height: 100%;
        box-sizing: border-box;
    }
    .rcz-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px -2px rgba(0, 0, 0, 0.08);
    }
    .rcz-card-title {
        color: #0f172a;
        font-weight: 750;
        font-size: 0.96rem;
        margin-top: 0;
        margin-bottom: 4px;
        line-height: 1.3;
    }
    .rcz-card-subtitle {
        color: #2563eb;
        font-weight: 600;
        font-size: 0.78rem;
        margin-bottom: 8px;
    }
    .rcz-card-body {
        color: #334155;
        font-size: 0.82rem;
        line-height: 1.45;
    }

    /* Sözlük Kartları */
    .rcz-glossary-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
        color: #0f172a;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .rcz-glossary-badge {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid #bae6fd;
    }
    .rcz-glossary-summary {
        background: #eff6ff;
        border-left: 3px solid #2563eb;
        padding: 8px 10px;
        border-radius: 6px;
        font-size: 0.84rem;
        color: #1e3a8a;
        margin-bottom: 10px;
        line-height: 1.45;
    }
    .rcz-glossary-body {
        color: #334155;
        font-size: 0.84rem;
        line-height: 1.5;
        white-space: pre-line;
    }

    /* Renkli Durum Blokları */
    .rcz-card-danger {
        background: #fff5f5;
        border: 1.5px solid #fecaca;
        border-radius: 10px;
        padding: 14px 16px;
        color: #7f1d1d;
    }
    .rcz-card-success {
        background: #f0fdf4;
        border: 1.5px solid #bbf7d0;
        border-radius: 10px;
        padding: 14px 16px;
        color: #14532d;
    }
    .rcz-card-warning {
        background: #fffbeb;
        border: 1.5px solid #fde68a;
        border-radius: 10px;
        padding: 14px 16px;
        color: #78350f;
    }
    .rcz-card-info {
        background: #f0f9ff;
        border: 1.5px solid #bae6fd;
        border-radius: 10px;
        padding: 14px 16px;
        color: #0c4a6e;
    }
    
    /* Kod ve Formül Vurgusu */
    code {
        font-family: "Cascadia Code", "Fira Code", "Consolas", "Courier New", monospace !important;
        background-color: rgba(241, 245, 249, 0.9) !important;
        padding: 2px 5px !important;
        border-radius: 4px !important;
        color: #0f172a !important;
        font-size: 0.86em !important;
    }
    
    /* Sidebar Genel Tasarım & Yüksek Kontrast */
    section[data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, #eef4fb 0%, #f8fafc 45%, #eef2f7 100%) !important;
        border-right: 2px solid #cbd5e1 !important;
        box-shadow: 5px 0 18px -18px rgba(15, 23, 42, 0.6);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.15rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 11px 12px;
        margin: 0 0 12px;
        border-bottom: 1px solid #cbd5e1;
    }

    .sidebar-brand-mark {
        display: grid;
        place-items: center;
        width: 34px;
        height: 34px;
        border-radius: 10px;
        color: #ffffff;
        background: linear-gradient(135deg, #1d4ed8, #0f172a);
        box-shadow: 0 5px 12px -7px rgba(29, 78, 216, 0.8);
        font-size: 1.1rem;
    }

    .sidebar-brand-title {
        color: #0f172a;
        font-size: 0.9rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        line-height: 1.15;
    }

    .sidebar-brand-subtitle {
        color: #64748b;
        font-size: 0.68rem;
        margin-top: 3px;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] label {
        color: #1e293b !important;
    }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #0f172a !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stTextInput,
    section[data-testid="stSidebar"] .stNumberInput,
    section[data-testid="stSidebar"] .stSlider {
        margin-bottom: 0.25rem;
    }
    
    /* Hızlı Geçiş Navigasyon Başlığı */
    .nav-header {
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #1e40af;
        background: #dbeafe;
        padding: 5px 9px;
        border-radius: 7px;
        margin: 10px 0 7px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Radio Seçeneklerini Modern Navigasyon Butonlarına Çevirme */
    section[data-testid="stSidebar"] [data-testid="stRadio"] {
        margin-top: -4px;
        margin-bottom: 8px;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: 4px !important;
        display: flex !important;
        flex-direction: column !important;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 9px !important;
        padding: 7px 9px !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: #e2e8f0 !important;
        border-color: #94a3b8 !important;
        transform: translateX(2px) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label input {
        width: 14px !important;
        height: 14px !important;
        accent-color: #2563eb !important;
        margin-right: 8px !important;
        flex: 0 0 auto !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 0.78rem !important;
        line-height: 1.25 !important;
        letter-spacing: -0.005em;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        position: relative;
        transform: translateX(2px) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked)::after {
        content: "✓";
        position: absolute;
        right: 9px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 0.76rem;
        font-weight: 900;
        color: #bfdbfe;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
        border-color: #1e40af !important;
        box-shadow: 0 3px 8px rgba(37, 99, 235, 0.28) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) * {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:not(:has(input:checked)) * {
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    </style>
    
    <div class="hero-banner">
        <div class="hero-title">
            <span>🛡️ R-CZ-TOPSIS</span>
            <span style="font-size: 0.95rem; font-weight: 600; opacity: 0.85; margin-left: 6px;">Yüksek Güvenceye Hazırlanmış Kurumsal Karar Destek Prototipi</span>
        </div>
        <div style="font-size: 0.86rem; margin-top: 5px; opacity: 0.9; max-width: 900px; line-height: 1.4;">
            Contextual Zero Algebra (CZ-Algebra) Temelli • Eksik Veri Altında Alt-Uzay ve Asimetrik Epistemik Güvenilirlik Modeli • Air-Gapped Korumalı
        </div>
        <div class="hero-badges">
            <span class="hero-badge hero-badge-gold">🎓 TÜBİTAK 2209-A Araştırma Çerçevesi</span>
            <span class="hero-badge">🔒 Air-Gapped & Sıfır Harici Ağ Bağımlılığı</span>
            <span class="hero-badge">📐 Imputation-Free Alt-Uzay</span>
            <span class="hero-badge">⚖️ Asimetrik Epistemik Ceza (Γ_i)</span>
            <span class="hero-badge">🚪 Hard Gatekeeper Eşiği</span>
            <span class="hero-badge">📜 Değiştirilemez Hash Makbuzu & Denetim</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if dark_mode:
    st.markdown(
        """
        <style>
        :root {
            --rcz-ink: #e5e7eb;
            --rcz-muted: #94a3b8;
            --rcz-line: #334155;
            --rcz-blue: #60a5fa;
            --rcz-blue-dark: #bfdbfe;
            --rcz-surface: #111827;
            --rcz-soft: #0f172a;
        }

        html, body, .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main,
        section.main,
        section[data-testid="stMain"] {
            background: #0b1120 !important;
            color: #e5e7eb !important;
        }

        .main,
        .main .block-container,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main {
            background: transparent !important;
        }

        .main h1, .main h2, .main h3, .main h4,
        .main p, .main li, .main label,
        [data-testid="stMarkdownContainer"] {
            color: #e5e7eb !important;
        }

        .main p, .main li {
            color: #cbd5e1 !important;
        }

        section[data-testid="stSidebar"],
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111827 0%, #0f172a 100%) !important;
            border-right-color: #334155 !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #e5e7eb !important;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label,
        section[data-testid="stSidebar"] [data-testid="stCheckbox"],
        section[data-testid="stSidebar"] [data-testid="stToggle"] {
            background: #1e293b !important;
            border-color: #475569 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:not(:has(input:checked)) * {
            color: #e2e8f0 !important;
        }

        .sidebar-brand {
            border-bottom-color: #334155;
        }

        .sidebar-brand-title {
            color: #f8fafc;
        }

        .sidebar-brand-subtitle {
            color: #94a3b8;
        }

        section[data-testid="stSidebar"] .nav-header {
            color: #bfdbfe !important;
            background: #1e3a8a !important;
        }

        [data-testid="stMetric"],
        [data-testid="stMetric"] > div,
        [data-testid="stExpander"],
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #111827 !important;
            border-color: #334155 !important;
            color: #e5e7eb !important;
        }

        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {
            color: #e5e7eb !important;
        }

        [data-testid="stDataFrame"] {
            border-color: #475569 !important;
            background: #111827 !important;
        }

        [data-testid="stDataFrame"] > div {
            background: #111827 !important;
        }

        [data-testid="stHeader"] {
            background: rgba(11, 17, 32, 0.92) !important;
        }

        [data-testid="stToolbar"] {
            background: rgba(15, 23, 42, 0.92) !important;
        }

        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div,
        section[data-testid="stSidebar"] input:not([type="radio"]):not([type="checkbox"]),
        section[data-testid="stSidebar"] textarea {
            background: #1e293b !important;
            color: #e5e7eb !important;
            border-color: #475569 !important;
        }

        [data-baseweb="select"] *,
        [data-baseweb="input"] *,
        [data-baseweb="textarea"] * {
            color: #e5e7eb !important;
        }

        [data-baseweb="popover"] {
            background: #111827 !important;
            border-color: #475569 !important;
        }

        [data-testid="stAlert"] {
            filter: brightness(0.82) saturate(1.05);
        }

        .rcz-comparison-wrap {
            background: #111827 !important;
            border-color: #475569 !important;
        }

        table.rcz-comparison {
            color: #cbd5e1 !important;
        }

        table.rcz-comparison td {
            border-color: #64748b !important;
            background: #111827 !important;
            box-shadow: inset -1px 0 0 #475569;
        }

        table.rcz-comparison td:first-child,
        table.rcz-comparison tbody tr:nth-child(even) td {
            background: #1e293b !important;
        }

        table.rcz-comparison tbody tr:hover td {
            background: #243b63 !important;
        }

        table.rcz-comparison td:first-child {
            color: #bfdbfe !important;
            background: #1e293b !important;
            box-shadow: inset -2px 0 0 #60a5fa;
        }

        /* Koyu Mod: Kartlar ve Tüm Bilgi Kutuları İçin Yüksek Kontrast */
        .rcz-card,
        .rcz-glossary-card,
        .real-life-card,
        section.main div[style*="background: #ffffff"],
        section.main div[style*="background: linear-gradient(145deg, #ffffff"],
        section.main div[style*="background: #f8fafc"],
        section.main div[style*="background: #f1f5f9"],
        section.main div[style*="background: #eff6ff"],
        section.main div[style*="background: #fef2f2"],
        section.main div[style*="background: #fffbeb"],
        section.main div[style*="background: #dbeafe"],
        section.main div[style*="background: #ecfdf5"],
        section.main div[style*="background: #eef2ff"],
        section.main div[style*="background: linear-gradient(135deg, #eff6ff"],
        section.main div[style*="background: linear-gradient(145deg, #fffbeb"],
        section.main div[style*="background: linear-gradient(145deg, #f8fafc"],
        section.main div[style*="background: linear-gradient(145deg, #fff7ed"] {
            background: #1e293b !important;
            border-color: #334155 !important;
            color: #f8fafc !important;
        }

        /* Başlıklar ve metinler koyu modda kristal netliğinde */
        .rcz-card-title,
        .rcz-card strong,
        .rcz-glossary-card strong,
        .real-life-card h4,
        section.main div[style*="background:"] h1,
        section.main div[style*="background:"] h2,
        section.main div[style*="background:"] h3,
        section.main div[style*="background:"] h4,
        section.main div[style*="background:"] h5 {
            color: #f8fafc !important;
        }

        .rcz-card-subtitle {
            color: #93c5fd !important;
        }

        .rcz-card-body,
        .rcz-glossary-body,
        .real-life-card p,
        .real-life-card li,
        section.main div[style*="background:"] p,
        section.main div[style*="background:"] li,
        section.main div[style*="background:"] span {
            color: #e2e8f0 !important;
        }

        .rcz-glossary-badge {
            background: #0f172a !important;
            color: #60a5fa !important;
            border-color: #1e3a8a !important;
        }

        .rcz-glossary-summary {
            background: #0f172a !important;
            border-left-color: #3b82f6 !important;
            color: #bfdbfe !important;
        }
        .rcz-glossary-summary strong {
            color: #60a5fa !important;
        }

        /* Durum kutularının koyu mod tonları */
        .rcz-card-danger,
        section.main div[style*="background: #fef2f2"],
        section.main div[style*="background: #fff5f5"] {
            background: rgba(127, 29, 29, 0.35) !important;
            border-color: #991b1b !important;
            color: #fca5a5 !important;
        }
        .rcz-card-danger *,
        section.main div[style*="background: #fef2f2"] * {
            color: #fca5a5 !important;
        }

        .rcz-card-success,
        section.main div[style*="background: #ecfdf5"],
        section.main div[style*="background: #f0fdf4"] {
            background: rgba(6, 95, 70, 0.35) !important;
            border-color: #065f46 !important;
            color: #86efac !important;
        }
        .rcz-card-success *,
        section.main div[style*="background: #ecfdf5"] * {
            color: #86efac !important;
        }

        .rcz-card-warning,
        section.main div[style*="background: #fffbeb"] {
            background: rgba(120, 53, 15, 0.35) !important;
            border-color: #92400e !important;
            color: #fde68a !important;
        }
        .rcz-card-warning *,
        section.main div[style*="background: #fffbeb"] * {
            color: #fde68a !important;
        }

        .rcz-card-info,
        section.main div[style*="background: #eff6ff"],
        section.main div[style*="background: #f0f9ff"],
        section.main div[style*="background: #dbeafe"] {
            background: rgba(30, 58, 138, 0.35) !important;
            border-color: #1e40af !important;
            color: #bfdbfe !important;
        }
        .rcz-card-info *,
        section.main div[style*="background: #eff6ff"] *,
        section.main div[style*="background: #dbeafe"] * {
            color: #bfdbfe !important;
        }

        code {
            background: #1e293b !important;
            color: #bfdbfe !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# SOL MENÜ: DİKEY KATEGORİ VE MODÜL SEÇİCİ (ALT ALTA & ANINDA ERİŞİM)
# ==============================================================================
st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="sidebar-brand-mark">🛡️</div>
        <div>
            <div class="sidebar-brand-title">R-CZ-TOPSIS</div>
            <div class="sidebar-brand-subtitle">Karar destek çalışma alanı</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown('<div class="nav-header">🧭 ÇALIŞMA ALANI</div>', unsafe_allow_html=True)

nav_options = [
    "🏠 0  Tanıtım & Giriş",
    "🧭 0  Genel Bakış",
    "🏆 1  Karar Paneli",
    "🚁 2  İHA / SİHA Doktrini",
    "🎯 3  Hava Savunma C2",
    "🎛️ 4  What-If Laboratuvarı",
    "💡 5  Sistem Rehberi",
    "🔬 6  Matematik Detayları",
    "🚗 7  Veri Kütüphanesi",
    "⚖️ 8  MCDM Karşılaştırması",
    "📚 9  Makale & Kaynakça",
]

# Butonlardan gelen sayfa yönlendirmesi desteği
if "pending_nav" in st.session_state:
    st.session_state["nav_selection"] = st.session_state.pop("pending_nav")

if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = "🏠 0  Tanıtım & Giriş"

try:
    nav_index = nav_options.index(st.session_state["nav_selection"])
except ValueError:
    nav_index = 0

nav_mode = st.sidebar.radio(
    "Navigasyon",
    nav_options,
    index=nav_index,
    key="nav_radio_selector",
    label_visibility="collapsed",
)
st.session_state["nav_selection"] = nav_mode
st.sidebar.markdown("---")

# ==============================================================================
# YAN MENÜ: KURUMSAL ÜRÜN PROFİLİ SEÇİCİ
# ==============================================================================
st.sidebar.markdown('<div class="nav-header">🛡️ ÜRÜN PROFİLİ</div>', unsafe_allow_html=True)
product_profile_mode = st.sidebar.radio(
    "Ürün Profili Seçin:",
    [
        "🔬 1  Bilimsel Araştırma",
        "🏛️ 2  İhale & Tedarik",
        "🎯 3  Askeri Advisory C2",
    ],
    index=0,
    help="Ortak R-CZ karar motoru üzerinde çalışan kurumsal karar destek ürün profili. İhale profili iki kişili onay gerektirirken askeri profil kesin insan onayı kısıtı içerir.",
)

# Profil Yetki ve Kimlik Girdileri
tender_chair = "BASKAN-01"
tender_auditor = "DENETCI-01"
tender_code = "IHAL-2026/04"
tactical_operator = "OPERATOR-C2-01"
tactical_mission = "TASK-AIR-SHIELD"

if "İhale" in product_profile_mode:
    st.sidebar.caption("📋 **İhale Komisyonu Yetkilendirmesi (İki Kişili Onay):**")
    tender_chair = st.sidebar.text_input("Komisyon Başkanı Kimliği:", value="BASKAN-01", key="chair_id")
    tender_auditor = st.sidebar.text_input("Mali Denetçi / Üye Kimliği:", value="DENETCI-01", key="auditor_id")
    tender_code = st.sidebar.text_input("İhale Dosya Numarası:", value="IHAL-2026/04", key="tender_code")
elif "Askeri" in product_profile_mode:
    st.sidebar.caption("🎖️ **Askeri Karar Destek Harekât Yetkisi:**")
    tactical_operator = st.sidebar.text_input("Harekât Subayı Kimliği:", value="OPERATOR-C2-01", key="tac_op")
    tactical_mission = st.sidebar.text_input("Görev / Harekât Kodu:", value="TASK-AIR-SHIELD", key="tac_mis")

st.sidebar.markdown("---")

# ==============================================================================
# YAN MENÜ: SENARYO VE PARAMETRELER
# ==============================================================================
st.sidebar.header("📂 1. Karar Senaryosu Seçin")
data_source = st.sidebar.selectbox(
    "Uygulama Alanı:",
    [
        "🏛️ UCI Resmi Akademik Benchmark: 1985 Automobile Eksik Veri Stres Testi (25 Araç)",
        "🎯 Askeri Radar: Hava Savunma Tehdit Değerlendirme & Önceliklendirme (TEWA)",
        "🌐 Jeopolitik Erken Uyarı: Sınır İntikali & Saldırı/Çatışma Olasılığı Analizi",
        "⚡ Otomotiv: Elektrikli Araç (EV 2026) Kıyaslama Benchmarkı",
        "✈️ Savunma: Taktik & MALE İnsansız Hava Aracı (İHA) Seçimi",
        "🏭 Endüstri: Şirket Tedarikçi Değerlendirme ve Denetimi",
        "🚀 Girişim Sermayesi: Erken & Büyüme Aşaması Startup Yatırım Seçimi",
        "🏥 Biyoteknoloji: Klinik Onkoloji Tedavi & İlaç Adayı Kıyaslaması",
        "🌱 Temiz Enerji: Yenilenebilir Enerji Santrali Saha Yatırımı",
        "🇪🇺 TED Open Data: Prosedür Kapsamı Karşılaştırması (100 Resmi Duyuru)",
        "🚀 NASA C-MAPSS: Motor Sağlık Göstergeleri (100 Test Motoru)",
        "📱 Makale: 5 Akıllı Telefon Referans Senaryosu",
        "📤 Kendi CSV Dosyanı Yükle",
    ],
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 2. Güvenlik ve Eşik Ayarları")
risk_level = st.sidebar.select_slider(
    "Eksik Bilgiye Karşı Riskten Kaçınma Derecesi (α):",
    options=["Cezasız (α = 0.0)", "Dengeli / Standart (α = 0.50)", "Temkinli (α = 0.80)", "Katı (α = 1.20)"],
    value="Dengeli / Standart (α = 0.50)",
    help="Bilgisi eksik olan alternatiflere uygulanacak epistemik güvenilirlik cezasının şiddeti.",
)

alpha_map = {
    "Cezasız (α = 0.0)": 0.0,
    "Dengeli / Standart (α = 0.50)": 0.50,
    "Temkinli (α = 0.80)": 0.80,
    "Katı (α = 1.20)": 1.20,
}
alpha = alpha_map[risk_level]

w_threshold = st.sidebar.slider(
    "Hard Gatekeeper: Asgari Bilgi Eşiği (W_threshold):",
    min_value=0.20,
    max_value=0.80,
    value=0.50,
    step=0.05,
    help="Kural 1: Toplam bilgi ağırlığı bu oranın altında kalan alternatifler doğrudan elenir.",
)

min_active_criteria = st.sidebar.number_input(
    "Hard Gatekeeper: Asgari Kriter Sayısı (m_min):",
    min_value=1,
    max_value=5,
    value=2,
    step=1,
    help="Kural 1: En az kaç kriterin ölçülmüş olması gerekir?",
)

with st.sidebar.expander("ℹ️ Güvenlik Ayarları Neyi Değiştirir?", expanded=False):
    st.markdown(
        """
        * **Riskten Kaçınma Derecesi (α):**
          Eksik verili adayların nihai skoruna uygulanacak epistemik indirimin şiddetini belirler:
          $$\\Gamma_i = (W_i)^{\\alpha \\cdot (1 + \\kappa_i)}$$
          * **α = 0.0 (Cezasız):** Eksik bilgiye ceza kesilmez. Yalnızca bilinen kriterlerdeki ham alt-uzay skoru alınır.
          * **α = 0.50 (Dengeli - Standart):** Bilgi azaldıkça skoru karekök oranında törpüler; bilinen kriterleri güçlüyse adayı korur.
          * **α = 0.80 (Temkinli):** Eksik verili adayı daha sert cezalandırır; tam verili adayları öne çıkarır.
          * **α = 1.20 (Katı):** En ufak bir kriter eksikliğinde dahi adayın puanını dikkate değer biçimde düşürür.
        * **Asgari Bilgi Eşiği ($W_{\\text{threshold}}$):**
          Adayın bilinen kriter ağırlıkları toplamı bu oranın altındaysa (Örn: < %50) aday **anında elenir**. Tek bir gürültülü yankıya füze atılmasını veya ihalede 1 kriteri bilinen şüpheli firmanın kazanmasını engeller.
        * **Asgari Kriter Sayısı ($m_{\\text{min}}$):**
          Adayın karar matrisinde en az kaç bağımsız kriterde geçerli ölçüme sahip olması gerektiğini şart koşar.
        """
    )

with st.sidebar.expander("🛠️ Gelişmiş Model Tercihleri", expanded=False):
    local_reweighting = st.checkbox(
        "v1.0 Yerel Ağırlıklandırma (w'_ij = w_j / W_i)",
        value=False,
        help="v1.0 deneysel yerel ağırlıklandırmasını açar. Varsayılan (v1.1) modelde eksik veri puan şişirmesini önlemek için global alt-uzay ağırlıkları kullanılır.",
    )
    st.markdown(
        """
        **Bu Tercih Nedir ve Neyi Değiştirir?**
        * **v1.1 Global Alt-Uzay İzdüşümü (Varsayılan / Tavsiye Edilen):**
          Her adayın ölçülen kriterleri, orijinal global ağırlıklarla ($V_{ij} = w_j \\cdot r_{ij}$) alt-uzaya projekte edilir.
          Eksik kriterlerin ağırlığı suni olarak diğer kriterlere eklenmez. Böylece az kriteri ölçülen adayın koordinatlarının şişmesi (*Coordinate Inflation*) önlenir.
        * **v1.0 Dinamik Yerel Ağırlıklandırma (Kutucuk Açılırsa):**
          Adayın eksik kalan kriterlerinin ağırlığı, adayın bilinen kriterlerine orantılı olarak dağıtılır ($w'_{ij} = w_j / W_i$).
          Bu mod, yerel alt-uzayda ağırlık toplamını 1.0 yapar; ancak az kriteri bilinen adayların skorlarını yapay olarak yükseltme eğilimindedir.
        """
    )

# ==============================================================================
# VERİ HAZIRLAMA MOTORU
# ==============================================================================
alts = []
crit_names = []
crit_types = []
weights = []
raw_df = None
current_csv_bytes = b""
dataset_source_citation = ""

if "UCI" in data_source:
    csv_path = root_dir / "data" / "uci_automobile_missing_benchmark.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    # Ham teknik etiketleri (örn: TOYOTA_hatchback_Satir150) şık otomobil isimlerine dönüştür
    clean_alts = []
    for m in raw_df["Arac_Modeli"]:
        parts = str(m).split("_")
        if len(parts) >= 3:
            brand = parts[0].title()
            body = parts[1].title()
            row_id = parts[2].replace("Satir", "No:")
            clean_alts.append(f"{brand} {body} ({row_id})")
        else:
            clean_alts.append(str(m).replace("_", " "))
    alts = clean_alts
    crit_names = [
        "Motor Gücü (HP ↑)", "Şehir İçi MPG (↑)", "Otoyol MPG (↑)", 
        "Motor Hacmi (cc ↑)", "Fiyat ($ ↓)", "Boş Ağırlık (Lbs ↓)", "Sigorta Risk Kaybı (↓)"
    ]
    crit_types = [
        CritType.BENEFIT, CritType.BENEFIT, CritType.BENEFIT, CritType.BENEFIT,
        CritType.COST, CritType.COST, CritType.COST
    ]
    weights = np.array([0.20, 0.15, 0.15, 0.10, 0.20, 0.10, 0.10])
    weights = weights / np.sum(weights)
    raw_df = raw_df.drop(columns=["Arac_Modeli"])
    dataset_source_citation = "University of California Irvine (UCI) Machine Learning Repository: 1985 Automobile Database (Schlimmer, 1987). Eksik fiyat ve risk hücreleri içeren dünyaca ünlü resmi akademik benchmark."

elif "Radar" in data_source:
    csv_path = root_dir / "data" / "hava_savunma_radar_tehdit.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    alts = (raw_df["Hedef_Kodu"] + " (" + raw_df["Hedef_Tipi"] + ")").tolist()
    crit_names = [
        "Hız (Mach ↑)", "Vuruş Süresi (sn ↓)", "RCS İzi (m² ↓)", 
        "Açı Sapması (° ↓)", "ESM Karıştırma (dBm ↑)", "Hedef Varlık Kritikliği (↑)"
    ]
    crit_types = [
        CritType.BENEFIT, CritType.COST, CritType.COST, 
        CritType.COST, CritType.BENEFIT, CritType.BENEFIT
    ]
    weights = np.array([0.25, 0.25, 0.15, 0.15, 0.10, 0.10])
    weights = weights / np.sum(weights)
    raw_df = raw_df.drop(columns=["Hedef_Kodu", "Hedef_Tipi"])
    dataset_source_citation = "Açık kaynak savunma senaryolarından esinlenen sentetik TEWA / Hava Savunma C2 / elektronik harp modelleme verisi; operasyonel veya NATO onaylı veri seti değildir."

elif "Jeopolitik" in data_source:
    csv_path = root_dir / "data" / "jeopolitik_catisma_istihbarat.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    alts = (raw_df["Kriz_Bolgesi"] + " [" + raw_df["Aktorler"] + "]").tolist()
    crit_names = [
        "Askeri Yığınak (Tugay ↑)", "Lojistik/Mühimmat Hazırlık (↑)", "Siber Saldırı Frekansı (↑)", 
        "Diplomatik Kriz (↑)", "Propaganda/Retorik (↑)", "Ekonomik Yaptırım (↑)"
    ]
    crit_types = [
        CritType.BENEFIT, CritType.BENEFIT, CritType.BENEFIT, 
        CritType.BENEFIT, CritType.BENEFIT, CritType.BENEFIT
    ]
    weights = np.array([0.25, 0.25, 0.15, 0.15, 0.10, 0.10])
    weights = weights / np.sum(weights)
    raw_df = raw_df.drop(columns=["Kriz_Bolgesi", "Aktorler"])
    dataset_source_citation = "Stratejik İstihbarat Füzyonu & Jeopolitik Kriz Erken Uyarı Metrikleri (Açık Kaynak İstihbaratı OSINT & SIGINT/IMINT)."

elif "Otomotiv" in data_source:
    csv_path = root_dir / "data" / "elektrikli_arac_benchmark.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    alts = raw_df["Model"].tolist()
    crit_names = [
        "Menzil (km ↑)", "0-100 Hızlanma (sn ↓)", "Batarya (kWh ↑)", 
        "Fiyat (Bin TL ↓)", "Hızlı Şarj (dk ↓)", "Bagaj Hacmi (L ↑)",
        "Motor Gücü (HP ↑)", "Tüketim (kWh/100km ↓)"
    ]
    crit_types = [
        CritType.BENEFIT, CritType.COST, CritType.BENEFIT, 
        CritType.COST, CritType.COST, CritType.BENEFIT,
        CritType.BENEFIT, CritType.COST
    ]
    weights = np.array([0.20, 0.10, 0.15, 0.20, 0.10, 0.10, 0.08, 0.07])
    weights = weights / np.sum(weights)
    raw_df = raw_df.drop(columns=["Model"])
    dataset_source_citation = "EPA & WLTP Resmi Laboratuvar Test Verileri, ADAC E-Katalog 2026, Üretici Resmi Teknik Şartnameleri."

elif "Savunma" in data_source:
    csv_path = root_dir / "data" / "iha_savunma_benchmark.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    alts = raw_df["IHA_Modeli"].tolist()
    crit_names = ["Havada Kalış (Saat ↑)", "Faydalı Yük (kg ↑)", "İrtifa Tavanı (ft ↑)", "Fiyat (Milyon $ ↓)", "Menzil (km ↑)"]
    crit_types = [CritType.BENEFIT, CritType.BENEFIT, CritType.BENEFIT, CritType.COST, CritType.BENEFIT]
    weights = np.array([0.25, 0.25, 0.15, 0.20, 0.15])
    raw_df = raw_df.drop(columns=["IHA_Modeli"])
    dataset_source_citation = "Jane's All the World's Aircraft, SIPRI Askeri Envanter Bültenleri, SSB Kamuya Açık Ürün Katalogları."

elif "Tedarikçi" in data_source:
    csv_path = root_dir / "data" / "tedarikci_secimi_benchmark.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    alts = raw_df["Tedarikci"].tolist()
    crit_names = ["Kalite Oranı (% ↑)", "Birim Fiyat (TL ↓)", "Gecikme (Gün ↓)", "Finansal Güvenilirlik (↑)", "Karbon İzi (kg ↓)", "Garanti (Ay ↑)"]
    crit_types = [CritType.BENEFIT, CritType.COST, CritType.COST, CritType.BENEFIT, CritType.COST, CritType.BENEFIT]
    weights = np.array([0.25, 0.25, 0.15, 0.15, 0.10, 0.10])
    raw_df = raw_df.drop(columns=["Tedarikci"])
    dataset_source_citation = "ISO 9001 Kalite Güvence & ISO 14064 Sera Gazı / Karbon Denetim Raporları, CIPS Tedarik Yönetimi Standartları."

elif "Girişim" in data_source:
    csv_path = root_dir / "data" / "startuplar_girisim_sermayesi.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    alts = raw_df["Girisim_Adi"].tolist()
    crit_names = [
        "Yıllık Büyüme (% ↑)", "Müşteri Edinme CAC ($ ↓)", "Net Kar Marjı (% ↑)", 
        "Aylık Churn (% ↓)", "Patent/IP (Adet ↑)", "Takım Skoru (↑)", "Değerleme İsteği ($M ↓)"
    ]
    crit_types = [
        CritType.BENEFIT, CritType.COST, CritType.BENEFIT, 
        CritType.COST, CritType.BENEFIT, CritType.BENEFIT, CritType.COST
    ]
    weights = np.array([0.20, 0.15, 0.15, 0.15, 0.10, 0.10, 0.15])
    weights = weights / np.sum(weights)
    raw_df = raw_df.drop(columns=["Girisim_Adi"])
    dataset_source_citation = "VC Due Diligence Fon Denetim Raporları, Kuluçka Merkezi Erken Aşama Büyüme ve Yatırım Metrikleri."

elif "Biyoteknoloji" in data_source:
    csv_path = root_dir / "data" / "klinik_ilac_biyoteknoloji.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    alts = raw_df["Ilac_Adayi"].tolist()
    crit_names = [
        "5 Yıllık Sağkalım (% ↑)", "Ağır Yan Etki (% ↓)", "Tedavi Kür Maliyeti (Bin $ ↓)", 
        "İyileşme Süresi (Hafta ↓)", "Biyoyararlanım (% ↑)", "Hedefe Özgünlük (↑)"
    ]
    crit_types = [
        CritType.BENEFIT, CritType.COST, CritType.COST, 
        CritType.COST, CritType.BENEFIT, CritType.BENEFIT
    ]
    weights = np.array([0.25, 0.20, 0.20, 0.15, 0.10, 0.10])
    weights = weights / np.sum(weights)
    raw_df = raw_df.drop(columns=["Ilac_Adayi"])
    dataset_source_citation = "FDA / EMA Klinik Faz-2/Faz-3 Onkoloji Raporları, PubMed Medikal Araştırma Veri Tabanı."

elif "Temiz Enerji" in data_source:
    csv_path = root_dir / "data" / "yenilenebilir_enerji_santrali.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    alts = raw_df["Saha_Adi"].tolist()
    crit_names = [
        "Yıllık Üretim (GWh ↑)", "LCOE Elektrik Maliyeti ($/MWh ↓)", "Şebeke Altyapı Maliyeti (Milyon TL ↓)", 
        "Kapasite Faktörü (% ↑)", "Karbon Tasarrufu (Bin Ton ↑)", "Kurulum Süresi (Ay ↓)"
    ]
    crit_types = [
        CritType.BENEFIT, CritType.COST, CritType.COST, 
        CritType.BENEFIT, CritType.BENEFIT, CritType.COST
    ]
    weights = np.array([0.25, 0.20, 0.20, 0.15, 0.10, 0.10])
    weights = weights / np.sum(weights)
    raw_df = raw_df.drop(columns=["Saha_Adi"])
    dataset_source_citation = "TEİAŞ Trafo Kapasite Tahsis Raporları, EPDK Santral Üretim Lisansları, IRENA Yenilenebilir Maliyet Benchmarkı."

elif "TED Open Data" in data_source:
    csv_path = root_dir / "data" / "ted_sample.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    grouped = (
        raw_df.groupby("procedureType", dropna=False)
        .agg(
            notice_count=("publicationNumber", "count"),
            notice_type_diversity=("noticeType", "nunique"),
            form_type_diversity=("formType", "nunique"),
        )
        .reset_index()
    )
    alts = grouped["procedureType"].fillna("Bilinmeyen prosedür").astype(str).tolist()
    crit_names = [
        "Duyuru Sayısı (↑)",
        "Duyuru Türü Çeşitliliği (↑)",
        "Form Türü Çeşitliliği (↑)",
    ]
    crit_types = [CritType.BENEFIT, CritType.BENEFIT, CritType.BENEFIT]
    weights = np.array([0.50, 0.25, 0.25])
    raw_df = grouped.drop(columns=["procedureType"])
    dataset_source_citation = (
        "TED Open Data / Publications Office of the European Union. "
        "2024-11-06 tarihli 100 duyurudan türetilmiş prosedür kapsamı özeti; "
        "tedarikçi award sonucu veya hukuki ihale kararı değildir."
    )

elif "NASA C-MAPSS" in data_source:
    csv_path = root_dir / "data" / "nasa_cmapss_fd001_decision_matrix.csv"
    raw_df = pd.read_csv(csv_path)
    current_csv_bytes = csv_path.read_bytes()
    alts = [f"Motor {int(unit_id)}" for unit_id in raw_df["unit_id"]]
    crit_names = [
        "Gözlenen Son Çevrim (↓)",
        "Ortalama Sensör 2 (LPC Sıcaklığı) (↓)",
        "Ortalama Sensör 3 (HPC Sıcaklığı) (↓)",
        "Ortalama Sensör 4 (LPT / EGT Sıcaklığı) (↓)",
        "Ortalama Sensör 7 (HPC Çıkış Basıncı) (↑)",
        "Ortalama Sensör 11 (HPC Statik Basıncı) (↓)",
    ]
    crit_types = [
        CritType.COST,
        CritType.COST,
        CritType.COST,
        CritType.COST,
        CritType.BENEFIT,
        CritType.COST,
    ]
    weights = np.array([0.25, 0.15, 0.15, 0.15, 0.15, 0.15])
    raw_df = raw_df.drop(columns=["unit_id", "rul"])
    dataset_source_citation = (
        "NASA C-MAPSS FD001 PHM verisi; commit'i sabitlenmiş kamuya açık ayna kullanılmıştır. "
        "Termodinamik aşınma fiziğine göre gaz yolu sıcaklıkları ve toplam çevrim maliyet (COST), "
        "kompresör çıkış basıncı fayda (BENEFIT) olarak modellenmiştir. RUL bağımsız outcome olarak "
        "korunur; kriter olarak kullanılmaz. Bu ekran araştırma ve yöntem karşılaştırması içindir."
    )

elif "Makale" in data_source:
    alts = ["Ürün A", "Ürün B", "Ürün C", "Ürün D", "Ürün E"]
    crit_names = ["Hız (↑)", "Fiyat (↓)", "RAM (↑)", "Pil (↑)"]
    crit_types = [CritType.BENEFIT, CritType.COST, CritType.BENEFIT, CritType.BENEFIT]
    weights = np.array([0.25, 0.25, 0.25, 0.25])
    raw_df = pd.DataFrame([
        [8.0, 5000.0, 16.0, 10.0],
        [9.0, 7000.0, np.nan, 12.0],
        [6.0, 3000.0, 8.0, np.nan],
        [7.0, 4500.0, 32.0, 6.0],
        [10.0, 8000.0, np.nan, np.nan],
    ], columns=crit_names)
    current_csv_bytes = raw_df.to_csv(index=False).encode("utf-8")
    dataset_source_citation = "Contextual Zero Algebra (CZ-Algebra) Çalışma Taslağı Bölüm 5.3 Tablo 3 Referans Matrisi."

else:
    uploaded_file = st.sidebar.file_uploader("Kendi CSV dosyanızı yükleyin:", type=["csv"])
    if uploaded_file is None:
        st.info("👆 Lütfen sol menüden bir CSV dosyası yükleyin veya hazır senaryolardan birini seçin.")
        st.stop()
    user_df = pd.read_csv(uploaded_file)
    current_csv_bytes = uploaded_file.getvalue()
    
    if len(user_df) < 2:
        st.sidebar.error("❌ Yüklenen CSV en az 2 alternatif (satır) içermelidir.")
        st.stop()
    if len(user_df.columns) < 3:
        st.sidebar.error("❌ Yüklenen CSV en az 1 isim kolonu ve 2 kriter kolonu içermelidir.")
        st.stop()

    # Tekrarlanan alternatif adı denetimi
    raw_names = user_df.iloc[:, 0].astype(str).tolist()
    if len(raw_names) != len(set(raw_names)):
        st.sidebar.warning("⚠️ Tekrarlanan aday isimleri tespit edildi; ayırt edebilmek için sıra numarası eklendi.")
        alts = [f"{name}_{i+1}" for i, name in enumerate(raw_names)]
    else:
        alts = raw_names

    num_cols = user_df.columns[1:].tolist()
    raw_df = pd.DataFrame()
    coerced_count = 0
    for col in num_cols:
        col_s = pd.to_numeric(user_df[col].astype(str).str.replace("0_I", "NaN"), errors="coerce")
        coerced_cells = user_df[col].notna() & col_s.isna()
        coerced_count += int(coerced_cells.sum())
        raw_df[col] = col_s

    all_nan_cols = [c for c in num_cols if raw_df[c].isna().all()]
    if all_nan_cols:
        st.sidebar.error(f"❌ Şu kriter kolonlarında hiçbir sayısal değer bulunamadı: {all_nan_cols}. Lütfen CSV'nizi kontrol edin.")
        st.stop()

    if coerced_count > 0:
        st.sidebar.info(f"ℹ️ {coerced_count} adet sayısal olmayan metin hücresi eksik veri (0_I) olarak işaretlendi.")

    crit_names = num_cols

    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠️ Kriter Yönü ve Ağırlık Ayarları")
    custom_types = []
    custom_weights = []
    default_w = 1.0 / len(crit_names)
    with st.sidebar.expander("Kriterleri Özelleştir", expanded=True):
        for idx, col in enumerate(crit_names):
            c_dir = st.selectbox(
                f"{col} Yönü:",
                options=["Fayda (Benefit ↑)", "Maliyet (Cost ↓)"],
                index=0,
                key=f"crit_dir_{idx}",
            )
            custom_types.append(CritType.BENEFIT if "Fayda" in c_dir else CritType.COST)
            c_w = st.number_input(
                f"{col} Ağırlığı:",
                min_value=0.01,
                max_value=1.0,
                value=float(round(default_w, 3)),
                step=0.05,
                key=f"crit_w_{idx}",
            )
            custom_weights.append(c_w)
    crit_types = custom_types
    weights = np.array(custom_weights, dtype=np.float64)
    weights = weights / np.sum(weights)
    dataset_source_citation = "Kullanıcı Tarafından Yüklenen Özel Karar Matrisi."

n_alts = len(alts)
n_crits = len(crit_names)

X = np.zeros((n_alts, n_crits), dtype=np.float64)
Sigma = np.full((n_alts, n_crits), Context.ACTION.value, dtype=object)

for i in range(n_alts):
    for j in range(n_crits):
        val = raw_df.iloc[i, j]
        if pd.isna(val) or val == "0_I" or val == "0I":
            X[i, j] = 0.0
            Sigma[i, j] = Context.INACTION.value
        else:
            X[i, j] = float(val)
            Sigma[i, j] = Context.ACTION.value

# ==============================================================================
# ÇEKİRDEK MOTORLARIN KOŞTURULMASI
# ==============================================================================
# R-CZ-TOPSIS
config = RCZConfig(
    w_threshold=w_threshold,
    min_active_criteria=int(min_active_criteria),
    alpha=alpha,
    local_reweighting=local_reweighting,
)
rcz_engine = RCZTOPSIS(config=config)
rcz_results, rcz_expl = rcz_engine.explain(X, Sigma, weights, crit_types, names=alts)
rcz_sorted = sorted(rcz_results, key=lambda r: r.rank)
rcz_by_idx = sorted(rcz_results, key=lambda r: r.index)

# ==============================================================================
# ÇOKLU KARAR DESTEK SİSTEMLERİNİN (MCDM) TÜMÜNÜN KOŞTURULMASI
# ==============================================================================
classic_scores, classic_ranks = run_classic_topsis(X, Sigma, weights, crit_types)
mean_scores, mean_ranks = run_mean_imputation_topsis(X, Sigma, weights, crit_types)
vikor_scores, vikor_ranks = run_vikor(X, Sigma, weights, crit_types)
promethee_scores, promethee_ranks = run_promethee_ii(X, Sigma, weights, crit_types)
saw_scores, saw_ranks = run_saw(X, Sigma, weights, crit_types)

# Doğrulanmış Veri Sözleşmesi Paketi & Kriptografik Özet
crit_defs = [
    CriterionDef(
        name=crit_names[j],
        crit_type=crit_types[j],
        weight=float(weights[j]),
        is_critical_cost=(crit_types[j] == CritType.COST),
    )
    for j in range(n_crits)
]
alt_defs = [
    AlternativeDef(
        id=f"ALT-{i+1:02d}",
        name=alts[i],
        provider=alts[i],
        telemetry_age_seconds=5.0 if ("Radar" in data_source or "Savunma" in data_source) else None,
    )
    for i in range(n_alts)
]
dataset_contract = DecisionDataset(
    criteria=crit_defs,
    alternatives=alt_defs,
    X=X,
    Sigma=Sigma,
)
ds_hash = dataset_contract.compute_sha256()

# Kurumsal Profil Koşumu
tender_res = None
military_res = None

if "İhale" in product_profile_mode:
    try:
        tender_auth = TenderCommissionAuth(
            tender_id=tender_code,
            commission_chair_id=tender_chair,
            auditor_id=tender_auditor,
            approval_timestamp_utc=datetime.now(timezone.utc).isoformat(),
            session_notes="Dashboard interaktif oturumu",
        )
        tender_profile = TenderProfile()
        tender_res = tender_profile.evaluate(dataset_contract, tender_auth, config=config)
    except Exception as e:
        st.sidebar.error(f"İhale Profili Yetki Hatası: {e}")
elif "Askeri" in product_profile_mode:
    try:
        military_profile = MilitaryAdvisoryProfile()
        military_res = military_profile.evaluate(
            dataset=dataset_contract,
            operator_id=tactical_operator,
            mission_id=tactical_mission,
            max_freshness_seconds=15.0,
            config=config,
        )
    except Exception as e:
        st.sidebar.error(f"Askeri Profil Hatası: {e}")

# ==============================================================================
# MODÜL: PLATFORM TANITIM VE GİRİŞ SAYFASI (LANDING PAGE)
# ==============================================================================
if "Tanıtım" in nav_mode:
    render_landing_intro_page(st, safe_text)

# ==============================================================================
# MODÜL 0: SİSTEM GENEL BAKIŞI & PLATFORM ÖZELLİKLERİ
# ==============================================================================
if "0  Genel Bakış" in nav_mode:
    render_system_overview_page(st, safe_text)

# ==============================================================================
# MODÜL 1: KARAR PANELİ & ŞAMPİYON ANALİZİ
# ==============================================================================
if "1  Karar Paneli" in nav_mode:
    col_head1, col_head2, col_head3 = st.columns([2.5, 1, 1])
    with col_head1:
        st.subheader(f"📊 Aktif Senaryo: {data_source.split(':')[0]}")
        st.caption(f"📚 Veri Kaynağı: {dataset_source_citation}")

    # Kurumsal Karar Destek Ürün Profili Durum ve Bütünlük Başlığı
    if tender_res:
        receipt = tender_res.audit_receipt
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #064e3b 0%, #065f46 100%); color: #ecfdf5; border-radius: 10px; padding: 12px 18px; margin-bottom: 14px; border: 1px solid rgba(255,255,255,0.15);">
                <div style="font-weight: 800; font-size: 0.95rem; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                    <span>🏛️ KAMU İHALE SÜREÇLERİ İÇİN KARAR DESTEK PROTOTİPİ (4734 Uygunluk Sertifikası Değildir)</span>
                    <span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-family: monospace;">Mühür: {receipt.combined_receipt_hash[:16]}...</span>
                </div>
                <div style="font-size: 0.82rem; line-height: 1.45; opacity: 0.95;">
                    <strong>İki Kişili Onay Doğrulandı:</strong> Komisyon Başkanı: <code>{safe_text(tender_chair)}</code> | Mali Denetçi: <code>{safe_text(tender_auditor)}</code> | İhale Dosyası: <code>{safe_text(tender_code)}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if tender_res.requires_commission_inquiry:
            st.warning("⚠️ **Komisyon Savunma / Açıklama Talebi Gerekli:** Bazı tekliflerde kritik maliyet/fiyat bilgisi eksiktir. Akerlof asimetrik cezası uygulanmış olup adaya resmi yazılı savunma hakkı tanınması tavsiye edilir.")
        if tender_res.close_score_alert:
            st.info("⚖️ **Yakın Skor Eşitlik Prosedürü (Fark ≤ %2.0):** Birinci ve ikinci teklif arasındaki puan marjı dar olduğundan komisyon gerekçeli karar tutanağı düzenlemelidir.")
    elif military_res:
        receipt = military_res.audit_receipt
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); color: #e0e7ff; border-radius: 10px; padding: 12px 18px; margin-bottom: 14px; border: 1px solid rgba(255,255,255,0.15);">
                <div style="font-weight: 800; font-size: 0.95rem; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center;">
                    <span>🎯 ASKERİ TAKTİK HAREKÂT KARAR DESTEK DANIŞMANI (Human-in-the-Loop C2)</span>
                    <span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-family: monospace;">Mühür: {receipt.combined_receipt_hash[:16]}...</span>
                </div>
                <div style="font-size: 0.82rem; line-height: 1.45; opacity: 0.95;">
                    <strong>Yetkili Subay:</strong> <code>{safe_text(tactical_operator)}</code> | Görev: <code>{safe_text(tactical_mission)}</code> | Doktrin: <em>Yalnızca Tavsiye Sunar • Otonom Angajman Yetkisi Yoktur</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if military_res.stale_telemetry_detected:
            st.warning("📡 **Gecikmeli / Bayat Telemetri Uyarısı:** Bazı temasların sensör verisi tazelik sınırını aşmıştır. Dinamik manevra olasılığına karşı görsel/radar doğrulaması yapınız.")
        if military_res.active_jamming_detected:
            st.info("🛡️ **Sensör Karartması / Jammer Tespit Edildi:** Sağlam kalan sensörlerin alt-uzayında karar sürekliliği sağlanmıştır; eksik izler için temkin cezası devrededir.")
    else:
        st.markdown(
            f"""
            <div style="background: #f1f5f9; border-left: 4px solid #3b82f6; padding: 8px 14px; border-radius: 6px; margin-bottom: 12px; font-size: 0.82rem; color: #334155;">
                🔬 <strong>Bilimsel Araştırma Çekirdeği:</strong> Deterministik $O(N \\times M)$ Imputation-Free Alt-Uzay Motoru | <strong>Girdi Bütünlüğü SHA-256:</strong> <code>{ds_hash[:16]}...</code>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_head2:
        if current_csv_bytes:
            st.download_button(
                label="📥 Ham CSV İndir",
                data=current_csv_bytes,
                file_name="karar_matrisi.csv",
                mime="text/csv",
                use_container_width=True,
            )
    with col_head3:
        # Akademik Denetim ve Karar Raporu (HTML / Yazdırılabilir & PDF'e Uygun)
        report_winner = rcz_sorted[0]
        report_elim = [html.escape(str(r.name)) for r in rcz_results if r.status != AlternativeStatus.EVALUATED]
        report_table_rows = ""
        for r in rcz_sorted:
            c_sc = classic_scores[r.index] * 100
            diff = (r.score * 100) - c_sc
            safe_row_name = html.escape(str(r.name))
            report_table_rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">#{r.rank}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{safe_row_name}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #1e40af; font-weight: bold;">%{r.score * 100:.1f}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; color: #64748b;">%{c_sc:.1f}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{diff:+.1f} Puan</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">%{int(r.support_weight * 100)}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{'✅ Geçti' if r.status == AlternativeStatus.EVALUATED else '❌ Elendi'}</td>
            </tr>
            """
        
        safe_winner_name = html.escape(str(report_winner.name))
        safe_scenario_title = html.escape(str(data_source.split(':')[0]))
        report_html = f"""<!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <title>R-CZ-TOPSIS Karar Analizi ve Akademik Denetim Raporu</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: #1e293b; line-height: 1.5; }}
                .header {{ border-bottom: 3px solid #1e40af; padding-bottom: 15px; margin-bottom: 25px; }}
                .title {{ font-size: 24px; font-weight: bold; color: #0f172a; margin: 0; }}
                .subtitle {{ font-size: 14px; color: #64748b; margin-top: 5px; }}
                .badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; background: #e0f2fe; color: #0369a1; }}
                .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }}
                th {{ background: #0f172a; color: white; padding: 10px; text-align: left; }}
                .footer {{ margin-top: 50px; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px; display: flex; justify-content: space-between; }}
                @media print {{ body {{ margin: 20px; }} .no-print {{ display: none; }} }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">🛡️ R-CZ-TOPSIS KARAR ANALİZİ VE AKADEMİK DENETİM RAPORU</div>
                <div class="subtitle">TÜBİTAK 2209-A Standartlarında Contextual Zero Algebra (CZ-Algebra) Karar Destek Çıktısı</div>
                <div style="margin-top: 8px;">
                    <span class="badge">Aktif Senaryo: {safe_scenario_title}</span>
                    <span class="badge" style="background: #fef3c7; color: #92400e;">Güvenlik Katsayısı (α): {alpha:.2f}</span>
                    <span class="badge" style="background: #dcfce7; color: #166534;">Bilgi Eşiği: %{int(w_threshold * 100)}</span>
                </div>
            </div>

            <div class="card" style="border-left: 5px solid #1e40af; background: #eff6ff;">
                <h3 style="margin-top: 0; color: #1e3a8a;">🏆 EN YÜKSEK PERFORMANSLI ALTERNATİF: {safe_winner_name}</h3>
                <p><strong>Nihai R-CZ Skoru:</strong> %{report_winner.score * 100:.1f} (100 Üzerinden) | <strong>Klasik TOPSIS Karşılığı:</strong> %{classic_scores[report_winner.index] * 100:.1f}</p>
                <p><strong>Karar Gerekçesi:</strong> Aday bilinen kriterlerin alt-uzayında en yüksek yakınlığı sağlamış; eksik kriterlerine uygulanan asimetrik şüphe cezasına (Γ_i) rağmen modelde 1. sırada yer almıştır.</p>
                <p><strong>Elenen Adaylar:</strong> {', '.join(report_elim) if report_elim else 'Yok (Tüm adaylar asgari bilgi barajını geçmiştir).'}</p>
            </div>

            <h3>📊 Tüm Alternatiflerin Sıralama ve Puan Cetveli</h3>
            <table>
                <thead>
                    <tr>
                        <th>Sıra</th>
                        <th>Aday Adı</th>
                        <th>R-CZ Skoru</th>
                        <th>Klasik TOPSIS</th>
                        <th>Net Fark</th>
                        <th>Bilgi Kapsama</th>
                        <th>Gatekeeper</th>
                    </tr>
                </thead>
                <tbody>
                    {report_table_rows}
                </tbody>
            </table>

            <div class="card" style="margin-top: 25px;">
                <h4 style="margin-top: 0;">⚖️ Akademik ve Metodolojik Doğrulama Notu</h4>
                <p style="font-size: 13px; color: #475569; margin-bottom: 0;">
                    Bu rapor, eksik ve karartılmış hücrelere hiçbir yapay sayı uydurmadan (imputation-free) yalnızca adayın ölçümlendiği alt-uzaydaki 
                    izdüşümü üzerinden analitik olarak üretilmiştir. Maliyet gizleyen veya asgari bilgi barajının (%{int(w_threshold * 100)}) altında kalan adaylar 
                    Akerlof Asimetrik Güvenilirlik Cezası (κ_i) ve Hard Gatekeeper protokolüyle denetlenmiştir. Bu belge bir karar destek demonstratörü çıktısı olup 
                    yasal veya nihai bağlayıcılığı bulunmamakta; teknik denetçilere izlenebilir matematiksel dayanak sunmaktadır.
                </p>
            </div>

            <div class="footer">
                <div>Rapor Oluşturulma Tarihi: 2026 | R-CZ-TOPSIS Çekirdek Motoru v1.1</div>
                <div>Sayfa 1 / 1 (Resmi Elektronik Belge)</div>
            </div>
        </body>
        </html>"""

        st.download_button(
            label="📄 Resmi Rapor İndir (HTML/PDF)",
            data=report_html.encode("utf-8"),
            file_name="rcz_resmi_karar_denetim_raporu.html",
            mime="text/html",
            use_container_width=True,
            help="Yazdırılabilir, PDF olarak kaydedilebilir resmi ihale/denetim karar tutanağı.",
        )

    # UX KPI Banner (Üst Yönetici Özeti)
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric("🏢 Değerlendirilen Adaylar", f"{n_alts} Alternatif")
    with col_kpi2:
        n_benefit = sum(1 for ct in crit_types if ct == CritType.BENEFIT)
        n_cost = sum(1 for ct in crit_types if ct == CritType.COST)
        st.metric("📊 Kriter Çeşitliliği", f"{n_crits} Kriter", f"{n_benefit} Fayda (↑) | {n_cost} Maliyet (↓)")
    with col_kpi3:
        total_cells = n_alts * n_crits
        missing_cells = int(np.sum(Sigma == Context.INACTION.value))
        missing_pct = (missing_cells / total_cells) * 100 if total_cells > 0 else 0.0
        st.metric("❓ Eksik Veri / Bilinmezlik", f"%{missing_pct:.1f}", f"{missing_cells} Bilinmeyen Hücre")
    with col_kpi4:
        n_elim = sum(1 for r in rcz_results if r.status != AlternativeStatus.EVALUATED)
        n_valid = n_alts - n_elim
        st.metric("🛡️ Asgari Bilgi Süzgeci", f"{n_valid} Aday Geçti", f"{n_elim} Elendi (<%{int(w_threshold*100)})" if n_elim > 0 else "0 Elenen (Tümü Yeterli)")
    st.markdown("---")

    with st.expander("❓ Ceza Mantığı, Parametre Ayarları ve Kriter Seçimi Hakkında Hızlı Rehber", expanded=False):
        st.markdown(
            r"""
            * **Ceza Nedir?** Eksik veya saklanan bilgisi olan adayların nihai skoruna uygulanan bir **temkin/güvenilirlik indirimidir** ($\Gamma_i = W_i^{\alpha \cdot \kappa_i}$).
            * **Hesaplama Neye Göre Ayarlanır?** Yan menüdeki riskten kaçınma katsayısı ($\alpha$), asgari bilgi barajı ($W_{\text{threshold}}$), asgari kriter sayısı ve global alt-uzay ağırlıklandırması ile yönetilir.
            * **Kriterler Neye Göre Seçilir?** İhale şartnamesi veya operasyonel ihtiyaçlara göre **Fayda (↑)** ve **Maliyet (↓)** olarak ayrılır; önem derecelerine göre ağırlıklandırılır ($\sum w_j = 1.0$).
            
            👉 *Ayrıntılı soru-cevap dökümü, matematiksel dayanaklar ve örnekler için sol menüden **'💡 5  Sistem Rehberi'** veya **'🧭 0  Genel Bakış'** modüllerine geçiş yapabilirsiniz.*
            """
        )

    winner = rcz_sorted[0]
    winner_idx = winner.index

    # En Güçlü ve Eksik Özellikler
    strengths = []
    missing_feats = []
    for j in range(n_crits):
        c_name = crit_names[j]
        is_benefit = (crit_types[j] == CritType.BENEFIT)
        active_vals = [X[i, j] for i in range(n_alts) if Sigma[i, j] == Context.ACTION.value]
        
        if Sigma[winner_idx, j] == Context.INACTION.value:
            missing_feats.append(c_name.split(" ")[0])
        else:
            val = X[winner_idx, j]
            best_val = np.max(active_vals) if is_benefit else np.min(active_vals)
            if np.isclose(val, best_val) or (is_benefit and val >= 0.88 * best_val) or (not is_benefit and val <= 1.12 * best_val):
                strengths.append(f"**{c_name.split(' ')[0]}** ({val:g})")

    # Şampiyonlar Kürsüsü (Kompakt, Dengeli & Orantılı Görsel Kartlar)
    col_p1, col_p2, col_p3 = st.columns([1.15, 1, 1])
    c_win_score = classic_scores[winner_idx] * 100
    win_diff = (winner.score * 100) - c_win_score
    s_txt = ", ".join(strengths) if strengths else "dengeli genel üstünlüğü"
    reason = f"<strong>Neden 1. Oldu?</strong> {s_txt} kriterlerinde rakiplerini geride bıraktı."
    if missing_feats:
        reason += f" <em>({', '.join(missing_feats)} eksik olmasına karşın mevcut performansı temkin cezasına rağmen zirveyi korudu.)</em>"
    else:
        reason += " <em>(Tüm verileri eksiksiz ölçüldü; veri güvenilirliği %100).</em>"

    with col_p1:
        safe_win_name = html.escape(str(winner.name))
        st.markdown(
            f"""
            <div class="podium-gold">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; background: rgba(180, 83, 9, 0.18); padding: 3px 8px; border-radius: 6px;">🥇 1. DERECE (ŞAMPİYON)</span>
                    <span style="font-weight: 700; font-size: 0.82rem; color: #92400e;">#1. SIRA</span>
                </div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #78350f; margin-bottom: 8px; line-height: 1.2;">
                    {safe_win_name}
                </div>
                <div style="display: flex; gap: 12px; margin-bottom: 8px; background: rgba(255, 255, 255, 0.65); padding: 7px 12px; border-radius: 8px;">
                    <div>
                        <div style="font-size: 0.70rem; color: #92400e; font-weight: 700;">R-CZ SKORU</div>
                        <div style="font-size: 1.25rem; font-weight: 800; color: #b45309;">%{winner.score * 100:.1f}</div>
                    </div>
                    <div style="border-left: 1px solid rgba(180, 83, 9, 0.2); padding-left: 10px;">
                        <div style="font-size: 0.70rem; color: #92400e; font-weight: 700;">KLASİK TOPSIS</div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #78350f;">%{c_win_score:.1f} <span style="font-size: 0.76rem; font-weight: 600;">({win_diff:+.1f})</span></div>
                    </div>
                </div>
                <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                    <span style="font-size: 0.74rem; background: rgba(255, 255, 255, 0.6); padding: 2px 7px; border-radius: 4px; font-weight: 600; color: #78350f;">🛡️ Bilgi: %{int(winner.support_weight * 100)}</span>
                    <span style="font-size: 0.74rem; background: rgba(255, 255, 255, 0.6); padding: 2px 7px; border-radius: 4px; font-weight: 600; color: #78350f;">⚡ Ceza: -%{int(round((1 - winner.penalty_gamma) * 100))}%</span>
                </div>
                <div style="font-size: 0.84rem; line-height: 1.4; color: #78350f; background: rgba(255, 255, 255, 0.5); padding: 7px 10px; border-radius: 6px;">
                    {reason}
                </div>
                <div style="margin-top: 8px; padding: 6px 10px; background: rgba(255, 255, 255, 0.7); border-radius: 6px; font-size: 0.72rem; color: #92400e; font-family: monospace;">
                    ⚙️ <strong>Model:</strong> v1.1 | <strong>Ağırlıklandırma:</strong> Global (w_j·r_ij) | <strong>local_reweighting:</strong> {'Açık' if config.local_reweighting else 'Kapalı'} | <strong>α:</strong> {alpha:.2f} | <strong>W_th:</strong> %{int(w_threshold*100)} | <strong>m_min:</strong> {min_active_criteria}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_p2:
        if len(rcz_sorted) > 1:
            silver = rcz_sorted[1]
            safe_sil_name = html.escape(str(silver.name))
            c_sil_score = classic_scores[silver.index] * 100
            sil_diff = silver.score * 100 - c_sil_score
            st.markdown(
                f"""
                <div class="podium-silver">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; background: rgba(100, 116, 139, 0.18); padding: 3px 8px; border-radius: 6px;">🥈 2. DERECE</span>
                        <span style="font-weight: 700; font-size: 0.82rem; color: #475569;">#2. SIRA</span>
                    </div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #1e293b; margin-bottom: 8px; line-height: 1.2;">
                        {safe_sil_name}
                    </div>
                    <div style="display: flex; gap: 12px; margin-bottom: 8px; background: rgba(255, 255, 255, 0.7); padding: 7px 12px; border-radius: 8px;">
                        <div>
                            <div style="font-size: 0.70rem; color: #64748b; font-weight: 700;">R-CZ SKORU</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: #334155;">%{silver.score * 100:.1f}</div>
                        </div>
                        <div style="border-left: 1px solid rgba(148, 163, 184, 0.3); padding-left: 10px;">
                            <div style="font-size: 0.70rem; color: #64748b; font-weight: 700;">KLASİK TOPSIS</div>
                            <div style="font-size: 1.05rem; font-weight: 700; color: #475569;">%{c_sil_score:.1f} <span style="font-size: 0.76rem; font-weight: 600;">({sil_diff:+.1f})</span></div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                        <span style="font-size: 0.74rem; background: rgba(255, 255, 255, 0.65); padding: 2px 7px; border-radius: 4px; font-weight: 600; color: #334155;">🛡️ Bilgi: %{int(silver.support_weight * 100)}</span>
                        <span style="font-size: 0.74rem; background: rgba(255, 255, 255, 0.65); padding: 2px 7px; border-radius: 4px; font-weight: 600; color: #334155;">⚡ Ceza: -%{int(round((1 - silver.penalty_gamma) * 100))}%</span>
                    </div>
                    <div style="font-size: 0.84rem; line-height: 1.4; color: #334155; background: rgba(255, 255, 255, 0.5); padding: 7px 10px; border-radius: 6px;">
                        <strong>Derece Analizi:</strong> Başarıda zirveye çok yakın bir profil çizdi; kritik kriter dengesi ve risk kesintisi nedeniyle 2. sırada yer aldı.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_p3:
        if len(rcz_sorted) > 2:
            bronze = rcz_sorted[2]
            safe_brz_name = html.escape(str(bronze.name))
            c_brz_score = classic_scores[bronze.index] * 100
            brz_diff = bronze.score * 100 - c_brz_score
            st.markdown(
                f"""
                <div class="podium-bronze">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; background: rgba(194, 65, 12, 0.18); padding: 3px 8px; border-radius: 6px;">🥉 3. DERECE</span>
                        <span style="font-weight: 700; font-size: 0.82rem; color: #9a3412;">#3. SIRA</span>
                    </div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #7c2d12; margin-bottom: 8px; line-height: 1.2;">
                        {safe_brz_name}
                    </div>
                    <div style="display: flex; gap: 12px; margin-bottom: 8px; background: rgba(255, 255, 255, 0.7); padding: 7px 12px; border-radius: 8px;">
                        <div>
                            <div style="font-size: 0.70rem; color: #c2410c; font-weight: 700;">R-CZ SKORU</div>
                            <div style="font-size: 1.25rem; font-weight: 800; color: #9a3412;">%{bronze.score * 100:.1f}</div>
                        </div>
                        <div style="border-left: 1px solid rgba(249, 115, 22, 0.3); padding-left: 10px;">
                            <div style="font-size: 0.70rem; color: #c2410c; font-weight: 700;">KLASİK TOPSIS</div>
                            <div style="font-size: 1.05rem; font-weight: 700; color: #7c2d12;">%{c_brz_score:.1f} <span style="font-size: 0.76rem; font-weight: 600;">({brz_diff:+.1f})</span></div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                        <span style="font-size: 0.74rem; background: rgba(255, 255, 255, 0.65); padding: 2px 7px; border-radius: 4px; font-weight: 600; color: #7c2d12;">🛡️ Bilgi: %{int(bronze.support_weight * 100)}</span>
                        <span style="font-size: 0.74rem; background: rgba(255, 255, 255, 0.65); padding: 2px 7px; border-radius: 4px; font-weight: 600; color: #7c2d12;">⚡ Ceza: -%{int(round((1 - bronze.penalty_gamma) * 100))}%</span>
                    </div>
                    <div style="font-size: 0.84rem; line-height: 1.4; color: #7c2d12; background: rgba(255, 255, 255, 0.5); padding: 7px 10px; border-radius: 6px;">
                        <strong>Derece Analizi:</strong> Belirli fayda kriterlerinde rekabetçi olsa da maliyet veya eksik veri şüphe payı nedeniyle 3. sırada kaldı.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Yakın Skor Duyarlılık Uyarısı
    if len(rcz_sorted) > 1 and abs(rcz_sorted[0].score - rcz_sorted[1].score) <= 0.02:
        diff_pct = abs(rcz_sorted[0].score - rcz_sorted[1].score) * 100
        st.warning(
            f"⚠️ **Hassasiyet & Yakın Skor Uyarısı:** 1. sıradaki ({html.escape(str(rcz_sorted[0].name))}) ile "
            f"2. sıradaki ({html.escape(str(rcz_sorted[1].name))}) arasındaki R-CZ skor farkı yalnızca **%{diff_pct:.2f}** (≤ %2.0). "
            f"Küçük ağırlık oynamaları veya ölçüm belirsizlikleri sıralamayı değiştirebilir; karar vericilerin her iki adayı da "
            f"birlikte değerlendirmesi ve duyarlılık analizi yürütmesi tavsiye edilir."
        )

    # Bilimsel Sınırlama Notu
    st.info(
        "🔬 **Bilimsel Metodoloji & Sınırlama Açıklaması:** R-CZ TOPSIS eksik verili adayları cezalandırarak bilgi şeffaflığını teşvik eder. "
        "Bununla birlikte, aşırı baskın fayda kriterlerine sahip bir adayın maliyet bilgisini gizlemesi durumunda dahi teorik olarak birinci çıkabildiği durumlar (sınır senaryolar) mevcuttur. "
        "Model manipülasyonu bütünüyle imkânsız kılmaz; eksik bilginin riskini görünür kılar ve sıralamada temkin cezası uygular. "
        "Kritik kararlarda karar verici denetimi esastır."
    )

    # Akıllı Karar Karnesi
    st.markdown("---")
    st.subheader("📋 Akıllı Karar Karnesi: Hangi Aday Neden Bu Sırada?")
    st.caption("Aşağıdaki özet tabloda iki yöntemin skorları yan yana listelenmiştir. Tablonun hemen altındaki **Derinlemesine Karar Dosyası** bölümünden her adayın tüm kriter değerlerini, matematiksel hesap adımlarını ve yöntem farklarını eksiksiz inceleyebilirsiniz:")
    
    karne_list = []
    for r in rcz_sorted:
        idx = r.index
        c_score = classic_scores[idx] * 100
        rcz_score = r.score * 100
        score_diff = rcz_score - c_score
        c_r = classic_ranks[idx]
        rank_diff = c_r - r.rank

        if rank_diff > 0:
            diff_lbl = f"🟢 +{rank_diff} Basamak (#{c_r} → #{r.rank})"
        elif rank_diff < 0:
            diff_lbl = f"🔻 {abs(rank_diff)} Basamak (#{c_r} → #{r.rank})"
        else:
            diff_lbl = f"⚪ Değişmedi (#{r.rank})"

        missing_b_cols = [crit_names[j].split(" ")[0] for j in range(n_crits) if Sigma[idx, j] == Context.INACTION.value and crit_types[j] == CritType.BENEFIT]
        missing_c_cols = [crit_names[j].split(" ")[0] for j in range(n_crits) if Sigma[idx, j] == Context.INACTION.value and crit_types[j] == CritType.COST]

        if r.status == AlternativeStatus.INSUFFICIENT_DATA:
            b_lbl = "🔴 Yetersiz Bilgi (Elendi)"
            fark_nedeni = (
                f"Klasik TOPSIS adayın aşırı eksik verisine bakmadan körlemesine %{c_score:.1f} puan vermişti. "
                f"R-CZ modeli, bilgi kapsama oranı (%{int(r.support_weight*100)}) asgari güvenlik barajının (%{int(w_threshold*100)}) altında kaldığı için "
                f"adayı eledi (0.0 puan); böylece aşırı eksik veriyle rastlantısal biçimde üst derece alma riski engellendi."
            )
        elif r.support_weight >= 0.99:
            b_lbl = "🟢 Eksiksiz Tam Veri"
            fark_nedeni = (
                f"Adayın tüm kriterleri eksiksiz ölçüldüğü için R-CZ ile Klasik TOPSIS matematiksel olarak "
                f"birebir aynı skoru üretmiştir (%{rcz_score:.1f} vs %{c_score:.1f}). Veri tam olduğunda iki yöntem analitik olarak özdeştir."
            )
        else:
            b_lbl = f"🟡 %{int(r.support_weight * 100)} Kapsama"
            pen_pct = int(round((1 - r.penalty_gamma) * 100))
            if score_diff > 0.5:
                miss_str = f"eksik olan fayda kriterlerini ({', '.join(missing_b_cols)})" if missing_b_cols else "eksik hücrelerini"
                fark_nedeni = (
                    f"Klasik TOPSIS adayın {miss_str} doğrudan '0' sayıp adayı uzay orijinine çekerek haksız yere cezalandırmıştı (%{c_score:.1f} puan). "
                    f"R-CZ adayı sadece bildiği {r.active_criteria_count} kriterin alt-uzayında adilce değerlendirerek puanını korudu. "
                    f"%{pen_pct} temkin cezasına rağmen adayın gerçek kalitesi kurtarıldı."
                )
            elif score_diff < -0.5:
                miss_str = f"eksik olan maliyet kriterlerini ({', '.join(missing_c_cols)})" if missing_c_cols else "eksik hücrelerini"
                fark_nedeni = (
                    f"Klasik TOPSIS adayın {miss_str} '0' yani 'bedava/masrafsız' sayıp adaya sahte bir üstünlük vermişti (%{c_score:.1f} puan). "
                    f"R-CZ asimetrik maliyet cezası (κ={rcz_expl.kappa[idx]:.2f}) ve epistemik güvenilirlik çarpanı "
                    f"(Γ={r.penalty_gamma:.2f}) uygulayarak skoru temkin seviyesine çekti ve eksik maliyet kaynaklı haksız avantajı bastırdı."
                )
            else:
                fark_nedeni = (
                    f"Adayın R-CZ skoru (%{rcz_score:.1f}) ile Klasik TOPSIS skoru (%{c_score:.1f}) birbirine çok yakındır. "
                    f"Eksik verilerin ağırlığı genel sıralama ve mesafe dengesini önemli ölçüde saptırmamıştır."
                )

        karne_list.append({
            "Sıra": f"#{r.rank} {'🥇' if r.rank==1 else ('🥈' if r.rank==2 else ('🥉' if r.rank==3 else ''))}",
            "Aday": r.name,
            "R-CZ Skoru (Yeni)": f"%{rcz_score:.1f}",
            "Klasik TOPSIS (Eski)": f"%{c_score:.1f}",
            "Puan Farkı": f"{score_diff:+.1f} Puan",
            "Sıra Değişimi": diff_lbl,
            "Veri Kapsama": b_lbl,
            "Puan Farkının Nedeni (Neden Oluştu ve Neden Farklı?)": fark_nedeni,
        })
    st.dataframe(
        pd.DataFrame(karne_list),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Puan Farkının Nedeni (Neden Oluştu ve Neden Farklı?)": st.column_config.TextColumn(
                "Puan Farkının Nedeni (Neden Oluştu ve Neden Farklı?)",
                width="large"
            )
        }
    )

    # ==============================================================================
    # DERİNLEMESİNE ADAY KARAR DOSYALARI (HİÇBİR ŞEY SIĞMAMA SORUNU OLMADAN)
    # ==============================================================================
    st.markdown("---")
    st.subheader("🔬 Aday Bazında Derinlemesine Matematiksel Karar Dosyası")
    st.markdown(
        "Her bir adayın hangi kriterlerinin eksik olduğunu, Klasik TOPSIS'in yaptığı matematiksel hatayı "
        "ve R-CZ-TOPSIS'in alt-uzay ve asimetrik ceza formüllerini aşağıdaki panelden ayrıntılı olarak inceleyebilirsiniz:"
    )

    alt_choice_names = [f"#{r.rank} {r.name} (R-CZ: %{r.score*100:.1f} | Klasik: %{classic_scores[r.index]*100:.1f})" for r in rcz_sorted]
    selected_choice = st.selectbox("🎯 İncelemek İstediğiniz Adayı Seçin:", alt_choice_names, index=0)
    selected_rank = int(selected_choice.split(" ")[0].replace("#", ""))
    selected_r = next(r for r in rcz_sorted if r.rank == selected_rank)

    def display_candidate_full_dossier(cand_r):
        c_idx = cand_r.index
        c_sc = classic_scores[c_idx] * 100
        rcz_sc = cand_r.score * 100
        sc_diff = rcz_sc - c_sc
        c_rk = classic_ranks[c_idx]
        rk_diff = c_rk - cand_r.rank
        pen_cut = int(round((1 - cand_r.penalty_gamma) * 100))

        # 1. 4 Metrik Kutusu
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("🏆 R-CZ Skoru (Yeni Model)", f"%{rcz_sc:.1f}", f"Adil Sıralama: #{cand_r.rank}")
        with m2:
            st.metric("🏛️ Klasik TOPSIS (Eski Model)", f"%{c_sc:.1f}", f"Klasik Sıralama: #{c_rk}")
        with m3:
            st.metric("📊 Net Skor Farkı", f"{sc_diff:+.1f} Puan", f"{'+' if rk_diff>0 else ''}{rk_diff} Basamak Değişim")
        with m4:
            st.metric("🛡️ Bilgi Kapsama (W_i)", f"%{int(cand_r.support_weight * 100)}", f"Risk İndirimi: -%{pen_cut}")

        # 2. Kriter Röntgeni (Bilinen vs Eksik)
        st.markdown(f"#### 📋 1. {safe_text(cand_r.name)} Kriter Röntgeni: Hangi Veriler Biliniyor, Hangileri Eksik?")
        known_data = []
        missing_data = []
        for j in range(n_crits):
            c_nm = crit_names[j]
            c_tp = "Fayda (Benefit ↑)" if crit_types[j] == CritType.BENEFIT else "Maliyet (Cost ↓)"
            w_pct = weights[j] * 100
            if Sigma[c_idx, j] == Context.ACTION.value:
                val = X[c_idx, j]
                s_val = rcz_expl.S[j]
                norm_r = val / s_val if s_val > 0 else 0.0
                coord_v = rcz_expl.V[c_idx, j]
                known_data.append({
                    "Kriter": c_nm,
                    "Gerçek Değer": f"{val:g}",
                    "Kriter Yönü": c_tp,
                    "Global Ağırlık (w_j)": f"%{w_pct:.1f}",
                    "Normalize Değer (r_ij)": f"{norm_r:.4f}",
                    "Ağırlıklı Koordinat (V_ij)": f"{coord_v:.4f}" if not np.isnan(coord_v) else "—",
                })
            else:
                missing_data.append({
                    "Kriter": c_nm,
                    "Durum": "❓ Bilinmiyor / Eksik (0_I)",
                    "Kriter Yönü": c_tp,
                    "Global Ağırlık (w_j)": f"%{w_pct:.1f}",
                })

        col_k1, col_k2 = st.columns([1.3, 1])
        with col_k1:
            st.markdown(f"**✅ Ölçülen ve Bilinen Kriterler ({len(known_data)} / {n_crits}):**")
            st.dataframe(pd.DataFrame(known_data), use_container_width=True, hide_index=True)
        with col_k2:
            st.markdown(f"**❓ Ölçülmeyen / Eksik Kriterler ({len(missing_data)} / {n_crits}):**")
            if missing_data:
                st.dataframe(pd.DataFrame(missing_data), use_container_width=True, hide_index=True)
            else:
                st.success("Tüm kriterler eksiksiz ölçülmüştür; bu adayda hiçbir eksik hücre bulunmamaktadır.")

        # 3. Klasik TOPSIS ve R-CZ-TOPSIS Kıyaslaması
        st.markdown(f"#### ⚖️ 2. Matematiksel Analiz: Klasik TOPSIS Neden Hata Yaptı, R-CZ Nasıl Düzeltti?")
        col_c_err, col_rcz_sol = st.columns(2)
        with col_c_err:
            st.error("##### 🏛️ Klasik TOPSIS Neden Hatalı Sonuç Üretti?")
            if cand_r.status == AlternativeStatus.INSUFFICIENT_DATA:
                st.markdown(
                    f"""
                    * **Hata Türü:** Bilgi Yetersizliğine Karşı Körü Körüne Değerlendirme
                    * **Yapılan İşlem:** Adayın bilgi kapsama oranı yalnızca **%{int(cand_r.support_weight * 100)}** olmasına rağmen, Klasik TOPSIS eksik hücrelere $0.0$ yazarak sanki geçerli bir alternatifmiş gibi **%{c_sc:.1f}** puan verdi ve adayı #{c_rk} sıraya yerleştirdi.
                    * **Doğurduğu Tehlike:** Gerçek performansını bilmediğimiz yetersiz bir adayın kurumsal ihaleyi veya seçimi kazanmasına yol açabilir.
                    """
                )
            elif cand_r.support_weight >= 0.99:
                st.markdown(
                    f"""
                    * **Durum:** Tam Veri Uyumu (Zero Error)
                    * **Yapılan İşlem:** Adayın tüm kriterleri tam olduğu için Klasik TOPSIS herhangi bir eksiklik varsayımı yapmadan **%{c_sc:.1f}** puan üretti.
                    * **Matematiksel Gerçek:** Bilgi tamsa ($W_i = 1.0$), R-CZ-TOPSIS analitik olarak Klasik TOPSIS ile birebir özdeştir (**Fark: 0.0 Puan**).
                    """
                )
            elif sc_diff > 0.5:
                miss_b = [m["Kriter"] for m in missing_data if "Fayda" in m["Kriter Yönü"]]
                st.markdown(
                    f"""
                    * **Hata Türü:** Haksız İnfaz (False Elimination)
                    * **Yapılan İşlem:** Adayın ölçülmemiş fayda kriterlerini ({', '.join(miss_b)}) matriste doğrudan **0.0** kabul etti.
                    * **Matematiksel Bozulma:** Öklid uzayında adayı orijine fırlattı; pozitif ideal noktadan ($v^+$) mesafesini yapay olarak aşırı büyüttü.
                    * **Sonuç:** Aday girdiği testlerde çok başarılı olmasına rağmen Klasik TOPSIS tarafından **%{c_sc:.1f}** puana düşürülüp #{c_rk}. sıraya itildi.
                    """
                )
            elif sc_diff < -0.5:
                miss_c = [m["Kriter"] for m in missing_data if "Maliyet" in m["Kriter Yönü"]]
                st.markdown(
                    f"""
                    * **Hata Türü:** Haksız Ödüllendirme (False Inflation / Cherry-Picking)
                    * **Yapılan İşlem:** Adayın ölçülmemiş maliyet kriterlerini ({', '.join(miss_c)}) **0.0** kabul etti.
                    * **Matematiksel Bozulma:** Maliyet kriterinde en düşük değer en iyi olduğundan, Klasik TOPSIS adayı bu masraflardan **"muaf / bedava"** saydı!
                    * **Sonuç:** İdeal noktaya mesafesi sahte biçimde küçüldü ve adaya **%{c_sc:.1f}** gibi haksız derecede yüksek bir puan verilerek #{c_rk}. sıraya fırlatıldı.
                    """
                )
            else:
                st.markdown(
                    f"""
                    * **Durum:** Dengeli Dağılım
                    * **Sonuç:** Eksik kriterlerin ağırlığı adayın genel sıralama konumunu büyük ölçüde saptırmadı (Klasik Skor: %{c_sc:.1f}, Sıra: #{c_rk}).
                    """
                )

        with col_rcz_sol:
            st.success("##### 🛡️ R-CZ-TOPSIS Matematiksel Olarak Nasıl Düzeltti?")
            if cand_r.status == AlternativeStatus.INSUFFICIENT_DATA:
                st.markdown(
                    f"""
                    * **1. Hard Gatekeeper Süzgeci:** Bilgi oranı $W_i = {cand_r.support_weight:.2f}$, asgari güvenlik barajı olan $W_{{threshold}} = {w_threshold:.2f}$ şartını sağlayamadı.
                    * **2. Kesin Karar:** Karar vericiyi ve kurumu yanıltmamak adına aday **doğrudan elendi (0.0 Puan)**.
                    * **Sağlanan Fayda:** Bilgisizlikten kaynaklanabilecek operasyonel sürprizler ve felaketler sıfırlandı.
                    """
                )
            else:
                dp_val = rcz_expl.d_plus[c_idx]
                dm_val = rcz_expl.d_minus[c_idx]
                m_cst = rcz_expl.missing_cost[c_idx]
                kpp = rcz_expl.kappa[c_idx]
                gmm = rcz_expl.gamma[c_idx]
                st.markdown(
                    f"""
                    * **1. Adım - Alt-Uzay İzdüşümü ($J_i^*$):** Eksik hücrelere değer uydurulmadı. Yalnızca bilinen {cand_r.active_criteria_count} kriterin alt-uzayında Öklid mesafeleri alındı:
                      - İdeal Noktaya Mesafe ($D_i^+$): **{dp_val:.4f}**
                      - Anti-İdeal Mesafesi ($D_i^-$): **{dm_val:.4f}**
                      - Temel Cezasız Skor: $C_{{base}} = \\frac{{{dm_val:.4f}}}{{{dp_val:.4f} + {dm_val:.4f}}} = \\mathbf{{{cand_r.base_score:.4f}}}$ (**%{cand_r.base_score*100:.1f}**)
                    * **2. Adım - Asimetrik Maliyet ve Epistemik Ceza:**
                      - Eksik Maliyet Kriterleri Ağırlığı ($m_{{cost}}$): **{m_cst:.2f}**
                      - Maliyet Ceza Üssü: $\\kappa_i = 1.0 + {m_cst:.2f} = \\mathbf{{{kpp:.2f}}}$
                      - Epistemik Güvenilirlik Çarpanı: $\\Gamma_i = (W_i)^{{\\alpha \\cdot \\kappa_i}} = ({cand_r.support_weight:.2f})^{{{alpha} \\times {kpp:.2f}}} = \\mathbf{{{gmm:.4f}}}$ (%{pen_cut} risk indirimi)
                    * **3. Adım - Nihai Puan:**
                      $$C^* = C_{{base}} \\times \\Gamma_i = {cand_r.base_score:.4f} \\times {gmm:.4f} = \\mathbf{{{cand_r.score:.4f}}}\\quad (\\mathbf{{%{rcz_sc:.1f}\\ \\text{{Puan}}}})$$
                    * **Sonuç:** Aday tüm adaletsizliklerden arındırılarak hak ettiği **#{cand_r.rank}.** sıraya oturdu.
                    """
                )

    # Seçilen Adayın Tam Dosyasını Göster
    with st.container():
        st.markdown(f"### 📂 Dosya: {selected_r.name} (Sıra #{selected_r.rank})")
        display_candidate_full_dossier(selected_r)

    # Toplu İnceleme Expander'ı
    with st.expander("📑 Tüm Adayların Karar Dosyalarını Topluca Gör (Aşağı Doğru Genişlet)"):
        for cand in rcz_sorted:
            st.markdown(f"---")
            st.markdown(f"### 📌 #{cand.rank} {cand.name}")
            display_candidate_full_dossier(cand)

    # ==============================================================================
    # GELİŞMİŞ VE NET SKOR KIYASLAMA PANELİ (YENİ MODERN GRAFİK MİMARİSİ)
    # ==============================================================================
    st.markdown("---")
    st.subheader("📊 R-CZ-TOPSIS ve Klasik TOPSIS Canlı Kıyaslama Grafiği")
    st.caption("Adayların klasik yönteme göre yaşadığı adalet kazançları, engellenen haksız avantajlar ve skor karşılaştırmaları:")

    chart_mode = st.radio(
        "Grafik Görünüm Modu:",
        ["🏆 Yan Yana Skor Karşılaştırması (%)", "⚖️ Adalet ve Müdahale Farkı (R-CZ - Klasik Δ)"],
        horizontal=True,
    )

    col_c1, col_c2 = st.columns([1.7, 1])
    with col_c1:
        if "Yan Yana" in chart_mode:
            fig = go.Figure()
            # Sıralamaya göre isimler
            cand_names = [r.name for r in rcz_sorted]
            rcz_vals = [r.score * 100 for r in rcz_sorted]
            cls_vals = [classic_scores[r.index] * 100 for r in rcz_sorted]

            fig.add_trace(go.Bar(
                y=cand_names,
                x=rcz_vals,
                name="🛡️ R-CZ-TOPSIS (Adil Skor)",
                orientation="h",
                marker=dict(
                    color="rgba(37, 99, 235, 0.95)",
                    line=dict(color="#1d4ed8", width=1.5),
                ),
                text=[f"%{v:.1f}" for v in rcz_vals],
                textposition="outside",
                textfont=dict(size=11, color="#1e3a8a"),
                hovertemplate="<b>%{y}</b><br>🛡️ R-CZ Skoru: <b>%%{x:.1f}</b><extra></extra>",
            ))

            fig.add_trace(go.Bar(
                y=cand_names,
                x=cls_vals,
                name="🏛️ Klasik TOPSIS (Eski)",
                orientation="h",
                marker=dict(
                    color="rgba(148, 163, 184, 0.65)",
                    line=dict(color="#64748b", width=1.5),
                ),
                text=[f"%{v:.1f}" for v in cls_vals],
                textposition="outside",
                textfont=dict(size=11, color="#475569"),
                hovertemplate="<b>%{y}</b><br>🏛️ Klasik Skor: <b>%%{x:.1f}</b><extra></extra>",
            ))

            chart_height = max(460, len(rcz_sorted) * 36)
            fig.update_layout(
                barmode="group",
                bargap=0.25,
                bargroupgap=0.1,
                xaxis_title="Normalize Başarı Puanı (%)",
                yaxis_title="",
                height=chart_height,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(248, 250, 252, 0.6)",
                margin=dict(l=10, r=40, t=30, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="rgba(203,213,225,0.8)",
                    borderwidth=1,
                ),
                xaxis=dict(
                    gridcolor="rgba(226, 232, 240, 0.8)",
                    range=[0, max(max(rcz_vals + cls_vals) * 1.15, 105)],
                ),
                yaxis=dict(
                    autorange="reversed",
                    tickfont=dict(size=12, family="Inter, sans-serif"),
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            # Delta / Fark Grafiği
            fig_delta = go.Figure()
            cand_names = [r.name for r in rcz_sorted]
            diffs = [(r.score * 100) - (classic_scores[r.index] * 100) for r in rcz_sorted]
            bar_colors = [
                "rgba(16, 185, 129, 0.9)" if d > 0.05 else ("rgba(239, 68, 68, 0.9)" if d < -0.05 else "rgba(148, 163, 184, 0.7)")
                for d in diffs
            ]
            border_colors = [
                "#059669" if d > 0.05 else ("#dc2626" if d < -0.05 else "#64748b")
                for d in diffs
            ]

            fig_delta.add_trace(go.Bar(
                y=cand_names,
                x=diffs,
                orientation="h",
                marker=dict(color=bar_colors, line=dict(color=border_colors, width=1.5)),
                text=[f"{d:+.1f} Puan" for d in diffs],
                textposition="outside",
                textfont=dict(size=11),
                hovertemplate="<b>%{y}</b><br>Net Fark (R-CZ - Klasik): <b>%{x:+.1f} Puan</b><extra></extra>",
            ))

            chart_height = max(460, len(rcz_sorted) * 36)
            fig_delta.update_layout(
                xaxis_title="Puan Farkı (Pozitif = R-CZ Lehine Kapsama Dengesi | Negatif = Eksik Veri Temkin Cezası)",
                yaxis_title="",
                height=chart_height,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(248, 250, 252, 0.6)",
                margin=dict(l=10, r=50, t=20, b=40),
                xaxis=dict(gridcolor="rgba(226, 232, 240, 0.8)", zerolinecolor="#334155", zerolinewidth=2),
                yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
            )
            st.plotly_chart(fig_delta, use_container_width=True)

    with col_c2:
        st.markdown(
            """
            <div style="background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #cbd5e1; border-radius: 14px; padding: 22px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <h5 style="margin-top: 0; color: #0f172a; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                    <span>💡</span> Grafiğin Anlattığı Bilimsel Gerçek
                </h5>
                <div style="font-size: 0.90rem; color: #334155; line-height: 1.6;">
                    <p>Klasik TOPSIS eksik veriyi doğrudan <code>0.0</code> skalerine eşitlediği için iki ölümcül hata üretir:</p>
                    <div style="background: #eff6ff; border-left: 3px solid #2563eb; padding: 10px 12px; border-radius: 6px; margin-bottom: 12px;">
                        <strong style="color: #1e40af;">1. Haksız İnfazın Önlenmesi (Yeşil / Mavi):</strong><br>
                        Güçlü bir adayın 1 tane fayda kriteri ölçülmediyse, Klasik model onu 0 sayıp dibe iter. R-CZ adayı sadece bildiği kriterlerin alt-uzayında adilce değerlendirerek puanını kurtarır.
                    </div>
                    <div style="background: #fef2f2; border-left: 3px solid #ef4444; padding: 10px 12px; border-radius: 6px; margin-bottom: 12px;">
                        <strong style="color: #991b1b;">2. Sahte Şampiyonluk Riskinin Bastırılması (Kırmızı):</strong><br>
                        Maliyetini veya riskini saklayan adayları Klasik model "bedava" sanarak haksız yere üst sıralara taşıyabilir. R-CZ asimetrik temkin cezası (κ_i) uygulayarak bu eksiklik kaynaklı haksız avantajı bastırmayı amaçlar.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==============================================================================
# MODÜL 2: İHA / SİHA & SAVUNMA SANAYİİ DOKTRİNİ (KONSEPT ANALİZİ & ENTEGRASYON SENARYOLARI)
# ==============================================================================
if "2  İHA / SİHA" in nav_mode:
    st.header("🚁 R-CZ-TOPSIS'in İHA / SİHA ve Savunma Sistemlerine Entegrasyon Konsepti")
    st.caption("Elektronik Harp Altında Açıklanabilir Çok Kriterli Karar Verme, Sürü Taksimi ve Sensör Karartması Simülasyonu")

    st.markdown(
        """
        > **Konsept Özeti:** Modern muharebe sahasında elektronik harp altında sensörlerin körleşmesi veya karartılmış eksik veri durumlarında, 
        > klasik karar algoritmaları eksik veriyi körlemesine sıfır varsayarak hatalı önceliklendirme yapabilir. 
        > R-CZ-TOPSIS, $O(N \\times M)$ deterministik hesaplama karmaşıklığı ve çift-sıfır ($0_A \\neq 0_I$) cebiriyle 
        > insansız sistem görev bilgisayarlarında açıklanabilir (XAI) bir karar destek katmanı konsepti sunar.
        """
    )

    st.markdown("---")
    st.markdown("### 🌟 Savunma ve Otonom Sistemlerde 5 Potansiyel Entegrasyon Alanı")

    c_def1, c_def2 = st.columns(2)
    with c_def1:
        st.markdown(
            """
            <div class="real-life-card" style="border-left-color: #ef4444; margin-bottom: 10px; padding: 12px 15px;">
                <h4 style="margin-top:0; margin-bottom: 6px; font-size: 0.98rem; color: #991b1b;">1. ⚡ Düşük Hesaplama Karmaşıklığı (O(NM) Edge AI Uyumluluğu)</h4>
                <p style="font-size: 0.88rem; line-height: 1.45; color: #1e293b; margin-bottom: 6px;">Derin öğrenme modelleri gibi ağır GPU'lara ihtiyaç duymaz. Küçük bir ARM/FPGA yongasında deterministik matematiksel formülasyonla hızlı OODA karar döngüleri döndürebilir.</p>
                <div style="background: #fef2f2; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #7f1d1d;">
                    <strong>Konsept Potansiyeli:</strong> İHA, SİHA ve insansız kara/deniz araçlarının görev bilgisayarlarına gömülü C++/Rust kütüphanesi olarak entegre edilebilir.
                </div>
            </div>
            
            <div class="real-life-card" style="border-left-color: #2563eb; margin-bottom: 10px; padding: 12px 15px;">
                <h4 style="margin-top:0; margin-bottom: 6px; font-size: 0.98rem; color: #1e3a8a;">2. 🛡️ Kısmi Sensör Kaybında Dayanıklılık (Graceful Degradation)</h4>
                <p style="font-size: 0.88rem; line-height: 1.45; color: #1e293b; margin-bottom: 6px;">Düşman Jammer veya karıştırması nedeniyle sensörlerin bir kısmı karardığında, R-CZ yalnızca aktif kalan optik/termal sensörlerin alt-uzayında karar desteğini sürdürür.</p>
                <div style="background: #eff6ff; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #1e40af;">
                    <strong>Konsept Potansiyeli:</strong> Sensör kesintilerinde tüm sistemin çökmesi yerine mevcut kanallarla güvenli karar sürekliliği desteklenir.
                </div>
            </div>

            <div class="real-life-card" style="border-left-color: #f59e0b; margin-bottom: 10px; padding: 12px 15px;">
                <h4 style="margin-top:0; margin-bottom: 6px; font-size: 0.98rem; color: #92400e;">3. 🛸 Sürü Sistemlerinde Kaynak ve Görev Taksimi</h4>
                <p style="font-size: 0.88rem; line-height: 1.45; color: #1e293b; margin-bottom: 6px;">Sürüdeki platformların bazılarında sensör hasarı veya batarya düşüşü olduğunda, R-CZ eksik verilerine rağmen her platformun durumunu şeffaf biçimde puanlar.</p>
                <div style="background: #fffbeb; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #92400e;">
                    <strong>Konsept Potansiyeli:</strong> Hasarlı ve tam donanımlı platformların kabiliyetlerine uygun hedeflere yönlendirilmesinde karar vericiye yardımcı olur.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_def2:
        st.markdown(
            """
            <div class="real-life-card" style="border-left-color: #7c3aed; margin-bottom: 10px; padding: 12px 15px;">
                <h4 style="margin-top:0; margin-bottom: 6px; font-size: 0.98rem; color: #5b21b6;">4. 🚀 Eksik İmzalı Aldatıcı Hedeflerin Ayrıştırılması</h4>
                <p style="font-size: 0.88rem; line-height: 1.45; color: #1e293b; margin-bottom: 6px;">Sahte hedefler ve yemler belirli kriterlerde (hız) yüksek görünürken motor izi veya telemetriyi gizleyebilir. R-CZ'nin asimetrik temkin cezası eksik kritik verileri görünür kılar.</p>
                <div style="background: #f5f3ff; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #5b21b6;">
                    <strong>Konsept Potansiyeli:</strong> Mühimmatın şüpheli sahte hedeflere erken harcanması riskini azaltmaya yardımcı olur.
                </div>
            </div>

            <div class="real-life-card" style="border-left-color: #10b981; margin-bottom: 10px; padding: 12px 15px;">
                <h4 style="margin-top:0; margin-bottom: 6px; font-size: 0.98rem; color: #065f46;">5. 🎯 Belirsizlik Altında Tehdit Önceliklendirme ve Karar Desteği</h4>
                <p style="font-size: 0.88rem; line-height: 1.45; color: #065f46;">Transponderı veya kimliklendirmesi (IFF) eksik hedeflerde Hard Gatekeeper eşiği (%50 bilgi barajı) şüpheli temasları işaretleyerek operatör onayına yönlendirir.</p>
                <div style="background: #ecfdf5; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #065f46;">
                    <strong>Konsept Potansiyeli:</strong> Eksik bilgiyle erken angajman veya dost unsurları yanlış sınıflama riskini azaltmayı hedefler.
                </div>
            </div>

            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; border-radius: 10px; padding: 14px 18px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="margin-top: 0; font-weight: 700; font-size: 0.92rem; color: #38bdf8; margin-bottom: 5px;">📋 STANAG ve Sistem Entegrasyon Notu</div>
                <p style="font-size: 0.84rem; line-height: 1.45; opacity: 0.9; margin: 0;">
                    R-CZ-TOPSIS, sensör füzyonu ve Tehdit Değerlendirme & Silah Tahsisi (TEWA) konseptleriyle uyumlu çalışabilecek deterministik bir matematiksel araştırma prototipidir. Kara kutu yapay zekalar yerine her kararın matematiksel adımlarını şeffaf biçimde sunarak karar vericiye açıklanabilir karar desteği sağlar.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==============================================================================
# MODÜL 3: TAKTİK HAVA SAVUNMA RADAR C2 & TEWA KONSOLU
# ==============================================================================
if "3  Hava Savunma C2" in nav_mode:
    st.header("🎯 Taktik Hava Savunma Radar C2 & Tehdit Önceliklendirme (TEWA) Konsolu")
    st.caption("Elektronik Harp & Sensör Karartması Altında Tehdit Değerlendirme ve Angajman Tahsisi (TEWA) Araştırma Konsolu")

    # Radar Veri Setini Yükle
    radar_csv_p = root_dir / "data" / "hava_savunma_radar_tehdit.csv"
    if radar_csv_p.exists():
        r_df = pd.read_csv(radar_csv_p)
        r_alts = (r_df["Hedef_Kodu"] + " (" + r_df["Hedef_Tipi"] + ")").tolist()
        r_crit_names = ["Hız (Mach ↑)", "Vuruş Süresi (sn ↓)", "RCS İzi (m² ↓)", "Açı Sapması (° ↓)", "ESM Karıştırma (dBm ↑)", "Hedef Varlık Kritikliği (↑)"]
        r_types = [CritType.BENEFIT, CritType.COST, CritType.COST, CritType.COST, CritType.BENEFIT, CritType.BENEFIT]
        r_weights = np.array([0.25, 0.25, 0.15, 0.15, 0.10, 0.10])
        r_weights = r_weights / np.sum(r_weights)
        
        r_clean = r_df.drop(columns=["Hedef_Kodu", "Hedef_Tipi"])
        r_n = len(r_alts)
        r_m = len(r_crit_names)
        r_X = np.zeros((r_n, r_m))
        r_Sig = np.full((r_n, r_m), Context.ACTION.value, dtype=object)
        for i_idx in range(r_n):
            for j_idx in range(r_m):
                val_ij = r_clean.iloc[i_idx, j_idx]
                if pd.isna(val_ij) or val_ij == "0_I":
                    r_X[i_idx, j_idx] = 0.0
                    r_Sig[i_idx, j_idx] = Context.INACTION.value
                else:
                    r_X[i_idx, j_idx] = float(val_ij)
                    r_Sig[i_idx, j_idx] = Context.ACTION.value

        # Radar için R-CZ Çözümü
        r_cfg = RCZConfig(w_threshold=0.45, min_active_criteria=2, alpha=0.60)
        r_res, r_exp = RCZTOPSIS(config=r_cfg).explain(r_X, r_Sig, r_weights, r_types, names=r_alts)
        r_sorted = sorted(r_res, key=lambda r: r.rank)

        # Kontrol ve Simülatör Barı
        col_rad_ctrl1, col_rad_ctrl2 = st.columns([2, 1])
        with col_rad_ctrl1:
            st.info("🛰️ **Taktik Durum:** Radar sensörleri yoğun elektronik taarruz (ECM Jamming) ve arazi maskelemesi altında 12 taktik hedef izlemektedir. TGT-12 meteorolojik gürültü olduğundan Gatekeeper tarafından anında elenmelidir.")
        with col_rad_ctrl2:
            radar_filter = st.selectbox("Hedef Filtresi:", ["Tüm Hedefler", "Yalnızca Geçerli Tehditler (Gatekeeper Onaylı)", "Öncelikli Angajman (Top 3)"])

        # Polar PPI Radar Ekranı
        col_ppi, col_threat_list = st.columns([1.3, 1])
        with col_ppi:
            st.markdown("##### 📡 Canlı PPI Plan Position Indicator (360° Taktik Radar)")
            
            # Taktik Koordinat Üretimi (Menzil ve Açı)
            np.random.seed(42)
            angles = [15, 45, 80, 110, 140, 175, 210, 245, 280, 310, 335, 195]
            ranges = [85, 140, 45, 220, 95, 60, 30, 180, 110, 260, 70, 150]
            
            tgt_labels = [r_df.iloc[k]["Hedef_Kodu"] for k in range(r_n)]
            threat_colors = []
            symbol_sizes = []
            
            for k in range(r_n):
                rk_item = next(r for r in r_sorted if r.index == k)
                if rk_item.status != AlternativeStatus.EVALUATED:
                    threat_colors.append("#94a3b8")  # Elenen / Zararsız (Gri)
                    symbol_sizes.append(10)
                elif rk_item.rank == 1:
                    threat_colors.append("#ef4444")  # 1. Tehdit (Kırmızı Flaş)
                    symbol_sizes.append(22)
                elif rk_item.rank <= 3:
                    threat_colors.append("#f97316")  # Yüksek Tehdit (Turuncu)
                    symbol_sizes.append(18)
                else:
                    threat_colors.append("#eab308")  # Orta Tehdit (Sarı)
                    symbol_sizes.append(14)

            fig_polar = go.Figure()
            fig_polar.add_trace(go.Scatterpolar(
                r=ranges,
                theta=angles,
                mode='markers+text',
                text=tgt_labels,
                textposition="top center",
                textfont=dict(size=11, color="white", family="JetBrains Mono"),
                marker=dict(
                    size=symbol_sizes,
                    color=threat_colors,
                    line=dict(color="#ffffff", width=2),
                ),
                hovertemplate="<b>%{text}</b><br>Menzil: %{r} km<br>Kerteriz: %{theta}°<extra></extra>",
            ))

            fig_polar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 300], gridcolor="#1e293b", linecolor="#334155"),
                    angularaxis=dict(direction="clockwise", gridcolor="#1e293b", linecolor="#334155"),
                    bgcolor="#090d16",
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                height=480,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False,
            )
            st.plotly_chart(fig_polar, use_container_width=True)

        with col_threat_list:
            st.markdown("##### 🚀 TEWA Otomatik Angajman ve Sıralama Kuyruğu")
            top_target = r_sorted[0]
            st.error(f"""
            **🚨 1. ANGAJMAN HEDEFİ: {top_target.name}**  
            * Tehdit Skoru: **%{top_target.score * 100:.1f}**  
            * Bilgi Güvenilirliği: **%{int(top_target.support_weight * 100)}**  
            * Savunma Kararı: **Hemen Önleme Füzesi Tahsis Et (Fire Control Lock)**
            """)
            
            radar_table_rows = []
            for r in r_sorted:
                idx_k = r.index
                st_code = "🔴 #1 ÖNCELİK" if r.rank == 1 else (f"🟠 #{r.rank} Kritik" if r.rank <= 3 else (f"🟡 #{r.rank} Takip" if r.rank else "⚪ ELENDİ"))
                radar_table_rows.append({
                    "Hedef": r_df.iloc[idx_k]["Hedef_Kodu"],
                    "Hedef Tipi": r_df.iloc[idx_k]["Hedef_Tipi"][:28] + "...",
                    "Tehdit Skoru": f"%{r.score * 100:.1f}",
                    "Vuruş (sn)": f"{r_df.iloc[idx_k]['Vurus_Suresi_sn']}" if not pd.isna(r_df.iloc[idx_k]['Vurus_Suresi_sn']) else "❓ Yok",
                    "C2 Kararı": st_code,
                })
            st.dataframe(pd.DataFrame(radar_table_rows), use_container_width=True, hide_index=True)

# ==============================================================================
# MODÜL 4: CANLI 'WHAT-IF' DUYARLILIK & MANİPÜLASYON LABORATUVARI
# ==============================================================================
if "4  What-If" in nav_mode:
    st.header("🎛️ Canlı 'What-If' Duyarlılık & Manipülasyon Laboratuvarı")
    st.caption("Aktif Karar Matrisinde Ağırlıkları Değiştirerek Duyarlılığı İnceleyin veya Bir Adayın Maliyetini Gizleyerek Sistemin Epistemik Ceza Tepkisini Test Edin")
    st.info("ℹ️ **Not:** Bu bölüm parametrik duyarlılık (sensitivity) ve stres testi simülasyonudur; kriter ağırlıkları ve hücre karartma durumları anlık olarak kullanıcı tarafından simüle edilmektedir.")

    st.markdown("### 🧪 1. Kriter Ağırlık Duyarlılık Simülatörü (Sensitivity Test)")
    st.markdown("Herhangi bir kriterin ağırlığını anlık olarak değiştirin; sıralamanın ve şampiyonun nasıl değiştiğini izleyin:")
    
    # Kriter kaydırıcıları
    col_w1, col_w2, col_w3 = st.columns(3)
    sim_weights = []
    for c_i, c_nm in enumerate(crit_names):
        cur_w_val = float(weights[c_i])
        with (col_w1 if c_i % 3 == 0 else (col_w2 if c_i % 3 == 1 else col_w3)):
            nw = st.slider(f"{c_nm}:", min_value=0.01, max_value=0.80, value=cur_w_val, step=0.05, key=f"sim_w_{c_i}")
            sim_weights.append(nw)
    
    sim_w_arr = np.array(sim_weights, dtype=np.float64)
    sim_w_arr = sim_w_arr / np.sum(sim_w_arr)

    # Simülasyon R-CZ Koştur
    sim_res, sim_exp = rcz_engine.explain(X, Sigma, sim_w_arr, crit_types, names=alts)
    sim_sorted = sorted(sim_res, key=lambda r: r.rank)
    sim_winner = sim_sorted[0]

    st.markdown("---")
    st.markdown("### 🦹 2. 'Kasıtlı Bilgi Gizleme' (Akerlof Limon) Stres Testi")
    st.write("Aşağıdan bir aday ve gizlenecek maliyet kriteri seçerek eski Klasik TOPSIS'in nasıl etkilendiğini, R-CZ'nin ise asimetrik ceza ile haksız avantajı nasıl sınırlandırdığını canlı görün:")
    
    col_st1, col_st2, col_st3 = st.columns(3)
    with col_st1:
        target_cand_name = st.selectbox("Manipülasyon Yapılacak Aday:", alts, index=0)
        target_idx = alts.index(target_cand_name)
    with col_st2:
        cost_crit_indices = [ci for ci, ct in enumerate(crit_types) if ct == CritType.COST]
        if cost_crit_indices:
            target_cost_crit_idx = st.selectbox("Gizlenecek / Karartılacak Maliyet Kriteri:", cost_crit_indices, format_func=lambda idx: crit_names[idx])
        else:
            target_cost_crit_idx = 0
            st.info("Bu senaryoda maliyet kriteri bulunmuyor.")
    with col_st3:
        do_manipulate = st.checkbox("🚨 Bu Kriteri 'Bilinmiyor / 0_I' Olarak Karart!", value=False)

    if do_manipulate and cost_crit_indices:
        sim_X = X.copy()
        sim_Sig = Sigma.copy()
        sim_X[target_idx, target_cost_crit_idx] = 0.0
        sim_Sig[target_idx, target_cost_crit_idx] = Context.INACTION.value

        # İki yöntemi de manipüle edilmiş matrisle koştur
        m_cls_scores, m_cls_ranks = run_classic_topsis(sim_X, sim_Sig, sim_w_arr, crit_types)
        m_rcz_res, m_rcz_exp = rcz_engine.explain(sim_X, sim_Sig, sim_w_arr, crit_types, names=alts)
        
        m_cand_rcz = next(r for r in m_rcz_res if r.index == target_idx)
        m_cand_cls_sc = m_cls_scores[target_idx] * 100
        m_cand_cls_rk = m_cls_ranks[target_idx]

        st.warning(f"#### 🔎 Manipülasyon Analiz Sonucu: {target_cand_name}")
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.error(f"""
            **🏛️ Klasik TOPSIS Sonucu:**  
            * Eski Yöntem Skoru: **%{m_cand_cls_sc:.1f}**  
            * Eski Yöntem Sıralaması: **#{m_cand_cls_rk}**  
            * *Klasik TOPSIS adayın gizlediği maliyeti 0.0 (bedava) saydığı için adaya haksız puan avantajı sağlayabilir!*
            """)
        with c_res2:
            st.success(f"""
            **🛡️ R-CZ-TOPSIS Asimetrik Cezayı Devreye Aldı!**  
            * R-CZ Nihai Skoru: **%{m_cand_rcz.score * 100:.1f}**  
            * R-CZ Sıralaması: **#{m_cand_rcz.rank}**  
            * Akerlof Ceza Üssü: **κ = {m_rcz_exp.kappa[target_idx]:.2f}** (Maliyet gizlendiği için ceza katsayısı arttı)  
            * *R-CZ epistemik ceza çarpanı (Γ = {m_cand_rcz.penalty_gamma:.2f}) uygulayarak haksız avantajı sınırlandırdı.*
            """)
    else:
        st.info("💡 Yukarıdaki kutucuğu işaretleyerek adayın maliyetini kasıtlı gizleyebilir ve iki modelin tepkisini canlı kıyaslayabilirsiniz.")

# ==============================================================================
# MODÜL 5: SADE VE ANLAŞILIR SİSTEM REHBERİ (PRATİK HAYAT & GERÇEK DÜNYA)
# ==============================================================================
if "5  Sistem Rehberi" in nav_mode:
    st.subheader("💡 Sade ve Anlaşılır Sistem Rehberi: Pratik Hayatta Ne İşe Yarar?")
    st.markdown(
        """
        Bu platform, karmaşık formülleri bir kenara bıraktığımızda **"eksik veya saklanan bilgi karşısında en doğru, en adil ve en güvenli kararı vermek"** için geliştirilmiş yeni nesil bir akıl yürütme motorudur.
        
        Gündelik hayatta ve kamusal ihalelerde karşılaştığımız en büyük açmaz şudur: **Elinizdeki adayların bazı bilgileri eksiktir.**
        Eski yöntemler bu eksikliği ya adayı tamamen yok sayarak ya da sahte sayılar uydurarak geçiştirmeye çalışır ve her iki durumda da büyük zararlara yol açar.
        """
    )

    tab_guide_glossary, tab_guide_faq, tab_guide_examples = st.tabs([
        "📚 Terimler & Kavramlar Sözlüğü (Hard Gatekeeper, Transponder, Epistemik Ceza, Akerlof vb.)",
        "❓ Sıkça Sorulan Sorular (Ceza Nedir? Kriterler Neye Göre Seçilir?)",
        "🏘️ Pratik Hayattan Örnekler & Senaryolar",
    ])

    with tab_guide_glossary:
        st.markdown("### 📚 Kapsamlı Terimler & Kavramlar Sözlüğü (Glossary)")
        st.caption("Sistemde geçen tüm kavramlar, formülleri ve sade vatandaş açıklamalarıyla (Arama ve Kategori Filtreli):")
        render_glossary_component(st, safe_text, key_prefix="guide_glossary")

    with tab_guide_faq:
        st.markdown("### ❓ Merak Edilenler ve Sıkça Sorulan Sorular (Soru - Cevap Rehberi)")
        st.caption("Ceza nedir? Hesaplama neye göre ayarlanır? Kriterler neye göre seçilir? İşte sistemin tüm mantığı:")
        faq_items = get_faq_items()
        for item in faq_items:
            with st.expander(f"{item['category']} | {safe_text(item['question'])}", expanded=True if item["id"] in ("FAQ-01", "FAQ-02", "FAQ-03") else False):
                st.markdown(
                    f"""
                    <div style="background: #eff6ff; border-left: 4px solid #2563eb; padding: 12px 16px; border-radius: 8px; margin-bottom: 14px;">
                        <strong style="color: #1e40af; font-size: 0.92rem;">💡 Kısa ve Net Özet:</strong><br>
                        <span style="color: #1e293b; font-size: 0.90rem; line-height: 1.5;">{safe_text(item['short_answer'])}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(item["full_answer"])

    with tab_guide_examples:
        st.markdown("### 🏘️ Hayatın İçinden 3 Somut Örnekle Sistemin Mantığı")
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            st.markdown(
                """
                <div class="real-life-card" style="border-left-color: #2563eb; padding: 13px 15px;">
                    <h4 style="margin-top:0; font-size: 1.0rem; color: #1e3a8a;">🏠 1. Ev Kiralama Çıkmazı</h4>
                    <p style="font-size: 0.88rem; margin-bottom: 6px;"><strong>Durum:</strong> İki kiralık ev karşılaştırılıyor.</p>
                    <ul style="padding-left: 18px; font-size: 0.86rem; line-height: 1.45; margin-bottom: 8px;">
                        <li><strong>A Evi:</strong> Kira 20.000 TL, yakıt 4.000 TL (Toplam 24.000 TL).</li>
                        <li><strong>B Evi:</strong> Kira 15.000 TL, yakıt <strong>boş / bilinmiyor</strong>.</li>
                    </ul>
                    <div style="background: #fef2f2; border-left: 3px solid #ef4444; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #991b1b; margin-bottom: 6px;">
                        <strong>Eski Sistem:</strong> Boş kutuyu 0 TL sayıp B evini 15.000 TL sanarak 1. yapar. Kışın faturayla kiracı mağdur olur.
                    </div>
                    <div style="background: #ecfdf5; border-left: 3px solid #10b981; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #065f46;">
                        <strong>🛡️ R-CZ Sistemi:</strong> "Yakıtı saklıyor" diyerek şüphe ve asimetrik maliyet cezası keser; haksız şampiyonluğu bozar.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_g2:
            st.markdown(
                """
                <div class="real-life-card" style="border-left-color: #f59e0b; padding: 13px 15px;">
                    <h4 style="margin-top:0; font-size: 1.0rem; color: #92400e;">🚗 2. İkinci El Araba Satın Alma</h4>
                    <p style="font-size: 0.88rem; margin-bottom: 6px;"><strong>Durum:</strong> İki araç karşılaştırılıyor.</p>
                    <ul style="padding-left: 18px; font-size: 0.86rem; line-height: 1.45; margin-bottom: 8px;">
                        <li><strong>Araç 1:</strong> 2021 model, 150 HP, tramer hasarı 40.000 TL.</li>
                        <li><strong>Araç 2:</strong> 2023 model, 200 HP, tramer <strong>girilmemiş (boş)</strong>.</li>
                    </ul>
                    <div style="background: #fef2f2; border-left: 3px solid #ef4444; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #991b1b; margin-bottom: 6px;">
                        <strong>Eski Sistem:</strong> Tramer boş diye hasarı 0 TL sayıp Araç 2'yi şampiyon seçer. Alıcı ağır hasarlı araba alır.
                    </div>
                    <div style="background: #ecfdf5; border-left: 3px solid #10b981; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #065f46;">
                        <strong>🛡️ R-CZ Sistemi:</strong> Hasar beyan etmeyene asimetrik ceza (κ_i) uygular; alıcıyı yanıltıcı ilandan korur.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_g3:
            st.markdown(
                """
                <div class="real-life-card" style="border-left-color: #10b981; padding: 13px 15px;">
                    <h4 style="margin-top:0; font-size: 1.0rem; color: #065f46;">🏛️ 3. Kamu İhalesi & Cihaz Alımı</h4>
                    <p style="font-size: 0.88rem; margin-bottom: 6px;"><strong>Durum:</strong> Hastaneye kritik cihaz alımı.</p>
                    <ul style="padding-left: 18px; font-size: 0.86rem; line-height: 1.45; margin-bottom: 8px;">
                        <li><strong>Firma X:</strong> Cihaz 10M TL, yıllık bakım 1M TL.</li>
                        <li><strong>Firma Y:</strong> Cihaz 6M TL, yıllık bakım <strong>belirtilmemiş</strong>.</li>
                    </ul>
                    <div style="background: #fef2f2; border-left: 3px solid #ef4444; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #991b1b; margin-bottom: 6px;">
                        <strong>Eski Sistem:</strong> Bakımı 0 TL sayıp ihaleyi Firma Y'ye verir. 2 yıl sonra yedek parçadan devlete 15M masraf çıkar.
                    </div>
                    <div style="background: #ecfdf5; border-left: 3px solid #10b981; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #065f46;">
                        <strong>🛡️ R-CZ Sistemi:</strong> Asgari bilgi eşiğiyle (Gatekeeper) saklanan teklifi eler; kamunun zarara uğramasını önler.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("### ⚖️ Sistemin 3 Temel İlkesi (Neden Bu Kadar Güvenilir?)")
        st.markdown(
            """
            1. **Hakkaniyet İlkesi (Haksız İnfazı Önleme):**
               Eğer bir adayın çok güçlü özellikleri varsa ama sadece 1 tane önemsiz bilgisi eksikse, sistem onu çöpe atmaz. Bilinen özelliklerinin hakkını tam olarak verir.
               
            2. **Şüphecilik ve Asimetrik Tedbir İlkesi (Kurnazlığı Cezalandırma):**
               Bir aday avantajlı özelliklerini (beygir gücü, hız, menzil) gururla sergileyip olumsuz özelliklerini (fiyat, arıza oranı, yakıt tüketimi) gizliyorsa, sistem bunu anlar. Saklanan her olumsuz kriter için adaya katlanan bir şüphe cezası keser.
               
            3. **İhtiyat ve Kapı Bekçisi İlkesi (Hard Gatekeeper):**
               Yeterli asgari bilgiye sahip olmayan, kimliği veya özellikleri belirsiz adaylar masaya dahi oturamaz. Örneğin 10 kriterden 8'i boş olan bir adayın şans eseri birinci olmasına asla izin verilmez; doğrudan elenir.
            """
        )

        st.markdown("---")
        st.markdown("### 📊 Eski Sistemler ile R-CZ Sistemi Arasındaki Fark")
        
        citizen_comp = pd.DataFrame([
            {
                "Karşılaşılan Durum": "Bir aday yakıt veya bakım masrafını gizlediğinde",
                "Klasik Eski Yöntem": "Masrafı 0 TL (bedava) sayar ve adayı birinci yapar ❌",
                "Ortalama Dolduran Yöntem": "Herkesin ortalamasını yazar, gerçek dışı uydurur ⚠️",
                "🛡️ Yeni R-CZ Sistemi": "Maliyet saklayana sert ceza keser, haksız avantajı sınırlar ✅"
            },
            {
                "Karşılaşılan Durum": "Bir adayın 10 bilgiden 8'i eksik olduğunda",
                "Klasik Eski Yöntem": "Bilinen 2 bilgisi iyiyse şampiyon ilan edebilir ❌",
                "Ortalama Dolduran Yöntem": "Uydurma sayılarla yapay olarak yarışta tutar ⚠️",
                "🛡️ Yeni R-CZ Sistemi": "Kapı Bekçisi (Gatekeeper) devreye girer, adayı eler ✅"
            },
            {
                "Karşılaşılan Durum": "Çok güçlü bir adayın 1 önemsiz bilgisi eksik olduğunda",
                "Klasik Eski Yöntem": "O kriteri 0 sayıp adayı haksız yere çöpe atar ❌",
                "Ortalama Dolduran Yöntem": "Ortalama değer atayarak adayın puanını düşürür ⚠️",
                "🛡️ Yeni R-CZ Sistemi": "Bilinen gücünü adilce korur, sadece hafif temkin payı bırakır ✅"
            },
            {
                "Karşılaşılan Durum": "Veri uydurma ve sahte sayı türetme",
                "Klasik Eski Yöntem": "Yok ama eksik hücreyi 0.0 kabul eder ❌",
                "Ortalama Dolduran Yöntem": "Sürekli yapay ortalama sayılar üretir ❌",
                "🛡️ Yeni R-CZ Sistemi": "Tek bir yapay sayı dahi uydurmaz (Imputation-Free) ✅"
            }
        ])
        st.dataframe(citizen_comp, use_container_width=True, hide_index=True)


# ==============================================================================
# MODÜL 6: ADIM ADIM MATEMATİKSEL HESAPLAMA DETAYLARI
# ==============================================================================
if "6  Matematik" in nav_mode:
    st.subheader("🔬 R-CZ-TOPSIS Motorunun Matematiksel Ara Hesaplama Matrisleri")
    
    weight_mode_str = "Tarihsel Karşılaştırma — v1.0 Dinamik Yerel Ağırlıklandırma (w'_ij = w_j / W_i)" if config.local_reweighting else "v1.1 Kanonik Varsayılan — Global Ağırlıklı Alt-Uzay İzdüşümü (V_ij = w_j · r_ij)"
    st.info(f"📐 **Aktif Hesaplama Modu:** {weight_mode_str}")
    st.markdown(
        """
        `matematiksel formülasyon.md` şartnamesine göre işletilen tüm ara adımların sayısal dökümü çekirdek motordan doğrudan çekilmiştir:
        """
    )

    # 1. Norm Paydaları
    st.markdown("#### 1. Adım: Sütun Norm Paydaları ($S_j$) ve Vektör Normalizasyonu")
    st.latex(r"S_j = \sqrt{\sum_{k \in \mathcal{A}_j} X_{kj}^2}, \quad r_{ij} = \frac{X_{ij}}{S_j}, \quad V_{ij} = w_j \cdot r_{ij}")
    st.caption(r"Klasik TOPSIS tüm satırları 0 ile toplarken, R-CZ yalnızca ölçülen aktif nesnelerin ($\mathcal{A}_j$) kareler toplamının karekökünü alır.")
    df_norms = pd.DataFrame({
        "Kriter": crit_names,
        "Yön": [ct.value for ct in crit_types],
        "Ağırlık (w_j)": np.round(rcz_expl.weights, 4),
        "Aktif Eleman Sayısı": [int(x) for x in rcz_expl.active_mask.sum(axis=0)],
        "Sütun Norm Paydası (S_j)": np.round(rcz_expl.S, 4),
    })
    st.dataframe(df_norms, use_container_width=True, hide_index=True)

    # 2. Gatekeeper ve Bilgi Kapsama
    st.markdown(f"#### 2. Adım: Hard Gatekeeper Süzgeci ($W_i \\ge {w_threshold:.2f}$ ve $m_i^* \\ge {min_active_criteria}$)")
    st.latex(r"W_i = \sum_{j \in J_i^*} w_j \ge W_{\text{threshold}}, \quad m_i^* = |J_i^*| \ge m_{\text{min}}")
    st.caption("Toplam bilgi kapsamı barajın altında kalan alternatifler, sahte alarm ve şans eseri birincilikleri önlemek için anında elenir.")
    gate_status = [
        "✅ GEÇTİ (Valid)" if ok else f"❌ ELENDİ (Bilgi < %{int(w_threshold * 100)} veya < {min_active_criteria} Kriter)"
        for ok in rcz_expl.valid_gate
    ]
    df_gate = pd.DataFrame({
        "Aday": alts,
        "Aktif Kriter Sayısı (m_i*)": rcz_expl.m_active,
        "Bilgi Kapsama Oranı (W_i)": np.round(rcz_expl.W_cov, 4),
        "Hard Gatekeeper Kararı": gate_status,
    })
    st.dataframe(df_gate, use_container_width=True, hide_index=True)

    # 3. İdeal Noktalar
    st.markdown("#### 3. Adım: Alt-Uzay İdeal ($v^+$) ve Anti-İdeal ($v^-$) Çözüm Noktaları")
    st.latex(r"v_j^+ = \begin{cases} \max_{k \in \mathcal{A}_j} V_{kj}, & j \in \text{Benefit} \\ \min_{k \in \mathcal{A}_j} V_{kj}, & j \in \text{Cost} \end{cases}, \quad v_j^- = \begin{cases} \min_{k \in \mathcal{A}_j} V_{kj}, & j \in \text{Benefit} \\ \max_{k \in \mathcal{A}_j} V_{kj}, & j \in \text{Cost} \end{cases}")
    df_ideals = pd.DataFrame({
        "Kriter": crit_names,
        "Yön": [ct.value for ct in crit_types],
        "İdeal Çözüm (v+)": np.round(rcz_expl.v_plus, 4),
        "Anti-İdeal Çözüm (v-)": np.round(rcz_expl.v_minus, 4),
    })
    st.dataframe(df_ideals, use_container_width=True, hide_index=True)

    # 4. Mesafeler, Asimetrik Ceza ve Nihai Skor
    st.markdown("#### 4. ve 5. Adım: Alt-Uzay Mesafeleri ($D^+, D^-$), Asimetrik Ceza ($\\kappa_i, \\Gamma_i$) ve Nihai Skor ($C^*$)")
    st.latex(r"D_i^+ = \sqrt{\sum_{j \in J_i^*} (V_{ij} - v_j^+)^2}, \quad D_i^- = \sqrt{\sum_{j \in J_i^*} (V_{ij} - v_j^-)^2}, \quad C_{\text{base}, i} = \frac{D_i^-}{D_i^+ + D_i^-}")
    st.latex(r"\kappa_i = 1.0 + \sum_{j \notin J_i^*, j \in \text{Cost}} w_j, \quad \Gamma_i = (W_i)^{\alpha \cdot \kappa_i}, \quad C_i^* = C_{\text{base}, i} \cdot \Gamma_i")
    st.caption("Adayın eksik maliyet/risk kriterleri (Cost) varsa κ_i üssü artar, temkin çarpanı Γ_i küçülür; böylece eksik maliyet bilgisinden kaynaklanabilecek haksız avantaj bastırılmaya çalışılır (ancak aşırı baskın fayda durumlarında mutlak engelleme garantisi vermez).")
    step5_rows = []
    for r in rcz_by_idx:
        idx = r.index
        d_p = rcz_expl.d_plus[idx]
        d_m = rcz_expl.d_minus[idx]
        m_cost = rcz_expl.missing_cost[idx]
        kap = rcz_expl.kappa[idx]
        gam = rcz_expl.gamma[idx]

        step5_rows.append({
            "Aday": r.name,
            "D+ (İdeal Mesafe)": f"{d_p:.4f}" if not np.isnan(d_p) else "— (Elendi)",
            "D- (Anti-İdeal Mesafe)": f"{d_m:.4f}" if not np.isnan(d_m) else "— (Elendi)",
            "Temel Skor (C_base)": f"{r.base_score:.4f}",
            "Eksik Maliyet Ağırlığı": f"{m_cost:.2f}",
            "Maliyet Üssü (κ_i)": f"{kap:.2f}",
            "Güvenilirlik Çarpanı (Γ_i)": f"{gam:.4f}",
            "Nihai Skor (C* = C_base × Γ)": f"{r.score:.4f}",
            "Sıra": f"#{r.rank}" if r.rank else "—",
        })
    st.dataframe(pd.DataFrame(step5_rows), use_container_width=True, hide_index=True)

# ==============================================================================
# MODÜL 7: GERÇEK VERİ SETLERİ & CSV İNDİRME
# ==============================================================================
if "7  Veri Kütüphanesi" in nav_mode:
    st.subheader("📚 Veri Kütüphanesi, Sentetik/Gerçek Veri Ayrımı ve Doğrulama Raporu")
    st.markdown(
        """
        Bilimsel dürüstlük ve tekrarlanabilirlik ilkesi uyarınca, sistemde kullanılan tüm veri setlerinin kökeni, 
        **gerçek / sentetik ayrımı**, eksik veri oluşturma yöntemi ve bilinen sınırlamaları tam şeffaflıkla aşağıda sunulmuştur:
        """
    )

    meta_path = root_dir / "data" / "DATASET_METADATA.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f_meta:
                meta_data = json.load(f_meta)
            meta_rows = []
            for ds in meta_data.get("datasets", []):
                meta_rows.append({
                    "Veri Seti Başlığı": ds.get("title", ""),
                    "Veri Türü": "🟢 Gerçek Benchmark" if not ds.get("is_synthetic") else "🟠 Sentetik Modelleme",
                    "Alan": ds.get("domain", ""),
                    "Kaynak & Lisans": f"{ds.get('source_name', '')} ({ds.get('license', '')})",
                    "Eksiklik Yöntemi": ds.get("induction_method", ""),
                    "Bilinen Sınırlamalar": ds.get("known_limitations", ""),
                })
            st.dataframe(pd.DataFrame(meta_rows), use_container_width=True, hide_index=True)
        except Exception as err:
            st.warning(f"Metadata tablosu okunamadı: {err}")

    st.markdown("---")
    st.markdown("### 🌐 Gerçek Kurumsal Veri Doğrulama Hatları")
    st.caption(
        "Aşağıdaki kaynaklar resmi açık veri sağlayıcılarıdır. Aktarım durumu ayrı bir acquisition status "
        "manifestiyle gösterilir; her yerel dosya lisans, erişim zamanı ve SHA-256 provenance kaydıyla tutulur."
    )
    acquisition_status = {}
    status_path = root_dir / "data" / "EXTERNAL_ACQUISITION_STATUS.json"
    if status_path.exists():
        with status_path.open("r", encoding="utf-8") as status_file:
            acquisition_status = {
                item["source_id"]: item
                for item in json.load(status_file).get("acquisitions", [])
            }
    external_rows = []
    for spec in SOURCE_SPECS.values():
        status = acquisition_status.get(spec.source_id, {})
        external_rows.append({
            "Hat": "🏛️ Kamu ihale" if spec.domain.startswith("public_procurement") else "⚙️ Mühendislik/risk",
            "Kaynak": spec.title,
            "Aktarım": status.get("status", "not_started"),
            "Yerel dosyalar": ", ".join(status.get("local_files", [])) or "—",
            "Yayıncı": spec.publisher,
            "Format": spec.raw_format,
            "Eksiklik notu": spec.missingness_note,
            "Sonuç/etiket notu": spec.outcome_note,
            "Resmi URL": spec.source_url,
        })
    st.dataframe(pd.DataFrame(external_rows), use_container_width=True, hide_index=True)
    st.info(
        "TED ve World Bank hattı kamu ihale verisini; NASA ve NREL hattı mühendislik/risk verisini temsil eder. "
        "Bir kaynaktaki her boş hücre MNAR değildir; doğal eksiklik, yapısal eksiklik ve kontrollü maskeleme ayrı "
        "provenance değerleriyle raporlanır."
    )

    st.markdown("### 📊 NASA–TED R-CZ Karşılaştırmalı Çalıştırma Raporu")
    st.caption(
        "İki gerçek veri hattı aynı R-CZ çekirdeğiyle ayrı ayrı çalıştırılır. Skorlar farklı alanların "
        "ölçeklerini değil, her veri setinin kendi içindeki göreli sıralamayı ifade eder; doğrudan birbirleriyle "
        "yarıştırılamaz."
    )
    external_report_rows = []
    external_rank_rows = []

    def _run_external_report(
        label: str,
        source_note: str,
        frame: pd.DataFrame,
        criterion_columns: list[str],
        criterion_types: list[CritType],
        criterion_weights: np.ndarray,
        alternative_names: list[str],
        outcome_note: str,
    ) -> None:
        matrix = {
            "X": frame[criterion_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float),
            "Sigma": np.where(frame[criterion_columns].notna(), Context.ACTION.value, Context.INACTION.value),
        }
        report_results, _ = RCZTOPSIS(config=config).explain(
            matrix["X"],
            matrix["Sigma"],
            criterion_weights,
            criterion_types,
            names=alternative_names,
        )
        evaluated = [result for result in report_results if result.status == AlternativeStatus.EVALUATED]
        ranked = sorted(evaluated, key=lambda result: result.rank or 10**9)
        external_report_rows.append({
            "Hat": label,
            "Alternatif sayısı": len(report_results),
            "Kriter sayısı": len(criterion_columns),
            "Değerlendirilen": len(evaluated),
            "Elendi": len(report_results) - len(evaluated),
            "En yüksek skor": round(ranked[0].score, 4) if ranked else None,
            "En iyi alternatif": ranked[0].name if ranked else "—",
            "Outcome durumu": outcome_note,
            "Kaynak notu": source_note,
        })
        for result in ranked[:5]:
            external_rank_rows.append({
                "Hat": label,
                "Sıra": result.rank,
                "Alternatif": result.name,
                "R-CZ skoru": round(result.score, 4),
                "Bilgi kapsama W_i": round(result.support_weight, 4),
                "Aktif kriter": result.active_criteria_count,
            })

    ted_report_path = root_dir / "data" / "ted_sample.csv"
    if ted_report_path.exists():
        ted_report = pd.read_csv(ted_report_path)
        ted_grouped = (
            ted_report.groupby("procedureType", dropna=False)
            .agg(
                notice_count=("publicationNumber", "count"),
                notice_type_diversity=("noticeType", "nunique"),
                form_type_diversity=("formType", "nunique"),
            )
            .reset_index()
        )
        _run_external_report(
            "TED Open Data",
            "2024-11-06 tarihli 100 duyuru; prosedür grubu özeti.",
            ted_grouped,
            ["notice_count", "notice_type_diversity", "form_type_diversity"],
            [CritType.BENEFIT] * 3,
            np.array([0.50, 0.25, 0.25]),
            ted_grouped["procedureType"].fillna("Bilinmeyen prosedür").astype(str).tolist(),
            "Award/tedarikçi sonucu yok",
        )

    nasa_report_path = root_dir / "data" / "nasa_cmapss_fd001_decision_matrix.csv"
    if nasa_report_path.exists():
        nasa_report = pd.read_csv(nasa_report_path)
        nasa_criteria = [
            "final_cycle",
            "mean_sensor_2",
            "mean_sensor_3",
            "mean_sensor_4",
            "mean_sensor_7",
            "mean_sensor_11",
        ]
        from src.rcz_topsis.nasa_validation import NASA_GROUNDED_TYPES, validate_nasa_health_ranking
        _run_external_report(
            "NASA C-MAPSS FD001",
            "100 test motoru; commit'i sabitlenmiş kamuya açık ayna.",
            nasa_report,
            nasa_criteria,
            NASA_GROUNDED_TYPES,
            np.array([0.25, 0.15, 0.15, 0.15, 0.15, 0.15]),
            [f"Motor {int(unit_id)}" for unit_id in nasa_report["unit_id"]],
            "RUL bağımsız outcome olarak mevcut (Spearman rho = +0.60)",
        )

    if external_report_rows:
        st.dataframe(pd.DataFrame(external_report_rows), use_container_width=True, hide_index=True)
        st.markdown("#### İlk 5 R-CZ sonucu")
        st.dataframe(pd.DataFrame(external_rank_rows), use_container_width=True, hide_index=True)
        st.warning(
            "Bu rapor karar desteği ve yöntem doğrulaması içindir. TED tablosu tedarikçi kazananı üretmez; "
            "NASA sıralaması da bir regresyon RUL tahmini değildir. Sıralama ile bağımsız outcome arasındaki "
            "ilişki, aşağıdaki fizik temelli doğrulama protokolüyle incelenmektedir."
        )

        st.markdown("---")
        st.markdown("### 🔬 NASA C-MAPSS FD001: Fizik Temelli Doğrulama ve RUL Outcome Analizi")
        st.caption(
            "Türbofan gaz yolu aşınma termodinamiğine göre kriter yönleri bağlandığında, "
            "R-CZ sağlık sıralaması ile bağımsız Kalan Faydalı Ömür (RUL) outcome'ı arasındaki istatistiksel ilişki:"
        )

        nasa_val = validate_nasa_health_ranking()
        col_nv1, col_nv2, col_nv3, col_nv4 = st.columns(4)
        with col_nv1:
            st.metric(
                "Spearman Sıra Korelasyonu (ρ)",
                f"+{nasa_val['spearman_rho']:.4f}",
                f"p = {nasa_val['spearman_pvalue']:.2e}",
            )
        with col_nv2:
            st.metric(
                "Kendall Sıra Korelasyonu (τ)",
                f"+{nasa_val['kendall_tau']:.4f}",
                f"p = {nasa_val['kendall_pvalue']:.2e}",
            )
        with col_nv3:
            ci_l, ci_h = nasa_val["bootstrap_rho_ci95"]
            st.metric(
                "Bootstrap %95 Güven Aralığı (ρ)",
                f"[{ci_l:.2f}, {ci_h:.2f}]",
                "2000 tekrar",
            )
        with col_nv4:
            st.metric(
                "Naif Ters Yön Baseline'ı (ρ)",
                f"{nasa_val['spearman_rho_inverted_baseline']:.4f}",
                "Tümü BENEFIT seçilirse",
                delta_color="inverse",
            )

        col_n_top, col_n_bot = st.columns(2)
        with col_n_top:
            st.markdown("##### 🟢 R-CZ'ye Göre En Sağlıklı 10 Motor (Top 10)")
            st.write(
                f"**Ortalama Kalan Ömür (RUL):** `{nasa_val['top_10']['mean_rul']:.1f} çevrim` "
                f"(min: {nasa_val['top_10']['min_rul']}, max: {nasa_val['top_10']['max_rul']}, std: {nasa_val['top_10']['std_rul']:.1f})"
            )
            top_df = pd.DataFrame({
                "Sıra": nasa_val["top_10"]["ranks"],
                "Motor ID": [f"Motor {u}" for u in nasa_val["top_10"]["engine_ids"]],
                "R-CZ Skoru": nasa_val["top_10"]["scores"],
                "Gerçek RUL (Çevrim)": nasa_val["top_10"]["ruls"],
            })
            st.dataframe(top_df, use_container_width=True, hide_index=True)

        with col_n_bot:
            st.markdown("##### 🔴 R-CZ'ye Göre En Yıpranmış 10 Motor (Bottom 10)")
            st.write(
                f"**Ortalama Kalan Ömür (RUL):** `{nasa_val['bottom_10']['mean_rul']:.1f} çevrim` "
                f"(min: {nasa_val['bottom_10']['min_rul']}, max: {nasa_val['bottom_10']['max_rul']}, std: {nasa_val['bottom_10']['std_rul']:.1f})"
            )
            bot_df = pd.DataFrame({
                "Sıra": nasa_val["bottom_10"]["ranks"],
                "Motor ID": [f"Motor {u}" for u in nasa_val["bottom_10"]["engine_ids"]],
                "R-CZ Skoru": nasa_val["bottom_10"]["scores"],
                "Gerçek RUL (Çevrim)": nasa_val["bottom_10"]["ruls"],
            })
            st.dataframe(bot_df, use_container_width=True, hide_index=True)

        st.info(
            "💡 **Domain Doğrulaması:** Top 10 motorun ortalama kalan ömrü **116.9 çevrim** iken, "
            "Bottom 10 motorun ortalama kalan ömrü **37.8 çevrime** kadar düşmektedir (79.1 çevrimlik net ayrışma). "
            "Kriter yönleri tümü fayda yapıldığında korelasyon -0.60'a dönmektedir; bu da sensör yönlerinin "
            "alan uzmanı tarafından fizik yasalarına göre belirlenmesinin hayati önemini kanıtlamaktadır."
        )

    st.markdown("---")

    uci_csv_path = root_dir / "data" / "uci_automobile_missing_benchmark.csv"
    radar_csv_path = root_dir / "data" / "hava_savunma_radar_tehdit.csv"
    geopol_csv_path = root_dir / "data" / "jeopolitik_catisma_istihbarat.csv"
    ev_csv_path = root_dir / "data" / "elektrikli_arac_benchmark.csv"
    uav_csv_path = root_dir / "data" / "iha_savunma_benchmark.csv"
    sup_csv_path = root_dir / "data" / "tedarikci_secimi_benchmark.csv"
    vc_csv_path = root_dir / "data" / "startuplar_girisim_sermayesi.csv"
    bio_csv_path = root_dir / "data" / "klinik_ilac_biyoteknoloji.csv"
    energy_csv_path = root_dir / "data" / "yenilenebilir_enerji_santrali.csv"
    ted_sample_path = root_dir / "data" / "ted_sample.csv"
    nasa_decision_matrix_path = root_dir / "data" / "nasa_cmapss_fd001_decision_matrix.csv"

    st.markdown("#### 🏛️ Dünyaca Ünlü Resmi Akademik Stres Testi:")
    col_u1, col_u2 = st.columns([1.5, 1])
    with col_u1:
        st.markdown("**UCI Machine Learning Repository: 1985 Automobile Eksik Veri Benchmarkı (25 Gerçek Araç)**")
        st.caption("Kaynak: University of California Irvine (UCI) Repository (Schlimmer 1987). Gerçek eksik fiyat ve risk verisi içerir.")
        st.write("Klasik TOPSIS'in ve Ortalama Atamanın 'Eksik Fiyatlı Porsche'yi ($0 sanarak) haksız yere üst sıralara taşıdığı, R-CZ modelinin ise eksik maliyet için uyguladığı asimetrik ceza ile haksız avantajı sınırlandırdığı örnek benchmark veri setidir.")
    with col_u2:
        if uci_csv_path.exists():
            st.download_button("📥 UCI Resmi Benchmark CSV İndir", uci_csv_path.read_bytes(), "uci_automobile_missing_benchmark.csv", "text/csv")

    st.markdown("---")
    col_v0a, col_v0b = st.columns(2)
    with col_v0a:
        st.markdown("#### 🎯 1. Askeri Radar: Hava Savunma Tehdit Değerlendirme (TEWA)")
        st.caption("Kaynak: Literatürdeki tehdit değerlendirme yaklaşımlarından esinlenen sentetik taktik modelleme; Hava Savunma C2 simülasyonu.")
        st.write("12 Taktik Hedef (Hipersonik, Stealth, Kamikaze İHA, Jammer). Eksik IFF ve karıştırma verisi içerir.")
        if radar_csv_path.exists():
            st.download_button("📥 Radar TEWA CSV İndir", radar_csv_path.read_bytes(), "hava_savunma_radar_tehdit.csv", "text/csv")
    with col_v0b:
        st.markdown("#### 🌐 2. Jeopolitik Erken Uyarı: Sınır İntikali & Saldırı Olasılığı")
        st.caption("Kaynak: Stratejik İstihbarat Füzyonu, Açık Kaynak OSINT, Uydu IMINT ve SIGINT Analizi.")
        st.write("10 Kriz Hattı, 6 İstihbarat Kriteri. Bulut örtüsü nedeniyle eksik uydu ve telsiz sessizliği içerir.")
        if geopol_csv_path.exists():
            st.download_button("📥 Jeopolitik Erken Uyarı CSV İndir", geopol_csv_path.read_bytes(), "jeopolitik_catisma_istihbarat.csv", "text/csv")

    st.markdown("---")
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        st.markdown("#### ⚡ 3. Elektrikli Araç (EV 2026)")
        st.caption("Kaynak: EPA & WLTP Testleri, ADAC E-Katalog, Üretici Bültenleri.")
        st.write("14 Model, 8 Teknik Kriter. Eksik şarj ve kış tüketimi hücreleri içerir.")
        if ev_csv_path.exists():
            st.download_button("📥 EV CSV İndir", ev_csv_path.read_bytes(), "elektrikli_arac_benchmark.csv", "text/csv")
    with col_v2:
        st.markdown("#### ✈️ 4. İHA Savunma Sanayii")
        st.caption("Kaynak: Jane's All the World's Aircraft, SIPRI, SSB Katalogları.")
        st.write("10 Taktik/MALE İHA, 5 Kriter. Gizli maliyet ve menzil eksikleri içerir.")
        if uav_csv_path.exists():
            st.download_button("📥 İHA CSV İndir", uav_csv_path.read_bytes(), "iha_savunma_benchmark.csv", "text/csv")
    with col_v3:
        st.markdown("#### 🏭 5. Endüstriyel Tedarikçi")
        st.caption("Kaynak: ISO 9001 / ISO 14064 Raporları, CIPS Standartları.")
        st.write("8 Tedarikçi, 6 Kriter. Karbon ayak izi ve özel fiyat teklifi eksikleri içerir.")
        if sup_csv_path.exists():
            st.download_button("📥 Tedarikçi CSV İndir", sup_csv_path.read_bytes(), "tedarikci_secimi_benchmark.csv", "text/csv")

    st.markdown("")
    col_v4, col_v5, col_v6 = st.columns(3)
    with col_v4:
        st.markdown("#### 🚀 6. Girişim Sermayesi (VC)")
        st.caption("Kaynak: VC Due Diligence Raporları, Kuluçka Merkezi Metrikleri.")
        st.write("10 Girişim, 7 Finansal/Büyüme Kriteri. Erken aşama gelir/churn eksikleri içerir.")
        if vc_csv_path.exists():
            st.download_button("📥 Startup CSV İndir", vc_csv_path.read_bytes(), "startuplar_girisim_sermayesi.csv", "text/csv")
    with col_v5:
        st.markdown("#### 🏥 7. Klinik İlaç & Biyoteknoloji")
        st.caption("Kaynak: FDA/EMA Onkolojik Klinik Araştırmalar Bülteni, PubMed.")
        st.write("10 İlaç Adayı, 6 Tıbbi Kriter. Olgunlaşmamış sağkalım ve üretim maliyeti eksikleri içerir.")
        if bio_csv_path.exists():
            st.download_button("📥 Klinik CSV İndir", bio_csv_path.read_bytes(), "klinik_ilac_biyoteknoloji.csv", "text/csv")
    with col_v6:
        st.markdown("#### 🌱 8. Yenilenebilir Enerji Sahası")
        st.caption("Kaynak: TEİAŞ Kapasite Raporları, EPDK Santral Lisansları, IRENA.")
        st.write("10 Proje Sahası, 6 Mühendislik Kriteri. Kesinleşmemiş şebeke ve izin süreleri içerir.")
        if energy_csv_path.exists():
            st.download_button("📥 Enerji CSV İndir", energy_csv_path.read_bytes(), "yenilenebilir_enerji_santrali.csv", "text/csv")

    st.markdown("")
    col_external_ted, col_external_nasa = st.columns(2)
    with col_external_ted:
        st.markdown("#### 🇪🇺 9. TED Open Data")
        st.caption("100 resmi duyuru; prosedür kapsamı özeti. Award/tedarikçi sonucu içermez.")
        if ted_sample_path.exists():
            st.download_button("📥 TED örnek CSV indir", ted_sample_path.read_bytes(), "ted_sample.csv", "text/csv")
    with col_external_nasa:
        st.markdown("#### 🚀 10. NASA C-MAPSS FD001")
        st.caption("100 test motoru, 6 gözlenen kriter ve ayrı RUL outcome etiketi.")
        if nasa_decision_matrix_path.exists():
            st.download_button("📥 NASA karar matrisi indir", nasa_decision_matrix_path.read_bytes(), "nasa_cmapss_fd001_decision_matrix.csv", "text/csv")

    st.markdown("---")
    st.markdown("#### 🔍 Aktif Senaryonun Ham Karar Matrisi:")
    raw_cells = []
    for i in range(n_alts):
        row = []
        for j in range(n_crits):
            if Sigma[i, j] == Context.ACTION.value:
                row.append(f"{X[i, j]:g}")
            else:
                row.append("❓ Eksik / 0_I")
        raw_cells.append(row)
    st.dataframe(pd.DataFrame(raw_cells, index=alts, columns=crit_names), use_container_width=True)

# ==============================================================================
# TAB 5: TÜM KARAR DESTEK SİSTEMLERİ (MCDM) CANLI KIYAS & AVANTAJ / DEZAVANTAJ
# ==============================================================================
if "8  MCDM" in nav_mode:
    st.subheader("⚖️ Çok Kriterli Karar Verme (MCDM) Sistemleri Canlı Kıyaslama & Avantaj / Dezavantaj Analizi")
    st.markdown(
        "Bu bölümde aktif senaryodaki karar matrisi, literatürdeki **6 farklı karar destek sistemi** "
        "(R-CZ-TOPSIS, Klasik TOPSIS, Ortalama Imputation TOPSIS, VIKOR, PROMETHEE II ve SAW) "
        "tarafından aynı anda canlı olarak çözülmüş; sonuçlar yan yana kıyaslanarak yöntemlerin R-CZ modeline göre "
        "tüm **avantaj ve dezavantajları** çıkarılmıştır."
    )

    # 1. Canlı Çoklu Karar Liderlik Tablosu
    st.markdown("### 📊 1. Canlı Çoklu Karar Motoru: Yöntemlerin Sıralama ve Skor Kıyası")
    st.caption("Aktif senaryodaki her aday için 6 farklı karar motorunun ürettiği nihai başarı puanı ve parantez içinde sıralaması listelenmiştir:")

    multi_mcdm_rows = []
    for r in rcz_sorted:
        idx = r.index
        c_sc = classic_scores[idx] * 100
        c_rk = classic_ranks[idx]
        m_sc = mean_scores[idx] * 100
        m_rk = mean_ranks[idx]
        v_sc = vikor_scores[idx] * 100
        v_rk = vikor_ranks[idx]
        p_sc = promethee_scores[idx] * 100
        p_rk = promethee_ranks[idx]
        s_sc = saw_scores[idx] * 100
        s_rk = saw_ranks[idx]

        ranks_arr = np.array([r.rank, c_rk, m_rk, v_rk, p_rk, s_rk])
        rank_std = float(np.std(ranks_arr))

        if rank_std < 0.8:
            cons_str = "🟢 Tam Uyuşum (Konsensüs)"
        elif rank_std < 2.0:
            cons_str = "🟡 Yüksek Uyum"
        elif rank_std < 3.5:
            cons_str = "🟠 Farklı Yaklaşım"
        else:
            cons_str = "🔴 Yüksek Çelişki / Sapma"

        multi_mcdm_rows.append({
            "R-CZ Sırası": f"#{r.rank} {'🥇' if r.rank==1 else ('🥈' if r.rank==2 else ('🥉' if r.rank==3 else ''))}",
            "Aday": r.name,
            "🛡️ R-CZ (v1.1)": f"%{r.score*100:.1f} (#{r.rank})",
            "🏛️ Klasik TOPSIS": f"%{c_sc:.1f} (#{c_rk})",
            "📊 Ortalama TOPSIS": f"%{m_sc:.1f} (#{m_rk})",
            "🎯 VIKOR (1-Q)": f"%{v_sc:.1f} (#{v_rk})",
            "🌊 PROMETHEE II": f"%{p_sc:.1f} (#{p_rk})",
            "📐 SAW (Ağırlıklı Top.)": f"%{s_sc:.1f} (#{s_rk})",
            "Yöntemler Arası Uyum": cons_str,
        })
    multi_mcdm_html = pd.DataFrame(multi_mcdm_rows).to_html(
        index=False,
        classes="rcz-comparison",
        border=0,
        escape=True,
    )
    st.markdown(
        f'<div class="rcz-comparison-wrap">{multi_mcdm_html}</div>',
        unsafe_allow_html=True,
    )

    # 2. Çoklu Karar Grafiği
    st.markdown("---")
    st.markdown("### 📈 2. Çoklu Yöntem Skor Dağılımı ve Kıyaslama Grafiği")
    fig_multi = go.Figure()
    fig_multi.add_trace(go.Bar(
        x=[r.name for r in rcz_sorted],
        y=[r.score * 100 for r in rcz_sorted],
        name="🛡️ R-CZ-TOPSIS",
        marker=dict(color="#1d4ed8", line=dict(color="#1e40af", width=1)),
        hovertemplate="<b>%{x}</b><br>R-CZ: %{y:.1f}%<extra></extra>",
    ))
    fig_multi.add_trace(go.Bar(
        x=[r.name for r in rcz_sorted],
        y=[classic_scores[r.index] * 100 for r in rcz_sorted],
        name="🏛️ Klasik TOPSIS",
        marker=dict(color="#94a3b8", line=dict(color="#64748b", width=1)),
        hovertemplate="<b>%{x}</b><br>Klasik: %{y:.1f}%<extra></extra>",
    ))
    fig_multi.add_trace(go.Bar(
        x=[r.name for r in rcz_sorted],
        y=[mean_scores[r.index] * 100 for r in rcz_sorted],
        name="📊 Ortalama Doldurma",
        marker=dict(color="#0d9488", line=dict(color="#0f766e", width=1)),
        hovertemplate="<b>%{x}</b><br>Ortalama: %{y:.1f}%<extra></extra>",
    ))
    fig_multi.add_trace(go.Bar(
        x=[r.name for r in rcz_sorted],
        y=[vikor_scores[r.index] * 100 for r in rcz_sorted],
        name="🎯 VIKOR (1 - Q)",
        marker=dict(color="#f59e0b", line=dict(color="#d97706", width=1)),
        hovertemplate="<b>%{x}</b><br>VIKOR: %{y:.1f}%<extra></extra>",
    ))
    fig_multi.add_trace(go.Bar(
        x=[r.name for r in rcz_sorted],
        y=[promethee_scores[r.index] * 100 for r in rcz_sorted],
        name="🌊 PROMETHEE II",
        marker=dict(color="#a855f7", line=dict(color="#9333ea", width=1)),
        hovertemplate="<b>%{x}</b><br>PROMETHEE II: %{y:.1f}%<extra></extra>",
    ))
    fig_multi.add_trace(go.Bar(
        x=[r.name for r in rcz_sorted],
        y=[saw_scores[r.index] * 100 for r in rcz_sorted],
        name="📐 SAW",
        marker=dict(color="#10b981", line=dict(color="#059669", width=1)),
        hovertemplate="<b>%{x}</b><br>SAW: %{y:.1f}%<extra></extra>",
    ))
    fig_multi.update_layout(
        barmode="group",
        xaxis_title="Alternatifler",
        yaxis_title="Normalize Başarı Skoru (%)",
        height=480,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248, 250, 252, 0.5)",
        margin=dict(l=40, r=20, t=30, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(226,232,240,0.8)",
            borderwidth=1,
        ),
        xaxis=dict(gridcolor="rgba(226, 232, 240, 0.6)"),
        yaxis=dict(gridcolor="rgba(226, 232, 240, 0.6)", range=[0, 105]),
    )
    st.plotly_chart(fig_multi, use_container_width=True)

    # 3. Yöntem Bazında Derinlemesine Avantaj ve Dezavantaj Analiz Dosyaları
    st.markdown("---")
    st.markdown("### 🔍 3. TOPSIS Dahil Tüm Sistemlerin R-CZ'ye Göre Avantaj ve Dezavantaj Analizi")
    st.caption("Aşağıdaki açılır menüden herhangi bir karar destek yöntemini seçerek matematiksel formülünü, bizim sistemimize göre nerede üstün olduğunu, nerede çöktüğünü ve R-CZ'nin ona karşı sağladığı üstünlüğü inceleyebilirsiniz:")

    selected_method_name = st.selectbox(
        "İncelemek İstediğiniz Karar Destek Sistemini Seçin:",
        list(MCDM_METHOD_DOSSIERS.keys()),
        index=0
    )
    dossier = MCDM_METHOD_DOSSIERS[selected_method_name]

    st.markdown(f"#### 📌 {dossier['tam_ad']}")
    st.caption(f"📚 Referans / Literatür: {dossier['literatur']}")
    st.latex(dossier["matematiksel_ozet"])

    if selected_method_name == "R-CZ-TOPSIS":
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.success("##### 🌟 R-CZ-TOPSIS Temel Güçlü Yönleri ve İnovasyonları")
            for adv in dossier["rcz_avantajlari"]:
                st.markdown(f"* {adv}")
        with col_r2:
            st.warning("##### ⚠️ R-CZ-TOPSIS'in Bilinen Sınırları ve İyileştirme Alanları")
            for lim in dossier["rcz_sinirlari"]:
                st.markdown(f"* {lim}")
    else:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.success(f"##### 🟢 Bu Yöntemin R-CZ-TOPSIS'e Göre Avantajları (Nerede Daha İyi?)")
            for adv in dossier["rcz_ye_gore_avantajlari"]:
                st.markdown(f"* {adv}")
        with col_m2:
            st.error(f"##### 🔴 Bu Yöntemin R-CZ-TOPSIS'e Göre Dezavantajları ve Zafiyetleri (Nerede Çöküyor?)")
            for dis in dossier["rcz_ye_gore_zafiyetleri"]:
                st.markdown(f"* {dis}")

    # 4. Kapsamlı Karşılaştırma Matrisi (Özet Tablo)
    st.markdown("---")
    st.markdown("#### 🏆 4. Tüm Çok Kriterli Karar Verme (MCDM) Yöntemlerinin Karşılaştırma Matrisi")
    
    mcdm_comp_data = [
        {
            "Yöntem": "🛡️ R-CZ-TOPSIS (Bizim Modelimiz)",
            "Eksik Veri Kabiliyeti": "🟢 Mükemmel (Doğal alt-uzay metriği)",
            "Yapay Veri Uydurma": "🟢 Sıfır (Asla uydurma değer üretmez)",
            "Epistemik Güvenlik Cezası": "🟢 Var (Asimetrik maliyet cezası Γ_i)",
            "Asgari Bilgi Barajı (Gatekeeper)": "🟢 Var (W_i ≥ 0.50 otomatik eleme)",
            "Hesaplama Hızı": "⚡ O(N × M) - Mikrosaniye (Radar uyumlu)",
            "En Uygun Olduğu Alan": "Eksik verili mühendislik, radar & istihbarat"
        },
        {
            "Yöntem": "🏛️ Klasik TOPSIS (Hwang & Yoon 1981)",
            "Eksik Veri Kabiliyeti": "🔴 Zayıf (Eksik hücreyi 0.0 kabul eder)",
            "Yapay Veri Uydurma": "🟡 Yok (Ancak 0 atayarak ekseni bozar)",
            "Epistemik Güvenlik Cezası": "🔴 Yok (Maliyet gizleyeni birinci yapar)",
            "Asgari Bilgi Barajı (Gatekeeper)": "🔴 Yok (1 kriterle şampiyon olabilir)",
            "Hesaplama Hızı": "⚡ O(N × M) - Çok Hızlı",
            "En Uygun Olduğu Alan": "Verinin %100 eksiksiz olduğu durumlar"
        },
        {
            "Yöntem": "📊 Ortalama Doldurmalı TOPSIS",
            "Eksik Veri Kabiliyeti": "🟡 Orta (Sütun ortalaması atar)",
            "Yapay Veri Uydurma": "🔴 Yüksek (Gerçek dışı sentetik sayı yazar)",
            "Epistemik Güvenlik Cezası": "🔴 Yok (Varyansı yapay olarak düşürür)",
            "Asgari Bilgi Barajı (Gatekeeper)": "🔴 Yok",
            "Hesaplama Hızı": "⚡ O(N × M) - Hızlı",
            "En Uygun Olduğu Alan": "MCAR rastgele veri kayıplı istatistik"
        },
        {
            "Yöntem": "🎯 VIKOR (Opricovic 1998)",
            "Eksik Veri Kabiliyeti": "🔴 Zayıf (Kutup f*, f- değerleri sapar)",
            "Yapay Veri Uydurma": "🟢 Yok (En kötü göreli mesafe sayar)",
            "Epistemik Güvenlik Cezası": "🟡 Kısmi (Maksimum Pişmanlık R_i)",
            "Asgari Bilgi Barajı (Gatekeeper)": "🔴 Yok",
            "Hesaplama Hızı": "⚡ O(N × M) - Hızlı",
            "En Uygun Olduğu Alan": "Uzlaşık ve karşıt paydaşlı müzakereler"
        },
        {
            "Yöntem": "🌊 PROMETHEE II (Brans & Vincke 1985)",
            "Eksik Veri Kabiliyeti": "🔴 Çok Zayıf (İkili farklar kilitlenir)",
            "Yapay Veri Uydurma": "🟢 Yok (Fark hesaplanamaz)",
            "Epistemik Güvenlik Cezası": "🔴 Yok (Net akış bozulur)",
            "Asgari Bilgi Barajı (Gatekeeper)": "🔴 Yok",
            "Hesaplama Hızı": "🐢 O(N² × M) - Çift karşılaştırma",
            "En Uygun Olduğu Alan": "Kriter bazlı kesin tercih eşikleri (p, q)"
        },
        {
            "Yöntem": "🌲 AHP (Saaty 1980)",
            "Eksik Veri Kabiliyeti": "🔴 Desteklemez (İkili matris çöker)",
            "Yapay Veri Uydurma": "🔴 Yok (Ancak anket zorunluluğu var)",
            "Epistemik Güvenlik Cezası": "🟡 Kısmi (Tutarlılık Oranı CR < 0.10)",
            "Asgari Bilgi Barajı (Gatekeeper)": "🔴 Yok",
            "Hesaplama Hızı": "🐢 O(N² × M) - Bilişsel yük çok yüksek",
            "En Uygun Olduğu Alan": "Niteliksel/sübjektif hiyerarşik anketler"
        },
        {
            "Yöntem": "⚖️ ELECTRE Serisi (Roy 1968)",
            "Eksik Veri Kabiliyeti": "🔴 Çok Zayıf (Uyum/Uyumsuzluk tanımsız)",
            "Yapay Veri Uydurma": "🟢 Yok",
            "Epistemik Güvenlik Cezası": "🟡 Kısmi (Kesin veto eşiği)",
            "Asgari Bilgi Barajı (Gatekeeper)": "🔴 Yok",
            "Hesaplama Hızı": "🐢 O(N² × M) - Graf analizi",
            "En Uygun Olduğu Alan": "Kesin veto hakkı istenen kurumsal eleme"
        },
        {
            "Yöntem": "📐 SAW / WSM (Churchman 1954)",
            "Eksik Veri Kabiliyeti": "🔴 Zayıf (Eksik hücre adayı sıfırlar)",
            "Yapay Veri Uydurma": "🟢 Yok",
            "Epistemik Güvenlik Cezası": "🔴 Yok (Tam telafi hatası)",
            "Asgari Bilgi Barajı (Gatekeeper)": "🔴 Yok",
            "Hesaplama Hızı": "⚡ O(N × M) - En Hızlı",
            "En Uygun Olduğu Alan": "Hızlı, kaba ve doğrusal puanlamalar"
        },
    ]

    # HTML tablo, Streamlit'in canvas tabanlı dataframe yüzeyinden farklı olarak
    # açık/koyu tema ve yatay kaydırmayı aynı şekilde destekler.
    mcdm_html = pd.DataFrame(mcdm_comp_data).to_html(
        index=False,
        classes="rcz-comparison",
        border=0,
        escape=True,
    )
    st.markdown(
        f'<div class="rcz-comparison-wrap">{mcdm_html}</div>',
        unsafe_allow_html=True,
    )

    # 5. MCDM Seçim Rehberi
    st.markdown("---")
    st.markdown("#### 🧭 5. Hangi Durumda Hangi Karar Destek Sistemi Tercih Edilmelidir?")
    guide_df = pd.DataFrame([
        {
            "Karar Probleminin Yapısı": "Sayısal mühendislik/ihale verisi + Eksik kriterler / Veri yokluğu",
            "Önerilen En İyi Yöntem": "🛡️ R-CZ-TOPSIS",
            "Gerekçe": "Eksik veriyi yapay sayı uydurmadan çözen, haksız infazı önleyen ve maliyet gizleme kaynaklı haksız avantajı asimetrik cezayla sınırlandıran modeldir."
        },
        {
            "Karar Probleminin Yapısı": "Sübjektif anketler, marka algısı, nitel hiyerarşik hedefler",
            "Önerilen En İyi Yöntem": "🌲 AHP (Analitik Hiyerarşi Süreci)",
            "Gerekçe": "1-9 Saaty ikili karşılaştırma ölçeği ve tutarlılık oranı (CR) ile soyut insan yargılarını en iyi sayısallaştıran yöntemdir."
        },
        {
            "Karar Probleminin Yapısı": "Karşıt paydaşların uzlaşması, çoğunluk faydası ile bireysel pişmanlık dengesi",
            "Önerilen En İyi Yöntem": "🎯 VIKOR",
            "Gerekçe": "Grup faydası (S) ve maksimum bireysel pişmanlık (R) dengesi ile uzlaşık çözüm üretir."
        },
        {
            "Karar Probleminin Yapısı": "Karar vericinin farksızlık (q) ve kesin tercih (p) eşikleri olan katı problemler",
            "Önerilen En İyi Yöntem": "🌊 PROMETHEE II",
            "Gerekçe": "Kriter bazında 6 farklı tercih eğrisi tanımlayarak insan psikolojisini non-compensatory modeller."
        },
        {
            "Karar Probleminin Yapısı": "Kriterlerde kesin veto hakkı istenen kurumsal filtrelemeler",
            "Önerilen En İyi Yöntem": "⚖️ ELECTRE Serisi",
            "Gerekçe": "Uyum ve uyumsuzluk eşikleriyle bir kriteri çok kötü olan adaya kesin veto uygular."
        },
        {
            "Karar Probleminin Yapısı": "Hiçbir hücresi eksik olmayan (%100 tam) standart mühendislik kıyaslaması",
            "Önerilen En İyi Yöntem": "🏛️ Klasik TOPSIS veya R-CZ-TOPSIS",
            "Gerekçe": "Veri tam olduğunda R-CZ ile Klasik TOPSIS matematiksel olarak %100 özdeştir; basit ve hızlıdır."
        },
    ])
    st.dataframe(guide_df, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 6: BİLİMSEL MAKALE, METODOLOJİ & AKADEMİK KAYNAKÇA
# ==============================================================================
if "9  Makale" in nav_mode:
    st.header("📚 Bilimsel Makale: R-CZ-TOPSIS Metodolojisi, Matematiksel Kanıtlar ve Literatür Kaynakçası")
    st.caption("TÜBİTAK 2209-A / Üniversite Araştırma Projesi Formatında Hazırlanmış Tam Metin ve Doğrulama Raporu")
    
    st.markdown(
        """
        > **Makale Başlığı:** Contextual Zero Cebiri (CZ-Algebra) ile Eksik Verili Çok Kriterli Karar Verme: R-CZ-TOPSIS Yöntemi ve Asimetrik Epistemik Güvenlik Modeli  
        > **Yazarlar & Proje Ekibi:** R-CZ Araştırma Grubu (2026)  
        > **Anahtar Kelimeler:** MCDM, TOPSIS, Contextual Zero Algebra, Eksik Veri (Missing Data), Asimetrik Maliyet Cezalandırması, Akerlof Limon Piyasası, Hard Gatekeeper.
        """
    )

    st.markdown("---")
    st.markdown("### 📄 1. Özet (Abstract)")
    col_ab1, col_ab2 = st.columns(2)
    with col_ab1:
        st.markdown("**🇹🇷 Türkçe Özet:**")
        st.write(
            "Çok Kriterli Karar Verme (MCDM) sistemleri, gerçek dünya uygulamalarında eksik ve karartılmış veri "
            "sorunuyla sıklıkla karşılaşmaktadır. Klasik TOPSIS'in bazı eksik veri uygulamaları eksik hücreyi sıfır "
            "kabul ederek kaliteli adayları haksız yere geriye atabilir; maliyet veya fiyat kriteri eksik olan adaylar "
            "da yanlış biçimde avantajlı görünebilir. Mean Imputation (ortalama atama) ise karar matrisine yapay "
            "değerler ekler. Bu çalışmada, proje içi çalışma adı olan Contextual Zero Algebra (CZ-Algebra) çerçevesine "
            "dayanan R-CZ-TOPSIS yöntemi önerilmiştir. Model, her alternatifin bilinen alt-uzayındaki "
            "izdüşümü üzerinden yapay veri uydurmadan (imputation-free) Öklid mesafesini hesaplamakta; asgari bilgi eşiğini "
            "(Hard Gatekeeper) geçemeyen adayları otomatik olarak değerlendirme dışı bırakmakta ve asimetrik bilgi "
            "çerçevesinden esinlenen ceza çarpanı (Γ_i) ile maliyet bilgisi eksikliğini skora yansıtmaktadır. "
            "UCI 1985 Automobile verisi ve sentetik Monte Carlo deneyleri prototipi değerlendirmek için kullanılmıştır; "
            "sonuçlar genel üstünlük veya ceza mekanizmasının her durumda etkinliği kanıtı değildir."
        )
    with col_ab2:
        st.markdown("**🇬🇧 English Abstract:**")
        st.write(
            "Multi-Criteria Decision Making (MCDM) problems frequently suffer from missing, unobserved, or intentionally "
            "withheld data. Some classical TOPSIS implementations can penalize high-performing candidates by treating missing "
            "values as absolute zeros and can make alternatives withholding cost criteria appear too favorable. "
            "Mean imputation introduces synthetic values. We propose R-CZ-TOPSIS, a project-specific framework using the "
            "working term Contextual Zero Algebra (CZ-Algebra). It computes imputation-free Euclidean distances within candidate-specific "
            "observed subspaces, enforces a regulatory Hard Gatekeeper threshold, and applies an asymmetric epistemic penalty (Γ_i) "
            "motivated by asymmetric-information theory. Evaluation on the UCI Automobile benchmark and synthetic Monte Carlo "
            "simulations is exploratory; it does not demonstrate universal superiority or eliminate manipulation incentives."
        )

    st.markdown("---")
    st.markdown("### 🔬 2. Bilimsel Doğrulama Protokolü (Validation Protocol)")
    st.markdown(
        r"""
        Karşılaştırmalar, karar teorisi literatüründe (Little & Rubin 2019, *Statistical Analysis with Missing Data*) 
        kabul görmüş **Sentetik Dejenerasyon ve Monte Carlo Doğrulama Protokolü** ile yürütülmüştür:
        
        1. **Zemin Gerçekliği (Ground Truth):** Hiçbir hücresi eksik olmayan tam karar matrisi ($X$) üzerinden ideal sıralama ($\sigma_{\text{GT}}$) hesaplanır.
        2. **Kontrollü Veri Bozulması:** Karar matrisine %10, %30 ve %50 oranlarında kontrollü **MCAR** (Missing Completely at Random), **MAR** (Missing at Random) ve kasıtlı maliyet gizleme **MNAR** (Missing Not at Random) kayıpları enjekte edilebilir. Bu sayfadaki sabit tablo önceki MCAR/MNAR koşularını gösterir; güncel benchmark motoru MAR'ı da destekler.
        3. **İstatistiksel Metrikler:** Üretilen sıralamaların zemin gerçekliği ile uyumu **Spearman Sıra Korelasyon Katsayısı ($\rho$)** ve **Kendall Tau ($\tau$)** üzerinden tekrarlanabilir Monte Carlo koşularıyla ölçülür. Tek bir sentetik protokol, gerçek dünya genellemesi veya yöntem üstünlüğü kanıtı değildir.

        **Karşılaştırma kapsamı:** Kodlanmış benchmark artık klasik sıfır doldurma, ortalama
        doldurma, ihtiyatlı en-kötü değer baseline'ı, gözlenen-altuzay yerel ağırlıklı TOPSIS,
        cezasız R-CZ altuzayı, R-CZ v1.1 ve tarihsel yerel R-CZ v1.0 yöntemlerini aynı protokolde
        ölçer. En-kötü ve yerel baseline'lar açık ve yeniden üretilebilir karşılaştırma
        referanslarıdır; belirli bir makalenin birebir implementasyonu olarak sunulmaz.
        Mahmoudi ve arkadaşlarının Fuzzy TOPSIS-OPA yöntemi ile Ben Othman–Ben Yahia'nın
        imputasyon değerlendirme yöntemi literatür kaydı olarak incelenmiş, ancak prototipte
        birebir uygulanmış yöntemler arasında gösterilmemiştir.

        **İstatistiksel raporlama:** MAR ve MNAR koşularında her tekrar aynı sentetik veri ve
        eksiklik maskesi üzerinde eşleştirilir. Güncel benchmark, R-CZ'ye göre paired
        Spearman/Kendall farkını, yüzde 2.5–97.5 bootstrap güven aralığını ve iki taraflı
        sign-flip randomization p-değerini üretir. Aynı mekanizma içindeki yöntem ve kayıp
        oranı karşılaştırmalarında Holm-düzeltilmiş p-değeri de raporlanır. Bunlar sentetik
        protokol içindeki fark ölçüleridir; gerçek veri genellemesi değildir. İstatistiksel
        anlamlılık, pratik etkinin veya karar kalitesinin tek başına kanıtı olarak yorumlanmaz.
        """
    )

    st.markdown("---")
    st.markdown("### 📊 3. Monte Carlo Deneysel Doğrulama Tablosu (MCAR & MNAR)")
    st.caption("20 alternatif ve 6 kriterli sentetik matrisler üzerinde her hücre kaybı için 100 bağımsız tekrarın ortalama Spearman ρ ve Kendall τ değerleri:")

    col_mc1, col_mc2 = st.columns(2)
    with col_mc1:
        st.markdown("#### 🎲 Rastgele Veri Kaybı (MCAR)")
        mcar_table_data = [
            {"Kayıp Oranı": "%10", "Yöntem": "🏛️ Klasik TOPSIS (Eksik = 0)", "Spearman ρ": "0.780 ± 0.022", "Kendall τ": "0.658 ± 0.022"},
            {"Kayıp Oranı": "%10", "Yöntem": "📊 Ortalama Doldurma", "Spearman ρ": "0.932 ± 0.010", "Kendall τ": "0.833 ± 0.016"},
            {"Kayıp Oranı": "%10", "Yöntem": "📐 R-CZ Alt-Uzay (α = 0)", "Spearman ρ": "0.922 ± 0.012", "Kendall τ": "0.822 ± 0.017"},
            {"Kayıp Oranı": "%10", "Yöntem": "🛡️ R-CZ v1.1 (α = 0.50)", "Spearman ρ": "0.884 ± 0.015", "Kendall τ": "0.775 ± 0.018"},
            {"Kayıp Oranı": "%30", "Yöntem": "🏛️ Klasik TOPSIS (Eksik = 0)", "Spearman ρ": "0.496 ± 0.038", "Kendall τ": "0.370 ± 0.030"},
            {"Kayıp Oranı": "%30", "Yöntem": "📊 Ortalama Doldurma", "Spearman ρ": "0.780 ± 0.021", "Kendall τ": "0.618 ± 0.022"},
            {"Kayıp Oranı": "%30", "Yöntem": "📐 R-CZ Alt-Uzay (α = 0)", "Spearman ρ": "0.759 ± 0.024", "Kendall τ": "0.605 ± 0.024"},
            {"Kayıp Oranı": "%30", "Yöntem": "🛡️ R-CZ v1.1 (α = 0.50)", "Spearman ρ": "0.689 ± 0.026", "Kendall τ": "0.533 ± 0.024"},
            {"Kayıp Oranı": "%50", "Yöntem": "🏛️ Klasik TOPSIS (Eksik = 0)", "Spearman ρ": "0.355 ± 0.036", "Kendall τ": "0.251 ± 0.027"},
            {"Kayıp Oranı": "%50", "Yöntem": "📊 Ortalama Doldurma", "Spearman ρ": "0.663 ± 0.031", "Kendall τ": "0.504 ± 0.027"},
            {"Kayıp Oranı": "%50", "Yöntem": "📐 R-CZ Alt-Uzay (α = 0)", "Spearman ρ": "0.628 ± 0.034", "Kendall τ": "0.478 ± 0.028"},
            {"Kayıp Oranı": "%50", "Yöntem": "🛡️ R-CZ v1.1 (α = 0.50)", "Spearman ρ": "0.576 ± 0.031", "Kendall τ": "0.426 ± 0.024"},
        ]
        st.dataframe(pd.DataFrame(mcar_table_data), use_container_width=True, hide_index=True)

    with col_mc2:
        st.markdown("#### 🎯 Kasıtlı Maliyet Gizleme (MNAR)")
        mnar_table_data = [
            {"Kayıp Oranı": "%10", "Yöntem": "🏛️ Klasik TOPSIS (Eksik = 0)", "Spearman ρ": "0.642 ± 0.037", "Kendall τ": "0.509 ± 0.032"},
            {"Kayıp Oranı": "%10", "Yöntem": "📊 Ortalama Doldurma", "Spearman ρ": "0.890 ± 0.011", "Kendall τ": "0.763 ± 0.016"},
            {"Kayıp Oranı": "%10", "Yöntem": "📐 R-CZ Alt-Uzay (α = 0)", "Spearman ρ": "0.875 ± 0.014", "Kendall τ": "0.750 ± 0.017"},
            {"Kayıp Oranı": "%10", "Yöntem": "🛡️ R-CZ v1.1 (α = 0.50)", "Spearman ρ": "0.863 ± 0.016", "Kendall τ": "0.733 ± 0.019"},
            {"Kayıp Oranı": "%30", "Yöntem": "🏛️ Klasik TOPSIS (Eksik = 0)", "Spearman ρ": "0.429 ± 0.036", "Kendall τ": "0.311 ± 0.027"},
            {"Kayıp Oranı": "%30", "Yöntem": "📊 Ortalama Doldurma", "Spearman ρ": "0.763 ± 0.021", "Kendall τ": "0.595 ± 0.021"},
            {"Kayıp Oranı": "%30", "Yöntem": "📐 R-CZ Alt-Uzay (α = 0)", "Spearman ρ": "0.731 ± 0.023", "Kendall τ": "0.568 ± 0.022"},
            {"Kayıp Oranı": "%30", "Yöntem": "🛡️ R-CZ v1.1 (α = 0.50)", "Spearman ρ": "0.692 ± 0.025", "Kendall τ": "0.534 ± 0.022"},
            {"Kayıp Oranı": "%50", "Yöntem": "🏛️ Klasik TOPSIS (Eksik = 0)", "Spearman ρ": "0.291 ± 0.038", "Kendall τ": "0.203 ± 0.028"},
            {"Kayıp Oranı": "%50", "Yöntem": "📊 Ortalama Doldurma", "Spearman ρ": "0.627 ± 0.031", "Kendall τ": "0.470 ± 0.026"},
            {"Kayıp Oranı": "%50", "Yöntem": "📐 R-CZ Alt-Uzay (α = 0)", "Spearman ρ": "0.599 ± 0.033", "Kendall τ": "0.450 ± 0.026"},
            {"Kayıp Oranı": "%50", "Yöntem": "🛡️ R-CZ v1.1 (α = 0.50)", "Spearman ρ": "0.556 ± 0.034", "Kendall τ": "0.416 ± 0.027"},
        ]
        st.dataframe(pd.DataFrame(mnar_table_data), use_container_width=True, hide_index=True)

    st.info(
        "💡 **Deneysel Bulguların Yorumu:**\n"
        "* **Klasik Sıfır Atama:** %30 eksiklikte korelasyon 0.429'a çökmekte; eksik hücreli adayı keyfi olarak saf dışı bırakmaktadır.\n"
        "* **Ortalama Doldurma:** Görünüşte yüksek korelasyon verse de sisteme sentetik veri uydurmakta ve gerçek varyansı bozmaktadır.\n"
        "* **R-CZ-TOPSIS:** Hiçbir yapay veri uydurmadan (imputation-free) alt-uzay geometrisiyle yüksek sıra kararlılığı sağlamakta ve asimetrik maliyet cezası (κ_i) ile kötü niyetli maliyet gizlemenin getireceği haksız avantajı sınırlandırmayı hedeflemektedir."
    )

    st.markdown("---")
    st.markdown("### 🔬 3.2. Gerçek Veri Doğrulaması: NASA C-MAPSS FD001 Üzerinde Kontrollü MAR / MNAR Stres Testi")
    st.caption(
        "Sentetik rastgele matris yerine gerçek mühendislik verisi (100 test motoru, 6 doğrulanmış kriter ve gerçek RUL etiketi) "
        "üzerinde %10, %25 ve %40 eksiklik enjeksiyonuyla yürütülen stres testi sonuçları:"
    )

    nasa_bench_file = root_dir / "data" / "nasa_cmapss_stress_benchmark.json"
    if nasa_bench_file.exists():
        import json
        with open(nasa_bench_file, "r", encoding="utf-8") as f:
            nasa_bench_data = json.load(f)

        bench_df = pd.DataFrame(nasa_bench_data)

        tab_mcar, tab_mar, tab_mnar = st.tabs(["🎲 MCAR (Rastgele Kayıp)", "📈 MAR (Bağlantılı Kayıp)", "🎯 MNAR (Maliyet Gizleme)"])

        def _format_bench_view(sub_df):
            display_rows = []
            for _, r in sub_df.iterrows():
                p_holm = r.get("rho_gt_delta_pvalue_holm")
                p_str = f"{p_holm:.4f}" if p_holm is not None and not np.isnan(p_holm) else "Referans (R-CZ)"
                display_rows.append({
                    "Kayıp": f"%{int(r['kayip']*100)}",
                    "Yöntem": r["yontem"],
                    "GT Sıra Uyumu (ρ ± CI)": f"{r['rho_gt']:.3f} ± {r['rho_gt_ci95']:.3f}",
                    "RUL Outcome Uyumu (ρ)": f"{r['rho_rul']:.3f} ± {r['rho_rul_ci95']:.3f}",
                    "Δ (Yöntem - R-CZ)": f"{r['rho_gt_delta_vs_rcz']:+.3f}",
                    "Holm Düzeltilmiş p": p_str,
                })
            return pd.DataFrame(display_rows)

        with tab_mcar:
            st.markdown("##### Gerçek Veride MCAR Sonuçları")
            st.dataframe(_format_bench_view(bench_df[bench_df["mekanizma"] == "MCAR"]), use_container_width=True, hide_index=True)

        with tab_mar:
            st.markdown("##### Gerçek Veride MAR Sonuçları (Gözlenen Kriter Bağımlı Kayıp)")
            st.dataframe(_format_bench_view(bench_df[bench_df["mekanizma"] == "MAR"]), use_container_width=True, hide_index=True)

        with tab_mnar:
            st.markdown("##### Gerçek Veride MNAR Sonuçları (Yüksek Aşınma / Maliyet Sensörlerini Gizleme)")
            st.dataframe(_format_bench_view(bench_df[bench_df["mekanizma"] == "MNAR"]), use_container_width=True, hide_index=True)

        st.info(
            r"""📌 **Bilimsel Metodoloji ve TÜBİTAK Hakem Notu:**
* **Klasik Sıfır İnfazı:** Klasik sıfır atama (`klasik_sifir`) gerçek veride %25 kayıpta 0.533'e, %40 kayıpta 0.368'e çökmektedir ($p < 0.015$).
* **Ortalama Atamanın Doğası:** Ortalama doldurma (`klasik_ortalama`), MCAR'da dağılım ortalamasını enjekte ettiği için tam matris sırasını matematiksel olarak yakından izler görünmektedir; fakat karar desteği açısından adayın gerçek riskini gizlemekte ve yapay homojenlik üretmektedir.
* **R-CZ'nin Epistemik Tercihi:** R-CZ-TOPSIS, eksik veriye ceza uygulayarak ($\Gamma_i = W_i^{\alpha \cdot \kappa_i}$) naif korelasyon yerine **karar güvenliğini ve Akerlof limon piyasası direncini** önceler. Gerçek kalan ömür (RUL) ile olan pozitif korelasyonunu (0.43 - 0.53) tüm eksiklik mekanizmalarında kararlı biçimde korur."""
        )

    st.markdown("---")
    st.markdown("### 📐 4. Matematiksel Formülasyon ve İspatlar")
    st.markdown(
        r"""
        #### 4.1. Vektör Normalizasyonu ve Alt-Uzay Ağırlıklandırması
        Yalnızca ölçülmüş aktif nesneler kümesi ($\mathcal{A}_j$) üzerinden sütun normu alınır:
        $$S_j = \sqrt{\sum_{k \in \mathcal{A}_j} X_{kj}^2}, \quad r_{ij} = \frac{X_{ij}}{S_j}, \quad V_{ij} = w_j \cdot r_{ij}$$

        #### 4.2. Hard Gatekeeper Süzgeci
        Asgari bilgi barajını geçemeyen alternatifler diskalifiye edilir:
        $$W_i = \sum_{j \in J_i^*} w_j \ge W_{\text{threshold}}, \quad m_i^* = |J_i^*| \ge m_{\text{min}}$$

        #### 4.3. Alt-Uzay Öklid Mesafeleri ve Temel Göreli Yakınlık
        $$D_i^+ = \sqrt{\sum_{j \in J_i^*} (V_{ij} - v_j^+)^2}, \quad D_i^- = \sqrt{\sum_{j \in J_i^*} (V_{ij} - v_j^-)^2}$$
        $$C_{\text{base}, i} = \frac{D_i^-}{D_i^+ + D_i^-}$$

        #### 4.4. Akerlof Asimetrik Maliyet Cezası ve Nihai Karar Skoru
        $$\kappa_i = 1.0 + \sum_{j \notin J_i^*, j \in \text{Cost}} w_j, \quad \Gamma_i = (W_i)^{\alpha \cdot \kappa_i}$$
        $$C_i^* = C_{\text{base}, i} \cdot \Gamma_i$$
        
        *Asimetrik Maliyet Cezalandırması İlkesi:* Maliyet kriterini saklayan bir alternatifin $\kappa_i$ üssü artacağından, gizlenen her maliyet adayın ceza çarpanını ($\Gamma_i$) katlanarak düşürür; böylece eksik bilgi arkasına saklanarak haksız avantaj elde etme teşviki önemli ölçüde sınırlandırılır (aşırı yüksek fayda üstünlüklerinde tam koruma için Hard Gatekeeper ve kurumsal ihale/askeri profil eşikleri birlikte işletilir).
        """
    )

    st.markdown("---")
    st.markdown("### 🌟 5. R-CZ-TOPSIS: Literatür Durumu ve Savunulabilir Katkı")
    st.markdown(
        r"""
        #### 🔎 Literatür taramasının sonucu
        **“R-CZ-TOPSIS” ve “Contextual Zero Algebra (CZ-Algebra)” için bağımsız, hakemli veya
        indekslenmiş bir yayın kaydı tespit edilmemiştir.** Bu adlar bu proje içinde kullanılan
        çalışma adlarıdır; yerleşik bir cebir teorisi veya kabul edilmiş bir MCDM standardı gibi
        sunulmamalıdır. “İlk”, “literatürde yok” ve “tamamen yeni” ifadeleri yayınlanmış sistematik
        tarama ve öncelik kanıtı olmadan kullanılmamalıdır.

        Eksik verili MCDM ve TOPSIS üzerine mevcut çalışmalar vardır. Örneğin Mahmoudi ve
        arkadaşları, eksik değerli büyük ölçekli MCDM için Fuzzy TOPSIS-OPA yaklaşımını
        incelemiştir. Bu nedenle R-CZ'nin yeniliği, eksik veri problemini ilk kez ele alması
        değildir.

        ---
        #### ✅ Bu prototipin şu an savunulabilir katkısı

        * **1. Açık bir durum modeli:** Ölçülmüş gerçek sıfır ile ölçülmemiş/eylemsiz hücreyi
          ($0_A$ ve $0_I$) veri şemasında ayrı durumlar olarak temsil eder. Bu, bu kod tabanındaki
          uygulama kararını açıklaştırır; tek başına yeni bir cebir teorisi kanıtlamaz.
        * **2. Belirli bir formülasyonun uçtan uca uygulanması:** Alternatifin gözlemlenen
          kriterleri üzerinde global ağırlıklı alt-uzay mesafesi, bilgi kapsamı eşiği ve
          $\Gamma_i = W_i^{\alpha\kappa_i}$ cezası tek bir denetlenebilir çekirdekte birleştirilmiştir.
        * **3. Tam veri geriye dönük uyumluluk hedefi:** Tam veri durumunda klasik TOPSIS ile
          eşdeğerlik testlerle kontrol edilmiştir; bu, yeni yöntemin üstün olduğunu göstermez.
        * **4. Denetlenebilir karşılaştırma protokolü:** MCAR, MAR ve MNAR sentetik senaryoları,
          Spearman/Kendall ölçümleri ve bilinen sınırlamalar kod ve testlerle görünürdür.

        #### ⚠️ Katkı iddiasının sınırı
        Mevcut benchmarklarda ortalama imputasyonlu TOPSIS bazı senaryolarda R-CZ'den daha yüksek
        sıra korelasyonu üretmiştir. Bu nedenle bu prototip, “R-CZ her durumda daha iyi” veya
        “maliyet gizlemeyi kesin olarak engeller” sonucunu desteklemez. Gerçek literatür katkısı
        sayılabilmesi için kaynak taraması, yöntemler arası adil deneyler, güven aralıkları,
        gerçek/anonimleştirilmiş veri ve hakem değerlendirmesi gerekir.
        """
    )

    st.markdown("---")
    st.markdown("### 📚 6. Akademik Kaynakça (References)")
    st.markdown(
        """
        * **[Hwang & Yoon, 1981]** Hwang, C. L., & Yoon, K. (1981). *Multiple Attribute Decision Making: Methods and Applications*. Springer-Verlag, Berlin/Heidelberg.
        * **[R-CZ çalışma taslağı, 2026]** R-CZ-TOPSIS ve CZ-Algebra: Bu proje içi çalışma adıdır; bağımsız hakemli yayın veya doğrulanmış literatür kaydı değildir.
        * **[Akerlof, 1970]** Akerlof, G. A. (1970). *The Market for 'Lemons': Quality Uncertainty and the Market Mechanism*. The Quarterly Journal of Economics, 84(3), 488-500.
        * **[Little & Rubin, 2019]** Little, R. J. A., & Rubin, D. B. (2019). *Statistical Analysis with Missing Data (3rd Edition)*. John Wiley & Sons, New Jersey.
        * **[Mahmoudi et al., 2021]** Mahmoudi, A., Deng, X., Javed, S. A., & Yuan, J. (2021). *Large-scale multiple criteria decision-making with missing values: project selection through TOPSIS-OPA*. Journal of Ambient Intelligence and Humanized Computing. [doi:10.1007/s12652-020-02649-w](https://doi.org/10.1007/s12652-020-02649-w)
        * **[Behzadian et al., 2012]** Behzadian, M., et al. (2012). *A state-of the-art survey of TOPSIS applications*. Expert Systems with Applications, 39(17), 13051-13069. [doi:10.1016/j.eswa.2012.04.055](https://doi.org/10.1016/j.eswa.2012.04.055)
        * **[Chen, 2000]** Chen, C. T. (2000). *Extensions of the TOPSIS for group decision-making under fuzzy environment*. Fuzzy Sets and Systems, 114(1), 1-9.
        * **[Saaty, 1980]** Saaty, T. L. (1980). *The Analytic Hierarchy Process: Planning, Priority Setting, Resource Allocation*. McGraw-Hill, New York.
        * **[Opricovic, 1998]** Opricovic, S. (1998). *Multicriteria Optimization of Civil Engineering Systems*. Faculty of Civil Engineering, Belgrade.
        * **[Brans & Vincke, 1985]** Brans, J. P., & Vincke, P. (1985). *A preference ranking organisation method: The PROMETHEE method for MCDM*. Management Science, 31(6), 647-656.
        * **[Roy, 1968]** Roy, B. (1968). *Classement et choix en présence de points de vue multiples*. Revue Française d'Informatique et de Recherche Opérationnelle, 2(8), 57-75.
        """
    )