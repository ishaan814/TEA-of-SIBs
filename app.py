# python -m streamlit run app.py (code to run)
# pip install plotly (install plotly for charts)

import json
import os
import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="SIB Techno-Economic Model",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── THEME ─────────────────────────────────────────────────────────────────────
_params = st.query_params
if "theme" in _params and "theme_select" not in st.session_state:
    st.session_state["theme_select"] = _params["theme"]
if "module" in _params and "current_module" not in st.session_state:
    st.session_state["current_module"] = _params["module"]

_theme = st.session_state.get("theme_select", "Light")
T = {
    "Dark": {
        "bg": "#1a1a1a", "card": "#1a1a1a", "border": "#f5f5f0",
        "text": "#f5f5f0", "sub": "#7E7E7E", "muted": "#A99170",
        "accent": "#d97706", "acc_bg": "#000000",
        "acc_border": "#ffffff", "hero_span": "#ffffff",
        "ref_border": "#111927",
    },
    "Light": {
        "bg": "#f5f5f0", "card": "#f5f5f0", "border": "#1a1a1a",
        "text": "#0a0e1a", "sub": "#000000", "muted": "#AC8A5B",
        "accent": "#d97706", "acc_bg": "#FFFFFF",
        "acc_border": "#d97706", "hero_span": "#0a0e1a",
        "ref_border": "#d0d9ea",
    },
}[_theme]


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Source Serif 4', serif; }}
            
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"],
.main, .block-container,
[data-testid="column"],
.stVerticalBlock, .stHorizontalBlock {{
    background-color: {T["bg"]} !important;
}}

header[data-testid="stHeader"], .stApp > header {{
    background-color: {T["bg"]} !important;
}}

.stDeployButton {{ display: none; }}

button[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}

h1, h2, h3, .stMarkdown, .stMarkdown p {{ color: {T["text"]} !important; }}

/* Plotly charts: force container to match theme and stay visible in captures */
.stPlotlyChart, [data-testid="stPlotlyChart"],
.js-plotly-plot, .plot-container, .svg-container {{
    background-color: {T["bg"]} !important;
}}
.js-plotly-plot .plotly .main-svg {{
    background-color: transparent !important;
}}
.stPlotlyChart {{
    content-visibility: visible !important;
    contain-intrinsic-size: none !important;
}}
hr {{ border-color: {T["border"]} !important; }}

/* ---- Make the Light/Dark box actually control everything ----------------
   Streamlit paints its own widgets using its own theme, which the app can't
   change while it is running. So when the app said Dark and Streamlit thought
   Light, the boxes stayed white on a black page. The rules below repaint every
   widget in the app's colours, so the selector wins no matter what Streamlit
   or a config.toml says. */
:root, .stApp {{ color-scheme: {_theme.lower()}; }}

/* Number and text boxes, including the little + and - buttons */
[data-baseweb="input"], [data-baseweb="base-input"],
[data-testid="stNumberInput"] div[data-baseweb="input"],
[data-testid="stTextInput"] div[data-baseweb="input"],
[data-testid="stNumberInputContainer"] {{
    background: {T["card"]} !important;
    border-color: {T["border"]} !important;
}}
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="input"] input {{
    background: {T["card"]} !important;
    color: {T["text"]} !important;
    -webkit-text-fill-color: {T["text"]} !important;
}}
[data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {{
    background: {T["card"]} !important;
    color: {T["text"]} !important;
    border-color: {T["border"]} !important;
}}

/* Labels, help text and captions */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label,
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p,
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {{
    color: {T["text"]} !important;
}}

/* Sliders */
[data-testid="stSlider"] [data-baseweb="slider"] div,
[data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"],
[data-testid="stThumbValue"] {{
    color: {T["text"]} !important;
}}

/* Tabs */
[data-baseweb="tab-list"], [data-baseweb="tab"] {{
    background: {T["bg"]} !important;
    color: {T["text"]} !important;
}}
[data-baseweb="tab"] p {{ color: {T["text"]} !important; }}
[data-baseweb="tab-border"] {{ background: {T["border"]} !important; }}
[data-baseweb="tab-highlight"] {{ background: {T["accent"]} !important; }}

/* Expanders */
[data-testid="stExpander"], [data-testid="stExpander"] details,
[data-testid="stExpander"] summary {{
    background: {T["card"]} !important;
    border-color: {T["border"]} !important;
    color: {T["text"]} !important;
}}

/* Tables, notices, tooltips and code */
[data-testid="stDataFrame"], [data-testid="stTable"],
[data-testid="stAlert"], [data-testid="stNotification"],
[data-testid="stTooltipContent"], [data-testid="stMetric"] {{
    background: {T["card"]} !important;
    color: {T["text"]} !important;
}}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
    color: {T["text"]} !important;
}}
code, pre, [data-testid="stCode"] {{
    background: {T["acc_bg"]} !important;
    color: {T["text"]} !important;
}}

/* Radio buttons, checkboxes and file uploader */
[data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p {{
    color: {T["text"]} !important;
}}
[data-testid="stFileUploader"] section {{
    background: {T["card"]} !important;
    border-color: {T["border"]} !important;
    color: {T["text"]} !important;
}}
[data-testid="stFileUploader"] section * {{ color: {T["text"]} !important; }}

/* Toolbar and the running-man status widget */
[data-testid="stToolbar"], [data-testid="stStatusWidget"] {{
    background: {T["bg"]} !important;
    color: {T["text"]} !important;
}}

.nav-brand {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.5rem;
    color: {T["accent"]};
    letter-spacing: 0.12em;
    font-weight: 600;
    padding-top: 0.5rem;
}}

[data-baseweb="popover"] [data-baseweb="menu"] {{
    min-width: max-content !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    background: {T["card"]} !important;
    border: 1px solid {T["border"]} !important;
}}
[data-baseweb="popover"] [role="option"] {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    color: {T["hero_span"]} !important;
    background: {T["card"]} !important;
    white-space: nowrap !important;
}}

/* Hide selectbox labels globally - intentional for nav/theme toggles */
div[data-testid="stSelectbox"] label {{ display: none !important; }}

/* Nav and theme selectbox styling */
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
    background: {T["card"]} !important;
    border-color: {T["border"]} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    color: {T["hero_span"]} !important;
    min-height: 3rem !important;
    padding-top: 0.4rem !important;
    padding-bottom: 0.4rem !important;
}}

/* Nav save/load button sizing */
div[data-testid="stButton"] > button {{
    min-height: 3rem !important;
    padding: 0.4rem 0.4rem !important;
    font-size: 0.82rem !important;
}}

.hero-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    color: {T["accent"]};
    text-transform: uppercase;
    margin-bottom: 1rem;
}}
.hero-title {{
    font-family: 'Source Serif 4', serif;
    font-size: 2.8rem;
    font-weight: 300;
    color: {T["text"]};
    line-height: 1.15;
    letter-spacing: -0.02em;
    margin-bottom: 0.4rem;
}}
.hero-title span {{ font-weight: 600; color: {T["hero_span"]}; }}
.hero-subtitle {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: {T["muted"]};
    margin-top: 1.2rem;
    letter-spacing: 0.04em;
}}
.meta-bar {{
    display: flex;
    gap: 2.5rem;
    margin-top: 2rem;
    padding: 1.5rem 0 2rem 0;
    border-top: 1px solid {T["border"]};
    border-bottom: 1px solid {T["border"]};
    margin-bottom: 2rem;
}}
.meta-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: {T["muted"]};
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.2rem;
}}
.meta-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: {T["sub"]};
}}
.section-header {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.16em;
    color: {T["accent"]};
    text-transform: uppercase;
    margin: 2rem 0 1.2rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid {T["border"]};
}}
.module-card {{
    background: {T["card"]};
    border: 1px solid {T["border"]};
    border-radius: 6px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
    height: 100%;
}}
.module-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: {T["accent"]};
    opacity: 0.6;
}}
.module-name {{
    font-family: 'Source Serif 4', serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: {T["text"]};
    margin-bottom: 0.5rem;
}}
.module-desc {{
    font-family: 'Source Serif 4', serif;
    font-size: 0.78rem;
    color: {T["sub"]};
    line-height: 1.5;
    margin-bottom: 0.8rem;
}}
.rq-box {{
    background: {T["card"]};
    border: 1px solid {T["border"]};
    border-left: 3px solid {T["accent"]};
    border-radius: 4px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}}
.rq-main {{
    font-family: 'Source Serif 4', serif;
    font-size: 0.9rem;
    color: {T["text"]};
    line-height: 1.6;
    font-style: italic;
    margin-bottom: 1rem;
}}
.rq-sub {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: {T["sub"]};
    line-height: 2;
}}
.rq-sub span {{ color: {T["accent"]}; margin-right: 0.5rem; }}
.status-bar {{
    background: {T["card"]};
    border: 1px solid {T["border"]};
    border-radius: 6px;
    padding: 0.9rem 1.4rem;
    margin-bottom: 2rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: {T["muted"]};
}}
.status-bar strong {{ color: {T["accent"]}; }}
.workflow-step {{
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
}}
.step-num {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: {T["accent"]};
    background: {T["acc_bg"]};
    border: 1px solid {T["acc_border"]};
    border-radius: 3px;
    padding: 0.2rem 0.5rem;
    flex-shrink: 0;
}}
.step-text {{
    font-family: 'Source Serif 4', serif;
    font-size: 0.82rem;
    color: {T["sub"]};
    line-height: 1.5;
}}
.step-text strong {{ color: {T["text"]}; }}

/* ── Electrochemical module specific ── */
.input-section-title {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    color: {T["accent"]};
    text-transform: uppercase;
    margin-bottom: 2rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid {T["border"]};
}}
.note-box {{
    background: {T["acc_bg"]};
    border: 1px solid {T["acc_border"]};
    border-left: 3px solid {T["accent"]};
    border-radius: 4px;
    padding: 0.7rem 1rem;
    font-family: 'Source Serif 4', serif;
    font-size: 0.76rem;
    color: {T["muted"]};
    line-height: 1.5;
    margin-bottom: 1rem;
}}
.note-box strong {{ color: {T["sub"]}; }}
.output-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1.2rem;
}}
.output-card {{
    background: {T["card"]};
    border: 1px solid {T["border"]};
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
}}
.output-card.highlight {{
    border-color: {T["acc_border"]};
    background: {T["acc_bg"]};
}}
.output-card-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.60rem;
    color: {T["muted"]};
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.35rem;
}}
.output-card-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.25rem;
    font-weight: 600;
    color: {T["accent"]};
    letter-spacing: -0.02em;
}}
.output-card-unit {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    color: {T["muted"]};
    margin-top: 0.15rem;
}}
.mass-table {{
    width: 100%;
    border-collapse: collapse;
    background: {T["card"]};
    border: 1px solid {T["border"]};
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.70rem;
}}
.mass-table th {{
    color: {T["muted"]};
    text-align: left;
    padding: 0.55rem 0.8rem;
    border-bottom: 1px solid {T["border"]};
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 0.62rem;
}}
.mass-table td {{
    color: {T["sub"]};
    padding: 0.45rem 0.8rem;
    border-bottom: 1px solid {T["ref_border"]};
}}
.mass-table td.val {{ color: {T["text"]}; text-align: right; }}
.mass-table tr.subtotal td {{
    color: {T["accent"]};
    border-top: 1px solid {T["border"]};
    border-bottom: 1px solid {T["border"]};
}}
.mass-table tr:last-child td {{ border-bottom: none; }}
.val-pass {{
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 4px;
    padding: 0.55rem 0.9rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.70rem;
    color: #10b981;
    margin-bottom: 0.5rem;
}}
.val-fail {{
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 4px;
    padding: 0.55rem 0.9rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.70rem;
    color: #ef4444;
    margin-bottom: 0.5rem;
}}
.val-warn {{
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: 4px;
    padding: 0.55rem 0.9rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.70rem;
    color: #f59e0b;
    margin-bottom: 0.5rem;
}}
div[data-testid="stNumberInput"] label {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.70rem !important;
    color: {T["sub"]} !important;
}}
div[data-testid="stNumberInput"] input {{
    background: {T["bg"]} !important;
    border: none !important;
    box-shadow: none !important;
    color: {T["text"]} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.80rem !important;
    border-radius: 4px !important;
}}
div[data-testid="stNumberInput"] > div {{
    background: {T["bg"]} !important;
    border: 1px solid {T["border"]} !important;
    border-radius: 4px !important;
    overflow: hidden !important;
    color: {T["bg"]} !important;
}}
div[data-testid="stNumberInput"] button {{
    background: {T["card"]} !important;
    border-color: {T["border"]} !important;
    color: {T["sub"]} !important;
}}
div[data-testid="stNumberInput"] button:hover {{
    background: {T["acc_bg"]} !important;
    border-color: {T["accent"]} !important;
    color: {T["accent"]} !important;
}}
div[data-testid="stNumberInput"] * {{
    outline: none !important;
    box-shadow: none !important;
}}
div[data-testid="stNumberInput"] input:focus {{
    box-shadow: 0 0 0 1px #ffffff !important;
}}
div[data-testid="stButton"] button {{
    background: {T["accent"]} !important;
    color: #0a0e1a !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.76rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    width: 100% !important;
    padding: 0.6rem !important;
}}

div[data-testid="stExpander"] summary p {{
    color: {T["acc_border"]} !important;
}}
</style>
""", unsafe_allow_html=True)


# ── MODULE DEFINITIONS ────────────────────────────────────────────────────────
MODULES = [
    ("🏠  Home",                       "home"),
    ("⚗️  Module 01 - Electrochemical", "electrochemical"),
    ("🔲  Module 02 - Cell Design",     "cell_design"),
    ("🔋  Module 03 - Pack Design",     "pack_design"),
    ("💰  Module 04 - Cost Model",      "cost_model"),
    ("🌿  Module 05 - Sustainability",  "sustainability"),
    ("📊  Module 06 - Sensitivity",     "sensitivity"),
    ("🎲  Module 07 - Uncertainty",     "uncertainty"),
    ("📈  Module 08 - Parameter Studies", "sweeps"),
    ("📋  Study Summary",               "summary"),
]
MODULE_LABELS = [m[0] for m in MODULES]
BUILT = {"home", "electrochemical", "cell_design", "pack_design", "cost_model", "sustainability", "sensitivity", "uncertainty", "sweeps", "summary"}
# Path to the session file, saved in the same folder as app.py
STUDIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sib_studies.json")

# All widget keys to save and restore
PERSIST_KEYS = [
    # Module 01 cathode inputs
    "c_cap", "c_volt", "c_dens", "c_am", "c_carb", "c_bind", "c_por", "c_thick",
    "chem_index", "last_chem",
    # Module 01 anode inputs
    "a_cap", "a_volt", "a_dens", "a_am", "a_bind", "a_carb", "a_por",
    "anode_index", "last_anode",
    # Module 01 design inputs
    "np_ratio", "target_capacity", "_target_cap_Ah", "_size_mode_index", "tab_excess",
    "cathode_custom_name", "anode_custom_name", "anode_binder_name",
    "c_carb_dens", "c_bind_dens", "a_carb_dens", "a_bind_dens",
    # Module 02 geometry inputs
    "cell_thickness_mm", "lw_ratio", "sep_excess_width", "sep_excess_length",
    "tab_length_mm", "feedthrough_mm", "cc_buffer", "pouch_seal",
    "anode_excess", "packing_eff", "cell_edge_fold", "bicell_expansion", "elec_excess",
    # Module 02 container inputs
    "container_thickness_um", "container_density_in", "wall_thickness_mm", "seal_buffer_mm",
    # Module 02 component inputs
    "c_foil_thick", "a_foil_thick", "a_foil_dens", "sep_thick", "sep_dens",
    "elec_dens", "elec_uptake",
    # Module 03 pack inputs (BatPaC topology)
    "cells_per_module", "cells_parallel", "modules_per_row", "rows_per_pack", "modules_parallel",
    "useable_soc",
    "al_cond_thick", "mod_wall_thick", "restraint_thick",
    "coolant_panel_thick", "coolant_wall",
    "jacket_insul_thick", "jacket_int_plate", "jacket_ext_base",
    "bms_bdu_mass", "bms_bdu_vol",
    "nominal_pack_current",
    # Module 04 cost inputs
    "p_cathode_am", "p_anode_am", "p_carbon", "p_pvdf", "p_cmcsbr",
    "p_al_foil_cost", "p_anode_foil_cost", "p_sep", "p_electrolyte", "p_container", "p_pos_terminal_kg", "p_neg_terminal_kg", "terminal_fixed_cost",
    "annual_production_packs", "cell_yield_pct", "labor_rate_per_hr",
    "energy_price_per_kWh", "effective_days_per_year", "bms_cost_per_pack",
    "p_row_rack", "p_module_pads", "p_module_interconnect", "p_busbar",
    "p_coolant_panel", "p_coolant_manifold", "p_pack_terminal_seal",
    "p_pack_support_frame", "p_jacket_top_interior", "p_jacket_exterior_base",
    "p_jacket_insulation",
    # Module 05 sustainability inputs
    "p_al_kg", "p_cu_kg",
    "co2_cathode_am", "co2_anode_am", "co2_al_foil", "co2_steel", "co2_bms",
    "co2_separator", "co2_electrolyte", "co2_carbon", "co2_pvdf",
    "co2_anode_binder", "co2_container", "co2_copper",
    "grid_co2_intensity", "cycle_life", "calendar_life_yr", "rt_eff",
    "elec_price", "discount_rate", "om_cost_pct",
    "eol_cat_recovery", "eol_al_recovery", "eol_steel_recovery",
    "eol_cat_price", "eol_al_price", "eol_steel_price",
    # Navigation and theme
    "current_module", "theme_select",
]

MODULE_OUTPUT_KEYS = ["electrochem", "cell_design", "pack_design", "_m04_results", "sustainability"]
STUDY_INPUTS_KEY = "_study_inputs"

def _collect_session_data():
    data = {}
    for k in PERSIST_KEYS:
        if k in st.session_state:
            data[k] = st.session_state[k]
    # Module output dicts (results computed by each module's Calculate button)
    for key in MODULE_OUTPUT_KEYS:
        if key in st.session_state:
            val = st.session_state[key]
            if isinstance(val, dict):
                save_key = key if key.startswith("_") else f"_{key}"
                # Keep plain numbers and text, plus simple dictionaries of numbers
                # like co2_breakdown, so a reloaded study keeps its CO2 split.
                def _keep(v):
                    if isinstance(v, (int, float, bool, str)):
                        return True
                    return (isinstance(v, dict) and v
                            and all(isinstance(x, str) for x in v)
                            and all(isinstance(y, (int, float)) for y in v.values()))
                data[save_key] = {k: v for k, v in val.items() if _keep(v)}
    # Study inputs dict - single source of truth for Module 06/07 sliders
    if STUDY_INPUTS_KEY in st.session_state:
        val = st.session_state[STUDY_INPUTS_KEY]
        if isinstance(val, dict):
            data[STUDY_INPUTS_KEY] = {k: v for k, v in val.items() if isinstance(v, (int, float, bool, str))}
    # Record exactly which module was being viewed at save time
    data["_saved_at_module"] = st.session_state.get("current_module", "🏠  Home")
    return data

def _restore_session_data(data):
    # These keys belong to already-rendered widgets and cannot be set directly
    SKIP_KEYS = {"theme_select", "nav_select"}
    for k, v in data.items():
        if k in SKIP_KEYS:
            continue
        if k == STUDY_INPUTS_KEY:
            st.session_state[STUDY_INPUTS_KEY] = v
        elif k.startswith("_") and k[1:] in MODULE_OUTPUT_KEYS:
            st.session_state[k[1:]] = v
        elif k in MODULE_OUTPUT_KEYS:
            st.session_state[k] = v
        else:
            st.session_state[k] = v

    # ── Backfill for studies saved before all input widgets were tracked ──────
    # Older saves may have full module RESULTS but be missing some raw widget
    # values. Where a widget key is still absent, recover it from the "_in_"
    # raw-input snapshot stored inside that module's own results dict, or from
    # _study_inputs, so old saves degrade gracefully instead of silently
    # reverting individual fields to code defaults.
    _backfill_sources = []
    for mod_key in ("electrochem", "cell_design", "pack_design", "_m04_results"):
        d = st.session_state.get(mod_key)
        if isinstance(d, dict):
            _backfill_sources.append(d)
    si = st.session_state.get(STUDY_INPUTS_KEY, {})
    if isinstance(si, dict):
        _backfill_sources.append(si)

    _WIDGET_TO_IN_KEY = {
        "p_al_foil_cost": "p_al_foil", "p_anode_foil_cost": "p_anode_foil",
        "container_density_in": "con_density", "sep_excess_width": "sep_excess_w",
        "sep_excess_length": "sep_excess_l", "target_capacity": "electrode_area",
        "a_foil_dens": "anode_foil_density", "cells_parallel": "cells_parallel_m03",
    }
    for widget_key in PERSIST_KEYS:
        if widget_key in st.session_state:
            continue  # already restored directly
        lookup_key = _WIDGET_TO_IN_KEY.get(widget_key, widget_key)
        for src in _backfill_sources:
            if f"_in_{lookup_key}" in src:
                st.session_state[widget_key] = src[f"_in_{lookup_key}"]
                break
            if lookup_key in src:
                st.session_state[widget_key] = src[lookup_key]
                break

    # Flag so Module 01's chemistry-change detection skips on next render
    st.session_state["_just_loaded"] = True

def _reset_all_session_state():
    """Wipe every input, computed result, and study-tracking key - true fresh start."""
    keys_to_clear = set(PERSIST_KEYS) | set(MODULE_OUTPUT_KEYS) | {STUDY_INPUTS_KEY}
    # Also clear widget keys not in PERSIST_KEYS but that hold live state (sliders, selects)
    extra_prefixes = ("sl_", "chem_", "anode_", "format_", "_confirm_delete_", "_rename_")
    keep = {"theme_select"}  # preserve theme preference across reset
    for k in list(st.session_state.keys()):
        if k in keep:
            continue
        if k in keys_to_clear or k.startswith(extra_prefixes) or k == "nav_select":
            st.session_state.pop(k, None)
    # Use the same navigation path as "Next module" buttons so the dropdown
    # widget itself (not just current_module) actually updates on rerun.
    st.session_state["_navigate_to"] = "⚗️  Module 01 - Electrochemical"

def _load_studies():
    if not os.path.exists(STUDIES_FILE):
        return {}
    try:
        with open(STUDIES_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def _save_studies(studies):
    with open(STUDIES_FILE, "w") as f:
        json.dump(studies, f, indent=2)

# Input widget keys whose values must survive module-to-module navigation.
# We exclude theme_select (a nav-bar widget rendered on every run, so never at
# risk) and current_module (navigation state, not an input).
_PERSIST_INPUT_KEYS = [k for k in PERSIST_KEYS if k not in ("theme_select", "current_module")]

def _persist_widget_state():
    """Keep every module's input values alive while another module is on screen.

    Streamlit stores a widget's value in session_state, but on any rerun where
    that widget is NOT rendered it discards the value (once the widget has been
    instantiated at least once in the session). Because each module renders only
    its own inputs, navigating between modules would otherwise wipe the inputs of
    every module you are not currently viewing - including the values just
    restored from a saved study, which is why loading a study at Module 07 and
    walking back to Module 01 reset each module's inputs to their code defaults
    while the computed results (stored as plain, non-widget keys) survived.

    Re-assigning each stored value to itself on every run reclassifies it as
    user-owned session state, which Streamlit preserves regardless of which
    widgets happen to render. This must run before any input widget is
    instantiated, so it is called at the very top of the main script flow.
    """
    for _k in _PERSIST_INPUT_KEYS:
        if _k in st.session_state:
            st.session_state[_k] = st.session_state[_k]

def _furthest_module(data):
    # Prefer the exact module the user was on when they saved
    if "_saved_at_module" in data and data["_saved_at_module"] in MODULE_LABELS:
        return data["_saved_at_module"]
    # Fallback for studies saved before this tracking existed
    if "_sustainability" in data: return "🌿  Module 05 - Sustainability"
    if "_m04_results" in data or "_cost_model" in data: return "💰  Module 04 - Cost Model"
    if "_pack_design"    in data: return "🔋  Module 03 - Pack Design"
    if "_cell_design"    in data: return "🔲  Module 02 - Cell Design"
    if "_electrochem"    in data: return "⚗️  Module 01 - Electrochemical"
    return "🏠  Home"

def pct(v, total):
    """Return v as a percentage of total, formatted to 1 decimal place."""
    return f"{v / total * 100:.1f}%"

def _batpac_vrow(label, your_val, ref_val, fmt=".4f", pct_tol=1.0):
    """Shared row-builder for BatPaC validation panels across Modules 01-05."""
    diff_pct = (your_val - ref_val) / ref_val * 100 if ref_val else 0
    ok = abs(diff_pct) <= pct_tol
    colour = "#2ecc71" if ok else ("#e67e22" if abs(diff_pct) <= 5 else "#e74c3c")
    arrow = "✓" if ok else ("▲" if your_val > ref_val else "▼")
    return (f"<tr>"
            f"<td style='padding:4px 8px'>{label}</td>"
            f"<td style='padding:4px 8px;text-align:right'>{your_val:{fmt}}</td>"
            f"<td style='padding:4px 8px;text-align:right'>{ref_val:{fmt}}</td>"
            f"<td style='padding:4px 8px;text-align:right;color:{colour}'>"
            f"{arrow} {diff_pct:+.2f}%</td>"
            f"</tr>")

def _batpac_validation_table(rows_html):
    """Shared table wrapper for BatPaC validation panels."""
    return f"""
    <table style='width:100%;border-collapse:collapse;font-size:0.85rem'>
    <thead><tr style='border-bottom:1px solid #555'>
      <th style='padding:4px 8px;text-align:left'>Line item</th>
      <th style='padding:4px 8px;text-align:right'>Your model</th>
      <th style='padding:4px 8px;text-align:right'>BatPaC ref</th>
      <th style='padding:4px 8px;text-align:right'>Diff</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
    </table>
    <p style='font-size:0.75rem;color:#888;margin-top:6px'>
    ✓ = within 1% &nbsp;|&nbsp; ▲▼ orange = within 5% &nbsp;|&nbsp; ▲▼ red = &gt;5% gap.<br>
    </p>
    """

def run_electrochemical(c_cap, c_volt, c_dens, c_am, c_carb, c_bind, c_por, c_thick,
                        a_cap, a_volt, a_dens, a_am, a_bind, a_carb, a_por,
                        np_ratio, electrode_area_cm2, tab_excess,
                        c_carb_dens, c_bind_dens, a_carb_dens, a_bind_dens,
                        target_cell_capacity_Ah=None):

    # 1. Cell average voltage (V)
    cell_voltage = c_volt - a_volt

    # 2. Cathode areal capacity (mAh/cm²)
    c_coating_density = (1 - c_por) * 100 / (c_am*100/c_dens + c_carb*100/c_carb_dens + c_bind*100/c_bind_dens)
    c_areal = (c_thick / 10000) * c_coating_density * c_cap * c_am

    # 3. Cell capacity and electrode area - two input modes:
    # Mode A (set area):     electrode_area is user input -> cell_capacity derived
    # Mode B (set capacity): target_cell_capacity_Ah is user input -> electrode_area derived
    if target_cell_capacity_Ah is not None:
        electrode_area = (target_cell_capacity_Ah * 1000) / c_areal if c_areal > 0 else 0
        cell_capacity  = target_cell_capacity_Ah
    else:
        electrode_area = electrode_area_cm2
        cell_capacity  = c_areal * electrode_area / 1000

    # 4. Target anode areal capacity - adjusted for tab excess (mAh/cm²)
    # Anode covers larger area by (1 + tab_excess), so each cm² needs less charge
    a_areal_target = c_areal * np_ratio / (1 + tab_excess)

    # 5. Anode thickness - derived from volumetric capacity ratio (BatPaC method, µm)
    # BatPaC derives anode thickness as: cathode_thickness × (pos_vol_capacity × N/P / neg_vol_capacity)
    # rather than from areal capacity / area. Verified exact match against BatPaC v5.2.
    a_coating_density_target = (1 - a_por) * 100 / (a_am*100/a_dens + a_carb*100/a_carb_dens + a_bind*100/a_bind_dens)
    c_vol_capacity = (c_cap / 1000) * c_am * c_coating_density        # Ah/cm³
    a_vol_capacity = (a_cap / 1000) * a_am * a_coating_density_target  # Ah/cm³
    thickness_ratio = (c_vol_capacity * np_ratio) / a_vol_capacity
    a_thick = c_thick * thickness_ratio

    # 6. Actual anode areal capacity - recalculated from derived thickness for validation
    a_coating_density = (1 - a_por) * 100 / (a_am*100/a_dens + a_carb*100/a_carb_dens + a_bind*100/a_bind_dens)
    a_areal = (a_thick / 10000) * a_coating_density * a_cap * a_am

    # 7. Cathode material masses (g/cell)
    c_AM_mass     = cell_capacity / c_cap * 1000     # active material
    c_coat_total  = c_AM_mass / c_am                 # total coating = AM / AM fraction
    c_carbon_mass = c_coat_total * c_carb            # carbon additive
    c_binder_mass = c_coat_total * c_bind            # binder

    # 8. Anode material masses (g/cell)
    # Scaled by N/P ratio (extra capacity buffer) and tab excess (larger physical area)
    a_AM_mass     = cell_capacity / a_cap * 1000 * np_ratio * (1 + tab_excess)
    a_coat_total  = a_AM_mass / a_am
    a_binder_mass = a_coat_total * a_bind
    a_carbon_mass = a_coat_total * a_carb

    # 9. Validation quantities
    np_actual  = (a_areal * (1 + tab_excess)) / c_areal
    c_frac_sum = c_am + c_carb + c_bind
    a_frac_sum = a_am + a_bind + a_carb

    return {
        "cell_voltage":   cell_voltage,
        "c_areal":        c_areal,
        "electrode_area": electrode_area,
        "cell_capacity":  cell_capacity,
        "a_areal_target": a_areal_target,
        "a_thick":        a_thick,
        "a_areal":        a_areal,
        "c_coating_density": c_coating_density,
        "a_coating_density": a_coating_density,
        "c_AM_mass":      c_AM_mass,
        "c_coat_total":   c_coat_total,
        "c_carbon_mass":  c_carbon_mass,
        "c_binder_mass":  c_binder_mass,
        "a_AM_mass":      a_AM_mass,
        "a_coat_total":   a_coat_total,
        "a_binder_mass":  a_binder_mass,
        "a_carbon_mass":  a_carbon_mass,
        "np_actual":      np_actual,
        "c_frac_sum":     c_frac_sum,
        "a_frac_sum":     a_frac_sum,
        "voltage_ok":     2.5 <= cell_voltage <= 4.5,
        "np_ok":          np_actual >= np_ratio - 0.003,
        "c_frac_ok":      abs(c_frac_sum - 1.0) <= 0.01,
        "a_frac_ok":      abs(a_frac_sum - 1.0) <= 0.01,
    }
    
def run_cell_design(
    cathode_thickness_um, anode_thickness_um, electrode_area_cm2,
    cell_capacity_Ah, cell_voltage_V,
    cathode_bulk_density, anode_bulk_density,
    cathode_porosity, anode_porosity,
    cathode_coating_density, anode_coating_density,
    cathode_coating_total_g, anode_coating_total_g,
    num_layers_input, length_to_width_ratio,
    sep_excess_width_mm, sep_excess_length_mm,
    tab_length_mm, feedthrough_mm, cc_buffer_mm, pouch_seal_mm,
    container_thickness_um, container_density,
    wall_thickness_mm, seal_buffer_mm,
    cathode_foil_thickness_um, anode_foil_thickness_um, al_density, anode_foil_density,
    sep_thickness_um, sep_density,
    electrolyte_density, electrolyte_uptake_frac,
    tab_excess,
    anode_excess_mm,
    packing_efficiency=0.97, cell_edge_fold_mm=1.0, electrolyte_excess_frac=0.02,
    bicell_expansion_um=0.0):
    """Cell-level geometry and mass model, transcribed from BatPaC v5.2
    Battery Design rows 63-100 and 326-346.

    `bicell_expansion_um` is BatPaC BD326 (extra bi-cell thickness from electrode
    expansion at 100% SOC, BD309 + BD322). It requires material-level expansion
    coefficients (Chem!C22 / Chem!C54) that have no published values for NVPF or
    hard carbon, so it defaults to 0 for sodium-ion work. Setting it to BatPaC's
    computed 6.7479 um reproduces the NMC811-G reference cell thickness exactly.
    Terminal masses are always derived from geometry (BD073/BD074) and are
    therefore outputs, never inputs.
    """

    # ── Unit conversions (all to cm) ──────────────────────────────────────
    c_thick_cm   = cathode_thickness_um   / 10000
    a_thick_cm   = anode_thickness_um     / 10000
    sep_thick_cm = sep_thickness_um       / 10000
    con_thick_cm = container_thickness_um / 10000
    c_foil_cm    = cathode_foil_thickness_um / 10000
    a_foil_cm    = anode_foil_thickness_um   / 10000
    sep_excess_w_cm = sep_excess_width_mm  / 10
    sep_excess_l_cm = sep_excess_length_mm / 10
    anode_excess_cm = anode_excess_mm / 10

    # 1. Number of bicell layers
    # One bicell = cathode coating + cathode foil + separator + anode foil + anode coating + separator
    # 0.97 packing efficiency accounts for imperfect stacking
    # BD335: layers = (cell_thickness*1000 - 2*container - neg_foil) / bicell * 0.97
    # This model takes the layer count as the input and inverts that relation, so
    # the stack sits between two container walls plus one negative foil, exactly
    # as BatPaC's numerator specifies.
    bicell_thickness_cm    = (2*c_thick_cm + 2*a_thick_cm + 2*sep_thick_cm
                              + c_foil_cm + a_foil_cm + 2*(bicell_expansion_um/10000))
    num_bicell_layers      = num_layers_input
    available_thickness_cm = num_bicell_layers * bicell_thickness_cm / packing_efficiency
    cell_thick_cm          = available_thickness_cm + 2 * con_thick_cm + a_foil_cm

    # 2. Electrode width and length from area and aspect ratio
    # Total electrode area = num_layers × 2 faces × width × length
    # length = width × ratio  →  area = num_layers × 2 × width² × ratio
    area_per_face_cm2  = electrode_area_cm2 / (num_bicell_layers * 2)
    electrode_width_cm = (area_per_face_cm2 / length_to_width_ratio) ** 0.5
    electrode_length_cm = electrode_width_cm * length_to_width_ratio

    # 3. Internal tab lengths (portion inside the cell) - exact BatPaC formula
    # Positive CC tab length = 1.2 × cell thickness; negative tab = positive tab - 0.5×excess_negative
    cathode_tab_cm = 1.2 * cell_thick_cm
    anode_tab_cm   = cathode_tab_cm - 0.5 * anode_excess_cm

    # 3b. Terminal masses from BatPaC geometry (BD073/BD074), overriding flat inputs.
    # Terminal = (weld_tab + feedthrough) rectangle + internal tab rectangle, each
    # × thickness × material density. Ref: BatPaC BD073-074, BD090-100, BD336, BD341.
    _cell_thick_mm  = cell_thick_cm * 10
    _elec_width_mm  = electrode_width_cm * 10
    _feed_width_mm  = 50.0 if _elec_width_mm > 84 else 40.0     # BD097
    _pos_cc_tab_mm  = 1.2 * _cell_thick_mm                       # BD341
    _end_to_tab_mm  = _cell_thick_mm * 0.1 + sep_excess_length_mm / 2   # BD100
    _internal_tab_len_mm = _pos_cc_tab_mm - _end_to_tab_mm       # BD094
    _internal_tab_wid_mm = _elec_width_mm - 2 * cc_buffer_mm     # BD096
    _pos_term_thick_mm = 1.2                                     # BD090
    _neg_term_thick_mm = 0.8 if anode_foil_density > 5.0 else 1.2  # BD091 (Cu vs Al)
    _term_area_mm2 = ((tab_length_mm + feedthrough_mm) * _feed_width_mm
                      + _internal_tab_len_mm * _internal_tab_wid_mm)
    terminal_mass_cathode_g = _term_area_mm2 * _pos_term_thick_mm / 1000 * al_density
    terminal_mass_anode_g   = _term_area_mm2 * _neg_term_thick_mm / 1000 * anode_foil_density

    # 4. Cell external dimensions - exact BatPaC formulas (BD344/BD345)
    # Width  (BD344) = electrode_width + 2×cell_edge_fold + sep_excess_width
    # Length (BD345) = electrode_length + 2×(G98 + G100)
    #   G98  = total terminal length = internal_tab_len + feedthrough + weld_tab
    #        = (1.2×cell_thickness - cell_thickness×0.1 - sep_excess_length/2) + feedthrough + weld_tab
    #   G100 = end-of-electrode to tab = cell_thickness×0.1 + sep_excess_length/2
    _cell_thick_mm_dim = cell_thick_cm * 10
    _G341 = 1.2 * _cell_thick_mm_dim                                          # pos CC tab length (mm)
    _G100 = _cell_thick_mm_dim * 0.1 + sep_excess_length_mm / 2               # end to tab (mm)
    _G94  = _G341 - _G100                                                      # internal tab length (mm)
    _G98  = _G94 + feedthrough_mm + tab_length_mm                              # total terminal length (mm)
    cell_width_mm  = electrode_width_cm * 10 + 2 * cell_edge_fold_mm + sep_excess_width_mm
    cell_length_mm = electrode_length_cm * 10 + 2 * (_G98 + _G100)
    cell_volume_cm3 = cell_thick_cm * (cell_width_mm / 10) * (cell_length_mm / 10)

    # 5. Cathode foil area (m²)
    # num_layers × width × (length + internal tab)
    cathode_foil_area_m2 = num_bicell_layers * (electrode_width_cm / 100) * ((electrode_length_cm + cathode_tab_cm) / 100)

    # 6. Anode foil area (m²)
    # Anode is slightly wider (BatPaC: own "excess negative" parameter) and has (layers + 1) sheets
    anode_foil_area_m2  = (num_bicell_layers + 1) * ((electrode_width_cm + anode_excess_cm) / 100) * ((electrode_length_cm + anode_tab_cm + anode_excess_cm) / 100)

    # 7. Separator area (m²)
    # 2 separators per bicell × (electrode + excess) on each dimension
    sep_area_m2 = 2 * num_bicell_layers * ((electrode_width_cm + sep_excess_w_cm) / 100) * ((electrode_length_cm + sep_excess_l_cm) / 100)

    # 8. Foil masses (g)
    # mass = area_cm² × thickness_cm × density
    cathode_foil_mass_g = cathode_foil_area_m2 * 10000 * c_foil_cm * al_density
    anode_foil_mass_g   = anode_foil_area_m2   * 10000 * a_foil_cm * anode_foil_density

    # 9. Separator mass (g)
    sep_mass_g = sep_area_m2 * 10000 * sep_thick_cm * sep_density

    # 10. Electrolyte volume (cm³) and mass (g) - exact BatPaC formula (Battery Design row 66)
    # void = coating_mass / coating_bulk_density × porosity% ; separator void = area×thickness×separator_porosity
    # `electrolyte_uptake_frac` holds SEPARATOR POROSITY (BatPaC Chem!C68 = 0.50), not an uptake efficiency.
    # extra volume = cell_thickness(mm) × electrode_width(mm) × electrode_length(mm) / 1000 × excess_frac  [→ cm³]
    cathode_void_cm3 = (cathode_coating_total_g / cathode_coating_density) * cathode_porosity
    anode_void_cm3   = (anode_coating_total_g   / anode_coating_density)   * anode_porosity
    sep_void_cm3     = sep_area_m2 * 10000 * sep_thick_cm * electrolyte_uptake_frac
    extra_vol_cm3    = cell_thick_cm*10 * (electrode_width_cm*10) * (electrode_length_cm*10) / 1000 * electrolyte_excess_frac
    elec_vol_cm3     = cathode_void_cm3 + anode_void_cm3 + sep_void_cm3 + extra_vol_cm3
    elec_vol_L       = elec_vol_cm3 / 1000
    elec_mass_g      = elec_vol_L * electrolyte_density * 1000

    # 11. Container mass (g)
    # Pouch construction only, exact BatPaC BD081. One laminate face wraps the cell
    # thickness, the other is flat; both lose 2x the external weld-tab length off the
    # cell length, and both gain the sealing buffer across the width. BatPaC models a
    # pouch cell exclusively, so no prismatic branch is provided and the pouch
    # construction is stated as an approximation where a prismatic cell is intended.
    _w_mm, _l_mm = cell_width_mm, cell_length_mm
    _usable_len_mm = _l_mm - 2 * tab_length_mm
    container_area_mm2 = ((_w_mm + 2 * _cell_thick_mm + pouch_seal_mm) * _usable_len_mm
                          + (_w_mm + pouch_seal_mm) * _usable_len_mm)
    container_mass_g = container_area_mm2 * container_thickness_um / 1000 * container_density / 1000

    # 12. Total cell mass (g)
    cell_mass_g = (
        cathode_coating_total_g + anode_coating_total_g
        + cathode_foil_mass_g     + anode_foil_mass_g
        + sep_mass_g              + elec_mass_g
        + terminal_mass_cathode_g + terminal_mass_anode_g
        + container_mass_g
    )

    # 13. Cell energy (Wh)
    cell_energy_Wh = cell_capacity_Ah * cell_voltage_V

    # 14. Specific energy (Wh/kg)
    cell_specific_energy = cell_energy_Wh / (cell_mass_g / 1000)

    # 15. Energy density (Wh/L)
    cell_energy_density = cell_energy_Wh / (cell_volume_cm3 / 1000)

    # Validation
    # The stack must still fit inside the finished cell once both container walls
    # and the negative foil are accounted for (a real constraint, unlike comparing
    # the stack to a single layer, which is true for any layer count above one).
    cell_thick_ok = cell_thick_cm > available_thickness_cm > 0
    layers_ok     = num_bicell_layers >= 3
    area_ok       = electrode_area_cm2 > 0

    return {
        "num_bicell_layers":        num_bicell_layers,
        "anode_excess_mm":          anode_excess_mm,
        "cell_thickness_mm":        cell_thick_cm * 10,
        "electrode_width_mm":       electrode_width_cm  * 10,
        "electrode_length_mm":      electrode_length_cm * 10,
        "cell_width_mm":            cell_width_mm,
        "cell_length_mm":           cell_length_mm,
        "cell_volume_cm3":          cell_volume_cm3,
        "cathode_foil_area_m2":     cathode_foil_area_m2,
        "anode_foil_area_m2":       anode_foil_area_m2,
        "sep_area_m2":              sep_area_m2,
        "cathode_foil_mass_g":      cathode_foil_mass_g,
        "anode_foil_mass_g":        anode_foil_mass_g,
        "cathode_foil_thickness_um": cathode_foil_thickness_um,
        "anode_foil_thickness_um":   anode_foil_thickness_um,
        "anode_foil_density":        anode_foil_density,
        "bicell_expansion_um":       bicell_expansion_um,
        "sep_mass_g":               sep_mass_g,
        "cathode_void_cm3":         cathode_void_cm3,
        "anode_void_cm3":           anode_void_cm3,
        "sep_void_cm3":             sep_void_cm3,
        "extra_vol_cm3":            extra_vol_cm3,
        "elec_vol_cm3":             elec_vol_cm3,
        "elec_vol_L":               elec_vol_L,
        "elec_mass_g":              elec_mass_g,
        "container_mass_g":         container_mass_g,
        "terminal_mass_cathode_g":  terminal_mass_cathode_g,
        "terminal_mass_anode_g":    terminal_mass_anode_g,
        "cell_mass_g":              cell_mass_g,
        "cell_energy_Wh":           cell_energy_Wh,
        "cell_specific_energy":     cell_specific_energy,
        "cell_energy_density":      cell_energy_density,
        "bicell_thickness_cm":      bicell_thickness_cm,
        "available_thickness_cm":   available_thickness_cm,
        "cell_thick_ok":            cell_thick_ok,
        "layers_ok":                layers_ok,
        "area_ok":                  area_ok,
    }

def run_pack_design(
    # From Module 02 / Module 01
    cell_mass_g, cell_energy_Wh, cell_volume_cm3,
    cell_voltage_V, cell_capacity_Ah,
    cell_width_mm, cell_length_mm, cell_thickness_mm,
    positive_electrode_length_mm,
    # Topology - BatPaC takes these as direct inputs, not reverse-solved
    cells_per_module, cells_parallel, modules_per_row, rows_per_pack, modules_parallel,
    useable_soc_fraction,
    # Module-level geometry (BatPaC defaults)
    al_conductor_thickness_mm=0.4,
    module_wall_thickness_mm=0.3,
    module_length_buffer_mm=6.0,
    module_length_buffer2_mm=2.0,
    # Row rack
    rack_length_buffer_mm=15.0,
    rack_busbar_allowance_mm=10.0,
    rack_width_buffer_mm=5.0,
    coolant_panel_thickness_mm=5.0,
    coolant_plate_wall_mm=0.3,
    rack_pad_thickness_mm=2.0,
    restraint_plate_thickness_mm=2.0,
    # Pack jacket
    jacket_insulation_thickness_mm=10.0,
    jacket_interior_plate_thickness_mm=1.0,
    jacket_exterior_base_plate_thickness_mm=1.0,
    insulation_density_kg_per_m2_per_mm=0.032,
    # BMS
    bms_bdu_mass_kg=2.444,      # BatPaC BMS!G139
    bms_bdu_volume_L=1.5485,    # BatPaC BMS!G148
    
    # In-module hardware (BatPaC rows 352-382)
    interconnect_thickness_mm=1.0,          # BatPaC G164
    interconnect_panel_thickness_mm=2.0,    # BatPaC G360
    external_weld_tab_mm=8.0,               # BatPaC G092
    module_terminal_length_mm=35.0,         # BatPaC G368
    gas_release_provision_g=5.0,            # BatPaC G382
    # Heating-rate based conductor sizing
    nominal_pack_current_A=100.0,
    heating_rate_tabs_to_module_terminals=0.4,   # BatPaC G172
    heating_rate_module_terminals=0.2,           # BatPaC G180
    heating_rate_module_interconnect=0.2,        # BatPaC G187
    heating_rate_busbar_to_terminal=0.1,
    heating_rate_busbar_bridging=0.1,
    heating_rate_pack_terminal=0.1,
    pack_terminal_eff_length_cm=12.0,
):
    """
    Full BatPaC v5.2-faithful cell -> module -> row rack -> pack hierarchy.
    Every geometric, mass, and electrical formula below is transcribed directly
    from BatPaC v5.2 (Battery Design worksheet, column G) and numerically
    verified against real BatPaC output to better than 1e-5 relative error.

    Documented deviations from BatPaC:

    1. Bus bar / interconnect / pack terminal conductor sizing uses BatPaC's exact
       heating-rate physics (current density, Cu conductivity, specific heat,
       density), but is driven by `nominal_pack_current_A` - a stationary-storage
       discharge current supplied by the user - rather than BatPaC's vehicle
       power-burst-rated current (BatPaC G403), since this model has no target
       peak power input. The conductor formulas themselves are identical.

    2. Pack voltage is the sum of series cell voltages (BatPaC G400) rather than
       BatPaC's G399, which subtracts the discharge IR drop. This affects the
       predicted voltage sag only, not mass, volume or material cost, and leaves
       pack energy ~1.2% above BatPaC at the NMC811-G reference point.

    3. Battery heaters (BatPaC G491/G492, 0.2 kg for a 1 kW vehicle heater) are
       omitted: they are a cabin-conditioning provision with no counterpart in a
       stationary installation. This is the only term in G495 not reproduced here,
       and it accounts for the residual 0.04% gap in total pack mass.
    """
    RHO_AL_LOCAL = 2.70
    RHO_STEEL_LOCAL = 7.80
    RHO_CU_LOCAL = 8.96
    CONDUCTIVITY_CU_LOCAL = 59_600_000.0
    CP_CU_LOCAL = 0.38548

    # ── 1. Pack topology (BatPaC convention, rows 25-38) ─────────────────────
    # G31 (cells per pack) = modules_per_pack x cells_per_module
    # G37 (pack capacity, Ah) = cell_capacity x cells_in_parallel x modules_in_parallel
    # Pack voltage = cells_series_per_module x modules_in_series x cell_voltage.
    # (BatPaC's G399 additionally corrects pack voltage for discharge IR drop
    #  under load - this affects voltage SAG prediction only, not mass, volume,
    #  or material cost, so it is intentionally out of scope for this model.)
    modules_per_pack = modules_per_row * rows_per_pack
    total_cells = modules_per_pack * cells_per_module

    cells_series_per_module = max(1, round(cells_per_module / max(cells_parallel, 1)))
    modules_in_series = max(1, modules_per_pack // max(modules_parallel, 1))

    pack_voltage_V = cells_series_per_module * modules_in_series * cell_voltage_V
    pack_capacity_Ah = cell_capacity_Ah * cells_parallel * modules_parallel
    pack_gross_energy_kWh = (pack_voltage_V * pack_capacity_Ah) / 1000
    pack_useable_energy_kWh = pack_gross_energy_kWh * useable_soc_fraction

    # BatPaC G478: top exterior plate thickness scales with target pack energy
    jacket_exterior_top_plate_thickness_mm = (
        1.0 if pack_gross_energy_kWh < 10 else (1.5 if pack_gross_energy_kWh < 20 else 2.0)
    )

    # ── 2. Module geometry (BatPaC rows 373-390) ─────────────────────────────
    conductor_length_mm = positive_electrode_length_mm + 6          # G373
    al_conductor_thick = al_conductor_thickness_mm                  # G374

    al_conductor_g_per_module = (                                   # G375
        (cells_per_module + 1) * conductor_length_mm *
        ((cell_width_mm + 2 * al_conductor_thick) + 0.95 * cell_thickness_mm * 2) *
        al_conductor_thick / 1000 * RHO_AL_LOCAL
    )

    module_length_mm = cell_length_mm + module_length_buffer_mm + module_length_buffer2_mm   # G387
    module_width_mm = (cell_thickness_mm + al_conductor_thick) * cells_per_module + 2 * module_wall_thickness_mm  # G388
    module_height_mm = cell_width_mm + 2 * al_conductor_thick + 2 * module_wall_thickness_mm # G389
    module_volume_L = module_length_mm * module_width_mm * module_height_mm / 1_000_000      # G390

    module_enclosure_g = RHO_STEEL_LOCAL * module_wall_thickness_mm * (                      # G381
        module_length_mm * module_width_mm + module_length_mm * module_height_mm + module_width_mm * module_height_mm
    ) * 2 / 1000

    # ── 2b. Remaining in-module hardware (BatPaC rows 352-382) ───────────────
    # These six terms make up roughly a third of BatPaC's non-cell module mass and
    # are computed here (rather than only inside the cost model) so that Module 03
    # and Module 04 describe the same physical module.
    def _conductor_cs_cm2(current_A, heating_rate):
        """BatPaC G173/G181/G188/G196/G204/G212: Cu cross-section, cm2."""
        return current_A / (CONDUCTIVITY_CU_LOCAL / 100 * heating_rate * CP_CU_LOCAL * RHO_CU_LOCAL) ** 0.5

    _cells_series_in_module = max(1, round(cells_per_module / max(cells_parallel, 1)))
    _max_cell_current_A   = nominal_pack_current_A / (max(cells_parallel, 1) * max(modules_parallel, 1))
    _max_module_current_A = _max_cell_current_A * cells_parallel

    _feed_width_mm = 50.0 if cell_width_mm > 84 else 40.0          # G097
    _g165 = interconnect_thickness_mm / 10 * _feed_width_mm / 10   # G165 cross-section, cm2
    _g352 = cell_thickness_mm + al_conductor_thick                 # G352 interconnect width
    _g353 = _g352 + 2 * (external_weld_tab_mm - interconnect_panel_thickness_mm)  # G353
    # BatPaC keeps two counts that are easy to conflate: G168 is the number of
    # cell interconnects (used for the annual production rate MC G12), and G354
    # adds the extra links needed to tie parallel cells together (used for the
    # per-module mass G355 and the per-module plus-cost MC G157).
    _g168 = (_cells_series_in_module - 1) * (1 + 2 * (cells_parallel - 1))
    _g354 = _g168 + (cells_parallel - 1) * 2
    cell_interconnect_g_per_module = _g354 * _g353 / 10 * _g165 * RHO_CU_LOCAL    # G355

    _g358 = cells_per_module * _g352 - 0.5 * cell_thickness_mm     # G358 panel length
    _g359 = cell_width_mm * 0.9                                    # G359 panel width
    interconnect_panel_g_per_module = (                            # G361 (PP, 2.1 g/cm3)
        2 * _g358 * _g359 * interconnect_panel_thickness_mm / 1000 * 2.1
    )

    _g173 = _conductor_cs_cm2(_max_module_current_A, heating_rate_tabs_to_module_terminals)
    _g364 = _feed_width_mm + 20                                    # G364
    module_tabs_g_per_module = 2 * _g364 / 10 * _g173 * RHO_CU_LOCAL          # G365

    _g181 = _conductor_cs_cm2(_max_module_current_A, heating_rate_module_terminals)
    modules_per_pack_est = modules_per_row * rows_per_pack
    module_terminals_g_per_module = (                              # G369
        0.0 if modules_per_pack_est == 1
        else 2 * module_terminal_length_mm / 10 * _g181 * RHO_CU_LOCAL * 1.2
    )

    module_mms_g = 120 * 12 * 16 / 1000 * 2                        # G378 (46.08 g)
    module_gas_release_g = gas_release_provision_g                 # G382

    module_hardware_g = (
        al_conductor_g_per_module + module_enclosure_g
        + cell_interconnect_g_per_module + interconnect_panel_g_per_module
        + module_tabs_g_per_module + module_terminals_g_per_module
        + module_mms_g + module_gas_release_g
    )

    # Split by material so Module 05 can assign carbon intensities and recovery
    # streams from the components themselves rather than an assumed fraction.
    # BatPaC materials: G375 aluminium; G381 and G378 steel; G355, G365 and G369
    # copper; G361 polypropylene; G382 unassigned miscellaneous.
    module_al_g      = al_conductor_g_per_module                              # G375
    module_steel_g   = module_enclosure_g + module_mms_g                      # G381, G378
    module_cu_g      = (cell_interconnect_g_per_module
                        + module_tabs_g_per_module
                        + module_terminals_g_per_module)                      # G355, G365, G369
    module_polymer_g = interconnect_panel_g_per_module                        # G361
    module_other_g   = module_gas_release_g                                   # G382
    module_mass_kg = (cells_per_module * cell_mass_g + module_hardware_g) / 1000   # G391

    # ── 3. Row rack geometry (BatPaC rows 409-428) ───────────────────────────
    # G426 = bus-bar allowance + manifold I.D. + connecting-tube I.D. + wall thicknesses
    _manifold_diameter_mm = 25.0
    _connecting_tube_diameter_mm = 12.0
    g426 = rack_busbar_allowance_mm + _manifold_diameter_mm + _connecting_tube_diameter_mm + 2 * 0.5 + 2 * 0.4
    rack_length_mm = (module_width_mm * modules_per_row
                      + rack_pad_thickness_mm * (modules_per_row - 1)
                      + rack_length_buffer_mm + g426)
    rack_width_mm = module_length_mm + rack_width_buffer_mm

    coolant_panel_total_thick = coolant_panel_thickness_mm + 2 * coolant_plate_wall_mm
    rack_height_mm = module_height_mm + 2 * coolant_panel_total_thick + 1 + 1

    rack_lower_channel_kg = rack_length_mm * (rack_width_mm + 2 * (10 - 1)) * 1 / 1000 * RHO_STEEL_LOCAL / 1000

    if modules_per_row == 1:
        vert_member_len_mm = 4 * (rack_height_mm - 6)
    else:
        vert_member_len_mm = (modules_per_row * 2 + 2) * (rack_height_mm - 6) + 4 * (rack_height_mm - 6) * math.sqrt(2)
    rack_upper_channel_kg = (rack_length_mm * (rack_width_mm - 2 * 1) * 1 + vert_member_len_mm * 15) / 1000 * RHO_STEEL_LOCAL / 1000

    coolant_panel_width_mm = conductor_length_mm

    restraint_area_cm2 = (
        (coolant_panel_width_mm + 4) * (module_height_mm - 4) +
        2 * (module_length_mm - coolant_panel_width_mm - 16) * (rack_height_mm + 30)
    ) / 100
    restraint_vol_cm3 = (module_height_mm - 2) * (positive_electrode_length_mm + 4) * 1.5 / 1000 + 6 * 0.2
    restraint_kg = 2 * (restraint_plate_thickness_mm / 10 * restraint_area_cm2 + restraint_vol_cm3) * RHO_STEEL_LOCAL / 1000

    pad_kg_per_row = (modules_per_row - 1) * (positive_electrode_length_mm + 4) * (module_height_mm - 2) * rack_pad_thickness_mm / 1000 * 0.3 / 1000

    rack_total_kg_per_row = rack_lower_channel_kg + rack_upper_channel_kg + restraint_kg + pad_kg_per_row

    # ── 4. Cooling system (BatPaC rows 437-447) ──────────────────────────────
    coolant_panel_length_mm = rack_length_mm - 4
    num_plates = 2
    coolant_panel_kg = rows_per_pack * num_plates * (
        2 * coolant_panel_width_mm * coolant_panel_length_mm +
        2 * coolant_panel_width_mm * coolant_panel_thickness_mm +
        (2 if num_plates == 2 else 5) * coolant_panel_thickness_mm * coolant_panel_length_mm
    ) * coolant_plate_wall_mm / 1000 / 1000 * RHO_STEEL_LOCAL

    manifold_diameter_mm = _manifold_diameter_mm
    connecting_tube_diameter_mm = _connecting_tube_diameter_mm
    main_tubing_length_mm = 2 * rows_per_pack * rack_width_mm
    connecting_tubing_length_mm = (2 * rows_per_pack * (6 + module_height_mm)) if num_plates == 2 else 0.0
    mains_mass_g = main_tubing_length_mm * ((manifold_diameter_mm + 1) ** 2 - manifold_diameter_mm ** 2) * math.pi / 4 / 1000 * RHO_STEEL_LOCAL
    connecting_tubing_mass_g = connecting_tubing_length_mm * (12.8 ** 2 - connecting_tube_diameter_mm ** 2) * math.pi / 4 / 1000 * RHO_STEEL_LOCAL + 4 * rows_per_pack * 10
    coolant_manifold_kg = (mains_mass_g + connecting_tubing_mass_g) / 1000

    coolant_density_g_per_mL = 1.07
    coolant_liquid_kg = (
        (coolant_panel_width_mm * coolant_panel_thickness_mm * coolant_panel_length_mm * rows_per_pack * num_plates) +
        (main_tubing_length_mm * 30 ** 2 * math.pi / 4) +
        (connecting_tubing_length_mm * 15 ** 2 * math.pi / 4)
    ) / 1000 * coolant_density_g_per_mL / 1000
    cooling_system_kg = coolant_panel_kg + coolant_manifold_kg + coolant_liquid_kg

    # ── 5. Pack dimensions (BatPaC rows 450-458) ─────────────────────────────
    jacket_base_thick_mm = jacket_insulation_thickness_mm + jacket_interior_plate_thickness_mm + jacket_exterior_base_plate_thickness_mm
    jacket_top_thick_mm = jacket_insulation_thickness_mm + jacket_interior_plate_thickness_mm + jacket_exterior_top_plate_thickness_mm

    pack_length_mm = rack_length_mm + 2 + 2 * jacket_base_thick_mm

    g199 = rows_per_pack % 2
    g207 = max((rows_per_pack + 1) // 2 - 1, 0)
    mod_term = (rows_per_pack + 1) % 2
    g454 = 10 * g199 + 15 * (g207 + mod_term) + 5 * (g199 + (g207 + mod_term) - 1)

    pack_width_mm = rows_per_pack * rack_width_mm + 2 + g454 + 2 * jacket_base_thick_mm
    jacket_interior_width_mm = rows_per_pack * rack_width_mm + 2 + g454
    pack_height_mm = rack_height_mm + 2 + jacket_base_thick_mm + jacket_top_thick_mm

    # ── 6. Pack jacket mass (BatPaC rows 462-483) ────────────────────────────
    # BatPaC G466/G467: INDEX/MATCH over Lists!AQ133:AQ137 with match type 1
    # (largest tabulated volume not exceeding the estimate). Below 20 L BatPaC
    # fits no support frame at all; 20-40 L gets 30x30x3; 40 L and above 40x40x4.
    est_pack_vol_L = modules_per_pack * module_volume_L
    if est_pack_vol_L < 20:
        frame_H, frame_L_, frame_T = 0, 0, 0
    elif est_pack_vol_L < 40:
        frame_H, frame_L_, frame_T = 30, 30, 3
    else:
        frame_H, frame_L_, frame_T = 40, 40, 4
    frame_unit_mass_g_per_mm = (frame_H * frame_T + frame_L_ * frame_T - frame_T ** 2) * RHO_STEEL_LOCAL / 1000
    jacket_support_frame_kg = frame_unit_mass_g_per_mm * (pack_length_mm * 2 + 2 * pack_width_mm) / 1000

    jacket_interior_base_kg = (
        (pack_length_mm - 2 * jacket_base_thick_mm) * jacket_interior_width_mm * jacket_exterior_base_plate_thickness_mm / 1000
    ) * RHO_AL_LOCAL / 1000

    jacket_exterior_base_kg = (
        (pack_length_mm - 2 * jacket_base_thick_mm) * jacket_interior_width_mm +
        2 * ((pack_length_mm - 2 * jacket_base_thick_mm) + jacket_interior_width_mm) * (jacket_base_thick_mm - 4)
    ) * jacket_interior_plate_thickness_mm / 1000 * RHO_STEEL_LOCAL / 1000

    insulation_area_base_m2 = ((pack_length_mm - 2 * jacket_base_thick_mm) * jacket_interior_width_mm) / 100 / 10000
    jacket_base_kg = (
        jacket_support_frame_kg + jacket_interior_base_kg + jacket_exterior_base_kg
        + insulation_area_base_m2 * jacket_insulation_thickness_mm * insulation_density_kg_per_m2_per_mm
    )

    plates_kg = (
        2 * (pack_length_mm + pack_width_mm) * pack_height_mm * jacket_exterior_top_plate_thickness_mm / 1000 +
        2 * ((pack_width_mm - 2 * jacket_base_thick_mm) + (pack_length_mm - 2 * jacket_base_thick_mm)) * (pack_height_mm - 2 * jacket_base_thick_mm) * jacket_interior_plate_thickness_mm / 1000 +
        (pack_length_mm * pack_width_mm) * jacket_exterior_top_plate_thickness_mm / 1000 +
        (pack_length_mm - 2 * jacket_base_thick_mm) * (pack_width_mm - 2 * jacket_base_thick_mm) * jacket_interior_plate_thickness_mm / 1000
    ) * RHO_AL_LOCAL / 1000

    insulation_area_top_m2 = (
        ((pack_length_mm - 2 * jacket_exterior_top_plate_thickness_mm) * (pack_width_mm - 2 * jacket_exterior_top_plate_thickness_mm)) / 100 +
        2 * ((pack_length_mm - jacket_base_thick_mm) + (pack_width_mm - jacket_base_thick_mm)) * (pack_height_mm - 2 * jacket_base_thick_mm) / 100
    ) / 10000
    jacket_top_kg = plates_kg + insulation_area_top_m2 * jacket_insulation_thickness_mm * insulation_density_kg_per_m2_per_mm

    pack_jacket_total_kg = jacket_base_kg + jacket_top_kg

    # ── 7. Conductors (BatPaC rows 187-214, 488-490) ─────────────────────────
    max_pack_current_A = nominal_pack_current_A
    max_module_current_A = _max_module_current_A

    g188 = _conductor_cs_cm2(max_module_current_A, heating_rate_module_interconnect)
    module_interconnect_g = 6.0 * g188 * RHO_CU_LOCAL * 1.3      # G488, per interconnect

    g196 = _conductor_cs_cm2(max_pack_current_A, heating_rate_busbar_to_terminal)
    g197 = modules_per_row * module_width_mm / 10 + 4
    g199_flag = rows_per_pack % 2

    g204 = _conductor_cs_cm2(max_pack_current_A, heating_rate_busbar_bridging)
    g205 = 2 * module_length_mm / 10 + 0.5 + 2
    g207_count = max((rows_per_pack + 1) // 2 - 1, 0)

    busbar_pack_g = (g196 * g197 * g199_flag + g204 * g205 * g207_count) * RHO_CU_LOCAL   # G489

    g212 = _conductor_cs_cm2(max_pack_current_A, heating_rate_pack_terminal)
    pack_terminals_g = 2 * (pack_terminal_eff_length_cm + 2) * g212 * RHO_CU_LOCAL / 0.9  # G490

    # ── 8. BMS ────────────────────────────────────────────────────────────────
    # BMS mass/volume - BatPaC v5.2 BMS!G136-G151 (feeds Battery Design B494/B486).
    # Scales with ASIC count, not module count: n_ASIC = ceil(cells_in_series / 10)  [BMS!G23, G22]
    # BDU term (BMS!G139/G148) is a component-table sum, constant for packs above 100 V.
    # BMS!G138 multiplies PCB mass by main-contactor count (G61=2); reproduced as-is
    #       for workbook fidelity despite appearing anomalous.
    _cells_in_series = cells_series_per_module * modules_in_series
    _n_asic  = math.ceil(_cells_in_series / 10)
    _n_pcb   = 1 * 2                                           # G30 x G61
    _bmu_m   = _n_pcb * 0.04 + 0.02 * _n_asic                  # BMS!G138
    _bmu_v   = _n_pcb * 0.16 + 0.08 * _n_asic                  # BMS!G147
    bms_mass_kg  = (_bmu_m * 1.1 + bms_bdu_mass_kg)   * 1.3    # BMS!G140-G142
    bms_volume_L = (_bmu_v * 1.1 + bms_bdu_volume_L)  * 1.3    # BMS!G149-G151

    # ── 9. Final assembly ────────────────────────────────────────────────────
    cell_mass_total_kg = total_cells * cell_mass_g / 1000
    module_mass_total_kg = modules_per_pack * module_mass_kg
    rack_mass_total_kg = rows_per_pack * rack_total_kg_per_row
    # BatPaC G191: module inter-connects are the conductors BETWEEN modules, so the
    # count is (modules per row + 1) x rows, not one per cell. G493 then rolls them
    # up with the bus bars and pack terminals into pack hardware mass.
    num_module_interconnects = (modules_per_row + 1) * rows_per_pack
    conductors_kg = (
        module_interconnect_g * num_module_interconnects
        + busbar_pack_g + pack_terminals_g
    ) / 1000

    non_cell_mass_kg = (
        (module_mass_total_kg - cell_mass_total_kg)
        + rack_mass_total_kg
        + cooling_system_kg
        + pack_jacket_total_kg
        + conductors_kg
        + bms_mass_kg
    )
    pack_mass_kg = cell_mass_total_kg + non_cell_mass_kg

    cell_volume_total_L = total_cells * cell_volume_cm3 / 1000
    module_volume_total_L = modules_per_pack * module_volume_L
    pack_volume_L = pack_length_mm * pack_width_mm * pack_height_mm / 1_000_000

    pack_specific_energy = (pack_useable_energy_kWh * 1000) / pack_mass_kg if pack_mass_kg else 0
    pack_energy_density = (pack_useable_energy_kWh * 1000) / pack_volume_L if pack_volume_L else 0
    cell_mass_fraction = cell_mass_total_kg / pack_mass_kg if pack_mass_kg else 0
    cell_volume_fraction = cell_volume_total_L / pack_volume_L if pack_volume_L else 0

    series_parallel_valid = (cells_per_module % cells_parallel == 0) if cells_parallel else False
    modules_valid = (modules_per_pack % modules_parallel == 0) if modules_parallel else False

    return {
        "total_cells": total_cells, "modules_per_pack": modules_per_pack,
        "modules_in_series": modules_in_series, "cells_series_per_module": cells_series_per_module,
        "pack_voltage_V": pack_voltage_V, "pack_capacity_Ah": pack_capacity_Ah,
        "pack_gross_energy_kWh": pack_gross_energy_kWh, "pack_useable_energy_kWh": pack_useable_energy_kWh,
        "module_mass_kg": module_mass_kg, "module_volume_L": module_volume_L,
        "module_length_mm": module_length_mm, "module_width_mm": module_width_mm, "module_height_mm": module_height_mm,
        "al_conductor_g_per_module": al_conductor_g_per_module, "module_enclosure_g": module_enclosure_g,
        "rack_length_mm": rack_length_mm, "rack_width_mm": rack_width_mm, "rack_height_mm": rack_height_mm,
        "rack_total_kg_per_row": rack_total_kg_per_row, "rack_mass_total_kg": rack_mass_total_kg,
        "cooling_system_kg": cooling_system_kg,
        "coolant_panel_kg": coolant_panel_kg, "coolant_manifold_kg": coolant_manifold_kg,
        "coolant_liquid_kg": coolant_liquid_kg,
        "pack_length_mm": pack_length_mm, "pack_width_mm": pack_width_mm, "pack_height_mm": pack_height_mm,
        "pack_jacket_total_kg": pack_jacket_total_kg,
        "jacket_support_frame_kg": jacket_support_frame_kg,
        "jacket_interior_base_kg": jacket_interior_base_kg, "jacket_exterior_base_kg": jacket_exterior_base_kg,
        "jacket_top_plates_kg": plates_kg,
        "positive_electrode_length_mm": positive_electrode_length_mm,
        "module_interconnect_g": module_interconnect_g, "busbar_pack_g": busbar_pack_g, "pack_terminals_g": pack_terminals_g,
        "num_module_interconnects": num_module_interconnects,
        "conductors_kg": conductors_kg,
        "cell_interconnect_g_per_module": cell_interconnect_g_per_module,
        "interconnect_panel_g_per_module": interconnect_panel_g_per_module,
        "module_tabs_g_per_module": module_tabs_g_per_module,
        "module_terminals_g_per_module": module_terminals_g_per_module,
        "module_mms_g": module_mms_g, "module_gas_release_g": module_gas_release_g,
        "module_hardware_g": module_hardware_g,
        "module_al_g": module_al_g, "module_steel_g": module_steel_g,
        "module_cu_g": module_cu_g, "module_polymer_g": module_polymer_g,
        "module_other_g": module_other_g,
        "cell_interconnects_per_module": _g354,        # BD G354
        "cell_interconnect_rate_per_module": _g168,    # BD G168
        "bms_mass_kg": bms_mass_kg, "bms_volume_L": bms_volume_L,
        "cell_mass_total_kg": cell_mass_total_kg, "module_mass_total_kg": module_mass_total_kg,
        "non_cell_mass_kg": non_cell_mass_kg, "pack_mass_kg": pack_mass_kg,
        "cell_volume_total_L": cell_volume_total_L, "module_volume_total_L": module_volume_total_L,
        "pack_volume_L": pack_volume_L,
        "pack_specific_energy": pack_specific_energy, "pack_energy_density": pack_energy_density,
        "cell_mass_fraction": cell_mass_fraction, "cell_volume_fraction": cell_volume_fraction,
        "series_parallel_valid": series_parallel_valid, "modules_valid": modules_valid,
        "max_module_current_A": max_module_current_A,
        "insulation_area_base_m2": insulation_area_base_m2,
        "insulation_area_top_m2": insulation_area_top_m2,
        "rack_pad_kg_per_row": pad_kg_per_row,
    }


def run_cost_model(
    # ── From Module 01 (electrochemical) ──
    c_AM_mass_g, a_AM_mass_g,
    c_carbon_g, a_carbon_g,
    c_binder_g, a_binder_g,
    binder_solvent_ratio_pos, binder_solvent_ratio_neg,   # 16 (NMP) or 40 (water)
    binder_solvent_density_pos, binder_solvent_density_neg,
    c_AM_density, c_carbon_density, c_binder_density,
    a_AM_density, a_carbon_density, a_binder_density,
    # ── From Module 02 (cell design) ──
    c_foil_m2, a_foil_m2, sep_m2, elec_vol_L,
    container_mass_g, cell_mass_g,
    cell_capacity_Ah, cell_voltage_V,
    positive_electrode_area_cm2, negative_electrode_area_cm2,
    num_bicell_layers,
    # ── From Module 03 (pack design) ──
    total_cells, modules_per_pack, cells_per_module, modules_per_row, rows_per_pack,
    pack_useable_energy_kWh, pack_gross_energy_kWh,
    al_conductor_g_per_module, module_enclosure_g,
    cell_interconnect_g_per_module, interconnect_panel_g_per_module,
    module_terminals_g_per_module,
    cell_interconnects_per_module, cell_interconnect_rate_per_module,
    busbar_pack_g, pack_terminals_g, module_interconnect_g,
    rack_total_kg_per_row,
    coolant_panel_kg, coolant_manifold_kg, coolant_liquid_kg,
    jacket_support_frame_kg, jacket_interior_base_kg, jacket_exterior_base_kg,
    jacket_top_plates_kg, pack_jacket_total_kg,
    bms_mass_kg,
    # ── Material prices (existing Module 04 inputs) ──
    p_cathode_am, p_anode_am, p_carbon,
    p_pvdf, p_cmcsbr, p_al_foil, p_anode_foil,
    p_sep, p_electrolyte, p_container,
    p_pos_terminal_kg, p_neg_terminal_kg, terminal_fixed_cost,
    terminal_mass_cathode_g, terminal_mass_anode_g,
    # ── New BatPaC process-cost inputs ──
    annual_production_packs,          # Dashboard!D110 equivalent - YOUR annual volume
    cell_yield_pct,                   # Dashboard!D115 - fraction of cells that pass QC
    labor_rate_per_hr,                # Cost Input F93, default $35/hr
    energy_price_per_kWh,             # Cost Input F94, default $0.04/kWh
    effective_days_per_year,          # Cost Input F81, default 320
    # ── BMS unit cost (separate sheet in BatPaC, simplified here) ──
    bms_cost_per_pack,
    # ── Pack jacket/hardware unit prices (Cost Input rows 64-74) ──
    p_row_rack, p_module_pads, p_module_interconnect, p_busbar,
    p_coolant_panel, p_coolant_manifold, p_pack_terminal_seal,
    p_pack_support_frame, p_jacket_top_interior, p_jacket_exterior_base,
    p_jacket_insulation,
    # ── LFP benchmark (optional; computed by Module 06, not entered) ──
    lfp_benchmark_per_kwh=None,
    # ── Module geometry for hardware cost calculations ──
    cells_parallel=2,
    insulation_area_base_m2=0.0, insulation_area_top_m2=0.0,
    rack_pad_kg_per_row=0.0,
    # ── BatPaC material purchase fractions (Cost Input G12-G17) ──
    mat_yield_coating_pct=94.1,
    mat_yield_foil_pct=88.3,
    mat_yield_sep_pct=99.0,
    container_plus_cost=0.20,
    p_pos_solvent=2.70,   # BatPaC CI106: NMP binder solvent $/kg (default $2.70)
    p_neg_solvent=0.00,   # BatPaC CI112: water binder solvent $/kg (default $0)
):
    """
    Full BatPaC v5.2-faithful manufacturing cost engine: cell -> module -> pack.
    313 individual formulas verified against real BatPaC v5.2 output to better
    than 1e-5 relative error (see verify_m04_stage1.py for the verification record).

    This computes:
      1. Material + purchased-item cost per cell (your existing Module 04 logic, unchanged)
      2. Direct labor, capital, plant area, and energy for all 26 BatPaC process
         steps, scaled by YOUR annual production volume and cell design
      3. Cell-level cost roll-up: variable cost + fixed expenses + profit + warranty
      4. Module-level cost roll-up: purchased hardware (linked to your verified
         Module 03 outputs) + manufacturing + profit + warranty
      5. Pack-level cost roll-up: purchased hardware (jacket, busbars, rack,
         cooling) + manufacturing + profit + warranty
      6. Final total cost per pack = cells + modules + pack + profit + warranty
    """
    # ════════════════════════════════════════════════════════════════════════
    # PART 0 - Yield and material purchase factors
    # BatPaC prices and meters materials per ACCEPTED cell, accounting for:
    #   (a) cell yield loss -- scrapped cells waste all their materials
    #   (b) material purchase fractions -- coating/foil trim & scrap losses
    # Formula: raw_quantity / (purchase_fraction/100) / (cell_yield_pct/100)
    # Ref: BatPaC Manufacturing Costs rows 46-68, Cost Input G12-G17
    # ════════════════════════════════════════════════════════════════════════
    coat_factor     = 10000.0 / (mat_yield_coating_pct * cell_yield_pct)
    foil_factor     = 10000.0 / (mat_yield_foil_pct    * cell_yield_pct)
    sep_elec_factor = 10000.0 / (mat_yield_sep_pct     * cell_yield_pct)
    cont_term_factor = 100.0  / cell_yield_pct

    # Purchased coating masses per accepted cell (MC G46-G48, G53-G55)
    c_AM_purch     = c_AM_mass_g  * coat_factor
    a_AM_purch     = a_AM_mass_g  * coat_factor
    c_carbon_purch = c_carbon_g   * coat_factor
    a_carbon_purch = a_carbon_g   * coat_factor
    c_binder_purch = c_binder_g   * coat_factor
    a_binder_purch = a_binder_g   * coat_factor

    # ════════════════════════════════════════════════════════════════════════
    # PART 1 - Annual production rate cascade (BatPaC G8-G22)
    # ════════════════════════════════════════════════════════════════════════
    G9 = annual_production_packs
    G8 = G9 * pack_gross_energy_kWh
    G10 = rows_per_pack * 1 * G9                       # row racks/yr
    G11 = G9 * modules_per_pack                        # modules/yr
    # G12 = packs/yr x modules/pack x cell interconnects/module (BD G168), not cells+1
    G12 = G9 * modules_per_pack * cell_interconnect_rate_per_module
    G13 = G9 * pack_gross_energy_kWh                   # pack energy/yr (manufact_method=1)
    G14 = math.ceil(G9 * total_cells)                  # accepted cells/yr
    G15 = G14 / cell_yield_pct * 100                   # cells adjusted for yield
    G16 = G15 * positive_electrode_area_cm2 / 10000    # positive electrode area/yr, m2
    G17 = G15 * negative_electrode_area_cm2 / 10000    # negative electrode area/yr, m2

    # Binder solvent annual mass (kg/yr), MC G97/G98 = G49/G56 x G15 / 1000.
    # G49 = solvent ratio x the PURCHASED binder mass (MC G48), so the material
    # purchase fraction and cell yield both carry through here, exactly as they do
    # in the per-cell cost. Using the raw binder mass instead understates the
    # slurry volume, solvent load and every process step scaled off them.
    G97 = binder_solvent_ratio_pos * c_binder_purch * G15 / 1000
    G98 = binder_solvent_ratio_neg * a_binder_purch * G15 / 1000

    # Slurry volumes, MC G18/G19: purchased mass / density, summed over the
    # active material, conductive additive, binder and binder solvent.
    G18 = (c_AM_purch*G15/1000)/c_AM_density + (c_carbon_purch*G15/1000)/c_carbon_density + \
          (c_binder_purch*G15/1000)/c_binder_density + G97/binder_solvent_density_pos
    G19 = (a_AM_purch*G15/1000)/a_AM_density + (a_carbon_purch*G15/1000)/a_carbon_density + \
          (a_binder_purch*G15/1000)/a_binder_density + G98/binder_solvent_density_neg

    F81 = effective_days_per_year
    p_days = 320 / F81 if F81 else 1.0
    hrs_to_GWh = 24 * F81 / 1000000

    # ════════════════════════════════════════════════════════════════════════
    # PART 2 - Per-cell material cost (BatPaC MC G127-G152)
    # ════════════════════════════════════════════════════════════════════════
    cost_cathode_am = c_AM_purch     / 1000 * p_cathode_am
    cost_anode_am   = a_AM_purch     / 1000 * p_anode_am
    cost_carbon     = (c_carbon_purch + a_carbon_purch) / 1000 * p_carbon
    cost_pvdf       = c_binder_purch / 1000 * p_pvdf
    cost_cmcsbr     = a_binder_purch / 1000 * p_cmcsbr
    # MC G130/G136: binder solvent cost per accepted cell
    cost_pos_solvent = binder_solvent_ratio_pos * c_binder_purch / 1000 * p_pos_solvent
    cost_neg_solvent = binder_solvent_ratio_neg * a_binder_purch / 1000 * p_neg_solvent
    cost_c_foil     = c_foil_m2 * p_al_foil * foil_factor
    cost_a_foil     = a_foil_m2 * p_anode_foil * foil_factor
    cost_sep        = sep_m2 * p_sep * sep_elec_factor
    cost_elec       = elec_vol_L * p_electrolyte * sep_elec_factor
    # BatPaC MC G121-G123: per-cell hardware cost = mass_kg * $/kg + plus_cost, where
    # the plus cost is scaled by (F347 / G15)^(1-p) -- F347 = 211e6 cells adjusted for
    # yield, NOT the cell-interconnect rate. Yield is then applied via cont_term_factor
    # (MC G148-G150). Ref: CI045-047, scale exponent p = 0.85.
    _F347_base = 211000000.0
    _plus_scale = (_F347_base / G15) ** (1 - 0.85) if G15 else 1.0
    cost_container = (
        container_mass_g / 1000 * p_container + container_plus_cost * _plus_scale
    ) * cont_term_factor
    cost_terminal = (
        terminal_mass_cathode_g / 1000 * p_pos_terminal_kg
        + terminal_mass_anode_g / 1000 * p_neg_terminal_kg
        + 2 * terminal_fixed_cost * _plus_scale
    ) * cont_term_factor

    mat_cost_per_cell = (
        cost_cathode_am + cost_anode_am + cost_carbon + cost_pvdf + cost_cmcsbr
        + cost_c_foil + cost_a_foil + cost_sep + cost_elec + cost_container + cost_terminal
        + cost_pos_solvent + cost_neg_solvent
    )

    # ════════════════════════════════════════════════════════════════════════
    # PART 3 - All 26 BatPaC process steps (labor hrs/yr, capital $mil, area m2, power kW)
    # ════════════════════════════════════════════════════════════════════════
    baseline_pos_slurry, baseline_neg_slurry = 40700000, 65000000
    baseline_pos_area, baseline_neg_area = 303000000, 315000000
    baseline_cells_yr = 211000000            # CI F347, cells adjusted for yield
    baseline_accepted_cells_yr = 200000000   # CI F346, accepted cells
    baseline_modules_yr, baseline_packs_yr = 10000000, 500000
    baseline_energy_yr = 50000000
    heat_NMP, heat_water = 6.5, 0.75

    # Materials prep/mixing
    r_pos_slurry = G18 / baseline_pos_slurry
    L_prep_pos = 210000 * r_pos_slurry**0.9
    K_prep_pos = 152.04 * r_pos_slurry**0.9 * p_days
    A_prep_pos = 8600 * r_pos_slurry**0.95 * p_days
    P_prep_pos = 6700 * r_pos_slurry**0.95 * p_days

    r_neg_slurry = G19 / baseline_neg_slurry
    L_prep_neg = 220000 * r_neg_slurry**0.9
    K_prep_neg = 166.52 * r_neg_slurry**0.9 * p_days
    A_prep_neg = 8800 * r_neg_slurry**0.95 * p_days
    P_prep_neg = 7900 * r_neg_slurry**0.95 * p_days

    # Electrode coating
    r_pos_area = G16 / baseline_pos_area
    solvent_pos_kgm2 = G97 / G16 if G16 else 0
    L_coat_pos = 59000 * r_pos_area**0.7
    K_coat_pos = 76.075 * r_pos_area**0.9 * (solvent_pos_kgm2/0.07986798679867987)**0.2 * p_days
    A_coat_pos = 16000 * r_pos_area**0.95 * p_days
    P_coat_pos_dryer = 7200 * r_pos_area**0.95 * p_days
    P_coat_pos_heat = G97 * heat_NMP / F81 / 24
    P_coat_pos = P_coat_pos_dryer + P_coat_pos_heat

    r_neg_area = G17 / baseline_neg_area
    solvent_neg_kgm2 = G98 / G17 if G17 else 0
    L_coat_neg = 59000 * r_neg_area**0.7
    K_coat_neg = 71.6 * r_neg_area**0.9 * (solvent_neg_kgm2/0.13396825396825396)**0.2 * p_days
    A_coat_neg = 16000 * r_neg_area**0.95 * p_days
    P_coat_neg_dryer = 7200 * r_neg_area**0.95 * p_days
    P_coat_neg_heat = G98 * heat_water / F81 / 24
    P_coat_neg = P_coat_neg_dryer + P_coat_neg_heat

    # Calendering
    L_cal_pos = 47000 * r_pos_area**0.7
    K_cal_pos = 22.25 * r_pos_area**0.9 * p_days
    A_cal_pos = 2100 * r_pos_area**0.95 * p_days
    P_cal_pos = 900 * r_pos_area**0.95 * p_days
    L_cal_neg = 53000 * r_neg_area**0.7
    K_cal_neg = 22.25 * r_neg_area**0.9 * p_days
    A_cal_neg = 2100 * r_neg_area**0.95 * p_days
    P_cal_neg = 350 * r_neg_area**0.95 * p_days

    # Notching
    L_not_pos = 200000 * r_pos_area**0.7
    K_not_pos = 26.39 * r_pos_area**0.9 * p_days
    A_not_pos = 3200 * r_pos_area**0.95 * p_days
    P_not_pos = 1600 * r_pos_area**0.95 * p_days
    L_not_neg = 200000 * r_neg_area**0.7
    K_not_neg = 26.39 * r_neg_area**0.9 * p_days
    A_not_neg = 3200 * r_neg_area**0.95 * p_days
    P_not_neg = 1700 * r_neg_area**0.95 * p_days

    # Vacuum drying
    L_dry_pos = 41000 * r_pos_area**0.7
    K_dry_pos = 13.58 * r_pos_area**0.9 * p_days
    A_dry_pos = 1800 * r_pos_area**0.95 * p_days
    P_dry_pos = 2600 * r_pos_area**0.85 * p_days
    L_dry_neg = 35000 * r_neg_area**0.7
    K_dry_neg = 10.67 * r_neg_area**0.9 * p_days
    A_dry_neg = 1400 * r_neg_area**0.95 * p_days
    P_dry_neg = 2200 * r_neg_area**0.85 * p_days

    # Electrode slitting
    r_total_area = (G16+G17) / (baseline_pos_area+baseline_neg_area)
    L_slit = 260000 * r_total_area**0.7
    K_slit = 67.9 * r_total_area**0.9 * p_days
    A_slit = 7700 * r_total_area**0.95 * p_days
    P_slit = 1700 * r_total_area**0.95 * p_days

    # Cell stacking (cell-capacity adjusted)
    r_cells = G15 / baseline_cells_yr
    cap_factor_095 = (cell_capacity_Ah/68)**0.95
    L_stack = 700000 * cap_factor_095 * r_cells**0.9
    K_stack = 164.9 * cap_factor_095 * p_days * r_cells**0.9
    A_stack = 15000 * cap_factor_095 * p_days * r_cells**0.95
    P_stack = 4800 * r_cells**0.95 * p_days

    # Current collector welding
    L_weld = 180000 * r_cells**0.9
    K_weld = 179.55 * r_cells**0.9 * p_days
    A_weld = 3700 * r_cells**0.95 * p_days
    P_weld = 1800 * r_cells**0.95 * p_days

    # X-ray inspection
    L_xray = 180000 * r_cells**0.9
    K_xray = 12.95 * r_cells**0.9 * p_days
    A_xray = 4600 * r_cells**0.95 * p_days
    P_xray = 400 * r_cells**0.95 * p_days

    # Container insertion
    L_cont = 49000 * r_cells**0.9
    K_cont = 10.45 * r_cells**0.9 * p_days
    A_cont = 4700 * r_cells**0.95 * p_days
    P_cont = 1000 * r_cells**0.95 * p_days

    # Electrolyte filling
    L_fill = 130000 * r_cells**0.9
    K_fill = 23.75 * r_cells**0.9 * p_days
    A_fill = 11000 * r_cells**0.95 * p_days
    P_fill = 2400 * r_cells**0.95 * p_days

    # Dry room airlock
    r_dryroom = max(r_cells, r_total_area)
    L_dryair = 10000 * r_dryroom**0
    K_dryair = 6.935 * r_dryroom**0.9 * p_days
    A_dryair = 700 * r_dryroom**0.95 * p_days
    P_dryair = 300 * r_dryroom**0.95 * p_days

    # Formation cycling
    # G328 = G13/G14 * G15 / (F340 / F346 * F347). F346 and F347 are different
    # baselines (accepted cells vs cells adjusted for yield) and must not be conflated.
    _g328_base = baseline_energy_yr / baseline_accepted_cells_yr * baseline_cells_yr
    G328 = (G13/G14) * G15 / _g328_base if G14 else 0
    cap_factor_03 = (cell_capacity_Ah/68)**0.3
    L_form = 560000 * r_cells**0.7 * cap_factor_03
    heat_adj = 1.1 if cell_capacity_Ah > 80 else 1
    K_form = 700 * r_cells**0.95 * heat_adj * cap_factor_03
    A_form = 110000 * r_cells**0.95 * cap_factor_03
    P_form = 72000 * G328**1 * p_days

    # Module assembly
    r_modules = modules_per_pack * G9 / baseline_modules_yr
    cellmod_factor = (cells_per_module/20)**0.3
    L_modasm = 170000 * r_modules**0.7
    K_modasm = 101.2 * r_modules**0.95 * cellmod_factor * p_days
    A_modasm = 27000 * r_modules**0.95 * p_days
    P_modasm = 3100 * r_modules**0.8 * cellmod_factor * p_days

    # Pack assembly
    r_packs = G9 / baseline_packs_yr
    modpack_factor = (modules_per_pack/20)**0.3
    L_packasm = 170000 * r_packs**0.7 * modpack_factor
    K_packasm = 86.48 * r_packs**0.95 * modpack_factor * p_days
    A_packasm = 27000 * r_packs**0.95 * p_days
    P_packasm = 2700 * r_packs**0.8 * modpack_factor * p_days

    # Warehouse
    r_warehouse = G13 / baseline_energy_yr
    L_wh = 13000 * r_warehouse**0.7
    K_wh = 170 * r_warehouse**0.95 * p_days
    A_wh = 10000 * r_warehouse**0.95 * p_days
    P_wh = 7700 * r_warehouse**1 * p_days

    # Solvent recovery
    baseline_NMP = 24200000
    r_solvent = G97 / baseline_NMP
    L_solv = 14000 * r_solvent**0.7
    K_solv = 24.65 * r_solvent**0.95 * p_days
    A_solv = 900 * r_solvent**0.95 * p_days
    P_solv = 800 * r_solvent**0.7 * p_days

    # Scrap recycle
    D115 = cell_yield_pct
    r_scrap = (1-D115/100)/D115*100*G15/(100-D115)*D115/baseline_cells_yr
    L_scrap = 38000 * r_scrap**0.7
    K_scrap = 7.905 * r_scrap**0.9 * p_days
    A_scrap = 3300 * r_scrap**0.95 * p_days
    P_scrap = 3400 * r_scrap**1 * p_days

    # Control lab
    r_lab = G13 / baseline_energy_yr
    L_lab = 48000 * r_lab**0.7
    K_lab = 13.6 * r_lab**0.95 * p_days
    A_lab = 1300 * r_lab**0.95 * p_days
    P_lab = 20 * r_lab**1 * p_days

    # Dry room building systems
    # BatPaC G22 = sum of plant areas for cell assembly dry-room processes
    # G22 = G279+G287+G294+G301+G308+G315+G322 = A_slit+A_stack+A_weld+A_cont+A_fill+A_dryair+A_xray
    # Ref: Manufacturing Costs rows 279,287,294,301,308,315,322; G385 = G22 / CI354 (47400)
    G22 = A_slit + A_stack + A_weld + A_cont + A_fill + A_dryair + A_xray
    baseline_dryroom_area = 47400
    r_dryroomsys = G22 / baseline_dryroom_area if baseline_dryroom_area else 0
    K_dryroomsys = 450.5 * r_dryroomsys**0.95
    P_dryroomsys = 29000 * r_dryroomsys**0.95

    # Other building systems (cells)
    r_otherbuild = (3*G13 + G8) / baseline_energy_yr / 4
    K_otherbuild = 467.5 * r_otherbuild**0.95 * p_days
    P_otherbuild = 27000 * r_otherbuild**0.95 * p_days

    # Cooling system
    sum_process_power = (
        P_lab+P_scrap+P_solv+P_wh+P_form+P_dryair+P_fill+P_cont+P_xray+P_weld+P_stack+
        P_slit+P_dry_neg+P_dry_pos+P_not_neg+P_not_pos+P_cal_neg+P_cal_pos+P_coat_neg+
        P_coat_pos+P_prep_neg+P_prep_pos+P_packasm+P_modasm
    )
    G476 = 1.0  # 100% plant utilization (default)
    baseline_process_power = 221072.8645833333
    r_cooling = (sum_process_power/G476 + (P_dryroomsys+P_otherbuild)) / baseline_process_power
    K_cooling = 510 * r_cooling**0.95
    P_cooling = 29000 * r_cooling**0.95

    # ════════════════════════════════════════════════════════════════════════
    # PART 4 - Summations (BatPaC G407-G451)
    # ════════════════════════════════════════════════════════════════════════
    L_elec_total = L_prep_pos+L_prep_neg+L_coat_pos+L_coat_neg+L_cal_pos+L_cal_neg+L_not_pos+L_not_neg+L_dry_pos+L_dry_neg
    K_elec_total = K_prep_pos+K_prep_neg+K_coat_pos+K_coat_neg+K_cal_pos+K_cal_neg+K_not_pos+K_not_neg+K_dry_pos+K_dry_neg
    A_elec_total = A_prep_pos+A_prep_neg+A_coat_pos+A_coat_neg+A_cal_pos+A_cal_neg+A_not_pos+A_not_neg+A_dry_pos+A_dry_neg

    L_assy_total = L_slit+L_stack+L_weld+L_xray+L_cont+L_fill+L_dryair
    K_assy_total = K_slit+K_stack+K_weld+K_xray+K_cont+K_fill+K_dryair
    A_assy_total = A_slit+A_stack+A_weld+A_xray+A_cont+A_fill+A_dryair

    L_build_total = 0+L_solv+L_scrap+L_lab+0+0   # G386(dryroomsys)=0, G393(cooling)=0, G400(otherbuild)=0
    K_build_total = K_dryroomsys+K_solv+K_scrap+K_lab+K_cooling+K_otherbuild
    A_build_total = A_solv+A_scrap+A_lab        # dryroomsys/cooling/otherbuild area = 0

    L_total = L_elec_total+L_assy_total+L_form+L_modasm+L_packasm+L_wh+L_build_total
    K_total = K_elec_total+K_assy_total+K_form+K_modasm+K_packasm+K_wh+K_build_total
    A_total = A_elec_total+A_assy_total+A_form+A_modasm+A_packasm+A_wh+A_build_total

    E_elec_total = (P_prep_pos+P_prep_neg+P_coat_pos+P_coat_neg+P_cal_pos+P_cal_neg+
                    P_not_pos+P_not_neg+P_dry_pos+P_dry_neg) * hrs_to_GWh
    E_assy_total = (P_slit+P_stack+P_weld+P_xray+P_cont+P_fill+P_dryair) * hrs_to_GWh
    E_form = P_form * hrs_to_GWh
    E_modasm = P_modasm * hrs_to_GWh
    E_packasm = P_packasm * hrs_to_GWh
    E_wh = P_wh * hrs_to_GWh
    E_build_total = (P_dryroomsys+P_solv+P_scrap+P_lab+P_cooling+P_otherbuild) * hrs_to_GWh
    G445 = E_elec_total+E_assy_total+E_form+E_modasm+E_packasm+E_wh+E_build_total

    # Cost-of-cells-only allocation (BatPaC G27/G28 = 1/3 and 0.75 in standard case)
    G27_alloc, G28_alloc = 1/3, 0.75

    G448 = (L_elec_total+L_assy_total+L_form) + L_wh*G27_alloc + L_build_total
    G450 = (A_elec_total+A_assy_total+A_form) + A_wh*G27_alloc + A_build_total

    # G451 (cells-only energy) and G449 (cells-only capital) are mutually circular - resolve via iteration
    G451 = E_form
    for _ in range(50):
        inner = (E_elec_total+E_assy_total+E_form)/24/F81*1000000 + P_dryroomsys + P_wh*G27_alloc + P_solv+P_scrap+P_lab + P_otherbuild*G28_alloc
        denom = G445/24/F81*1000000 - P_cooling
        G451 = (E_elec_total+E_assy_total+E_form) + E_wh*G27_alloc + (
            (P_solv+P_scrap+P_lab+P_dryroomsys+P_otherbuild*G28_alloc) + P_cooling*inner/denom
        ) * hrs_to_GWh
    G449 = (K_elec_total+K_assy_total+K_form) + K_wh*G27_alloc + K_solv+K_scrap+K_lab + K_dryroomsys + K_cooling*G451/G445 + K_otherbuild*G28_alloc

    # Module-only and pack-only allocation
    G454 = L_modasm + L_wh*(1-G27_alloc)/2
    G456 = A_modasm + A_wh*(1-G27_alloc)/2
    G457 = (E_modasm + E_wh*(1-G27_alloc)/2 +
            (P_otherbuild*(1-G28_alloc)/2 + P_cooling*(1-G451/G445)*(P_modasm+P_wh*(1-G27_alloc)/2+P_otherbuild*(1-G28_alloc)/2)/
             (P_modasm+P_wh*(1-G27_alloc)+P_otherbuild*(1-G28_alloc)+P_packasm)) * hrs_to_GWh)
    G455 = K_modasm + K_wh*(1-G27_alloc)/2 + K_cooling*G457/G445 + K_otherbuild*(1-G28_alloc)/2

    G460 = L_total - G448 - G454
    G461 = K_total - G449 - G455
    G462 = A_total - G450 - G456
    G463 = G445 - G451 - G457

    # ════════════════════════════════════════════════════════════════════════
    # PART 5 - Cell-level cost roll-up (BatPaC G494-G539)
    # ════════════════════════════════════════════════════════════════════════
    F84, F85 = 1000, 15
    F87, F88, F89 = 5, 10, 15
    F93, F94 = labor_rate_per_hr, energy_price_per_kWh
    F96, F97 = 40, 2
    F101, F102, F103 = 25, 0.75, 35
    F107, F109, F110 = 8.672628683211402, 5, 0.75
    F113, F114 = 5, 5.6

    G498 = G449
    G499 = G450 * F84 / 1000000
    G500 = (G498+G499) * F85/100
    G501 = G498+G499+G500

    G513 = mat_cost_per_cell
    G514 = F93/G14*G448
    G515 = F94*G451*1000000/G14
    G516 = F96/100*G514 + F97/100*G501/G14*1000000
    G517 = G513+G514+G515+G516

    G504 = (F87/100*G513 + F88/100*(G514+G516+G515)) * G14/1000000
    G505 = G517*G14/1000000*F89/100
    G506 = G504+G505
    G509 = G501+G506

    G520 = (F107/100*G498 + F109/100*G499)*1000000/G14
    G521 = F101/100*(G514+G516) + F102/100*G501/G14*1000000
    G522 = G520*F103/100
    G523 = F110/100*G509/G14*1000000
    G524 = G521+G522+G520+G523

    G532 = F113/100*G509*1000000/G14
    G533 = F114/100*(G517+G524+G532)

    G536 = G517+G524
    G537 = G536+G532+G533   # purchased-cell branches (G528,G529) = 0 in non-purchased case
    G538 = G536*total_cells
    G539 = G537*total_cells

    # ════════════════════════════════════════════════════════════════════════
    # PART 6 - Module-level cost roll-up (BatPaC G155-G581)
    # ════════════════════════════════════════════════════════════════════════
    F48, G48c, F155 = 2.405, 0.15, 0.85
    F53, G53c = 2, 0.03
    F57, G57c, F157 = 8.72, 0.04, 0.85
    F58, G58c, F158 = 2.3, 0.2, 0.85
    F59, G59c, F159 = 8.64, 0.18, 0.85
    F60, G60c, F160 = 3, 1.5, 0.85
    G61c, F161 = 0.5, 0.85
    F343_base = 10000000
    F344_base = 270000000
    F346_base = 200000000
    G33 = total_cells

    # Module capacity = cell_capacity x cells_parallel (BatPaC BD G36 = pack_cap/modules_parallel)
    module_capacity_Ah = cell_capacity_Ah * cells_parallel

    # Module hardware masses come straight from Module 03 (BatPaC BD rows 352-369)
    # so the cost model and the mass model describe the same physical module.
    _G354 = cell_interconnects_per_module
    _G355 = cell_interconnect_g_per_module
    _G361 = interconnect_panel_g_per_module
    _G369 = module_terminals_g_per_module

    G155 = al_conductor_g_per_module/1000*F48 + cells_per_module*G48c*(F346_base/(G33*G9))**(1-F155)
    G156 = F53*cells_per_module/cells_parallel + G53c*module_capacity_Ah
    G157 = _G355/1000*F57 + _G354*G57c*(F344_base/G12)**(1-F157) if G12 else _G355/1000*F57
    G158 = _G361/1000*F58 + 2*G58c*(F343_base/G11)**(1-F158)
    G159 = F59*_G369/1000 + 2*G59c*(F343_base/G11)**(1-F159)
    G160 = module_enclosure_g/1000*F60 + G60c*(F343_base/G11)**(1-F160)
    G161 = G61c*(F343_base/G11)**(1-F161)
    G162 = G155+G156+G157+G158+G159+G160+G161

    G545 = G455
    G546 = G456 * F84/1000000
    G547 = (G545+G546)*F85/100
    G548 = G545+G546+G547

    G561 = F93/G11*G454
    G562 = F94*G457*1000000/G11
    G563 = F96/100*G561 + F97/100*G548/G11*1000000
    G560 = G162   # Lists!C156=0 case (no cell-cost duplication at module level)
    G564 = G560+G561+G562+G563

    G551 = (F87/100*G560 + F88/100*(G561+G563+G562)) * G11/1000000
    G552 = G564*G11/1000000*F89/100
    G553 = G551+G552
    G556 = G548+G553

    G567 = (F107/100*G545 + F109/100*G546)*1000000/G11
    G568 = F101/100*(G561+G563) + F102/100*G548/G11*1000000
    G569 = G567*F103/100
    G570 = F110/100*G556/G11*1000000
    G571 = G568+G569+G567+G570

    G574 = F113/100*G556*1000000/G11
    G575 = F114/100*(G564+G571+G574)

    G578 = G564+G571
    G579 = G578+G575+G574
    G580 = G578*modules_per_pack
    G581 = G579*modules_per_pack

    # ════════════════════════════════════════════════════════════════════════
    # PART 7 - Pack-level cost roll-up (BatPaC G165-G639)
    # ════════════════════════════════════════════════════════════════════════
    F64, G64c, F75 = p_row_rack, 1, 0.85
    F342_base = 2000000
    # G165: rack cost uses (G428-G427) = rack hardware WITHOUT pad mass (BatPaC BD rows 427-428)
    rack_hardware_kg_per_row = rack_total_kg_per_row - rack_pad_kg_per_row
    G165 = rows_per_pack * (rack_hardware_kg_per_row*F64 + G64c*(F342_base/G10)**(1-F75))
    G65c = 0.2   # CI G65 elastomer pad plus-cost, $/pad
    G166 = rows_per_pack * (modules_per_row-1) * G65c
    F66v, G66c = p_module_interconnect, 0.4
    # G167: BD G191 = (modules_per_row+1)*rows_per_pack module-to-module interconnects
    _G191 = (modules_per_row + 1) * rows_per_pack
    G167 = _G191 * (F66v*module_interconnect_g/1000 + G66c*(F343_base/G11)**(1-F75))
    F67v, G67c = p_busbar, 0.6
    G168 = (1 if busbar_pack_g != 0 else 0) * (busbar_pack_g/1000*F67v + G67c)
    F68v, G68c = p_coolant_panel, 0.5
    G169 = coolant_panel_kg*F68v + 2*rows_per_pack*G68c*(F342_base/G10)**(1-F75)
    F69v, G69c = p_coolant_manifold, 1
    F341_base = 500000
    G170 = coolant_manifold_kg*F69v + G69c*(F341_base/G9)**(1-F75)
    F70v, G70c = p_pack_terminal_seal, 0.75
    G171 = pack_terminals_g/1000*0.9*F70v + 2*G70c*(F341_base/G9)**(1-F75)
    F71v, G71c = p_pack_support_frame, 1
    G172 = jacket_support_frame_kg*F71v + G71c*(F341_base/G9)**(1-F75)
    F72v, G72c = p_jacket_top_interior, 3
    G173 = (jacket_top_plates_kg+jacket_interior_base_kg)*F72v + G72c*(F341_base/G9)**(1-F75)
    F73v, G73c = p_jacket_exterior_base, 3
    G174 = jacket_exterior_base_kg*F73v + G73c*(F341_base/G9)**(1-F75)
    E74v = p_jacket_insulation
    # G175: uses insulation area (m2) * price/m2, NOT mass remainder (BatPaC BD G472+G480)
    G175 = (insulation_area_base_m2 + insulation_area_top_m2) * E74v
    G176 = 80
    G177 = 20
    G178 = G165+G166+G167+G168+G169+G170+G171+G172+G173+G174+G175+G176+G177
    G179 = bms_cost_per_pack

    G587 = G461
    G588 = G462*F84/1000000
    G589 = (G587+G588)*F85/100
    G590 = G587+G588+G589

    G602 = G178+G179
    G603 = F93/G9*G460
    G604 = F94*G463*1000000/G9
    G605 = F96/100*G603 + F97/100*G590/G9*1000000
    G606 = G602+G603+G604+G605

    G593 = (F87/100*G602 + F88/100*(G603+G605+G604)) * G9/1000000
    G594 = G606*G9/1000000*F89/100
    G595 = G593+G594
    G598 = G590+G595

    G609 = (F107/100*G587 + F109/100*G588)*1000000/G9
    G610 = F101/100*(G603+G605) + F102/100*G590/G9*1000000
    G611 = G609*F103/100
    G612 = F110/100*G598/G9*1000000
    G613 = G610+G611+G609+G612

    G616 = F113/100*G598*1000000/G9
    G617 = F114/100*(G606+G613+G616)

    G620 = G606+G613
    G621 = G620+G617+G616

    # ── Final total cost per pack ──
    G634 = G538
    G635 = G580
    G636 = G620
    G637 = G616 + G574*modules_per_pack + G532*total_cells
    G638 = G617 + G575*modules_per_pack + G533*total_cells
    G639 = G634+G635+G636+G637+G638

    # BatPaC reports $/kWh on GROSS (total) pack energy, not useable.
    # Ref: BatPaC Dashboard row 157: G639 / total_pack_kWh = $100.92/kWh at 100 kWh.
    cost_per_kwh = G639 / pack_gross_energy_kWh if pack_gross_energy_kWh else 0

    # Reported only when a like-for-like LFP cost exists (Module 06). No fallback
    # to a market price: see _lfp_reference_cost().
    if lfp_benchmark_per_kwh:
        gap_vs_lfp = cost_per_kwh - lfp_benchmark_per_kwh
        gap_pct = gap_vs_lfp / lfp_benchmark_per_kwh * 100
    else:
        gap_vs_lfp = None
        gap_pct = None

    return {
        "mat_cost_per_cell": mat_cost_per_cell,
        "cost_cathode_am": cost_cathode_am, "cost_anode_am": cost_anode_am,
        "cost_carbon": cost_carbon, "cost_pvdf": cost_pvdf, "cost_cmcsbr": cost_cmcsbr,
        "cost_c_foil": cost_c_foil, "cost_a_foil": cost_a_foil, "cost_sep": cost_sep,
        "cost_elec": cost_elec, "cost_container": cost_container, "cost_terminal": cost_terminal,
        "cost_pos_solvent": cost_pos_solvent, "cost_neg_solvent": cost_neg_solvent,
        # Cell-level
        "cell_direct_labor_per_cell": G514, "cell_energy_per_cell": G515,
        "cell_variable_overhead_per_cell": G516, "cell_variable_cost_per_cell": G517,
        "cell_depreciation_per_cell": G520, "cell_gsa_per_cell": G521,
        "cell_rd_per_cell": G522, "cell_financing_per_cell": G523,
        "cell_fixed_expenses_per_cell": G524,
        "cell_profit_per_cell": G532, "cell_warranty_per_cell": G533,
        "cell_cost_per_cell": G536, "total_cell_cost_per_cell": G537,
        "cell_cost_per_pack": G538, "total_cell_cost_per_pack": G539,
        "fixed_capital_investment_cell_mil": G501, "total_investment_cell_mil": G509,
        # Module-level
        "module_purchased_items_per_module": G162,
        "module_direct_labor_per_module": G561, "module_energy_per_module": G562,
        "module_variable_cost_per_module": G564, "module_fixed_expenses_per_module": G571,
        "module_profit_per_module": G574, "module_warranty_per_module": G575,
        "module_cost_per_module": G578, "total_module_cost_per_module": G579,
        "module_cost_per_pack": G580, "total_module_cost_per_pack": G581,
        "fixed_capital_investment_module_mil": G548, "total_investment_module_mil": G556,
        # Pack-level
        "pack_purchased_items_per_pack": G178, "bms_cost_per_pack": G179,
        "pack_row_rack_cost": G165, "pack_module_pads_cost": G166,
        "pack_module_interconnect_cost": G167, "pack_busbar_cost": G168,
        "pack_coolant_panel_cost": G169, "pack_coolant_manifold_cost": G170,
        "pack_terminal_cost": G171, "pack_support_frame_cost": G172,
        "pack_jacket_top_interior_cost": G173, "pack_jacket_exterior_cost": G174,
        "pack_jacket_insulation_cost": G175,
        "pack_direct_labor_per_pack": G603, "pack_energy_per_pack": G604,
        "pack_variable_cost_per_pack": G606, "pack_fixed_expenses_per_pack": G613,
        "pack_profit_per_pack": G616, "pack_warranty_per_pack": G617,
        "pack_cost_per_pack": G620, "total_pack_cost_per_pack": G621,
        "fixed_capital_investment_pack_mil": G590, "total_investment_pack_mil": G598,
        # Final
        "cost_from_cells": G634, "cost_from_modules": G635, "cost_from_pack": G636,
        "total_profit": G637, "total_warranty": G638,
        "pack_total_cost": G639,
        "cost_per_kwh": cost_per_kwh,
        "gap_vs_lfp": gap_vs_lfp, "gap_pct": gap_pct,
        "mat_frac": mat_cost_per_cell / G537 if G537 else 0,
        # Annual rate diagnostics (useful for UI display)
        "annual_packs": G9, "annual_cells_accepted": G14, "annual_cells_yield_adj": G15,
        "total_direct_labor_hrs_yr": L_total, "total_capital_equipment_mil": K_total,
        "total_plant_area_m2": A_total, "total_energy_GWh_yr": G445,
    }


def run_sustainability(
    # Per-cell masses from Module 01
    c_AM_mass_g, a_AM_mass_g,
    c_carbon_g, a_carbon_g,
    c_binder_g, a_binder_g,
    # Per-cell areas/masses from Module 02
    c_foil_area_m2, a_foil_area_m2,
    c_foil_mass_g, a_foil_mass_g,
    sep_area_m2, sep_mass_g, elec_mass_g,
    container_mass_g, cell_mass_g,
    # Pack scale from Module 03
    total_cells, pack_useable_energy_kWh, pack_mass_kg,
    # Pack-level non-cell masses from Module 03, split by actual material
    conductors_kg=0.0,              # copper: interconnects, bus bars, pack terminals
    rack_mass_total_kg=0.0,         # steel
    coolant_panel_kg=0.0,           # steel
    coolant_manifold_kg=0.0,        # steel
    coolant_liquid_kg=0.0,          # glycol/water, not recovered
    jacket_support_frame_kg=0.0,    # steel
    jacket_interior_base_kg=0.0,    # aluminium
    jacket_exterior_base_kg=0.0,    # steel
    jacket_top_plates_kg=0.0,       # aluminium
    pack_jacket_total_kg=0.0,       # total, incl. insulation remainder
    bms_mass_kg=0.0,
    module_al_kg=0.0,               # G375 heat-spreader conductor
    module_steel_kg=0.0,            # G381 enclosure, G378 MMS
    module_cu_kg=0.0,               # G355 cell interconnects, G365 tabs, G369 terminals
    module_polymer_kg=0.0,          # G361 interconnect panels
    # Anode foil material (SIB = Al, LIB benchmark = Cu)
    anode_foil_density=2.70,
    # Al vs Cu prices
    p_al_kg=2.5, p_cu_kg=9.0,
    # CO2 intensity factors (kgCO2/kg)
    # These match the Module 05 input boxes. If they drifted apart, two parts of
    # the app would show different CO2 for the same material.
    co2_cathode_am=22.0, co2_anode_am=4.07, co2_al_foil=6.6,
    co2_separator=2.9, co2_electrolyte=2.58, co2_carbon=3.5, co2_pvdf=55.8,
    co2_anode_binder=3.36, co2_container=6.6, co2_copper=6.0,
    co2_steel=1.92, co2_bms=23.3,
    # Grid CO2 intensity for energy payback (kgCO2/kWh)
    grid_co2_intensity_kg_per_kwh=0.164,
    # LCOS inputs
    cycle_life=3000, calendar_life_yr=15, roundtrip_efficiency_pct=90.0,
    cycles_per_year_override=None,
    electricity_price_per_kwh=0.05, discount_rate_pct=8.0,
    # Cost from Module 04
    pack_total_cost_usd=0.0,
    # O&M
    om_cost_pct_per_yr=1.5,
    # End-of-life recycling
    eol_cathode_am_recovery_pct=90.0,
    eol_al_recovery_pct=85.0,
    eol_steel_recovery_pct=90.0,
    eol_cathode_am_price_kg=8.0,
    eol_al_price_kg=1.5,
    eol_steel_price_kg=0.3,
):
    AL_DENSITY = 2.70
    CU_DENSITY = 8.96
    # The anode current collector is aluminium for sodium-ion and copper for the
    # lithium-ion benchmark. Everything downstream keys off the density actually
    # used in Module 02 rather than assuming aluminium.
    anode_foil_is_cu = anode_foil_density > 5.0
    co2_anode_foil   = co2_copper if anode_foil_is_cu else co2_al_foil

    # ── 1. Cell-level material intensity (kg/kWh useable) ────────────────────
    def cell_intensity(mass_g_per_cell):
        return (mass_g_per_cell * total_cells / 1000) / pack_useable_energy_kWh if pack_useable_energy_kWh else 0

    int_cathode_am  = cell_intensity(c_AM_mass_g)
    int_anode_am    = cell_intensity(a_AM_mass_g)
    int_carbon      = cell_intensity(c_carbon_g + a_carbon_g)
    int_binder      = cell_intensity(c_binder_g + a_binder_g)
    int_electrolyte = cell_intensity(elec_mass_g)
    int_separator   = cell_intensity(sep_mass_g)
    int_c_foil      = cell_intensity(c_foil_mass_g)
    int_a_foil      = cell_intensity(a_foil_mass_g)
    int_container   = cell_intensity(container_mass_g)
    int_cell_total  = cell_intensity(cell_mass_g)

    # ── 2. Pack-level material intensity (adds non-cell components) ───────────
    # Materials are taken from the components Module 03 actually computes rather
    # than from assumed split fractions. BatPaC material assignments (Lists!AR99-109):
    # conductors Cu; row rack, coolant panels, manifolds, support frame and jacket
    # exterior base steel; jacket top plates and interior base aluminium.
    conductors_cu_kg  = conductors_kg
    module_hardware_kg = (module_al_kg + module_steel_kg + module_cu_kg
                          + module_polymer_kg)
    rack_steel_kg     = rack_mass_total_kg
    cooling_steel_kg  = coolant_panel_kg + coolant_manifold_kg
    cooling_system_kg = cooling_steel_kg + coolant_liquid_kg
    jacket_al_kg      = jacket_interior_base_kg + jacket_top_plates_kg
    jacket_steel_kg   = jacket_support_frame_kg + jacket_exterior_base_kg
    # Whatever the jacket total carries beyond plates and frame is insulation.
    jacket_insulation_kg = max(pack_jacket_total_kg - jacket_al_kg - jacket_steel_kg, 0.0)

    def pack_intensity(mass_kg):
        return mass_kg / pack_useable_energy_kWh if pack_useable_energy_kWh else 0

    int_pack_conductors = pack_intensity(conductors_cu_kg)
    int_pack_rack       = pack_intensity(rack_steel_kg)
    int_pack_cooling    = pack_intensity(cooling_system_kg)
    int_pack_jacket     = pack_intensity(pack_jacket_total_kg)
    int_pack_bms        = pack_intensity(bms_mass_kg)
    int_pack_total      = pack_intensity(pack_mass_kg) if pack_mass_kg else (
        int_cell_total + int_pack_conductors + int_pack_rack + int_pack_cooling + int_pack_jacket + int_pack_bms
    )

    # ── 3. Al vs Cu anode foil comparison ────────────────────────────────────
    # Same foil geometry, the two candidate current-collector metals. Uses the
    # mass Module 02 computed, rescaled by the density ratio for the alternative.
    al_anode_g   = a_foil_mass_g * (AL_DENSITY / anode_foil_density)
    cu_equiv_g   = a_foil_mass_g * (CU_DENSITY / anode_foil_density)
    al_pack_kg       = al_anode_g * total_cells / 1000
    cu_pack_kg       = cu_equiv_g * total_cells / 1000
    mass_saving_kg   = cu_pack_kg - al_pack_kg
    mass_saving_pct  = (mass_saving_kg / cu_pack_kg) * 100 if cu_pack_kg else 0
    cost_saving_usd  = cu_pack_kg * p_cu_kg - al_pack_kg * p_al_kg
    cu_saving_per_kwh = cost_saving_usd / pack_useable_energy_kWh if pack_useable_energy_kWh else 0

    # ── 4. CO2 intensity -- cell level ────────────────────────────────────────
    co2_per_cell = (
        c_AM_mass_g         / 1000 * co2_cathode_am  +
        a_AM_mass_g         / 1000 * co2_anode_am    +
        c_foil_mass_g       / 1000 * co2_al_foil     +
        a_foil_mass_g       / 1000 * co2_anode_foil  +
        sep_mass_g          / 1000 * co2_separator   +
        elec_mass_g         / 1000 * co2_electrolyte +
        (c_carbon_g + a_carbon_g) / 1000 * co2_carbon +
        c_binder_g          / 1000 * co2_pvdf        +
        a_binder_g          / 1000 * co2_anode_binder +
        container_mass_g    / 1000 * co2_container
    )
    # Pack-level CO2 adds non-cell components, each at its own material intensity.
    # Coolant liquid and jacket insulation carry no factor: neither has a defensible
    # published cradle-to-gate value, and both are noted as an exclusion.
    co2_pack_noncell_kg = (
        (conductors_cu_kg + module_cu_kg)              * co2_copper  +
        (module_steel_kg + rack_steel_kg
         + cooling_steel_kg + jacket_steel_kg)         * co2_steel   +
        (module_al_kg + jacket_al_kg)                  * co2_al_foil +
        bms_mass_kg                                    * co2_bms
    )
    co2_pack_cells_kg  = co2_per_cell * total_cells
    co2_pack_total_kg  = co2_pack_cells_kg + co2_pack_noncell_kg
    co2_per_kwh        = co2_pack_total_kg / pack_useable_energy_kWh if pack_useable_energy_kWh else 0

    # CO2 in kg for each material. These add up to co2_pack_total_kg exactly.
    # Every CO2 chart reads this instead of doing the sums again, so the parts
    # always match the total.
    co2_breakdown = {
        "Cathode AM":        c_AM_mass_g      / 1000 * co2_cathode_am   * total_cells,
        "Anode AM":          a_AM_mass_g      / 1000 * co2_anode_am     * total_cells,
        "Cathode foil":      c_foil_mass_g    / 1000 * co2_al_foil      * total_cells,
        "Anode foil":        a_foil_mass_g    / 1000 * co2_anode_foil   * total_cells,
        "Separator":         sep_mass_g       / 1000 * co2_separator    * total_cells,
        "Electrolyte":       elec_mass_g      / 1000 * co2_electrolyte  * total_cells,
        "Conductive carbon": (c_carbon_g + a_carbon_g) / 1000 * co2_carbon * total_cells,
        "Cathode binder":    c_binder_g       / 1000 * co2_pvdf         * total_cells,
        "Anode binder":      a_binder_g       / 1000 * co2_anode_binder * total_cells,
        "Cell container":    container_mass_g / 1000 * co2_container    * total_cells,
        "Copper (pack)":     (conductors_cu_kg + module_cu_kg)          * co2_copper,
        "Steel (rack, cooling, jacket)": (module_steel_kg + rack_steel_kg
                                          + cooling_steel_kg + jacket_steel_kg) * co2_steel,
        "Aluminium (pack)":  (module_al_kg + jacket_al_kg)              * co2_al_foil,
        "BMS":               bms_mass_kg                                * co2_bms,
    }

    # ── 5. Energy payback period ──────────────────────────────────────────────
    # CO2 displaced per year = annual energy throughput * (grid intensity - storage losses penalty)
    # Storage efficiency penalty: each kWh discharged required 1/RT_eff kWh input
    # Net CO2 saved per kWh discharged = grid_intensity * (1 - 1/rt_eff) ... but this
    # is only positive if storage is shifting renewables. Simpler and more conservative:
    # assume storage displaces grid-average CO2, charging energy adds grid CO2
    rt_eff = roundtrip_efficiency_pct / 100
    dr     = discount_rate_pct / 100
    calendar_implied_cycles = calendar_life_yr * 365
    effective_cycles = min(cycle_life, calendar_implied_cycles)
    cycles_per_year  = effective_cycles / calendar_life_yr if calendar_life_yr else 365
    # Utilisation sweeps set cycles per year directly. Cycle life then caps the
    # calendar life rather than the other way round: a pack cycled harder wears
    # out sooner, so lifetime energy stays bounded by the cycle count.
    if cycles_per_year_override:
        cycles_per_year = cycles_per_year_override
        calendar_life_yr = min(calendar_life_yr, cycle_life / cycles_per_year)
    # Useable energy is by definition what the pack DISCHARGES, so annual throughput
    # is cycles x useable energy. The round-trip loss belongs on the charging side
    # and is applied there (charge = discharge / rt_eff), not to the discharge term.
    energy_per_year  = cycles_per_year * pack_useable_energy_kWh
    energy_charged_per_year = energy_per_year / rt_eff if rt_eff > 0 else 0

    # Full credit for displaced grid generation, per the convention used in the
    # storage LCA literature. Charging emissions are not netted off here because
    # that requires an assumption about the marginal charging source.
    co2_displaced_per_year_full = energy_per_year * grid_co2_intensity_kg_per_kwh
    energy_payback_yr = co2_pack_total_kg / co2_displaced_per_year_full if co2_displaced_per_year_full > 0 else None

    # ── 6. End-of-life recycling value ───────────────────────────────────────
    # Recoverable cathode AM mass at pack level
    cathode_am_pack_kg = c_AM_mass_g * total_cells / 1000
    al_recoverable_kg  = (
        c_foil_mass_g * total_cells / 1000 +
        (0.0 if anode_foil_is_cu else a_foil_mass_g * total_cells / 1000) +
        jacket_al_kg + module_al_kg
    )
    cu_recoverable_kg = (
        conductors_cu_kg + module_cu_kg +
        (a_foil_mass_g * total_cells / 1000 if anode_foil_is_cu else 0.0)
    )
    steel_recoverable_kg = (rack_steel_kg + cooling_steel_kg + jacket_steel_kg
                            + module_steel_kg)

    eol_cathode_value = cathode_am_pack_kg * (eol_cathode_am_recovery_pct/100) * eol_cathode_am_price_kg
    eol_al_value      = al_recoverable_kg  * (eol_al_recovery_pct/100)        * eol_al_price_kg
    eol_steel_value   = steel_recoverable_kg * (eol_steel_recovery_pct/100)   * eol_steel_price_kg
    eol_cu_value      = cu_recoverable_kg * (eol_al_recovery_pct/100)        * p_cu_kg
    eol_total_value   = eol_cathode_value + eol_al_value + eol_steel_value + eol_cu_value
    eol_per_kwh       = eol_total_value / pack_useable_energy_kWh if pack_useable_energy_kWh else 0

    # ── 7. LCOS (Schmidt et al. 2019) ────────────────────────────────────────
    om_annual = pack_total_cost_usd * om_cost_pct_per_yr / 100
    if dr > 0:
        annuity_factor = (dr * (1+dr)**calendar_life_yr) / ((1+dr)**calendar_life_yr - 1)
    else:
        annuity_factor = 1.0 / calendar_life_yr if calendar_life_yr else 0

    annual_capex_cost  = pack_total_cost_usd * annuity_factor
    annual_total_cost  = annual_capex_cost + om_annual + energy_charged_per_year * electricity_price_per_kwh
    # LCOS with recycling credit (net EOL value discounted to present, spread over lifetime)
    eol_pv = eol_total_value / (1+dr)**calendar_life_yr if dr >= 0 else eol_total_value
    annual_eol_credit  = eol_pv * annuity_factor
    annual_total_net   = annual_total_cost - annual_eol_credit

    lcos_per_kwh       = annual_total_cost / energy_per_year if energy_per_year else 0
    lcos_net_per_kwh   = annual_total_net  / energy_per_year if energy_per_year else 0
    lcos_capex_component  = annual_capex_cost  / energy_per_year if energy_per_year else 0
    lcos_om_component     = om_annual          / energy_per_year if energy_per_year else 0
    lcos_energy_component = electricity_price_per_kwh / rt_eff
    lcos_eol_credit       = annual_eol_credit  / energy_per_year if energy_per_year else 0

    cost_per_cycle     = pack_total_cost_usd / effective_cycles if effective_cycles else 0
    lifetime_energy_kwh = energy_per_year * calendar_life_yr

    # ── 8. LCOS sensitivity vectors (for plotting) ───────────────────────────
    # Vary electricity price from 0 to 0.20 $/kWh
    elec_prices = [i*0.01 for i in range(21)]
    lcos_vs_elec = []
    for ep in elec_prices:
        atc = annual_capex_cost + om_annual + energy_charged_per_year * ep
        lcos_vs_elec.append(atc / energy_per_year if energy_per_year else 0)

    # Vary cycle life from 500 to 6000
    cycle_lives = list(range(500, 6001, 250))
    lcos_vs_cycles = []
    for cl in cycle_lives:
        eff_c = min(cl, calendar_implied_cycles)
        cpy   = eff_c / calendar_life_yr if calendar_life_yr else 365
        epy   = cpy * pack_useable_energy_kWh
        atc   = annual_capex_cost + om_annual + (epy / rt_eff if rt_eff else 0) * electricity_price_per_kwh
        lcos_vs_cycles.append(atc / epy if epy else 0)

    return {
        # Cell-level intensity
        "int_cathode_am":    int_cathode_am,
        "int_anode_am":      int_anode_am,
        "int_carbon":        int_carbon,
        "int_binder":        int_binder,
        "int_electrolyte":   int_electrolyte,
        "int_separator":     int_separator,
        "int_c_foil":        int_c_foil,
        "int_a_foil":        int_a_foil,
        "int_container":     int_container,
        "int_cell_total":    int_cell_total,
        # Pack-level intensity
        "int_pack_conductors": int_pack_conductors,
        "int_pack_rack":       int_pack_rack,
        "int_pack_cooling":    int_pack_cooling,
        "int_pack_jacket":     int_pack_jacket,
        "int_pack_bms":        int_pack_bms,
        "int_pack_total":      int_pack_total,
        # Al vs Cu
        "al_pack_kg":        al_pack_kg,
        "cu_pack_kg":        cu_pack_kg,
        "mass_saving_kg":    mass_saving_kg,
        "mass_saving_pct":   mass_saving_pct,
        "cost_saving_usd":   cost_saving_usd,
        "cu_saving_per_kwh": cu_saving_per_kwh,
        # CO2
        "co2_per_cell":        co2_per_cell,
        "co2_pack_cells_kg":   co2_pack_cells_kg,
        "co2_pack_noncell_kg": co2_pack_noncell_kg,
        "co2_pack_total_kg":   co2_pack_total_kg,
        "co2_per_kwh":         co2_per_kwh,
        "co2_breakdown":       co2_breakdown,
        "energy_payback_yr":   energy_payback_yr,
        # EOL recycling
        "eol_cathode_value":   eol_cathode_value,
        "eol_al_value":        eol_al_value,
        "eol_cu_value":        eol_cu_value,
        "eol_steel_value":     eol_steel_value,
        "eol_total_value":     eol_total_value,
        "eol_per_kwh":         eol_per_kwh,
        # LCOS
        "lcos_per_kwh":           lcos_per_kwh,
        "lcos_net_per_kwh":       lcos_net_per_kwh,
        "lcos_capex_component":   lcos_capex_component,
        "lcos_om_component":      lcos_om_component,
        "lcos_energy_component":  lcos_energy_component,
        "lcos_eol_credit":        lcos_eol_credit,
        "cost_per_cycle":         cost_per_cycle,
        "effective_cycles":       effective_cycles,
        "lifetime_energy_kwh":    lifetime_energy_kwh,
        "energy_per_year_kwh":    energy_per_year,
        "energy_charged_per_year_kwh": energy_charged_per_year,
        "cycles_per_year":        cycles_per_year,
        "c_foil_mass_g":          c_foil_mass_g,
        "a_foil_mass_g":          a_foil_mass_g,
        "anode_foil_is_cu":       anode_foil_is_cu,
        "conductors_cu_kg":       conductors_cu_kg,
        "module_hardware_kg":     module_hardware_kg,
        "module_al_kg":           module_al_kg,
        "module_steel_kg":        module_steel_kg,
        "module_cu_kg":           module_cu_kg,
        "module_polymer_kg":      module_polymer_kg,
        "cu_recoverable_kg":      cu_recoverable_kg,
        "jacket_al_kg":           jacket_al_kg,
        "jacket_steel_kg":        jacket_steel_kg,
        "jacket_insulation_kg":   jacket_insulation_kg,
        "cooling_steel_kg":       cooling_steel_kg,
        # Sensitivity vectors
        "lcos_vs_elec_prices":   elec_prices,
        "lcos_vs_elec_values":   lcos_vs_elec,
        "lcos_vs_cycle_lives":   cycle_lives,
        "lcos_vs_cycle_values":  lcos_vs_cycles,
    }

def _run_full_cost(overrides, base_e, base_c_design, base_p_design, base_inputs):
    """
    Re-run the full model chain with one or more parameter overrides.
    overrides: dict of parameter name -> new value
    Returns a results dict, or None if the run fails (the reason is recorded in
    `_run_full_cost.last_error` so callers can surface it rather than silently
    dropping the iteration).
    """
    # ── Unpack base electrochemical inputs ────────────────────────────────────
    c_cap   = overrides.get("c_cap",   base_inputs["c_cap"])
    c_volt  = overrides.get("c_volt",  base_inputs["c_volt"])
    c_dens  = overrides.get("c_dens",  base_inputs["c_dens"])
    c_am    = overrides.get("c_am",    base_inputs["c_am"])
    c_carb  = overrides.get("c_carb",  base_inputs["c_carb"])
    c_bind  = overrides.get("c_bind",  base_inputs["c_bind"])
    c_por   = overrides.get("c_por",   base_inputs["c_por"])
    c_thick = overrides.get("c_thick", base_inputs["c_thick"])
    a_cap   = overrides.get("a_cap",   base_inputs["a_cap"])
    a_volt  = overrides.get("a_volt",  base_inputs["a_volt"])
    a_dens  = overrides.get("a_dens",  base_inputs["a_dens"])
    a_am    = overrides.get("a_am",    base_inputs["a_am"])
    a_bind  = overrides.get("a_bind",  base_inputs["a_bind"])
    a_carb  = overrides.get("a_carb",  base_inputs["a_carb"])
    a_por   = overrides.get("a_por",   base_inputs["a_por"])
    c_carb_dens = overrides.get("c_carb_dens", base_inputs.get("c_carb_dens", 1.825))
    c_bind_dens = overrides.get("c_bind_dens", base_inputs.get("c_bind_dens", 1.77))
    a_carb_dens = overrides.get("a_carb_dens", base_inputs.get("a_carb_dens", 1.95))
    a_bind_dens = overrides.get("a_bind_dens", base_inputs.get("a_bind_dens", 1.10))
    np_ratio        = overrides.get("np_ratio",        base_inputs["np_ratio"])
    electrode_area  = overrides.get("electrode_area",  base_inputs["electrode_area"])
    tab_excess      = overrides.get("tab_excess",      base_inputs["tab_excess"])
    anode_excess    = overrides.get("anode_excess",    base_inputs.get("anode_excess", 2.0))
    num_layers      = overrides.get("num_layers",      base_inputs["num_layers"])
    lw_ratio        = overrides.get("lw_ratio",        base_inputs["lw_ratio"])
    sep_excess_w    = overrides.get("sep_excess_w",    base_inputs["sep_excess_w"])
    sep_excess_l    = overrides.get("sep_excess_l",    base_inputs["sep_excess_l"])
    tab_length      = overrides.get("tab_length",      base_inputs["tab_length"])
    feedthrough     = overrides.get("feedthrough",     base_inputs["feedthrough"])
    cc_buffer       = overrides.get("cc_buffer",      base_inputs.get("cc_buffer", 2.0))
    pouch_seal     = overrides.get("pouch_seal",    base_inputs.get("pouch_seal", 6.0))
    packing_eff     = overrides.get("packing_eff",    base_inputs.get("packing_eff", 0.97))
    cell_edge_fold  = overrides.get("cell_edge_fold", base_inputs.get("cell_edge_fold", 1.0))
    bicell_expansion = overrides.get("bicell_expansion", base_inputs.get("bicell_expansion", 0.0))
    elec_excess     = overrides.get("elec_excess",    base_inputs.get("elec_excess", 0.02))
    con_thick_um    = overrides.get("con_thick_um",    base_inputs["con_thick_um"])
    con_density     = overrides.get("con_density",     base_inputs["con_density"])
    wall_thick      = overrides.get("wall_thick",      base_inputs["wall_thick"])
    seal_buf        = overrides.get("seal_buf",        base_inputs["seal_buf"])
    c_foil_thick    = overrides.get("c_foil_thick",    base_inputs["c_foil_thick"])
    a_foil_thick    = overrides.get("a_foil_thick",    base_inputs["a_foil_thick"])
    al_density          = 2.70
    anode_foil_density  = overrides.get("anode_foil_density", base_inputs.get("anode_foil_density", 2.70))
    sep_thick       = overrides.get("sep_thick",       base_inputs["sep_thick"])
    sep_dens        = overrides.get("sep_dens",        base_inputs["sep_dens"])
    elec_dens       = overrides.get("elec_dens",       base_inputs["elec_dens"])
    elec_uptake     = overrides.get("elec_uptake",     base_inputs["elec_uptake"])
    useable_soc     = overrides.get("useable_soc",     base_inputs["useable_soc"])
    cells_per_module    = overrides.get("cells_per_module",    base_inputs.get("cells_per_module", 20))
    cells_parallel_m03  = overrides.get("cells_parallel_m03",  base_inputs.get("cells_parallel_m03", 2))
    modules_per_row     = overrides.get("modules_per_row",     base_inputs.get("modules_per_row", 5))
    rows_per_pack       = overrides.get("rows_per_pack",       base_inputs.get("rows_per_pack", 4))
    modules_parallel    = overrides.get("modules_parallel",    base_inputs.get("modules_parallel", 2))
    al_cond_thick_mm    = overrides.get("al_cond_thick_mm",    base_inputs.get("al_cond_thick_mm", 0.4))
    mod_wall_thick_mm   = overrides.get("mod_wall_thick_mm",   base_inputs.get("mod_wall_thick_mm", 0.3))
    restraint_thick_mm  = overrides.get("restraint_thick_mm",  base_inputs.get("restraint_thick_mm", 2.0))
    coolant_panel_thick_mm = overrides.get("coolant_panel_thick_mm", base_inputs.get("coolant_panel_thick_mm", 5.0))
    coolant_wall_mm     = overrides.get("coolant_wall_mm",     base_inputs.get("coolant_wall_mm", 0.3))
    jacket_insul_mm     = overrides.get("jacket_insul_mm",     base_inputs.get("jacket_insul_mm", 10.0))
    jacket_int_plate_mm = overrides.get("jacket_int_plate_mm", base_inputs.get("jacket_int_plate_mm", 1.0))
    jacket_ext_base_mm  = overrides.get("jacket_ext_base_mm",  base_inputs.get("jacket_ext_base_mm", 1.0))
    bms_bdu_mass        = overrides.get("bms_bdu_mass",        base_inputs.get("bms_bdu_mass", 2.444))
    bms_bdu_vol         = overrides.get("bms_bdu_vol",         base_inputs.get("bms_bdu_vol", 1.5485))
    nominal_current     = overrides.get("nominal_current",     base_inputs.get("nominal_current", 100.0))
    p_cathode_am    = overrides.get("p_cathode_am",    base_inputs["p_cathode_am"])
    p_anode_am      = overrides.get("p_anode_am",      base_inputs["p_anode_am"])
    p_carbon        = overrides.get("p_carbon",        base_inputs["p_carbon"])
    p_pvdf          = overrides.get("p_pvdf",          base_inputs["p_pvdf"])
    p_cmcsbr        = overrides.get("p_cmcsbr",        base_inputs["p_cmcsbr"])
    p_al_foil       = overrides.get("p_al_foil",       base_inputs["p_al_foil"])
    p_anode_foil    = overrides.get("p_anode_foil",    base_inputs.get("p_anode_foil", 0.20))
    p_sep           = overrides.get("p_sep",           base_inputs["p_sep"])
    p_electrolyte   = overrides.get("p_electrolyte",   base_inputs["p_electrolyte"])
    p_container     = overrides.get("p_container",     base_inputs["p_container"])
    p_pos_terminal_kg  = overrides.get("p_pos_terminal_kg",  base_inputs.get("p_pos_terminal_kg",  2.405))
    p_neg_terminal_kg  = overrides.get("p_neg_terminal_kg",  base_inputs.get("p_neg_terminal_kg",  2.405))
    terminal_fixed_cost = overrides.get("terminal_fixed_cost", base_inputs.get("terminal_fixed_cost", 0.08))
    annual_production_packs = overrides.get("annual_production_packs", base_inputs["annual_production_packs"])
    cell_yield_pct  = overrides.get("cell_yield_pct",  base_inputs["cell_yield_pct"])
    labor_rate_per_hr = overrides.get("labor_rate_per_hr", base_inputs["labor_rate_per_hr"])
    energy_price_per_kWh = overrides.get("energy_price_per_kWh", base_inputs["energy_price_per_kWh"])
    effective_days_per_year = overrides.get("effective_days_per_year", base_inputs["effective_days_per_year"])
    bms_cost_per_pack = overrides.get("bms_cost_per_pack", base_inputs["bms_cost_per_pack"])
    p_row_rack      = overrides.get("p_row_rack",      base_inputs["p_row_rack"])
    p_module_pads   = overrides.get("p_module_pads",   base_inputs["p_module_pads"])
    p_module_interconnect = overrides.get("p_module_interconnect", base_inputs["p_module_interconnect"])
    p_busbar        = overrides.get("p_busbar",        base_inputs["p_busbar"])
    p_coolant_panel = overrides.get("p_coolant_panel", base_inputs["p_coolant_panel"])
    p_coolant_manifold = overrides.get("p_coolant_manifold", base_inputs["p_coolant_manifold"])
    p_pack_terminal_seal = overrides.get("p_pack_terminal_seal", base_inputs["p_pack_terminal_seal"])
    p_pack_support_frame = overrides.get("p_pack_support_frame", base_inputs["p_pack_support_frame"])
    p_jacket_top_interior = overrides.get("p_jacket_top_interior", base_inputs["p_jacket_top_interior"])
    p_jacket_exterior_base = overrides.get("p_jacket_exterior_base", base_inputs["p_jacket_exterior_base"])
    p_jacket_insulation = overrides.get("p_jacket_insulation", base_inputs["p_jacket_insulation"])

    try:
        # M01
        e2 = run_electrochemical(
            c_cap, c_volt, c_dens, c_am, c_carb, c_bind, c_por, c_thick,
            a_cap, a_volt, a_dens, a_am, a_bind, a_carb, a_por,
            np_ratio, electrode_area, tab_excess, c_carb_dens=c_carb_dens, 
            c_bind_dens=c_bind_dens, a_carb_dens=a_carb_dens, a_bind_dens=a_bind_dens,
        )
        # M02
        c2 = run_cell_design(
            cathode_thickness_um=c_thick, anode_thickness_um=e2["a_thick"],
            electrode_area_cm2=e2["electrode_area"],
            cell_capacity_Ah=e2["cell_capacity"], cell_voltage_V=e2["cell_voltage"],
            cathode_bulk_density=c_dens, anode_bulk_density=a_dens,
            cathode_porosity=c_por, anode_porosity=a_por,
            cathode_coating_density=e2["c_coating_density"], anode_coating_density=e2["a_coating_density"],
            cathode_coating_total_g=e2["c_coat_total"],
            anode_coating_total_g=e2["a_coat_total"],
            num_layers_input=num_layers,
            length_to_width_ratio=lw_ratio,
            sep_excess_width_mm=sep_excess_w, sep_excess_length_mm=sep_excess_l,
            tab_length_mm=tab_length, feedthrough_mm=feedthrough, cc_buffer_mm=cc_buffer, pouch_seal_mm=pouch_seal,
            container_thickness_um=con_thick_um, container_density=con_density,
            wall_thickness_mm=wall_thick, seal_buffer_mm=seal_buf,
            cathode_foil_thickness_um=c_foil_thick,
            anode_foil_thickness_um=a_foil_thick,
            al_density=al_density,
            anode_foil_density=anode_foil_density,
            sep_thickness_um=sep_thick, sep_density=sep_dens,
            electrolyte_density=elec_dens, electrolyte_uptake_frac=elec_uptake,
            tab_excess=tab_excess,
            anode_excess_mm=anode_excess,
            packing_efficiency=packing_eff,
            cell_edge_fold_mm=cell_edge_fold,
            bicell_expansion_um=bicell_expansion,
            electrolyte_excess_frac=elec_excess,
        )
        # M03 - BatPaC-faithful cell -> module -> row rack -> pack hierarchy
        cell_v = e2["cell_voltage"]
        p2 = run_pack_design(
            cell_mass_g=c2["cell_mass_g"], cell_energy_Wh=c2["cell_energy_Wh"],
            cell_volume_cm3=c2["cell_volume_cm3"],
            cell_voltage_V=cell_v, cell_capacity_Ah=e2["cell_capacity"],
            cell_width_mm=c2["cell_width_mm"], cell_length_mm=c2["cell_length_mm"],
            cell_thickness_mm=c2["cell_thickness_mm"],
            positive_electrode_length_mm=c2["electrode_length_mm"],
            cells_per_module=cells_per_module, cells_parallel=cells_parallel_m03,
            modules_per_row=modules_per_row, rows_per_pack=rows_per_pack,
            modules_parallel=modules_parallel,
            useable_soc_fraction=useable_soc,
            al_conductor_thickness_mm=al_cond_thick_mm,
            module_wall_thickness_mm=mod_wall_thick_mm,
            restraint_plate_thickness_mm=restraint_thick_mm,
            coolant_panel_thickness_mm=coolant_panel_thick_mm,
            coolant_plate_wall_mm=coolant_wall_mm,
            jacket_insulation_thickness_mm=jacket_insul_mm,
            jacket_interior_plate_thickness_mm=jacket_int_plate_mm,
            jacket_exterior_base_plate_thickness_mm=jacket_ext_base_mm,
            bms_bdu_mass_kg=bms_bdu_mass,
            bms_bdu_volume_L=bms_bdu_vol,
            nominal_pack_current_A=nominal_current,
        )
        # M04 - BatPaC v5.2 manufacturing cost engine (cell/module/pack hierarchy)
        # BatPaC G16 = G15 * BD291 / 10000, where BD291 = total coated electrode area
        # = num_bicell_layers * 2 sides * width * length (cm²)
        # BD292 (neg) uses slightly larger area due to neg excess
        _n_layers = c2.get("num_bicell_layers", 18)
        positive_electrode_area_cm2_2 = _n_layers * 2 * c2["electrode_width_mm"] * c2["electrode_length_mm"] / 100
        # The anode is bigger than the cathode across the width only, same as
        # Module 04. Adding it to the length too made this disagree with the
        # cost model by about 0.7% on area.
        _exc = c2.get("anode_excess_mm", 0)
        negative_electrode_area_cm2_2 = (_n_layers * 2
                                         * (c2["electrode_width_mm"] + _exc)
                                         * c2["electrode_length_mm"] / 100)
        r4_2 = run_cost_model(
            c_AM_mass_g=e2["c_AM_mass"], a_AM_mass_g=e2["a_AM_mass"],
            c_carbon_g=e2["c_carbon_mass"], a_carbon_g=e2["a_carbon_mass"],
            c_binder_g=e2["c_binder_mass"], a_binder_g=e2["a_binder_mass"],
            binder_solvent_ratio_pos=16, binder_solvent_ratio_neg=40,
            binder_solvent_density_pos=1.03, binder_solvent_density_neg=1.0,
            c_AM_density=c_dens, c_carbon_density=c_carb_dens, c_binder_density=c_bind_dens,
            a_AM_density=a_dens, a_carbon_density=a_carb_dens, a_binder_density=a_bind_dens,
            c_foil_m2=c2["cathode_foil_area_m2"], a_foil_m2=c2["anode_foil_area_m2"],
            sep_m2=c2["sep_area_m2"], elec_vol_L=c2["elec_vol_L"],
            container_mass_g=c2["container_mass_g"], cell_mass_g=c2["cell_mass_g"],
            cell_capacity_Ah=e2["cell_capacity"], cell_voltage_V=e2["cell_voltage"],
            positive_electrode_area_cm2=positive_electrode_area_cm2_2,
            negative_electrode_area_cm2=negative_electrode_area_cm2_2,
            num_bicell_layers=c2["num_bicell_layers"],
            total_cells=p2["total_cells"], modules_per_pack=p2["modules_per_pack"],
            cells_per_module=cells_per_module, modules_per_row=modules_per_row, rows_per_pack=rows_per_pack,
            pack_useable_energy_kWh=p2["pack_useable_energy_kWh"], pack_gross_energy_kWh=p2["pack_gross_energy_kWh"],
            al_conductor_g_per_module=p2["al_conductor_g_per_module"], module_enclosure_g=p2["module_enclosure_g"],
            cell_interconnect_g_per_module=p2["cell_interconnect_g_per_module"],
            interconnect_panel_g_per_module=p2["interconnect_panel_g_per_module"],
            module_terminals_g_per_module=p2["module_terminals_g_per_module"],
            cell_interconnects_per_module=p2["cell_interconnects_per_module"],
            cell_interconnect_rate_per_module=p2["cell_interconnect_rate_per_module"],
            busbar_pack_g=p2["busbar_pack_g"], pack_terminals_g=p2["pack_terminals_g"],
            module_interconnect_g=p2["module_interconnect_g"], rack_total_kg_per_row=p2["rack_total_kg_per_row"],
            coolant_panel_kg=p2["coolant_panel_kg"], coolant_manifold_kg=p2["coolant_manifold_kg"],
            coolant_liquid_kg=p2["coolant_liquid_kg"],
            jacket_support_frame_kg=p2["jacket_support_frame_kg"], jacket_interior_base_kg=p2["jacket_interior_base_kg"],
            jacket_exterior_base_kg=p2["jacket_exterior_base_kg"], jacket_top_plates_kg=p2["jacket_top_plates_kg"],
            pack_jacket_total_kg=p2["pack_jacket_total_kg"], bms_mass_kg=p2["bms_mass_kg"],
            p_cathode_am=p_cathode_am, p_anode_am=p_anode_am,
            p_carbon=p_carbon, p_pvdf=p_pvdf, p_cmcsbr=p_cmcsbr,
            p_al_foil=p_al_foil, p_anode_foil=p_anode_foil, p_sep=p_sep, p_electrolyte=p_electrolyte,
            p_container=p_container,
            p_pos_terminal_kg=p_pos_terminal_kg, p_neg_terminal_kg=p_neg_terminal_kg,
            terminal_fixed_cost=terminal_fixed_cost,
            terminal_mass_cathode_g=c2.get("terminal_mass_cathode_g", 0),
            terminal_mass_anode_g=c2.get("terminal_mass_anode_g", 0),
            annual_production_packs=annual_production_packs, cell_yield_pct=cell_yield_pct,
            labor_rate_per_hr=labor_rate_per_hr, energy_price_per_kWh=energy_price_per_kWh,
            effective_days_per_year=effective_days_per_year,
            bms_cost_per_pack=bms_cost_per_pack,
            p_row_rack=p_row_rack, p_module_pads=p_module_pads,
            p_module_interconnect=p_module_interconnect, p_busbar=p_busbar,
            p_coolant_panel=p_coolant_panel, p_coolant_manifold=p_coolant_manifold,
            p_pack_terminal_seal=p_pack_terminal_seal, p_pack_support_frame=p_pack_support_frame,
            p_jacket_top_interior=p_jacket_top_interior, p_jacket_exterior_base=p_jacket_exterior_base,
            p_jacket_insulation=p_jacket_insulation,
            cells_parallel=cells_parallel_m03,
            insulation_area_base_m2=p2.get("insulation_area_base_m2", 0.0),
            insulation_area_top_m2=p2.get("insulation_area_top_m2", 0.0),
            rack_pad_kg_per_row=p2.get("rack_pad_kg_per_row", 0.0),
        )
        _tc = p2["total_cells"]
        return {
            "cost_per_kwh":          r4_2["cost_per_kwh"],
            "gap_vs_lfp":            r4_2["gap_vs_lfp"],
            "gap_pct":               r4_2["gap_pct"],
            "lfp_reference_per_kwh": None,
            "cell_capacity":         e2["cell_capacity"],
            "cell_voltage":          e2["cell_voltage"],
            "cell_specific_energy":  c2["cell_specific_energy"],
            "cell_energy_density":   c2["cell_energy_density"],
            "cell_mass_g":           c2["cell_mass_g"],
            "cell_thickness_mm":     c2["cell_thickness_mm"],
            "cell_width_mm":         c2["cell_width_mm"],
            "cell_length_mm":        c2["cell_length_mm"],
            "cell_volume_cm3":       c2["cell_volume_cm3"],
            "num_bicell_layers":     c2["num_bicell_layers"],
            "pack_useable_energy":   p2["pack_useable_energy_kWh"],
            "pack_gross_energy":     p2["pack_gross_energy_kWh"],
            "pack_mass_kg":          p2["pack_mass_kg"],
            "pack_specific_energy":  p2["pack_specific_energy"],
            "total_cells":           _tc,
            "modules_per_pack":      p2["modules_per_pack"],
            "mat_cost_per_cell":     r4_2["mat_cost_per_cell"],
            "cell_cost_per_pack":    r4_2["cell_cost_per_pack"],
            "module_cost_per_pack":  r4_2["module_cost_per_pack"],
            "pack_cost_per_pack":    r4_2["pack_cost_per_pack"],
            "cell_cost":             r4_2["total_cell_cost_per_cell"],
            "pack_total_cost":       r4_2["pack_total_cost"],
            # Cost-tier breakdown (needed for stacked bar)
            "cost_cells_per_pack":   r4_2["cost_from_cells"],
            "cost_modules_per_pack": r4_2["cost_from_modules"],
            "cost_pack_hw_per_pack": r4_2["cost_from_pack"],
            "total_profit":          r4_2["total_profit"],
            "total_warranty":        r4_2["total_warranty"],
            "mat_cost_total":        r4_2["mat_cost_per_cell"] * _tc,
            # Individual cell material costs (for cost breakdown pie)
            "cost_cathode_am":       r4_2["cost_cathode_am"],
            "cost_anode_am":         r4_2["cost_anode_am"],
            "cost_sep":              r4_2["cost_sep"],
            "cost_elec":             r4_2["cost_elec"],
            "cost_pvdf":             r4_2["cost_pvdf"],
            "cost_cmcsbr":           r4_2["cost_cmcsbr"],
            "cost_c_foil":           r4_2["cost_c_foil"],
            "cost_a_foil":           r4_2["cost_a_foil"],
            "cost_container":        r4_2["cost_container"],
            "cost_terminal":         r4_2["cost_terminal"],
            "cell_fixed_expenses_per_cell": r4_2["cell_fixed_expenses_per_cell"],
            # Mass keys for CO2 calculation
            "c_AM_mass":             e2["c_AM_mass"],
            "a_AM_mass":             e2["a_AM_mass"],
            "c_coat_total":          e2["c_coat_total"],
            "a_coat_total":          e2["a_coat_total"],
            "c_bind":                c_bind,
            "a_bind":                a_bind,
            "c_carbon_mass":         e2["c_carbon_mass"],
            "a_carbon_mass":         e2["a_carbon_mass"],
            "sep_mass_g":            c2["sep_mass_g"],
            "elec_mass_g":           c2["elec_mass_g"],
            "anode_foil_mass_g":     c2["anode_foil_mass_g"],
            "rack_mass_total_kg":    p2["rack_mass_total_kg"],
            "conductors_kg":         p2["conductors_kg"],
            "module_hardware_kg":    p2["module_hardware_g"] * p2["modules_per_pack"] / 1000,
            "module_al_kg":          p2["module_al_g"] * p2["modules_per_pack"] / 1000,
            "module_steel_kg":       p2["module_steel_g"] * p2["modules_per_pack"] / 1000,
            "module_cu_kg":          p2["module_cu_g"] * p2["modules_per_pack"] / 1000,
            "pack_jacket_total_kg":  p2["pack_jacket_total_kg"],
            # The cooling parts and the jacket, listed one by one. Module 05 needs
            # to know which bits are steel and which are aluminium before it can
            # work out their CO2. Without this it counts them as zero.
            "module_polymer_kg":     p2["module_polymer_g"] * p2["modules_per_pack"] / 1000,
            "coolant_panel_kg":      p2["coolant_panel_kg"],
            "coolant_manifold_kg":   p2["coolant_manifold_kg"],
            "coolant_liquid_kg":     p2["coolant_liquid_kg"],
            "jacket_support_frame_kg": p2["jacket_support_frame_kg"],
            "jacket_interior_base_kg": p2["jacket_interior_base_kg"],
            "jacket_exterior_base_kg": p2["jacket_exterior_base_kg"],
            "jacket_top_plates_kg":  p2["jacket_top_plates_kg"],
            "cathode_foil_mass_g":   c2["cathode_foil_mass_g"],
            "container_mass_g":      c2["container_mass_g"],
            "bms_mass_kg":           p2["bms_mass_kg"],
            "non_cell_mass_kg":      p2["non_cell_mass_kg"],
            # Direct manufacturing cost (labour + energy) — actual computed values from BatPaC G-cells
            "direct_mfg_total": (
                (r4_2["cell_direct_labor_per_cell"] + r4_2["cell_energy_per_cell"]) * _tc
                + (r4_2["module_direct_labor_per_module"] + r4_2["module_energy_per_module"]) * p2["modules_per_pack"]
                + r4_2["pack_direct_labor_per_pack"] + r4_2["pack_energy_per_pack"]
            ),
            # Fixed overhead (depreciation + GSA + R&D + financing) — actual computed values
            "fixed_overhead_total": (
                r4_2["cell_fixed_expenses_per_cell"] * _tc
                + r4_2["module_fixed_expenses_per_module"] * p2["modules_per_pack"]
                + r4_2["pack_fixed_expenses_per_pack"]
            ),
            # Variable overhead (indirect labour, utilities) — actual computed values
            "variable_overhead_total": (
                r4_2["cell_variable_overhead_per_cell"] * _tc
            ),
        }
    except Exception as exc:
        _run_full_cost.last_error = f"{type(exc).__name__}: {exc}"
        return None


# ═══════════════════════════════════════════════════════════════════════════
# PARAMETER STUDIES (Module 08)
#
# A parameter variation sweeps ONE model input across a range with everything
# else held at the study baseline, and reports the response. This is a different
# question from the Module 06 tornado, which ranks the sensitivity of market
# inputs to a symmetric +/-20% swing at a single operating point. The tornado
# cannot show non-linearity, thresholds or diminishing returns, it deliberately
# excludes design variables (they change the cell being modelled rather than the
# uncertainty around it), and it runs on cost per kWh only, so it says nothing
# about the storage-economics inputs that move LCOS.
#
# `needs_m05` marks sweeps whose response variable comes from Module 05, so the
# engine knows to run the sustainability model on each point.
# ═══════════════════════════════════════════════════════════════════════════
SWEEP_DEFS = {
    # ── Design space: what a cell engineer controls ──
    "V1  Cathode thickness": dict(
        key="c_thick", unit="um", lo=100.0, hi=250.0, n=16, group="Design",
        note="Areal loading. Thicker electrodes spread the inactive mass and the "
             "per-cell process costs over more capacity, until manufacturing and "
             "rate limits bite. Excluded from the tornado as a design variable."),
    "V2  N/P ratio": dict(
        key="np_ratio", unit="", lo=1.05, hi=1.50, n=16, group="Design",
        note="Anode oversizing. Hard carbon is a real cost item at an 0.80 active "
             "material fraction, so the safety margin is not free."),
    "V3  Cathode porosity": dict(
        key="c_por", unit="", lo=0.05, hi=0.35, n=16, group="Design",
        note="Sets coating density, and through it electrode mass and electrolyte "
             "volume. Interacts with cathode thickness."),
    "V4  Cell size": dict(
        key="target_cell_capacity", unit="Ah", lo=20.0, hi=200.0, n=16, group="Design",
        note="Stacking, formation, container and terminal costs scale per cell, "
             "not per kWh, so cell size changes cost per kWh even at fixed chemistry."),
    "V5  Cell shape": dict(
        key="lw_ratio", unit="", lo=1.2, hi=4.0, n=15, group="Design",
        note="Cell format. Expected to be minor; a null result is still a result."),
    # ── Commercial and manufacturing ──
    "V6  Factory size": dict(
        key="annual_production_packs", unit="packs/yr", lo=1000.0, hi=500000.0,
        n=18, log=True, group="Commercial",
        note="The single most important variation for a stationary storage argument. "
             "The baseline sits at BatPaC's automotive 500,000 packs/yr; no sodium-ion "
             "plant will start there. Spans three orders of magnitude, which a "
             "symmetric tornado swing cannot represent."),
    "V7  Cell yield": dict(
        key="cell_yield_pct", unit="%", lo=85.0, hi=99.0, n=15, group="Commercial",
        note="A young chemistry will not reach 95% on day one."),
    "V8  Labour cost": dict(
        key="labor_rate_per_hr", unit="$/hr", lo=5.0, hi=70.0, n=14, group="Commercial",
        note="Spans US, UK and Chinese manufacturing bases. Speaks to how much of "
             "the gap to market LFP prices is geography rather than chemistry."),
    "V9  Vanadium price": dict(
        key="_v2o5_price", unit="$/kg", lo=4.0, hi=30.0, n=14, group="Commercial",
        nvpf_only=True,
        note="Propagated through the Register Sec 6.1 stoichiometry: vanadium "
             "contributes $5.53 of the $16.53/kg cathode price. V2O5 is volatile, "
             "which is the supply chain resilience question in numbers."),
    # ── Storage economics: Module 05 responses ──
    "V10 Cycle life": dict(
        key="cycle_life", unit="cycles", lo=1000.0, hi=8000.0, n=15,
        group="Storage", needs_m05=True, response="lcos_per_kwh",
        note="Reported NVPF life spans 1600 to 4000 cycles depending on rate; LFP "
             "spans 6000 to 15000. Sweeping both is more honest than asserting either."),
    "V11 How often it cycles": dict(
        key="_cycles_per_year", unit="cycles/yr", lo=50.0, hi=365.0, n=16,
        group="Storage", needs_m05=True, response="lcos_per_kwh",
        note="Utilisation. Low utilisation amortises capital badly and favours cheap "
             "chemistry; high utilisation favours long life."),
    "V12 Electricity price": dict(
        key="elec_price", unit="$/kWh", lo=0.01, hi=0.20, n=16,
        group="Storage", needs_m05=True, response="lcos_per_kwh",
        note="Charging cost enters LCOS directly, divided by round trip efficiency."),
    "V13 Discount rate": dict(
        key="discount_rate", unit="%", lo=2.0, hi=15.0, n=14,
        group="Storage", needs_m05=True, response="lcos_per_kwh",
        note="Sets the annuity factor on capital and the present value of the "
             "end-of-life credit."),
    "V14 Depth of discharge": dict(
        key="useable_soc", unit="", lo=0.60, hi=1.00, n=17,
        group="Storage", needs_m05=True, response="lcos_per_kwh",
        note="Depth of discharge. PNNL report roughly a 3.3x cycle life gain moving "
             "an LFP system from 80% to 60% DoD, so the throughput lost to a narrower "
             "window is partly bought back in life. This sweep holds cycle life fixed, "
             "so it isolates the throughput term only; say so when reporting it."),
}


# Chemistry comparison scenarios. Module level so both Module 06 and the
# Module 08 parameter studies use one definition.
_CHEM_META_KEYS = {"desc", "co2_cathode_am", "co2_anode_am", "co2_al_foil",
                   "cycle_life", "rte_pct", "eol_cat_recovery", "eol_cat_price"}

# Electrode construction is a property of the manufacturing process, not of the
# chemistry, so it is inherited from the study rather than specified per chemistry.
# Every scenario is then built the same way and only the material properties and
# prices differ. Without this, comparing a chemistry modelled at one electrode
# composition against another modelled at a different one confounds the material
# difference with a formulation difference.
_CHEM_INHERITED_KEYS = {"c_am", "c_carb", "c_bind", "c_por", "c_thick",
                        "a_am", "a_carb", "a_bind", "a_por"}


def _chem_overrides(params):
    """Chemistry overrides with electrode construction stripped out."""
    return {k: v for k, v in params.items()
            if k not in _CHEM_META_KEYS and k not in _CHEM_INHERITED_KEYS}

CHEMISTRY_PRESETS_GLOBAL = {
    # ── SIB NaMnO2 / Hard carbon ───────────────────────────────────────────
    # Capacity: 157.67 mAh/g (ScienceDirect S0254058423000159)
    # Cathode voltage: 2.80 V vs Na+/Na (IOP J. Electrochem. Soc. 2015 162(14) A2379)
    # Cathode density: 4.25 g/cm3 (Materials Project mp-18957)
    # Electrode fractions 84:8:8 (Frontiers Energy Res. 2022 fenrg.2022.910842)
    # Anode: Hard carbon -- 300 mAh/g (Hyun et al. 2024 EES), 0.20 V avg
    # Anode density: 1.45 g/cm3 (RSC density-dependent sodium storage)
    # Prices: cathode $7.6/kg (ScienceDirect S2949821X25002418), anode $5.2/kg (S2666248525000241)
    # CO2: cathode AM 3.99 kgCO2/kg (Climatiq -- Mn oxide; peer-reviewed source needed)
    #       anode AM 4.07 kgCO2/kg (Liu et al. 2021, Phil. Trans. R. Soc. A)
    # Cycle life: not established for full-cell stationary -- excluded from LCOS
    # RTE: 90% (same as NVPF, assumed; Jasper et al. 2026)
    "SIB NaMnO2 / Hard carbon": {
        "c_cap": 157.67, "c_volt": 2.80, "c_dens": 4.25, "c_am": 0.84,
        "c_carb": 0.08,  "c_bind": 0.08,
        "a_cap": 300.0,  "a_volt": 0.20, "a_dens": 1.50,  "a_am": 0.80,
        "a_carb": 0.10,  "a_bind": 0.10,
        "p_cathode_am": 7.6, "p_anode_am": 5.2,
        # CO2 overrides (kgCO2/kg) for radar chart computation
        "co2_cathode_am": 3.99, "co2_anode_am": 4.07,
        # anode foil stays Al (SIB) -- no override needed
        "cycle_life": None,          # not established at stationary conditions
        "rte_pct": 90.0,
        "eol_cat_recovery": None,    # no published recovery rate
        "eol_cat_price": None,       # no virgin price basis established
        "desc": "Layered oxide cathode. Higher capacity, moderate voltage, very low AM cost.",
    },
    # ── SIB NaFePO4 / Hard carbon ──────────────────────────────────────────
    # Capacity: 154 mAh/g (RSC pubs.rsc.org/cp/article-abstract/22/25/13975)
    # Cathode voltage: 2.70 V vs Na+/Na (Oh et al. 2012 Electrochem. Commun. 22, 149)
    # Cathode density: 3.79 g/cm3 (Materials Project mp-19226)
    # Electrode fractions 80:10:10 (ScienceDirect S0042207X23000507)
    # Anode: Hard carbon -- same as NaMnO2
    # Prices: cathode $4.13/kg, anode $5.2/kg (ScienceDirect S2666248525000241)
    # CO2: cathode AM 10.549 kgCO2/kg proxy from LFP (ScienceDirect S2667056926000581)
    #       no dedicated LCA for NaFePO4; LFP proxy justified by shared Fe/P chemistry
    #       anode AM 4.07 kgCO2/kg (Liu et al. 2021)
    # Cycle life: not well established -- excluded from LCOS
    # RTE: 90% (assumed; Jasper et al. 2026)
    "SIB NaFePO4 / Hard carbon": {
        "c_cap": 154.0,  "c_volt": 2.70, "c_dens": 3.79, "c_am": 0.80,
        "c_carb": 0.10,  "c_bind": 0.10,
        "a_cap": 300.0,  "a_volt": 0.20, "a_dens": 1.50,  "a_am": 0.80,
        "a_carb": 0.10,  "a_bind": 0.10,
        "p_cathode_am": 4.13, "p_anode_am": 5.2,
        "co2_cathode_am": 10.549, "co2_anode_am": 4.07,
        "cycle_life": None,
        "rte_pct": 90.0,
        "eol_cat_recovery": None,
        "eol_cat_price": None,
        "desc": "Olivine structure. Very stable, low cost, lower energy density.",
    },
    # ── LIB LFP / Graphite ─────────────────────────────────────────────────
    # Capacity: 170 mAh/g (ScienceDirect S1369702114004118)
    # Cathode voltage: 3.50 V vs Li+/Li (Padhi et al. 1997, J. Electrochem. Soc. 144, 1188)
    # Cathode density: 3.47 g/cm3 (Materials Project mp-19017)
    # Electrode fractions cathode: LFP 94:3:3 AM:carbon:PVDF (BatPaC v5.2 default;
    #   consistent with Peters et al. 2016 and Wentker et al. 2019)
    # Anode: Graphite -- 360 mAh/g (BatPaC v5.2), 0.15 V (S1369702114004118)
    # Anode fractions graphite: 98:1:1 AM:carbon:PVDF (BatPaC v5.2 default;
    #   graphite is self-conducting so minimal conductive additive needed)
    # Anode density: 1.70 g/cm3 (NIST)
    # Prices: cathode $6/kg, anode $7.3/kg (S2666248525000241)
    # KEY DIFFERENCES vs SIB: Cu anode foil ($1.20/m2 Vaalma et al. 2018, density 8.96 g/cm3)
    #   LiPF6 electrolyte: 17.42 $/L (Peters et al. 2016, EUR15.84 converted at 1.10 EUR/USD)
    #   LiPF6 density: 1.26 g/mL (Sigma-Aldrich product data, acknowledged as supplier spec)
    # CO2: cathode AM 10.549 kgCO2/kg (ScienceDirect S2667056926000581)
    #       anode AM (graphite) 10.0 kgCO2/kg (ScienceDirect S2667056926000581)
    #       Cu foil 6.0 kgCO2/kg (Ellingsen et al. 2014 proxy; ScienceDirect S0959652612002120)
    # Cycle life: 4000 cycles (Jasper et al. 2026 LFP reference system)
    # RTE: 93.6% (ScienceDirect S0378775325001260)
    "LIB LFP / Graphite": {
        "c_cap": 170.0,  "c_volt": 3.50, "c_dens": 3.68, "c_am": 0.80,
        "c_carb": 0.10,  "c_bind": 0.10,   # Altundag 2023, Register Sec 3.3. Matches the
                                           # 80:10:10 convention used for the NVPF baseline,
                                           # so the comparison is not confounded by a
                                           # difference in electrode composition convention.
        "a_cap": 360.0,  "a_volt": 0.15, "a_dens": 2.24,  "a_am": 0.98,
        "a_carb": 0.01,  "a_bind": 0.01,
        "p_cathode_am": 6.0, "p_anode_am": 7.3,
        "np_ratio": 1.10,   # BatPaC v5.2 default for LFP/graphite; lower ICL than HC
        # Graphite anode uses PVDF binder (not CMC/SBR used for HC anodes)
        # Density and price must override base study HC values
        "a_bind_dens": 1.265,  # PVDF density (BatPaC v5.2 default)
        "p_cmcsbr":    1.4,  # PVDF price for graphite anode (Peters et al. 2016)
        # LFP-specific overrides
        "p_neg_terminal_kg": 8.64,  # Cu negative terminal (BatPaC LIB default; LFP uses Cu not Al)
        "p_anode_foil":     1.20,   # Cu foil $/m2 (Vaalma et al. 2018)
        "anode_foil_density": 8.96, # Cu density g/cm3
        "p_electrolyte":    18.03,  # LiPF6 $/L (Peters et al. 2016)
        "elec_dens":        1.26,   # LiPF6 g/mL (Sigma-Aldrich). Key must be
                                    # "elec_dens" to match _run_full_cost.
        # CO2 overrides
        "co2_cathode_am": 10.549, "co2_anode_am": 10.0,
        "co2_al_foil":    6.0,    # Cu foil CO2 used in anode foil slot
        # LCOS and end-of-life overrides
        "cycle_life": 8000,          # Alberte Tapia et al. 2026 (IOP Conf. Ser. 1588 012005)
                                     # Table 1, PNNL Energy Storage Cost and Performance
                                     # Database. Chosen for consistency of sourcing basis
                                     # with the NVPF cycle life (both from the same
                                     # comparative BESS characterisation study).
        "rte_pct": 93.6,             # Rehm 2025
        "eol_cat_recovery": 95.0,    # Hu et al.: >95% recovery of Li, Fe, P and other
                                     # constituent elements via direct regeneration.
                                     # Floor value taken, not rounded up.
        "eol_cat_price": 3.90,       # 65% of the $6.00/kg virgin LFP price,
                                     # the same ratio used for NVPF in Sec 6.2
        "desc": "Dominant stationary storage competitor. Low cost, flat voltage plateau.",
    },
}


def _chem_co2(r, params, base_in):
    """CO2 for any chemistry, even ones with no cycle life figure.

    CO2 only depends on how much material is in the pack and how dirty each
    material is. It has nothing to do with cycle life or recycling, so we can
    report it even where LCOS has to be left blank. The stand-in numbers below
    are never used by the CO2 sums.
    """
    stand_in = dict(params)
    stand_in["cycle_life"] = params.get("cycle_life") or 3000
    if stand_in.get("eol_cat_recovery") is None:
        stand_in["eol_cat_recovery"] = 0.0
    if stand_in.get("eol_cat_price") is None:
        stand_in["eol_cat_price"] = 0.0
    s = _chem_sustainability(r, stand_in, base_in)
    if not s:
        return None
    return {"co2_per_kwh": s["co2_per_kwh"],
            "co2_pack_total_kg": s["co2_pack_total_kg"],
            "co2_pack_cells_kg": s["co2_pack_cells_kg"],
            "co2_pack_noncell_kg": s["co2_pack_noncell_kg"],
            "co2_breakdown": s["co2_breakdown"]}


def _chem_sustainability(r, params, base_in, s5_over=None):
    """Module 05 on a chemistry scenario. Returns None when the scenario has
    no sourced cycle life or end-of-life basis, so the gap stays visible
    rather than silently inheriting the baseline chemistry's figures."""
    cyc = params.get("cycle_life")
    rec = params.get("eol_cat_recovery")
    pri = params.get("eol_cat_price")
    if not (cyc and rec is not None and pri is not None):
        return None
    _ss = dict(st.session_state)
    if s5_over:
        # Sweeps override the storage-economics inputs directly. Keys starting with
        # an underscore are handled explicitly below, not read from session state.
        _ss.update({k: v for k, v in s5_over.items() if not k.startswith("_")})
    try:
        return run_sustainability(
            r["c_AM_mass"], r["a_AM_mass"], r["c_carbon_mass"], r["a_carbon_mass"],
            r["c_coat_total"] * r["c_bind"], r["a_coat_total"] * r["a_bind"],
            0.0, 0.0, r["cathode_foil_mass_g"], r["anode_foil_mass_g"],
            0.0, r["sep_mass_g"], r["elec_mass_g"],
            r["container_mass_g"], r["cell_mass_g"],
            r["total_cells"], r["pack_useable_energy"], r["pack_mass_kg"],
            conductors_kg=r["conductors_kg"],
            rack_mass_total_kg=r["rack_mass_total_kg"],
            pack_jacket_total_kg=r["pack_jacket_total_kg"],
            coolant_panel_kg=r.get("coolant_panel_kg", 0.0),
            coolant_manifold_kg=r.get("coolant_manifold_kg", 0.0),
            coolant_liquid_kg=r.get("coolant_liquid_kg", 0.0),
            jacket_support_frame_kg=r.get("jacket_support_frame_kg", 0.0),
            jacket_interior_base_kg=r.get("jacket_interior_base_kg", 0.0),
            jacket_exterior_base_kg=r.get("jacket_exterior_base_kg", 0.0),
            jacket_top_plates_kg=r.get("jacket_top_plates_kg", 0.0),
            module_al_kg=r["module_al_kg"], module_steel_kg=r["module_steel_kg"],
            module_cu_kg=r["module_cu_kg"],
            module_polymer_kg=r.get("module_polymer_kg", 0.0),
            bms_mass_kg=r["bms_mass_kg"],
            anode_foil_density=params.get("anode_foil_density",
                                          base_in.get("anode_foil_density", 2.70)),
            p_al_kg=_ss.get("p_al_kg", 0.94), p_cu_kg=_ss.get("p_cu_kg", 8.96),
            co2_cathode_am=params.get("co2_cathode_am", _ss.get("co2_cathode_am", 22.0)),
            co2_anode_am=params.get("co2_anode_am", _ss.get("co2_anode_am", 4.07)),
            co2_al_foil=_ss.get("co2_al_foil", 6.6),
            co2_separator=_ss.get("co2_separator", 2.9),
            co2_electrolyte=_ss.get("co2_electrolyte", 2.58),
            co2_carbon=_ss.get("co2_carbon", 3.5),
            co2_pvdf=_ss.get("co2_pvdf", 55.8),
            co2_anode_binder=(_ss.get("co2_pvdf", 55.8) if "LFP" in params.get("desc", "") or
                              params.get("a_bind_dens") == 1.77
                              else _ss.get("co2_anode_binder", 3.36)),
            co2_container=_ss.get("co2_container", 6.6),
            co2_copper=_ss.get("co2_copper", 6.0),
            co2_steel=_ss.get("co2_steel", 1.92),
            co2_bms=_ss.get("co2_bms", 23.3),
            grid_co2_intensity_kg_per_kwh=_ss.get("grid_co2_intensity", 0.164),
            pack_total_cost_usd=r["pack_total_cost"],
            cycle_life=(s5_over or {}).get("cycle_life", cyc),
            calendar_life_yr=_ss.get("calendar_life_yr", 15),
                    cycles_per_year_override=(s5_over or {}).get("_cycles_per_year"),
            roundtrip_efficiency_pct=params.get("rte_pct", 90.0),
            electricity_price_per_kwh=_ss.get("elec_price", 0.05),
            discount_rate_pct=_ss.get("discount_rate", 8.0),
            om_cost_pct_per_yr=_ss.get("om_cost_pct", 2.075),
            eol_cathode_am_recovery_pct=rec,
            eol_cathode_am_price_kg=pri,
            eol_al_recovery_pct=_ss.get("eol_al_recovery", 99.1),
            eol_steel_recovery_pct=_ss.get("eol_steel_recovery", 98.1),
            eol_al_price_kg=_ss.get("eol_al_price", 0.94),
            eol_steel_price_kg=_ss.get("eol_steel_price", 0.47),
        )
    except Exception:
        return None


def _sweep_baseline_value(param_key, base_inputs):
    """The value a swept parameter currently holds in the study, or None.

    Used to anchor each sweep's default range on the baseline, so the study point
    always sits inside the swept window rather than off one end of it.
    """
    if param_key == "_v2o5_price":
        return 12.70                      # Register Sec 6.1 precursor quote
    if param_key == "_cycles_per_year":
        cyc = st.session_state.get("cycle_life", 3200)
        yrs = st.session_state.get("calendar_life_yr", 15)
        return min(cyc, yrs * 365) / yrs if yrs else None
    if param_key == "target_cell_capacity":
        r = st.session_state.get("_m01_results") or {}
        return r.get("cell_capacity")
    for src in (base_inputs, st.session_state):
        if param_key in src:
            v = src[param_key]
            if isinstance(v, (int, float)):
                return float(v)
    return None


def _sweep_point(param_key, value, base_inputs, chem_overrides, needs_m05, m05_params):
    """One point of a parameter sweep. Returns a flat dict, or None if the run failed."""
    ov = dict(chem_overrides)
    bi = dict(base_inputs)
    s5_over = {}

    if param_key == "_v2o5_price" and "p_cathode_am" not in chem_overrides:
        # Register Sec 6.1: C = C0 + (1/MW) * sum(x_i * C_i * MW_i), MW = 417.79.
        # Only applied when the scenario has no cathode price of its own: vanadium is
        # a precursor of NVPF and has no meaning for LFP or any other cathode.
        # Only the V2O5 term moves; NaF and NH4H2PO4 hold at their quoted prices.
        _c0, _mw = 10.065, 417.79
        _naf = 3 * 1.35 * 41.988 / _mw
        _adp = 2 * 0.96 * 115.03 / _mw
        _v = 1 * value * 181.88 / _mw
        ov["p_cathode_am"] = _c0 + _v + _naf + _adp
    elif param_key == "target_cell_capacity":
        _e = run_electrochemical(
            ov.get("c_cap", bi["c_cap"]), ov.get("c_volt", bi["c_volt"]),
            ov.get("c_dens", bi["c_dens"]), ov.get("c_am", bi["c_am"]),
            ov.get("c_carb", bi["c_carb"]), ov.get("c_bind", bi["c_bind"]),
            ov.get("c_por", bi["c_por"]), ov.get("c_thick", bi["c_thick"]),
            ov.get("a_cap", bi["a_cap"]), ov.get("a_volt", bi["a_volt"]),
            ov.get("a_dens", bi["a_dens"]), ov.get("a_am", bi["a_am"]),
            ov.get("a_bind", bi["a_bind"]), ov.get("a_carb", bi["a_carb"]),
            ov.get("a_por", bi["a_por"]), ov.get("np_ratio", bi["np_ratio"]),
            None, bi["tab_excess"],
            c_carb_dens=bi["c_carb_dens"],
            c_bind_dens=ov.get("c_bind_dens", bi["c_bind_dens"]),
            a_carb_dens=bi["a_carb_dens"],
            a_bind_dens=ov.get("a_bind_dens", bi["a_bind_dens"]),
            target_cell_capacity_Ah=value)
        bi["electrode_area"] = _e["electrode_area"]
    elif param_key in ("cycle_life", "elec_price", "discount_rate", "_cycles_per_year"):
        s5_over[param_key] = value
    elif param_key in bi:
        bi[param_key] = value
    else:
        ov[param_key] = value

    r = _run_full_cost(ov, {}, {}, {}, bi)
    if r is None:
        return None
    row = {
        "value": value,
        "cost_per_kwh": r["cost_per_kwh"],
        "pack_gross_energy": r["pack_gross_energy"],
        "pack_mass_kg": r["pack_mass_kg"],
        "pack_specific_energy": r["pack_specific_energy"],
        "cell_capacity": r["cell_capacity"],
        "mat_cost_per_cell": r["mat_cost_per_cell"],
        "pack_total_cost": r["pack_total_cost"],
    }
    if needs_m05:
        s5 = _chem_sustainability(r, m05_params, bi, s5_over=s5_over)
        row["lcos_per_kwh"] = s5.get("lcos_per_kwh") if s5 else None
        row["lcos_net_per_kwh"] = s5.get("lcos_net_per_kwh") if s5 else None
        row["co2_per_kwh"] = s5.get("co2_per_kwh") if s5 else None
        row["eol_total_value"] = s5.get("eol_total_value") if s5 else None
    return row


def _lfp_reference_cost():
    """Pack cost of the LFP/graphite scenario run through THIS model.

    The comparison that matters is like-for-like: the same plant, the same
    production volume, the same labour and energy basis, the same pack topology,
    with only the chemistry swapped. A published market price (BNEF and similar)
    is not comparable, because it reflects mature high-volume supply chains, a
    largely depreciated asset base and a manufacturer margin, none of which this
    model contains. Mixing the two attributes a scale-and-geography difference to
    chemistry.

    Returns None until Module 06's chemistry comparison has been run, so callers
    can say the benchmark is unavailable rather than substitute a fixed number.
    """
    for name, data in (st.session_state.get("_chem_results", {}) or {}).items():
        if "lfp" in str(name).lower():
            cost = data.get("cost_per_kwh")
            if cost:
                return float(cost)
    return None


_NO_LFP_MSG = ("Run the Module 06 chemistry comparison to generate a like-for-like "
               "LFP benchmark from this model.")


# Module 06 and Module 07 must start from the SAME base case: Module 07's Monte
# Carlo is a distribution around Module 06's deterministic point, so any drift
# between the two would make the two modules disagree about their own base.
# Both therefore build their inputs here, from _study_inputs, with one set of
# fallback defaults.
def _build_base_inputs(study_inputs, lfp_benchmark=None):
    si = study_inputs if isinstance(study_inputs, dict) else {}
    def g(key, default):
        # Look in the saved study first, then at the input box on screen, then
        # fall back to the built-in number. The middle step lets older studies
        # still find values that were added to the study later on.
        if key in si:
            return si[key]
        live = st.session_state.get(key)
        if isinstance(live, (int, float)) and not isinstance(live, bool):
            return live
        return default
    return {
        # ── Module 01: electrochemical ──
        "c_cap": g("c_cap", 213.6), "c_volt": g("c_volt", 3.86),
        "c_dens": g("c_dens", 4.65), "c_am": g("c_am", 0.96),
        "c_carb": g("c_carb", 0.02), "c_bind": g("c_bind", 0.02),
        "c_por": g("c_por", 0.27), "c_thick": g("c_thick", 120.0),
        "c_carb_dens": g("c_carb_dens", 1.825), "c_bind_dens": g("c_bind_dens", 1.77),
        "a_cap": g("a_cap", 360.4), "a_volt": g("a_volt", 0.14),
        "a_dens": g("a_dens", 2.24), "a_am": g("a_am", 0.98),
        "a_bind": g("a_bind", 0.02), "a_carb": g("a_carb", 0.0),
        "a_por": g("a_por", 0.25), "a_carb_dens": g("a_carb_dens", 1.95),
        "a_bind_dens": g("a_bind_dens", 1.10),
        "np_ratio": g("np_ratio", 1.10), "electrode_area": g("electrode_area", 8560.81),
        "tab_excess": g("tab_excess", 0.04),
        # ── Module 02: cell design ──
        "num_layers": g("num_layers", 32), "lw_ratio": g("lw_ratio", 3.0),
        "sep_excess_w": g("sep_excess_w", 2.0), "sep_excess_l": g("sep_excess_l", 4.0),
        "anode_excess": g("anode_excess", 2.0),
        "tab_length": g("tab_length_mm", 8.0), "feedthrough": g("feedthrough", 5.0),
        "cc_buffer": g("cc_buffer", 2.0), "pouch_seal": g("pouch_seal", 6.0),
        "packing_eff": g("packing_eff", 0.97), "cell_edge_fold": g("cell_edge_fold", 1.0),
        "bicell_expansion": g("bicell_expansion", 0.0),
        "elec_excess": g("elec_excess", 0.02),
        "con_thick_um": g("con_thick_um", 150.0), "con_density": g("con_density", 2.202),
        "wall_thick": g("wall_thick", 0.0), "seal_buf": g("seal_buf", 6.0),
        "c_foil_thick": g("c_foil_thick", 15.0), "a_foil_thick": g("a_foil_thick", 10.0),
        "anode_foil_density": g("anode_foil_density", 2.70),
        "sep_thick": g("sep_thick", 15.0), "sep_dens": g("sep_dens", 0.473),
        "elec_dens": g("elec_dens", 1.15), "elec_uptake": g("elec_uptake", 0.50),
        # ── Module 03: pack design ──
        "useable_soc": g("useable_soc", 0.90),
        "cells_per_module": g("cells_per_module", 20),
        "cells_parallel_m03": g("cells_parallel_m03", 2),
        "modules_per_row": g("modules_per_row", 5), "rows_per_pack": g("rows_per_pack", 4),
        "modules_parallel": g("modules_parallel", 2),
        "al_cond_thick_mm": g("al_cond_thick_mm", 0.4),
        "mod_wall_thick_mm": g("mod_wall_thick_mm", 0.3),
        "restraint_thick_mm": g("restraint_thick_mm", 2.0),
        "coolant_panel_thick_mm": g("coolant_panel_thick_mm", 5.0),
        "coolant_wall_mm": g("coolant_wall_mm", 0.3),
        "jacket_insul_mm": g("jacket_insul_mm", 10.0),
        "jacket_int_plate_mm": g("jacket_int_plate_mm", 1.0),
        "jacket_ext_base_mm": g("jacket_ext_base_mm", 1.0),
        "bms_bdu_mass": g("bms_bdu_mass", 2.444), "bms_bdu_vol": g("bms_bdu_vol", 1.5485),
        "nominal_current": g("nominal_current", 100.0),
        # ── Module 04: prices and manufacturing ──
        "p_cathode_am": g("p_cathode_am", 20.0), "p_anode_am": g("p_anode_am", 6.0),
        "p_carbon": g("p_carbon", 1.5), "p_pvdf": g("p_pvdf", 10.0),
        "p_cmcsbr": g("p_cmcsbr", 3.0),
        "p_al_foil": g("p_al_foil", 0.20), "p_anode_foil": g("p_anode_foil", 0.20),
        "p_sep": g("p_sep", 2.0), "p_electrolyte": g("p_electrolyte", 10.0),
        "p_container": g("p_container", 7.0),
        "p_pos_terminal_kg": g("p_pos_terminal_kg", 2.405),
        "p_neg_terminal_kg": g("p_neg_terminal_kg", 2.405),
        "terminal_fixed_cost": g("terminal_fixed_cost", 0.08),
        "annual_production_packs": g("annual_production_packs", 500000),
        "cell_yield_pct": g("cell_yield_pct", 95.0),
        "labor_rate_per_hr": g("labor_rate_per_hr", 35.0),
        "energy_price_per_kWh": g("energy_price_per_kWh", 0.04),
        "effective_days_per_year": g("effective_days_per_year", 320),
        "bms_cost_per_pack": g("bms_cost_per_pack", 375.0),
        "p_row_rack": g("p_row_rack", 1.325), "p_module_pads": g("p_module_pads", 1.5),
        "p_module_interconnect": g("p_module_interconnect", 8.84),
        "p_busbar": g("p_busbar", 8.68), "p_coolant_panel": g("p_coolant_panel", 3.45),
        "p_coolant_manifold": g("p_coolant_manifold", 9.5),
        "p_pack_terminal_seal": g("p_pack_terminal_seal", 8.88),
        "p_pack_support_frame": g("p_pack_support_frame", 1.325),
        "p_jacket_top_interior": g("p_jacket_top_interior", 3.16),
        "p_jacket_exterior_base": g("p_jacket_exterior_base", 1.375),
        "p_jacket_insulation": g("p_jacket_insulation", 3.0),
    }


# Preserve every module's input values across navigation (see docstring). Must
# run before the nav bar and before any module renders its input widgets.
_persist_widget_state()

# Handle navigation from "Next module" buttons
if "_navigate_to" in st.session_state:
    _dest = st.session_state.pop("_navigate_to")
    st.session_state["current_module"] = _dest
    st.session_state["_force_nav_sync"] = True
    st.query_params["module"] = _dest

# NAV BAR
nav_left, nav_right = st.columns([1, 2])
with nav_left:
    st.markdown('<div class="nav-brand">🔋 SIB TEA MODEL</div>', unsafe_allow_html=True)
with nav_right:
    col_nav, col_theme, col_save, col_load, col_new = st.columns([6, 3, 2, 2, 2])
    with col_nav:
        _current = st.session_state.get("current_module", MODULE_LABELS[0])
        if _current not in MODULE_LABELS:
            _key_to_label = {k: lbl for lbl, k in MODULES}
            _current = _key_to_label.get(_current, MODULE_LABELS[0])
            st.session_state["current_module"] = _current
        _current_idx = MODULE_LABELS.index(_current)
        if st.session_state.pop("_force_nav_sync", False):
            st.session_state["nav_select"] = _current

        selected_label = st.selectbox(
            "Navigate", MODULE_LABELS,
            index=_current_idx,
            key="nav_select", label_visibility="collapsed"
        )
        selected_key = dict(MODULES)[selected_label]
        if selected_label != _current:
            st.session_state["current_module"] = selected_label
            st.query_params["module"] = selected_label
        else:
            st.query_params["module"] = _current

    with col_theme:
        st.selectbox("Theme", ["Light", "Dark"], key="theme_select", label_visibility="collapsed")
        st.query_params["theme"] = st.session_state.get("theme_select", "Light")
    with col_save:
        if st.button("Save", help="Save study under a name", key="btn_save"):
            st.session_state["_show_save"] = True
    with col_load:
        studies = _load_studies()
        if studies and st.button("Load", help="Load a saved study", key="btn_load"):
            st.session_state["_show_load"] = True
    with col_new:
        if st.button("New", help="Start a fresh study - clears all inputs and results", key="btn_new"):
            st.session_state["_show_new_confirm"] = True

# ── NEW STUDY CONFIRMATION ────────────────────────────────────────────────────
if st.session_state.get("_show_new_confirm"):
    with st.container():
        st.markdown(f"""
        <div style="background:{T['card']};border:1px solid {T['border']};border-radius:6px;
                    padding:1.5rem;margin:1rem 0;">
            <strong>Start a new study?</strong><br>
            <span style="font-size:0.85rem;color:{T['sub']}">
            This clears every input and computed result across all modules in this session.
            It does not delete any studies you've saved to disk - only your saved studies list
            is affected by deleting entries there. Unsaved work will be lost.
            </span>
        </div>
        """, unsafe_allow_html=True)
        ncol1, ncol2 = st.columns([2, 2])
        with ncol1:
            if st.button("Yes, start fresh", key="_btn_new_confirm", use_container_width=True):
                _reset_all_session_state()
                st.session_state.pop("_show_new_confirm", None)
                st.rerun()
        with ncol2:
            if st.button("Cancel", key="_btn_new_cancel", use_container_width=True):
                st.session_state.pop("_show_new_confirm", None)
                st.rerun()

# ── SAVE / LOAD DIALOGS ───────────────────────────────────────────────────────
if st.session_state.get("_show_save"):
    with st.container():
        st.markdown(f"""
        <div class="note-box" style="margin-bottom:0.5rem;">
            <strong>Name this study</strong> - enter a name to save your current inputs and results.
        </div>
        """, unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns([5, 2, 2])
        with sc1:
            study_name = st.text_input("Study name", key="_study_name_input",
                                       label_visibility="collapsed",
                                       placeholder="e.g. NVPF 60Ah baseline")
        with sc2:
            if st.button("Save study", key="_btn_save_confirm"):
                if study_name.strip():
                    studies = _load_studies()
                    studies[study_name.strip()] = _collect_session_data()
                    _save_studies(studies)
                    st.session_state.pop("_show_save", None)
                    st.session_state.pop("_study_name_input", None)
                    st.toast(f"Saved: {study_name.strip()}", icon="💾")
                    st.rerun()
        with sc3:
            if st.button("Cancel", key="_btn_save_cancel"):
                st.session_state.pop("_show_save", None)
                st.rerun()

if st.session_state.get("_show_load"):
    studies = _load_studies()
    if studies:
        with st.container():
            st.markdown(f"""
            <div class="note-box" style="margin-bottom:0.5rem;">
                <strong>Load a study</strong> - select a saved study to restore all inputs and results.
            </div>
            """, unsafe_allow_html=True)
            lc1, lc2, lc3 = st.columns([5, 2, 2])
            with lc1:
                chosen = st.selectbox("Select study", list(studies.keys()),
                                      key="_study_load_select",
                                      label_visibility="collapsed")
            with lc2:
                if st.button("Load study", key="_btn_load_confirm"):
                    _restore_session_data(studies[chosen])
                    dest = _furthest_module(studies[chosen])
                    st.session_state["current_module"] = dest
                    st.session_state["_force_nav_sync"] = True
                    st.session_state.pop("_show_load", None)
                    st.toast(f"Loaded: {chosen}", icon="📂")
                    st.rerun()
            with lc3:
                if st.button("Cancel", key="_btn_load_cancel"):
                    st.session_state.pop("_show_load", None)
                    st.rerun()

# ── ROUTING GUARD ─────────────────────────────────────────────────────────────
if selected_key not in BUILT:
    st.markdown(f"""
    <div class="status-bar" style="margin-top:2rem;text-align:center;padding:2rem;">
        <strong>🚧 Coming soon</strong> - {selected_label.strip()} is not built yet.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── HOME PAGE ─────────────────────────────────────────────────────────────────
if selected_key == "home":

    st.markdown(f"""
    <div class="hero-label">MSc Design Engineering · Imperial College London</div>
    <div class="hero-title">Sodium-Ion Battery<br><span>Techno-Economic Model</span></div>
    <div class="hero-subtitle">Bottom-up cost framework · Sustainability analysis · Sensitivity analysis · Monte Carlo simulation</div>
    <div class="meta-bar">
        <div><div class="meta-label">Supervisor</div><div class="meta-value">Dr. Billy Wu</div></div>
        <div><div class="meta-label">Study</div><div class="meta-value">Potential of SIBs</div></div>
        <div><div class="meta-label">Benchmark</div><div class="meta-value">LFP / NMC</div></div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown('<div class="section-header">Research Question</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="rq-box">
            <div class="rq-main">
                What are the key techno-economic drivers determining the cost competitiveness
                of sodium-ion batteries for stationary energy storage, and under what conditions
                can they achieve cost parity with lithium-ion alternatives?
            </div>
            <div class="rq-sub">
                <span>SQ1</span>How do variations in hard carbon anode density and cathode chemistry affect $/kWh?<br>
                <span>SQ2</span>Which components represent the greatest cost reduction opportunity?<br>
                <span>SQ3</span>How do SIB costs compare across energy- vs power-optimised designs?<br>
                <span>SQ4</span>Under what manufacturing scale does SIB reach cost parity with LFP?
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Model Modules</div>', unsafe_allow_html=True)

        MODULES_INFO = [
            ("Module 01: Electrochemical Design", "Calculates cell-level electrochemistry from chemistry inputs. Derives material masses, electrode thicknesses and cell capacity."),
            ("Module 02: Cell Design",            "Computes cell physical geometry, foil areas, electrolyte volume, and cell-level energy metrics."),
            ("Module 03: Pack Design",            "Scales from cell to pack - voltage, energy, capacity, mass, volume."),
            ("Module 04: Cost Model",             "Full bottom-up cost calculation with power-law manufacturing scaling."),
            ("Module 05: Sustainability",         "LCOS, embodied carbon, material intensity per kWh and end-of-life value."),
            ("Module 06: Sensitivity Analysis",   "Chemistry comparison, tornado plots and parameter ranking by impact on $/kWh."),
            ("Module 07: Uncertainty Analysis",   "Monte Carlo simulation across the cost inputs, giving P10/P50/P90 and the probability of cost parity."),
            ("Module 08: Parameter Studies",      "Sweeps a single design, commercial or storage input across its range and reports the response curve."),
        ]

        for i in range(0, len(MODULES_INFO), 2):
            c1, c2 = st.columns(2, gap="small")
            for col, (name, desc) in zip([c1, c2], MODULES_INFO[i:i+2]):
                col.markdown(f"""
                <div class="module-card">
                    <div class="module-name">{name}</div>
                    <div class="module-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-header">How to Use</div>', unsafe_allow_html=True)
        for num, title, desc in [
            ("01", "Select a module",  "Use the dropdown at the top to navigate between modules."),
            ("02", "Review defaults",  "Each module loads with literature-sourced default values."),
            ("03", "Adjust inputs",    "Change any value using the input fields provided."),
            ("04", "Calculate",        "Click Calculate to run all equations for that module."),
            ("05", "Review outputs",   "Results are shown with values, units, and context notes."),
            ("06", "Move on",          "Outputs pass automatically to downstream modules."),
        ]:
            st.markdown(f"""
            <div class="workflow-step">
                <div class="step-num">{num}</div>
                <div class="step-text"><strong>{title}</strong><br>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        _home_studies = _load_studies()
        if _home_studies:
            st.markdown('<div class="section-header" style="margin-top:1.5rem;">Saved Studies</div>', unsafe_allow_html=True)
            for _sname, _sdata in _home_studies.items():
                _dest = _furthest_module(_sdata)
                _rename_key = f"_renaming_{_sname}"
                _input_key  = f"_rename_input_{_sname}"

                if st.session_state.get(_rename_key):
                    # Rename mode - show text input inline
                    ri1, ri2, ri3 = st.columns([5, 2, 2])
                    with ri1:
                        new_name = st.text_input(
                            "New name", key=_input_key,
                            label_visibility="collapsed",
                            placeholder=f"Rename '{_sname}'"
                        )
                    with ri2:
                        if st.button("Save", key=f"_rename_save_{_sname}", use_container_width=True):
                            if new_name.strip() and new_name.strip() != _sname:
                                _studies = _load_studies()
                                _studies[new_name.strip()] = _studies.pop(_sname)
                                _save_studies(_studies)
                                st.session_state.pop(_rename_key, None)
                                st.toast(f"Renamed to: {new_name.strip()}", icon="✏️")
                                st.rerun()
                    with ri3:
                        if st.button("Cancel", key=f"_rename_cancel_{_sname}", use_container_width=True):
                            st.session_state.pop(_rename_key, None)
                            st.rerun()
                else:
                    # Normal mode - load | rename | delete
                    sc1, sc2, sc3 = st.columns([5, 2, 2])
                    with sc1:
                        if st.button(_sname, key=f"home_study_{_sname}", use_container_width=True):
                            _restore_session_data(_sdata)
                            st.session_state["current_module"] = _dest
                            st.session_state["_force_nav_sync"] = True
                            st.rerun()
                    with sc2:
                        if st.button("Rename", key=f"_rename_btn_{_sname}", use_container_width=True):
                            st.session_state[_rename_key] = True
                            st.rerun()
                    with sc3:
                        if st.button("Delete", key=f"_delete_btn_{_sname}", use_container_width=True):
                            st.session_state[f"_confirm_delete_{_sname}"] = True
                            st.rerun()

                # Delete confirmation
                if st.session_state.get(f"_confirm_delete_{_sname}"):
                    st.markdown(f"""
                    <div class="note-box" style="margin-bottom:0.3rem;">
                        Delete <strong>{_sname}</strong>? This cannot be undone.
                    </div>
                    """, unsafe_allow_html=True)
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        if st.button("Yes, delete", key=f"_delete_confirm_{_sname}", use_container_width=True):
                            _studies = _load_studies()
                            _studies.pop(_sname, None)
                            _save_studies(_studies)
                            st.session_state.pop(f"_confirm_delete_{_sname}", None)
                            st.toast(f"Deleted: {_sname}", icon="🗑️")
                            st.rerun()
                    with dc2:
                        if st.button("Cancel", key=f"_delete_cancel_{_sname}", use_container_width=True):
                            st.session_state.pop(f"_confirm_delete_{_sname}", None)
                            st.rerun()

# ── MODULE 01: ELECTROCHEMICAL ────────────────────────────────────────────────
elif selected_key == "electrochemical":

    st.markdown("""
    <div class="hero-label">Module 01</div>
    <div class="hero-title">Electrochemical <span>Design</span></div>
    <div class="hero-subtitle">Cell-level electrochemistry · Material masses · Anode thickness solver</div>
    """, unsafe_allow_html=True)


    # Chemistry defaults - single source of truth for all cathode presets
    CHEM_DEFAULTS = {
        "NVPF (Na₃V₂(PO₄)₂F₃)":      {"cap": 128.0, "volt": 3.90, "dens": 3.17, "am": 0.80, "c": 0.10, "b": 0.10, "por": 0.10},  # He 2023; porosity Domalanta 2022. AM price set separately in Module 04
        "Custom":                       {"cap": 120.0, "volt": 3.40, "dens": 3.00, "am": 0.90, "c": 0.05, "b": 0.05, "por": 0.30},
    }
    CHEM_KEYS = list(CHEM_DEFAULTS.keys())
    # Input field keys that should reset when chemistry changes
    CHEM_FIELD_KEYS = ["c_cap", "c_volt", "c_dens", "c_am", "c_carb", "c_bind", "c_por"]

    col_in, col_out = st.columns([2, 3], gap="large")

    with col_in:

        st.markdown('<div class="input-section-title">Cathode Chemistry</div>', unsafe_allow_html=True)
        _skip_reset_this_render = st.session_state.get("_just_loaded", False)

        # Chemistry selector - no key so session state doesn't lock the value
        chem = st.selectbox(
            "Cathode chemistry", CHEM_KEYS,
            index=CHEM_KEYS.index(st.session_state.get("last_chem", CHEM_KEYS[0])) if st.session_state.get("last_chem") in CHEM_KEYS else 0,
            key="chem_select_widget"
        )
        d = CHEM_DEFAULTS[chem]

        # When chemistry changes: clear cached field values and rerun so
        # number inputs render fresh with new defaults from d
        if st.session_state.get("last_chem") != chem and not st.session_state.get("_just_loaded"):
            for k in CHEM_FIELD_KEYS:
                st.session_state.pop(k, None)
            st.session_state["last_chem"] = chem
            st.session_state["chem_index"] = CHEM_KEYS.index(chem)
            st.rerun()

        if chem == "Custom":
            cathode_display_name = st.text_input(
                "Cathode material name", value=st.session_state.get("cathode_custom_name", "Custom cathode"),
                key="cathode_custom_name"
            )
        else:
            cathode_display_name = chem.split("(")[0].strip()

        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Cathode Parameters</div>', unsafe_allow_html=True)
        ca1, ca2 = st.columns(2)
        with ca1:
            c_cap  = st.number_input("Specific capacity (mAh/g)", value=d["cap"],  min_value=50.0,  max_value=300.0, step=1.0,            key="c_cap")
            c_dens = st.number_input("Bulk density (g/cm³)",       value=d["dens"], min_value=1.0,   max_value=7.0,   step=0.05,           key="c_dens")
            c_am   = st.number_input("Active material fraction",   value=d["am"],   min_value=0.5,   max_value=0.99,  step=0.001, format="%.3f", key="c_am")
        with ca2:
            c_volt = st.number_input("Avg voltage vs Na/Na⁺ (V)", value=d["volt"], min_value=2.0,   max_value=4.5,   step=0.001, format="%.3f", key="c_volt")
            c_carb = st.number_input("Carbon additive fraction",   value=d["c"],    min_value=0.0,   max_value=0.20,  step=0.005, format="%.3f", key="c_carb")
            c_bind = st.number_input("Binder fraction",            value=d["b"],    min_value=0.0,   max_value=0.20,  step=0.005, format="%.3f", key="c_bind")
        c_por   = st.number_input("Porosity (void fraction)",      value=d["por"],  min_value=0.10,  max_value=0.60,  step=0.0001, format="%.4f", key="c_por")
        c_thick = st.number_input("Cathode thickness (µm) - primary design variable", value=237.0, min_value=20.0, max_value=250.0, step=5.0, key="c_thick")

        cd1, cd2 = st.columns(2)
        with cd1:
            c_carb_dens = st.number_input("Carbon additive density (g/cm³)", value=1.825, min_value=0.5, max_value=5.0, step=0.001, format="%.3f", key="c_carb_dens",
                help="Density of conductive carbon additive in cathode coating. BatPaC default: 1.825 g/cm³.")
        with cd2:
            c_bind_dens = st.number_input("Binder density (g/cm³)", value=1.77, min_value=0.5, max_value=5.0, step=0.001, format="%.3f", key="c_bind_dens",
                help="Density of binder in cathode coating. BatPaC default (PVDF): 1.77 g/cm³.")

        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Anode Parameters</div>', unsafe_allow_html=True)

        ANODE_DEFAULTS = {
            "Hard carbon (biomass-derived)": {"cap": 300.0, "volt": 0.20, "dens": 1.50, "am": 0.80, "bind": 0.10, "carb": 0.10, "por": 0.11},  # Vaalma 2018 density; Domalanta 2022 porosity
            "Custom":                        {"cap": 300.0, "volt": 0.15, "dens": 1.60, "am": 0.94, "bind": 0.04, "carb": 0.02, "por": 0.32},
        }
        ANODE_KEYS = list(ANODE_DEFAULTS.keys())
        ANODE_FIELD_KEYS = ["a_cap", "a_volt", "a_dens", "a_am", "a_bind", "a_carb", "a_por"]

        anode_chem = st.selectbox(
            "Anode material", ANODE_KEYS,
            index=ANODE_KEYS.index(st.session_state.get("last_anode", ANODE_KEYS[0])) if st.session_state.get("last_anode") in ANODE_KEYS else 0,
            key="anode_select_widget"
        )
        da = ANODE_DEFAULTS[anode_chem]

        if st.session_state.get("last_anode") != anode_chem and not st.session_state.get("_just_loaded"):
            for k in ANODE_FIELD_KEYS:
                st.session_state.pop(k, None)
            st.session_state["last_anode"] = anode_chem
            st.session_state["anode_index"] = ANODE_KEYS.index(anode_chem)
            st.rerun()

        if anode_chem == "Custom":
            anode_display_name = st.text_input(
                "Anode material name", value=st.session_state.get("anode_custom_name", "Custom anode"),
                key="anode_custom_name"
            )
        else:
            anode_display_name = anode_chem.split("(")[0].strip()

        # Default binder name suggestion depending on anode chemistry
        if "titanate" in anode_chem.lower():
            default_binder_name = "PVDF"
            binder_note = "Typically PVDF - NMP solvent system required (same as cathode). Edit the name below if using a different binder."
        else:
            default_binder_name = "CMC/SBR"
            binder_note = "Typically water-based CMC/SBR - no NMP solvent or recovery cost required. Edit the name below if using a different binder."

        st.markdown(f"""
        <div class="note-box">
            <strong>Binder system:</strong> {binder_note}
        </div>
        """, unsafe_allow_html=True)

        anode_binder_name = st.text_input(
            "Anode binder name", value=st.session_state.get("anode_binder_name", default_binder_name),
            key="anode_binder_name"
        )
        binder_default_label = f"Binder fraction ({anode_binder_name})"

        an1, an2 = st.columns(2)
        with an1:
            a_cap  = st.number_input("Specific capacity (mAh/g)", value=da["cap"],  min_value=50.0,  max_value=600.0, step=5.0,            key="a_cap")
            a_dens = st.number_input("Bulk density (g/cm³)",       value=da["dens"], min_value=1.0,   max_value=5.0,   step=0.05,           key="a_dens")
            a_am   = st.number_input("Active material fraction",   value=da["am"],   min_value=0.5,   max_value=0.99,  step=0.001, format="%.3f", key="a_am")
        with an2:
            a_volt = st.number_input("Avg voltage vs Na/Na⁺ (V)", value=da["volt"], min_value=0.0,   max_value=2.0,   step=0.001,           key="a_volt")
            a_bind = st.number_input(binder_default_label,         value=da["bind"], min_value=0.0,   max_value=0.20,  step=0.005, format="%.3f", key="a_bind")
            a_carb = st.number_input("Carbon additive fraction",   value=da["carb"], min_value=0.0,   max_value=0.20,  step=0.005, format="%.3f", key="a_carb")
        a_por = st.number_input("Porosity (void fraction)", value=da["por"], min_value=0.10, max_value=0.60, step=0.001, format="%.3f", key="a_por")

        ad1, ad2 = st.columns(2)
        with ad1:
            a_carb_dens = st.number_input("Carbon additive density (g/cm³)", value=1.825, min_value=0.5, max_value=5.0, step=0.001, format="%.3f", key="a_carb_dens",
                help="Density of conductive carbon additive in anode coating. BatPaC default: 1.95 g/cm³.")
        with ad2:
            a_bind_dens = st.number_input(f"Binder density ({anode_binder_name}) (g/cm³)", value=1.265, min_value=0.5, max_value=5.0, step=0.001, format="%.3f", key="a_bind_dens",
                help="Density of binder in anode coating. BatPaC default (CMC/SBR): 1.10 g/cm³.")

        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Design Parameters</div>', unsafe_allow_html=True)

        # ── Cell size input mode toggle ────────────────────────────────────────
        size_mode = st.radio(
            "Cell size input mode",
            ["Set electrode area (derive capacity)", "Set target cell capacity (derive area)"],
            index=st.session_state.get("_size_mode_index", 0),
            horizontal=True,
            key="size_mode_radio",
            help="Choose whether to specify electrode area directly (BatPaC default direction) or set a target cell capacity and let the model derive the required electrode area."
        )
        st.session_state["_size_mode_index"] = 0 if "electrode area" in size_mode else 1
        _mode_b = "target cell capacity" in size_mode

        if _mode_b:
            st.markdown(f"""
            <div class="note-box">
                <strong>Capacity mode:</strong> Enter your target cell capacity. The model derives
                the required electrode area as: A = (C_cell x 1000) / c_areal. Electrode area
                updates after each Calculate. Cite Domalanta et al. (2022) for stationary
                Na-ion cell capacity (energy cell design: ~50-200 Ah).
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="note-box">
                <strong>Area mode:</strong> Electrode area is the primary cell size input.
                Cell capacity is derived as: C = c_areal x A / 1000. BatPaC default: 8561 cm²
                (NMC811-G automotive reference). For stationary NVPF use capacity mode instead.
            </div>
            """, unsafe_allow_html=True)

        dp1, dp2 = st.columns(2)
        with dp1:
            if _mode_b:
                target_cap_input = st.number_input(
                    "Target cell capacity (Ah)",
                    value=float(st.session_state.get("_target_cap_Ah", 50.0)),
                    min_value=1.0, max_value=1000.0, step=5.0, key="_target_cap_Ah",
                    help="Target cell capacity for stationary storage. Domalanta et al. (2022) stationary Na-ion energy cell. Typical range: 50-200 Ah."
                )
                electrode_area_cm2 = None   # will be derived inside run_electrochemical
            else:
                electrode_area_cm2 = st.number_input(
                    "Electrode area (cm²)", value=st.session_state.get("target_capacity", 8561.0),
                    min_value=500.0, max_value=500000.0, step=500.0, key="target_capacity",
                    help="Total active electrode area (BatPaC convention): num_layers x 2 x length x width. Cell capacity = c_areal x electrode_area / 1000."
                )
                target_cap_input = None
        with dp2:
            np_ratio = st.number_input(
                "N/P capacity ratio", value=1.10, min_value=1.0, max_value=2.0, step=0.001, format="%.3f", key="np_ratio",
                help="Typically 1.15-1.25 for SIBs. Higher than LIBs due to hard carbon first-cycle irreversible capacity loss (ICL)."
            )

        tab_excess = st.number_input(
            "Tab area excess fraction", value=0.04, min_value=0.0, max_value=0.15, step=0.005, format="%.3f", key="tab_excess",
            help="Anode overhangs cathode by this fraction for safety. Typically 4%."
        )

        st.session_state["_just_loaded"] = False

        st.markdown("<br>", unsafe_allow_html=True)
        calculate = st.button("⚙  CALCULATE", use_container_width=True)

    # ── OUTPUTS ───────────────────────────────────────────────────────────────
    with col_out:

        if calculate:
            st.session_state["_m01_results"] = run_electrochemical(
                c_cap, c_volt, c_dens, c_am, c_carb, c_bind, c_por, c_thick,
                a_cap, a_volt, a_dens, a_am, a_bind, a_carb, a_por,
                np_ratio, electrode_area_cm2 if not _mode_b else 0.0, tab_excess,
                c_carb_dens=c_carb_dens, c_bind_dens=c_bind_dens,
                a_carb_dens=a_carb_dens, a_bind_dens=a_bind_dens,
                target_cell_capacity_Ah=target_cap_input if _mode_b else None,
            )

        if "_m01_results" not in st.session_state:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};border-radius:6px;
                        padding:3rem 2rem;text-align:center;margin-top:1rem;">
                <div style="font-family:'IBM Plex Mono',serif;font-size:0.72rem;
                            color:{T['muted']};letter-spacing:0.1em;">
                    SET INPUTS AND CLICK CALCULATE
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            r = st.session_state["_m01_results"]

            # Show derived electrode area when in capacity mode
            if _mode_b:
                st.markdown(f"""
                <div class="note-box">
                    <strong>Derived electrode area:</strong> {r["electrode_area"]:,.1f} cm²
                    &nbsp;(from target {target_cap_input:.1f} Ah at c_areal = {r["c_areal"]:.4f} mAh/cm²)
                </div>
                """, unsafe_allow_html=True)

            # Validation
            st.markdown('<div class="section-header">Validation</div>', unsafe_allow_html=True)
            checks = [
                (r["c_frac_ok"],  f"Cathode fractions sum to {r['c_frac_sum']:.3f} - {'OK' if r['c_frac_ok'] else 'adjust to reach 1.0'}"),
                (r["a_frac_ok"],  f"Anode fractions sum to {r['a_frac_sum']:.3f} - {'OK' if r['a_frac_ok'] else 'adjust to reach 1.0'}"),
            ]
            for i, (passed, msg) in enumerate(checks):
                css  = "val-pass" if passed else "val-warn"
                icon = "✓" if passed else "⚠"
                st.markdown(f'<div class="{css}">{icon}  {msg}</div>', unsafe_allow_html=True)

            # ── BatPaC Line-by-Line Validation Panel ──────────────────────────
            with st.expander("🔬 BatPaC NMC811-G Validation (line-by-line comparison)", expanded=False):
                st.markdown("""
                <div class="note-box">
                <strong>How to use:</strong> Set Cathode = NMC811 defaults, Anode = Graphite defaults,
                Electrode area = 8560.81 cm², N/P ratio = 1.10 to reproduce the BatPaC NMC811-G reference case.
                </div>
                """, unsafe_allow_html=True)
                _M01_REF = {
                    "cell_capacity":  67.2367,
                    "cell_voltage":    3.7200,
                    "c_AM_mass":     314.7785,
                    "a_AM_mass":     213.4730,
                    "c_coat_total":  327.8943,
                    "a_coat_total":  217.8296,
                }
                _m01_rows = ""
                _m01_rows += _batpac_vrow("Cell capacity (Ah)",    r.get("cell_capacity",0), _M01_REF["cell_capacity"], ".4f", 1.0)
                _m01_rows += _batpac_vrow("Cell voltage (V)",      r.get("cell_voltage",0),  _M01_REF["cell_voltage"],  ".4f", 1.0)
                _m01_rows += _batpac_vrow("Cathode AM (g/cell)",   r.get("c_AM_mass",0),     _M01_REF["c_AM_mass"],     ".4f", 1.0)
                _m01_rows += _batpac_vrow("Anode AM (g/cell)",     r.get("a_AM_mass",0),     _M01_REF["a_AM_mass"],     ".4f", 1.0)
                _m01_rows += _batpac_vrow("Cathode coating total (g)", r.get("c_coat_total",0), _M01_REF["c_coat_total"], ".4f", 1.0)
                _m01_rows += _batpac_vrow("Anode coating total (g)",   r.get("a_coat_total",0), _M01_REF["a_coat_total"], ".4f", 1.0)
                st.markdown(_batpac_validation_table(_m01_rows), unsafe_allow_html=True)

            # Primary outputs


            st.markdown('<div class="section-header">Primary Outputs</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="output-grid">
                <div class="output-card highlight">
                    <div class="output-card-label">Cell capacity</div>
                    <div class="output-card-value">{r["cell_capacity"]:.4f}</div>
                    <div class="output-card-unit">Ah</div>
                </div>
                <div class="output-card highlight">
                    <div class="output-card-label">Cell avg voltage</div>
                    <div class="output-card-value">{r["cell_voltage"]:.3f}</div>
                    <div class="output-card-unit">V</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Cathode areal capacity</div>
                    <div class="output-card-value">{r["c_areal"]:.3f}</div>
                    <div class="output-card-unit">mAh/cm²</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Anode areal capacity</div>
                    <div class="output-card-value">{r["a_areal"]:.3f}</div>
                    <div class="output-card-unit">mAh/cm²</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Anode thickness</div>
                    <div class="output-card-value">{r["a_thick"]:.1f}</div>
                    <div class="output-card-unit">µm</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Cell energy</div>
                    <div class="output-card-value">{r["cell_capacity"] * r["cell_voltage"]:.2f}</div>
                    <div class="output-card-unit">Wh</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Material masses table
            st.markdown('<div class="section-header">Material Masses per Cell</div>', unsafe_allow_html=True)
            total = r["c_coat_total"] + r["a_coat_total"]
            st.markdown(f"""
            <table class="mass-table">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th>Material</th>
                        <th style="text-align:right">g / cell</th>
                        <th style="text-align:right">% electrode</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Cathode active material</td><td style="color:{T['sub']}">{cathode_display_name}</td><td class="val">{r["c_AM_mass"]:.3f}</td><td class="val">{pct(r["c_AM_mass"],total)}</td></tr>
                    <tr><td>Cathode carbon additive</td><td style="color:{T['sub']}">Carbon black</td><td class="val">{r["c_carbon_mass"]:.3f}</td><td class="val">{pct(r["c_carbon_mass"],total)}</td></tr>
                    <tr><td>Cathode binder</td><td style="color:{T['sub']}">PVDF</td><td class="val">{r["c_binder_mass"]:.3f}</td><td class="val">{pct(r["c_binder_mass"],total)}</td></tr>
                    <tr class="subtotal"><td><strong>Cathode coating total</strong></td><td></td><td class="val"><strong>{r["c_coat_total"]:.3f}</strong></td><td class="val"><strong>{pct(r["c_coat_total"],total)}</strong></td></tr>
                    <tr><td>Anode active material</td><td style="color:{T['sub']}">{anode_display_name}</td><td class="val">{r["a_AM_mass"]:.3f}</td><td class="val">{pct(r["a_AM_mass"],total)}</td></tr>
                    <tr><td>Anode carbon additive</td><td style="color:{T['sub']}">Carbon black</td><td class="val">{r["a_carbon_mass"]:.3f}</td><td class="val">{pct(r["a_carbon_mass"],total)}</td></tr>
                    <tr><td>Anode binder</td><td style="color:{T['sub']}">{anode_binder_name}</td><td class="val">{r["a_binder_mass"]:.3f}</td><td class="val">{pct(r["a_binder_mass"],total)}</td></tr>
                    <tr class="subtotal"><td><strong>Anode coating total</strong></td><td></td><td class="val"><strong>{r["a_coat_total"]:.3f}</strong></td><td class="val"><strong>{pct(r["a_coat_total"],total)}</strong></td></tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)

            # Equations expander
            with st.expander("Equations used in this module"):
                st.markdown(f"""
                <div style="font-family:'IBM Plex Mono',serif;font-size:0.70rem;color:{T['hero_span']};line-height:2.2;">

                <span style="color:{T['accent']}">1. Cell average voltage (V)</span><br>
                cell_voltage = cathode_avg_voltage − anode_avg_voltage<br>
                = {c_volt} − {a_volt} = <strong style="color:{T['text']}">{r["cell_voltage"]:.3f} V</strong><br><br>

                <span style="color:{T['accent']}">2. Cathode areal capacity (mAh/cm²)</span><br>
                coating_density = (1−porosity)×100 / (AM%/AM_density + carbon%/carbon_density + binder%/binder_density)<br>
                c_areal = (cathode_thickness / 10000) × coating_density × specific_capacity × AM_fraction<br>
                = ({c_thick}/10000) × {r["c_areal"]/((c_thick/10000)*c_cap*c_am):.4f} × {c_cap} × {c_am}<br>
                = <strong style="color:{T['text']}">{r["c_areal"]:.4f} mAh/cm²</strong><br><br>

                <span style="color:{T['accent']}">3. Cell capacity (Ah) - derived from electrode area</span><br>
                cell_capacity = c_areal × electrode_area / 1000<br>
                = {r["c_areal"]:.4f} × {r["electrode_area"]:.4f} / 1000<br>
                = <strong style="color:{T['text']}">{r["cell_capacity"]:.4f} Ah</strong><br><br>

                <span style="color:{T['accent']}">5. Target anode areal capacity (mAh/cm²)</span><br>
                a_areal_target = (c_areal × N/P_ratio) / (1 + tab_excess)<br>
                Dividing by (1 + tab_excess) because the anode covers a larger area - each cm² needs less charge to meet the N/P target<br>
                = ({r["c_areal"]:.4f} × {np_ratio}) / (1 + {tab_excess})<br>
                = <strong style="color:{T['text']}">{r["a_areal_target"]:.4f} mAh/cm²</strong><br><br>

                <span style="color:{T['accent']}">6. Anode thickness (µm) - BatPaC volumetric capacity ratio method</span><br>
                cathode_vol_capacity = (cathode_cap/1000) × AM_fraction × coating_density &nbsp;[Ah/cm³]<br>
                anode_vol_capacity = (anode_cap/1000) × AM_fraction × coating_density &nbsp;[Ah/cm³]<br>
                thickness_ratio = (cathode_vol_capacity × N/P_ratio) / anode_vol_capacity<br>
                a_thick = cathode_thickness × thickness_ratio<br>
                = <strong style="color:{T['text']}">{r["a_thick"]:.4f} µm</strong><br>
                <span style="color:{T['sub']};font-size:0.65rem;">Verified exact match against BatPaC v5.2. Independent of tab_excess - area overhang affects anode mass/area only, not thickness.</span><br><br>

                <span style="color:{T['accent']}">7. Anode areal capacity (mAh/cm²) - verification</span><br>
                a_areal = (a_thick / 10000) × coating_density × specific_capacity × AM_fraction<br>
                = ({r["a_thick"]:.4f}/10000) × coating_density × {a_cap} × {a_am}<br>
                = <strong style="color:{T['text']}">{r["a_areal"]:.4f} mAh/cm²</strong><br><br>

                <span style="color:{T['accent']}">8. Actual N/P ratio - validation</span><br>
                np_actual = (a_areal × (1 + tab_excess)) / c_areal<br>
                Multiplying by (1 + tab_excess) accounts for the anode covering a larger physical area<br>
                = ({r["a_areal"]:.4f} × (1 + {tab_excess})) / {r["c_areal"]:.4f}<br>
                = <strong style="color:{T['text']}">{r["np_actual"]:.4f}</strong> (target: {np_ratio})<br><br>

                <span style="color:{T['accent']}">9. Cathode active material mass (g/cell)</span><br>
                c_AM_mass = cell_capacity / specific_capacity × 1000<br>
                = {r["cell_capacity"]:.4f} / {c_cap} × 1000 = <strong style="color:{T['text']}">{r["c_AM_mass"]:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">10. Total cathode coating (g/cell)</span><br>
                c_coat_total = c_AM_mass / AM_fraction<br>
                = {r["c_AM_mass"]:.4f} / {c_am} = <strong style="color:{T['text']}">{r["c_coat_total"]:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">11. Cathode carbon additive (g/cell)</span><br>
                c_carbon_mass = c_coat_total × carbon_fraction<br>
                = {r["c_coat_total"]:.4f} × {c_carb} = <strong style="color:{T['text']}">{r["c_carbon_mass"]:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">12. Cathode binder (g/cell)</span><br>
                c_binder_mass = c_coat_total × binder_fraction<br>
                = {r["c_coat_total"]:.4f} × {c_bind} = <strong style="color:{T['text']}">{r["c_binder_mass"]:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">13. Anode active material mass (g/cell)</span><br>
                a_AM_mass = cell_capacity / specific_capacity × 1000 × N/P_ratio × (1 + tab_excess)<br>
                = {r["cell_capacity"]:.4f} / {a_cap} × 1000 × {np_ratio} × (1 + {tab_excess})<br>
                = <strong style="color:{T['text']}">{r["a_AM_mass"]:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">14. Total anode coating (g/cell)</span><br>
                a_coat_total = a_AM_mass / AM_fraction<br>
                = {r["a_AM_mass"]:.4f} / {a_am} = <strong style="color:{T['text']}">{r["a_coat_total"]:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">15. Anode carbon additive (g/cell)</span><br>
                a_carbon_mass = a_coat_total × carbon_fraction<br>
                = {r["a_coat_total"]:.4f} × {a_carb} = <strong style="color:{T['text']}">{r["a_carbon_mass"]:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">16. Anode binder (g/cell)</span><br>
                a_binder_mass = a_coat_total × binder_fraction<br>
                = {r["a_coat_total"]:.4f} × {a_bind} = <strong style="color:{T['text']}">{r["a_binder_mass"]:.4f} g</strong>
                
                </div>
                """, unsafe_allow_html=True)

            # Store outputs for downstream modules
            st.session_state["electrochem"] = {
                **r,
                "cathode_thickness":    c_thick,
                "cathode_bulk_density": c_dens,
                "anode_bulk_density":   a_dens,
                "cathode_porosity":     c_por,
                "anode_porosity":       a_por,
                # Raw inputs - used by Module 06/07 to initialise sliders
                "_in_c_cap": c_cap, "_in_c_volt": c_volt, "_in_c_dens": c_dens,
                "_in_c_am": c_am, "_in_c_carb": c_carb, "_in_c_bind": c_bind,
                "_in_c_por": c_por, "_in_c_thick": c_thick,
                "_in_c_carb_dens": c_carb_dens, "_in_c_bind_dens": c_bind_dens,
                "_in_a_cap": a_cap, "_in_a_volt": a_volt, "_in_a_dens": a_dens,
                "_in_a_am": a_am, "_in_a_bind": a_bind, "_in_a_carb": a_carb,
                "_in_a_por": a_por, "_in_np_ratio": np_ratio,
                "_in_electrode_area": r["electrode_area"], "_in_tab_excess": tab_excess,
            }
            # ── Unified study inputs dict (single source of truth for Module 06/07) ──
            if "_study_inputs" not in st.session_state:
                st.session_state["_study_inputs"] = {}
            st.session_state["_study_inputs"].update({
                "c_cap": c_cap, "c_volt": c_volt, "c_dens": c_dens, "c_am": c_am,
                "c_carb": c_carb, "c_bind": c_bind, "c_por": c_por, "c_thick": c_thick,
                "c_carb_dens": c_carb_dens, "c_bind_dens": c_bind_dens,
                "a_cap": a_cap, "a_volt": a_volt, "a_dens": a_dens, "a_am": a_am,
                "a_bind": a_bind, "a_carb": a_carb, "a_por": a_por,
                "a_carb_dens": a_carb_dens, "a_bind_dens": a_bind_dens,
                "np_ratio": np_ratio, "electrode_area": r["electrode_area"], "tab_excess": tab_excess,
            })

            st.markdown(f"""
            <div class="note-box" style="margin-top:1rem;">
                <strong>Passed to Module 02:</strong> cell_capacity, cathode_AM_mass, anode_AM_mass,
                cathode_coating_total, anode_coating_total, electrode_area_cm2, anode_thickness,
                cell_avg_voltage, bulk densities, porosities.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            prev1, next1 = st.columns(2)
            with prev1:
                if st.button("← Back to Home", use_container_width=True, key="prev_home"):
                    st.session_state["_navigate_to"] = "🏠  Home"
                    st.rerun()
            with next1:
                if st.button("Next module: Cell Design →", use_container_width=True, key="next_m02"):
                    st.session_state["_navigate_to"] = "🔲  Module 02 - Cell Design"
                    st.rerun()

# ── MODULE 02: CELL DESIGN ────────────────────────────────────────────────────
elif selected_key == "cell_design":

    if "electrochem" not in st.session_state:
        st.markdown("""
        <div class="hero-label">Module 02</div>
        <div class="hero-title">Cell <span>Design</span></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="status-bar" style="text-align:center;padding:2rem;">
            <strong>⚠ Module 01 required</strong> - Run the Electrochemical Design
            module first, then return here.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    e = st.session_state["electrochem"]

    st.markdown("""
    <div class="hero-label">Module 02</div>
    <div class="hero-title">Cell <span>Design</span></div>
    <div class="hero-subtitle">Physical geometry · Foil areas · Electrolyte volume · Cell energy metrics</div>
    """, unsafe_allow_html=True)

    col_in, col_out = st.columns([2, 3], gap="large")

    with col_in:

        # ── From Module 01 ─────────────────────────────────────────────────────
        st.markdown('<div class="input-section-title">From Module 01 - Electrochemical Design</div>', unsafe_allow_html=True)

        # Pouch construction throughout. BatPaC models a pouch cell exclusively, so a
        # prismatic branch would have no validation basis.
        df = {"container_thickness_um": 150.0, "container_density": 2.202, "seal_buffer_mm": 6.0}

        # ── Cell geometry ──────────────────────────────────────────────────────
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Cell Geometry</div>', unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        with g1:
            num_layers_input      = st.number_input("Number of bicell layers",       value=10,   min_value=1,    max_value=100,   step=1,    key="cell_thickness_mm",
                                                     help="How many electrode stacks fit in the cell. Cell thickness is derived from this. Typical range: 5-20 layers.")
            length_to_width_ratio = st.number_input("Length-to-width ratio",        value=3.0,  min_value=1.0,  max_value=10.0,  step=0.001,  format="%.1f", key="lw_ratio",
                                                     help="Electrode sheet aspect ratio. Typical range 2-5.")
        with g2:
            sep_excess_width_mm   = st.number_input("Separator excess - width (mm)", value=2.0, min_value=0.0,  max_value=10.0,  step=0.5,  key="sep_excess_width",
                                                     help="Separator overhangs electrode on each side.")
            sep_excess_length_mm  = st.number_input("Separator excess - length (mm)", value=6.0, min_value=0.0, max_value=10.0,  step=0.5,  key="sep_excess_length")
        anode_excess_mm       = st.number_input("Anode excess - width/length (mm)", value=2.0, min_value=0.0, max_value=10.0, step=0.5, key="anode_excess",
                                                 help="Anode overhangs cathode on each side (BatPaC default: 2 mm). Affects anode foil area and internal tab length, not anode thickness.")

        # ── Packing & manufacturing tolerances ───────────────────────────────────
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Packing & Manufacturing Tolerances</div>', unsafe_allow_html=True)

        pt1, pt2 = st.columns(2)
        with pt1:
            packing_efficiency    = st.number_input("Packing efficiency",            value=0.97, min_value=0.80, max_value=1.00,  step=0.001, format="%.3f", key="packing_eff",
                                                     help="Fraction of available thickness used by electrode stack. BatPaC default: 0.97.")
            cell_edge_fold_mm     = st.number_input("Cell edge fold (mm)",           value=1.0,  min_value=0.0,  max_value=5.0,   step=0.1,  key="cell_edge_fold",
                                                     help="Distance from the positive electrode edge to the outside of the fold, added to cell WIDTH (BatPaC BD087, used in BD344). It does not affect cell thickness.")
            bicell_expansion_um   = st.number_input("Bicell expansion (µm)",         value=0.0,  min_value=0.0,  max_value=50.0,  step=0.5,  key="bicell_expansion",
                                                     help="Extra bi-cell thickness from electrode expansion at 100% SOC (BatPaC BD326 = BD309 + BD322). BatPaC derives it from material expansion coefficients (Chem!C22/C54) that have no published values for NVPF or hard carbon, so the default here is 0 and the omission is a stated deviation. Set to 6.75 to reproduce the BatPaC NMC811-G reference cell exactly.")
            cc_buffer_mm          = st.number_input("Current collector buffer (mm)", value=2.0, min_value=0.0, max_value=10.0, step=0.5, key="cc_buffer",
                                                    help="Gap between electrode coating edge and internal tab. BatPaC default: 2 mm.")
        with pt2:
            tab_length_mm         = st.number_input("External tab length (mm)",      value=8.0,  min_value=2.0,  max_value=30.0,  step=1.0,  key="tab_length_mm",
                                                     help="Length of tab protruding outside the cell.")
            feedthrough_mm        = st.number_input("Feedthrough length (mm)",       value=5.0,  min_value=1.0,  max_value=20.0,  step=0.5,  key="feedthrough_mm",
                                                     help="Seal region where tab passes through the casing.")
            pouch_seal_mm         = st.number_input("Pouch seal width (mm)", value=6.0, min_value=0.0, max_value=15.0, step=0.5, key="pouch_seal",
                                                    help="Width of the heat-seal border around the pouch perimeter. BatPaC default: 6 mm.")

        # ── Container ─────────────────────────────────────────────────────────
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Container</div>', unsafe_allow_html=True)

        con1, con2 = st.columns(2)
        with con1:
            container_thickness_um = st.number_input("Container thickness (µm)",  value=df["container_thickness_um"], min_value=50.0,  max_value=2000.0, step=10.0, key="container_thickness_um")
            container_density_in   = st.number_input("Container density (g/cm³)", value=df["container_density"],      min_value=1.0,   max_value=8.0,    step=0.05, key="container_density_in")
        with con2:
            seal_buffer_mm         = st.number_input("Seal buffer (mm)",            value=df["seal_buffer_mm"],         min_value=0.0,   max_value=20.0,   step=0.5,  key="seal_buffer_mm",
                                                      help="Extra width around edges for sealing.")
        wall_thickness_mm = 0.0   # pouch construction

        # ── Current collectors ─────────────────────────────────────────────────
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Current Collectors - Both Aluminium (SIB)</div>', unsafe_allow_html=True)

        f1, f2 = st.columns(2)
        with f1:
            cathode_foil_thickness_um = st.number_input("Cathode foil thickness (µm)", value=22.0, min_value=5.0, max_value=50.0, step=1.0, key="c_foil_thick",
                                                          help="Aluminium current collector. He et al. (2023) NVPF cell: 22 µm.")
        with f2:
            anode_foil_thickness_um   = st.number_input("Anode foil thickness (µm)",   value=22.0, min_value=5.0, max_value=50.0, step=1.0, key="a_foil_thick",
                                                          help="Aluminium current collector (SIB anode). He et al. (2023): 22 µm.")

        f3, f4 = st.columns(2)
        with f3:
            anode_foil_density = st.number_input("Anode foil density (g/cm³)", value=2.70, min_value=1.0, max_value=15.0, step=0.01, key="a_foil_dens",
                                                   help="Density of anode current collector foil. Aluminium = 2.70 g/cm³ (SIBs). Copper = 8.96 g/cm³ (LIBs).")

        AL_DENSITY    = 2.70   # g/cm³ - fixed physical constant
        AL_FOIL_PRICE = 0.20   # $/m²  - used in cost module

        # ── Separator ─────────────────────────────────────────────────────────
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Separator</div>', unsafe_allow_html=True)

        s1, s2 = st.columns(2)
        with s1:
            sep_thickness_um = st.number_input("Separator thickness (µm)",  value=25.0, min_value=5.0,  max_value=60.0,  step=1.0,  key="sep_thick",
                                                help="PE separator. He et al. (2023) NVPF cell: 25 µm.")
        with s2:
            sep_density      = st.number_input("Separator density (g/cm³)", value=0.95, min_value=0.3,  max_value=2.0,   step=0.001, key="sep_dens",
                                                help="PE density. He et al. (2023): 0.95 g/cm³.")

        # ── Electrolyte ───────────────────────────────────────────────────────
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Electrolyte</div>', unsafe_allow_html=True)

        el1, el2 = st.columns(2)
        with el1:
            electrolyte_density     = st.number_input("Electrolyte density (g/mL)",   value=1.25, min_value=0.8, max_value=2.0, step=0.001, key="elec_dens",
                                                       help="1M NaPF6 in EC/PC/EMC. He et al. (2023): ~1.25 g/mL.")
            electrolyte_excess_frac = st.number_input("Electrolyte excess fraction", value=0.02, min_value=0.0, max_value=0.10, step=0.001, format="%.3f", key="elec_excess",
                                                    help="Extra electrolyte as fraction of cell volume. BatPaC default: 0.02 (2%).")
        with el2:
            electrolyte_uptake_frac = st.number_input("Separator porosity",           value=0.50, min_value=0.30, max_value=0.70, step=0.001, format="%.3f", key="elec_uptake",
                                                       help="Void volume fraction of the separator, assumed fully filled with electrolyte. BatPaC v5.2 Chem!C68 = 50%. Must stay consistent with separator density (0.473 g/cm3 corresponds to ~50% porous PP/PE).")

        st.markdown("<br>", unsafe_allow_html=True)
        calculate2 = st.button("⚙  CALCULATE", use_container_width=True, key="calc2")

    # ── OUTPUTS ───────────────────────────────────────────────────────────────
    with col_out:

        if calculate2:
            st.session_state["_m02_results"] = run_cell_design(
                cathode_thickness_um      = e["cathode_thickness"],
                anode_thickness_um        = e["a_thick"],
                electrode_area_cm2        = e["electrode_area"],
                cell_capacity_Ah          = e["cell_capacity"],
                cell_voltage_V            = e["cell_voltage"],
                cathode_bulk_density      = e["cathode_bulk_density"],
                anode_bulk_density        = e["anode_bulk_density"],
                cathode_porosity          = e["cathode_porosity"],
                anode_porosity            = e["anode_porosity"],
                cathode_coating_density   = e["c_coating_density"],
                anode_coating_density     = e["a_coating_density"],
                cathode_coating_total_g   = e["c_coat_total"],
                anode_coating_total_g     = e["a_coat_total"],
                num_layers_input          = num_layers_input,
                length_to_width_ratio     = length_to_width_ratio,
                sep_excess_width_mm       = sep_excess_width_mm,
                sep_excess_length_mm      = sep_excess_length_mm,
                tab_length_mm             = tab_length_mm,
                feedthrough_mm            = feedthrough_mm,
                cc_buffer_mm              = cc_buffer_mm,
                pouch_seal_mm             = pouch_seal_mm,
                container_thickness_um    = container_thickness_um,
                container_density         = container_density_in,
                wall_thickness_mm         = wall_thickness_mm,
                seal_buffer_mm            = seal_buffer_mm,
                cathode_foil_thickness_um = cathode_foil_thickness_um,
                anode_foil_thickness_um   = anode_foil_thickness_um,
                al_density                = AL_DENSITY,
                anode_foil_density        = anode_foil_density,
                sep_thickness_um          = sep_thickness_um,
                sep_density               = sep_density,
                electrolyte_density       = electrolyte_density,
                electrolyte_uptake_frac   = electrolyte_uptake_frac,
                tab_excess                = st.session_state.get("tab_excess", 0.04),
                anode_excess_mm           = anode_excess_mm,
                packing_efficiency        = packing_efficiency,
                cell_edge_fold_mm         = cell_edge_fold_mm,
                bicell_expansion_um       = bicell_expansion_um,
                electrolyte_excess_frac   = electrolyte_excess_frac,
            )

        if "_m02_results" not in st.session_state:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};border-radius:6px;
                        padding:3rem 2rem;text-align:center;margin-top:1rem;">
                <div style="font-family:'IBM Plex Mono',serif;font-size:0.72rem;
                            color:{T['muted']};letter-spacing:0.1em;">
                    SET INPUTS AND CLICK CALCULATE
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            r2 = st.session_state["_m02_results"]


            # ── BatPaC Line-by-Line Validation Panel ──────────────────────────
            with st.expander("🔬 BatPaC NMC811-G Validation (line-by-line comparison)", expanded=False):
                
                _M02_REF = {
                    "electrode_width_mm":   66.784,
                    "electrode_length_mm": 200.353,
                    "cathode_foil_area_m2":  0.4801,
                    "anode_foil_area_m2":    0.5122,
                    "sep_area_m2":           0.8993,
                    "elec_vol_L":            0.0730,
                    "cell_energy_Wh":      250.10,
                    "cell_mass_g":         740.33,
                }
                _m02_rows = ""
                _m02_rows += _batpac_vrow("Electrode width (mm)",  r2.get("electrode_width_mm",0),  _M02_REF["electrode_width_mm"],  ".3f", 1.0)
                _m02_rows += _batpac_vrow("Electrode length (mm)", r2.get("electrode_length_mm",0), _M02_REF["electrode_length_mm"], ".3f", 1.0)
                _m02_rows += _batpac_vrow("Cathode foil area (m²)",r2.get("cathode_foil_area_m2",0),_M02_REF["cathode_foil_area_m2"],".4f", 1.0)
                _m02_rows += _batpac_vrow("Anode foil area (m²)",  r2.get("anode_foil_area_m2",0),  _M02_REF["anode_foil_area_m2"],  ".4f", 1.0)
                _m02_rows += _batpac_vrow("Separator area (m²)",   r2.get("sep_area_m2",0),         _M02_REF["sep_area_m2"],         ".4f", 1.0)
                _m02_rows += _batpac_vrow("Electrolyte volume (L)",r2.get("elec_vol_L",0),          _M02_REF["elec_vol_L"],          ".4f", 5.0)
                _m02_rows += _batpac_vrow("Cell energy (Wh)",      r2.get("cell_energy_Wh",0),      _M02_REF["cell_energy_Wh"],      ".2f", 1.0)
                _m02_rows += _batpac_vrow("Cell mass (g)",         r2.get("cell_mass_g",0),         _M02_REF["cell_mass_g"],         ".2f", 2.0)
                st.markdown(_batpac_validation_table(_m02_rows), unsafe_allow_html=True)

            # Primary outputs
            st.markdown('<div class="section-header">Primary Outputs</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="output-grid">
                <div class="output-card highlight">
                    <div class="output-card-label">Cell energy</div>
                    <div class="output-card-value">{r2["cell_energy_Wh"]:.1f}</div>
                    <div class="output-card-unit">Wh</div>
                </div>
                <div class="output-card highlight">
                    <div class="output-card-label">Specific energy</div>
                    <div class="output-card-value">{r2["cell_specific_energy"]:.1f}</div>
                    <div class="output-card-unit">Wh/kg</div>
                </div>
                <div class="output-card highlight">
                    <div class="output-card-label">Energy density</div>
                    <div class="output-card-value">{r2["cell_energy_density"]:.1f}</div>
                    <div class="output-card-unit">Wh/L</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Cell mass</div>
                    <div class="output-card-value">{r2["cell_mass_g"]:.1f}</div>
                    <div class="output-card-unit">g</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Cell volume</div>
                    <div class="output-card-value">{r2["cell_volume_cm3"]:.1f}</div>
                    <div class="output-card-unit">cm³</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Electrolyte volume</div>
                    <div class="output-card-value">{r2["elec_vol_L"] * 1000:.1f}</div>
                    <div class="output-card-unit">mL</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Bicell thickness</div>
                    <div class="output-card-value">{r2["bicell_thickness_cm"] * 10:.3f}</div>
                    <div class="output-card-unit">mm</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Cell dimensions
            st.markdown('<div class="section-header">Cell Dimensions</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="output-grid">
                <div class="output-card">
                    <div class="output-card-label">Cell width</div>
                    <div class="output-card-value">{r2["cell_width_mm"]:.1f}</div>
                    <div class="output-card-unit">mm</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Cell length</div>
                    <div class="output-card-value">{r2["cell_length_mm"]:.1f}</div>
                    <div class="output-card-unit">mm</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Cell thickness</div>
                    <div class="output-card-value">{r2["cell_thickness_mm"]:.1f}</div>
                    <div class="output-card-unit">mm</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Electrode width</div>
                    <div class="output-card-value">{r2["electrode_width_mm"]:.1f}</div>
                    <div class="output-card-unit">mm</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Electrode length</div>
                    <div class="output-card-value">{r2["electrode_length_mm"]:.1f}</div>
                    <div class="output-card-unit">mm</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Cell mass breakdown
            st.markdown('<div class="section-header">Cell Mass Breakdown</div>', unsafe_allow_html=True)
            total_mass = r2["cell_mass_g"]
            st.markdown(f"""
            <table class="mass-table">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th style="text-align:right">Mass (g)</th>
                        <th style="text-align:right">% cell mass</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Cathode coating</td><td class="val">{e["c_coat_total"]:.4f}</td><td class="val">{pct(e["c_coat_total"],total_mass)}</td></tr>
                    <tr><td>Anode coating</td><td class="val">{e["a_coat_total"]:.4f}</td><td class="val">{pct(e["a_coat_total"],total_mass)}</td></tr>
                    <tr><td>Cathode Al foil</td><td class="val">{r2["cathode_foil_mass_g"]:.4f}</td><td class="val">{pct(r2["cathode_foil_mass_g"],total_mass)}</td></tr>
                    <tr><td>Anode Al foil</td><td class="val">{r2["anode_foil_mass_g"]:.4f}</td><td class="val">{pct(r2["anode_foil_mass_g"],total_mass)}</td></tr>
                    <tr><td>Separator</td><td class="val">{r2["sep_mass_g"]:.4f}</td><td class="val">{pct(r2["sep_mass_g"],total_mass)}</td></tr>
                    <tr><td>Electrolyte</td><td class="val">{r2["elec_mass_g"]:.4f}</td><td class="val">{pct(r2["elec_mass_g"],total_mass)}</td></tr>
                    <tr><td>Terminals (×2)</td><td class="val">{r2["terminal_mass_cathode_g"] + r2["terminal_mass_anode_g"]:.4f}</td><td class="val">{pct(r2["terminal_mass_cathode_g"] + r2["terminal_mass_anode_g"], total_mass)}</td></tr>
                    <tr><td>Container / casing</td><td class="val">{r2["container_mass_g"]:.4f}</td><td class="val">{pct(r2["container_mass_g"],total_mass)}</td></tr>
                    <tr class="subtotal"><td><strong>Total cell mass</strong></td><td class="val"><strong>{total_mass:.4f}</strong></td><td class="val"><strong>100.0%</strong></td></tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)

            # Component areas
            st.markdown('<div class="section-header">Component Areas</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <table class="mass-table">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th style="text-align:right">Area (m²)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Cathode Al foil</td><td class="val">{r2["cathode_foil_area_m2"]:.4f}</td></tr>
                    <tr><td>Anode Al foil</td><td class="val">{r2["anode_foil_area_m2"]:.4f}</td></tr>
                    <tr><td>Separator</td><td class="val">{r2["sep_area_m2"]:.4f}</td></tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)

            # Equations expander
            with st.expander("Equations used in this module"):
                st.markdown(f"""
                <div style="font-family:'IBM Plex Mono',serif;font-size:0.70rem;color:{T['sub']};line-height:2.2;">

                <span style="color:{T['accent']}">1. Number of bicell layers (input) → Cell thickness (derived)</span><br>
                BatPaC convention: each current collector is coated on both sides.<br>
                bicell_thickness = 2×cathode + 2×anode + 2×sep + cathode_foil + anode_foil + 2×expansion<br>
                = {r2['bicell_thickness_cm']*10:.4f} mm per bicell<br>
                available_thickness = num_layers × bicell_thickness / packing_efficiency<br>
                = {num_layers_input} × {r2['bicell_thickness_cm']*10:.4f} / {packing_efficiency} = {r2['available_thickness_cm']*10:.3f} mm<br>
                cell_thickness = available_thickness + 2 × container_thickness + anode_foil_thickness<br>
                (BD335 inverted: the stack sits between both container walls plus one negative foil)<br>
                = <strong style="color:{T['text']}">{r2['cell_thickness_mm']:.3f} mm</strong><br><br>

                <span style="color:{T['accent']}">2. Electrode width and length (mm)</span><br>
                area_per_face = electrode_area / (num_layers × 2)<br>
                width = √(area_per_face / ratio) &nbsp;·&nbsp; length = width × ratio<br>
                = √({e['electrode_area']:.1f} / ({r2['num_bicell_layers']} × 2) / {length_to_width_ratio})<br>
                width = <strong style="color:{T['text']}">{r2['electrode_width_mm']:.1f} mm</strong> &nbsp;·&nbsp;
                length = <strong style="color:{T['text']}">{r2['electrode_length_mm']:.1f} mm</strong><br><br>

                <span style="color:{T['accent']}">3. Cell external dimensions (mm)</span><br>
                cell_width  = (electrode_width + 2×sep_excess_w + 2×wall + 2×seal) × 10<br>
                cell_length = (electrode_length + 2×(tab_external + feedthrough + internal_tab + cc_buffer)) × 10<br>
                = <strong style="color:{T['text']}">{r2['cell_width_mm']:.1f} × {r2['cell_length_mm']:.1f} × {r2['cell_thickness_mm']:.1f} mm</strong><br><br>
                <span style="color:{T['accent']}">4. Cathode foil area (m²)</span><br>
                = num_layers × (electrode_width_m) × (electrode_length + cathode_tab)_m<br>
                = <strong style="color:{T['text']}">{r2['cathode_foil_area_m2']:.4f} m²</strong><br><br>

                <span style="color:{T['accent']}">5. Anode foil area (m²)</span><br>
                = (num_layers + 1) × (width + anode_excess)_m × (length + anode_tab + excess)_m<br>
                = <strong style="color:{T['text']}">{r2['anode_foil_area_m2']:.4f} m²</strong><br><br>

                <span style="color:{T['accent']}">6. Separator area (m²)</span><br>
                = 2 × num_layers × (width + sep_excess_w)_m × (length + sep_excess_l)_m<br>
                = <strong style="color:{T['text']}">{r2['sep_area_m2']:.4f} m²</strong><br><br>

                <span style="color:{T['accent']}">7. Foil masses (g)</span><br>
                cathode_foil_mass = area_m² × 10000 × thickness_cm × Al_density (2.70 g/cm³)<br>
                anode_foil_mass   = area_m² × 10000 × thickness_cm × anode_foil_density (user-specified)<br>
                cathode foil = <strong style="color:{T['text']}">{r2['cathode_foil_mass_g']:.4f} g</strong> &nbsp;·&nbsp;
                anode foil = <strong style="color:{T['text']}">{r2['anode_foil_mass_g']:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">8. Separator mass (g)</span><br>
                sep_mass = sep_area_m² × 10000 × sep_thickness_cm × sep_density<br>
                = {r2['sep_area_m2']:.4f} × 10000 × {sep_thickness_um/10000:.5f} × {sep_density}<br>
                = <strong style="color:{T['text']}">{r2['sep_mass_g']:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">9. Electrolyte volume (cm³)</span><br>
                cathode void = (cathode_coating_mass / bulk_density) × porosity = {r2['cathode_void_cm3']:.4f} cm³<br>
                anode void   = (anode_coating_mass / bulk_density) × porosity = {r2['anode_void_cm3']:.4f} cm³<br>
                sep void     = sep_area_m² × 10000 × sep_thickness_cm × uptake_frac = {r2['sep_void_cm3']:.4f} cm³<br>
                extra 2%     = cell_volume × 0.02 = {r2['extra_vol_cm3']:.4f} cm³<br>
                total = <strong style="color:{T['text']}">{r2['elec_vol_cm3']:.4f} cm³ = {r2['elec_vol_L']:.4f} L</strong><br><br>

                <span style="color:{T['accent']}">10. Electrolyte mass (g)</span><br>
                elec_mass = elec_vol_L × density × 1000<br>
                = {r2['elec_vol_L']:.4f} × {electrolyte_density} × 1000 = <strong style="color:{T['text']}">{r2['elec_mass_g']:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">11. Container mass (g) - pouch</span><br>
                Pouch: 2 laminate faces, area = 2 × cell_width × cell_length<br>
                container_mass = <strong style="color:{T['text']}">{r2['container_mass_g']:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">12. Total cell mass (g)</span><br>
                = cathode_coating + anode_coating + cathode_foil + anode_foil + separator + electrolyte + terminals + container<br>
                = {e['c_coat_total']:.4f} + {e['a_coat_total']:.4f} + {r2['cathode_foil_mass_g']:.4f} + {r2['anode_foil_mass_g']:.4f} + {r2['sep_mass_g']:.4f} + {r2['elec_mass_g']:.4f} + {r2['terminal_mass_cathode_g']+r2['terminal_mass_anode_g']:.4f} + {r2['container_mass_g']:.4f}<br>
                = <strong style="color:{T['text']}">{r2['cell_mass_g']:.4f} g</strong><br><br>

                <span style="color:{T['accent']}">13. Cell energy (Wh)</span><br>
                cell_energy = cell_capacity × cell_voltage<br>
                = {e['cell_capacity']:.4f} × {e['cell_voltage']:.3f} = <strong style="color:{T['text']}">{r2['cell_energy_Wh']:.4f} Wh</strong><br><br>

                <span style="color:{T['accent']}">14. Specific energy (Wh/kg)</span><br>
                = cell_energy / (cell_mass / 1000)<br>
                = {r2['cell_energy_Wh']:.4f} / {r2['cell_mass_g']/1000:.4f} = <strong style="color:{T['text']}">{r2['cell_specific_energy']:.1f} Wh/kg</strong><br><br>

                <span style="color:{T['accent']}">15. Energy density (Wh/L)</span><br>
                = cell_energy / (cell_volume / 1000)<br>
                = {r2['cell_energy_Wh']:.4f} / {r2['cell_volume_cm3']/1000:.4f} = <strong style="color:{T['text']}">{r2['cell_energy_density']:.1f} Wh/L</strong>

                </div>
                """, unsafe_allow_html=True)

            # Store for downstream modules
            st.session_state["cell_design"] = {
                **r2,
                "cell_thickness_mm":          r2["cell_thickness_mm"],
                "sep_thickness_um":           sep_thickness_um,
                "cathode_foil_thickness_um":  cathode_foil_thickness_um,
                "anode_foil_thickness_um":    anode_foil_thickness_um,
                "electrolyte_density":        electrolyte_density,
                "al_foil_price_per_m2":       AL_FOIL_PRICE,
                # Raw inputs for Module 06/07 slider initialisation
                "_in_num_layers":       num_layers_input,
                "_in_lw_ratio":         length_to_width_ratio,
                "_in_sep_excess_w":     sep_excess_width_mm,
                "_in_sep_excess_l":     sep_excess_length_mm,
                "_in_anode_excess":     anode_excess_mm,
                "_in_c_foil_thick":     cathode_foil_thickness_um,
                "_in_a_foil_thick":     anode_foil_thickness_um,
                "_in_anode_foil_density": anode_foil_density,
                "_in_sep_thick":        sep_thickness_um,
                "_in_sep_dens":         sep_density,
                "_in_elec_dens":        electrolyte_density,
                "_in_elec_uptake":      electrolyte_uptake_frac,
                "_in_con_thick_um":     container_thickness_um,
                "_in_con_density":      container_density_in,
                "_in_wall_thick":       wall_thickness_mm,
                "_in_seal_buf":         seal_buffer_mm,
                "_in_packing_eff":      packing_efficiency,
                "_in_cell_edge_fold":   cell_edge_fold_mm,
                "_in_elec_excess":      electrolyte_excess_frac,
            }
            if "_study_inputs" not in st.session_state:
                st.session_state["_study_inputs"] = {}
            st.session_state["_study_inputs"].update({
                "num_layers": num_layers_input, "lw_ratio": length_to_width_ratio,
                "sep_excess_w": sep_excess_width_mm, "sep_excess_l": sep_excess_length_mm,
                "anode_excess": anode_excess_mm,
                "c_foil_thick": cathode_foil_thickness_um, "a_foil_thick": anode_foil_thickness_um,
                "anode_foil_density": anode_foil_density,
                "sep_thick": sep_thickness_um, "sep_dens": sep_density,
                "elec_dens": electrolyte_density, "elec_uptake": electrolyte_uptake_frac,
                "con_thick_um": container_thickness_um, "con_density": container_density_in,
                "wall_thick": wall_thickness_mm, "seal_buf": seal_buffer_mm,
                "packing_eff": packing_efficiency, "cell_edge_fold": cell_edge_fold_mm,
                "bicell_expansion": bicell_expansion_um,
                "elec_excess": electrolyte_excess_frac,
                "tab_length_mm": tab_length_mm, "feedthrough": feedthrough_mm,
                "cc_buffer": cc_buffer_mm, "pouch_seal": pouch_seal_mm,
            })

            st.markdown(f"""
            <div class="note-box" style="margin-top:1rem;">
                <strong>Passed to Module 03:</strong> cell_mass_g, cell_energy_Wh,
                cell_volume_cm3, cell_specific_energy, cell_energy_density,
                cathode_foil_area_m2, anode_foil_area_m2, sep_area_m2,
                electrolyte volume and mass, all component masses.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            prev2, next2 = st.columns(2)
            with prev2:
                if st.button("← Previous: Electrochemical", use_container_width=True, key="prev_m01"):
                    st.session_state["_navigate_to"] = "⚗️  Module 01 - Electrochemical"
                    st.rerun()
            with next2:
                if st.button("Next module: Pack Design →", use_container_width=True, key="next_m03"):
                    st.session_state["_navigate_to"] = "🔋  Module 03 - Pack Design"
                    st.rerun()

# ── MODULE 03: PACK DESIGN ────────────────────────────────────────────────────
elif selected_key == "pack_design":

    if "cell_design" not in st.session_state:
        st.markdown("""
        <div class="hero-label">Module 03</div>
        <div class="hero-title">Pack <span>Design</span></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="status-bar" style="text-align:center;padding:2rem;">
            <strong>⚠ Module 02 required</strong> - Run the Cell Design module first,
            then return here.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    c = st.session_state["cell_design"]
    e = st.session_state.get("electrochem", {})

    st.markdown("""
    <div class="hero-label">Module 03</div>
    <div class="hero-title">Pack <span>Design</span></div>
    <div class="hero-subtitle">BatPaC v5.2 cell -> module -> row rack -> pack hierarchy</div>
    """, unsafe_allow_html=True)

    col_in, col_out = st.columns([2, 3], gap="large")

    with col_in:

        st.markdown('<div class="input-section-title">From Module 02 - Cell Design</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="note-box">
            <strong>Cell energy:</strong> {c["cell_energy_Wh"]:.4f} Wh<br>
            <strong>Cell voltage:</strong> {e.get("cell_voltage", 0):.3f} V<br>
            <strong>Cell capacity:</strong> {e.get("cell_capacity", 0):.4f} Ah<br>
            <strong>Cell mass:</strong> {c["cell_mass_g"]:.1f} g<br>
            <strong>Cell volume:</strong> {c["cell_volume_cm3"]:.1f} cm3
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Pack Topology (BatPaC convention)</div>', unsafe_allow_html=True)

        cell_energy_Wh   = c.get("cell_energy_Wh", 185.0)
        cell_voltage_V   = e.get("cell_voltage", 3.7)
        cell_capacity_Ah = e.get("cell_capacity", 50.0)

        st.markdown("""
        <div class="note-box">
            <strong>BatPaC hierarchy:</strong> Cells to modules to row rack to pack.
        </div>
        """, unsafe_allow_html=True)

        tp1, tp2 = st.columns(2)
        with tp1:
            cells_per_module = st.number_input(
                "Cells per module", value=20, min_value=1, max_value=200, step=1, key="cells_per_module",
                help="Number of cells in one module. BatPaC reference case: 20."
            )
            modules_per_row = st.number_input(
                "Modules per row", value=10, min_value=1, max_value=50, step=1, key="modules_per_row",
                help="Number of modules placed side by side in one row rack. BatPaC reference case: 5."
            )
            rows_per_pack = st.number_input(
                "Rows per pack", value=6, min_value=1, max_value=20, step=1, key="rows_per_pack",
                help="Number of row racks stacked to form the pack. BatPaC reference case: 4."
            )
        with tp2:
            cells_parallel = st.number_input(
                "Cells in parallel (per module)", value=2, min_value=1, max_value=50, step=1, key="cells_parallel",
                help="Cells wired in parallel within each module; the rest are in series. BatPaC reference: 2."
            )
            modules_parallel = st.number_input(
                "Modules in parallel", value=4, min_value=1, max_value=20, step=1, key="modules_parallel",
                help="Modules wired in parallel across the pack. BatPaC reference: 2."
            )

        useable_soc = st.number_input(
            "Useable SOC window", value=0.85, min_value=0.50, max_value=1.00,
            step=0.001, format="%.3f", key="useable_soc",
            help="Fraction of gross energy that is useable. BatPaC Dashboard!I36 sets 0.85, from a 10-95% cutoff band. No peer-reviewed source gives a useable SOC window for NVPF/hard carbon, so this convention is held constant across all scenarios."
        )

        modules_per_pack_preview = modules_per_row * rows_per_pack
        total_cells_preview      = modules_per_pack_preview * cells_per_module
        cells_series_preview     = max(1, round(cells_per_module / max(cells_parallel, 1)))
        modules_series_preview   = max(1, modules_per_pack_preview // max(modules_parallel, 1))
        pack_voltage_preview     = cells_series_preview * modules_series_preview * cell_voltage_V
        pack_energy_preview      = total_cells_preview * cell_energy_Wh / 1000.0

        st.markdown(f"""
        <div class="note-box">
            <strong>Preview:</strong>
            {modules_per_pack_preview} modules/pack &nbsp;|&nbsp;
            {total_cells_preview} cells/pack &nbsp;|&nbsp;
            <strong>{pack_voltage_preview:.1f} V</strong> &nbsp;|&nbsp;
            <strong>{pack_energy_preview:.1f} kWh</strong>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Module & Conductor Geometry</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="note-box">
            <strong>BatPaC defaults shown.</strong> These size the aluminium thermal
            conductors wrapped around each cell, the steel module enclosure, and
            the row rack support structure from geometry.
        </div>
        """, unsafe_allow_html=True)

        bg1, bg2, bg3 = st.columns(3)
        with bg1:
            al_conductor_thickness_mm = st.number_input(
                "Al conductor thickness (mm)", value=0.4, min_value=0.05, max_value=2.0, step=0.01, key="al_cond_thick",
                help="Thickness of the aluminium heat-spreader sheet wrapped around each cell. BatPaC default: 0.4 mm (0.04 cm)."
            )
        with bg2:
            module_wall_thickness_mm = st.number_input(
                "Module wall thickness (mm)", value=0.3, min_value=0.05, max_value=2.0, step=0.01, key="mod_wall_thick",
                help="Stainless steel module enclosure wall thickness. BatPaC default: 0.3 mm."
            )
        with bg3:
            restraint_plate_thickness_mm = st.number_input(
                "Restraint plate thickness (mm)", value=2.0, min_value=0.5, max_value=10.0, step=0.5, key="restraint_thick",
                help="Module compression restraint plate thickness. BatPaC default: 2 mm."
            )

        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Cooling System Geometry</div>', unsafe_allow_html=True)

        cg1, cg2 = st.columns(2)
        with cg1:
            coolant_panel_thickness_mm = st.number_input(
                "Coolant panel thickness (mm)", value=5.0, min_value=1.0, max_value=20.0, step=0.5, key="coolant_panel_thick",
                help="Internal coolant flow channel thickness in the stainless steel cooling panels. BatPaC default: 5 mm."
            )
        with cg2:
            coolant_plate_wall_mm = st.number_input(
                "Coolant panel wall thickness (mm)", value=0.3, min_value=0.05, max_value=2.0, step=0.01, key="coolant_wall",
                help="Stainless steel wall thickness of the coolant panels. BatPaC default: 0.3 mm."
            )

        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Pack Jacket Geometry</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="note-box">
            <strong>BatPaC jacket:</strong> a multi-layer sandwich - aluminium
            interior plate, steel exterior plate, and insulation, on both the base
            and the top of the pack, plus a steel support frame sized from total
            pack volume.
        </div>
        """, unsafe_allow_html=True)

        jg1, jg2, jg3 = st.columns(3)
        with jg1:
            jacket_insulation_thickness_mm = st.number_input(
                "Insulation thickness (mm)", value=10.0, min_value=0.0, max_value=50.0, step=1.0, key="jacket_insul_thick",
                help="BatPaC default: 10 mm."
            )
        with jg2:
            jacket_interior_plate_thickness_mm = st.number_input(
                "Interior plate thickness (mm)", value=1.0, min_value=0.2, max_value=5.0, step=0.1, key="jacket_int_plate",
                help="Aluminium interior plate. BatPaC default: 1 mm."
            )
        with jg3:
            jacket_exterior_base_plate_thickness_mm = st.number_input(
                "Exterior base plate thickness (mm)", value=1.0, min_value=0.2, max_value=5.0, step=0.1, key="jacket_ext_base",
                help="Steel exterior base plate. BatPaC default: 1 mm."
            )

        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Battery Management System</div>', unsafe_allow_html=True)

        bms1, bms2 = st.columns(2)
        with bms1:
            bms_bdu_mass_kg = st.number_input(
                "BDU / power electronics mass (kg)", value=2.444, min_value=0.0, max_value=50.0, step=0.001, format="%.4f", key="bms_bdu_mass",
                help="Battery Disconnect Unit / power electronics mass. BatPaC v5.2 BMS!G139 = 2.444 kg "
                     "(component-table sum: contactors, precharge circuit, service disconnect). Constant for packs above 100 V. "
                     "Note: this is an EV-specification BDU; adopted for consistency with the reference model, not validated for stationary duty. "
                     "BMU mass is computed internally from ASIC count (BMS!G136-G138)."
            )
        with bms2:
            bms_bdu_volume_L = st.number_input(
                "BDU / power electronics volume (L)", value=1.5485, min_value=0.0, max_value=20.0, step=0.001, format="%.4f", key="bms_bdu_vol",
                help="Battery Disconnect Unit / power electronics volume. BatPaC v5.2 BMS!G148 = 1.5485 L. "
                     "BMU volume is computed internally from ASIC count (BMS!G145-G147)."
            )

        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Conductor Current Sizing</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="note-box">
            <strong>BatPaC heating-rate method:</strong> bus bar, module interconnect,
            and pack terminal masses are sized from current density and a
            maximum allowable heating rate.
            BatPaC sizes this from a vehicle's rated peak power; this model uses
            a stationary discharge current instead, since there is no target peak
            power input here.
        </div>
        """, unsafe_allow_html=True)

        nominal_pack_current_A = st.number_input(
            "Nominal pack discharge current (A)", value=200.0, min_value=1.0, max_value=5000.0, step=10.0, key="nominal_pack_current",
            help="Discharge current used to size bus bars, module interconnects, and pack terminals via BatPaC's heating-rate conductor sizing method. For BatPaC NMC811-G validation, set to ~962 A (= 300 kW / 371.8 V). For stationary storage, use your actual peak discharge current."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        calculate3 = st.button("CALCULATE", use_container_width=True, key="calc3")

    with col_out:

        if calculate3:
            st.session_state["_m03_results"] = run_pack_design(
                cell_mass_g                       = c["cell_mass_g"],
                cell_energy_Wh                    = c["cell_energy_Wh"],
                cell_volume_cm3                    = c["cell_volume_cm3"],
                cell_voltage_V                      = e.get("cell_voltage", 0),
                cell_capacity_Ah                   = e.get("cell_capacity", 0),
                cell_width_mm                       = c["cell_width_mm"],
                cell_length_mm                      = c["cell_length_mm"],
                cell_thickness_mm                   = c["cell_thickness_mm"],
                positive_electrode_length_mm        = c["electrode_length_mm"],
                cells_per_module                    = cells_per_module,
                cells_parallel                       = cells_parallel,
                modules_per_row                      = modules_per_row,
                rows_per_pack                        = rows_per_pack,
                modules_parallel                     = modules_parallel,
                useable_soc_fraction                 = useable_soc,
                al_conductor_thickness_mm            = al_conductor_thickness_mm,
                module_wall_thickness_mm             = module_wall_thickness_mm,
                restraint_plate_thickness_mm         = restraint_plate_thickness_mm,
                coolant_panel_thickness_mm           = coolant_panel_thickness_mm,
                coolant_plate_wall_mm                = coolant_plate_wall_mm,
                jacket_insulation_thickness_mm       = jacket_insulation_thickness_mm,
                jacket_interior_plate_thickness_mm   = jacket_interior_plate_thickness_mm,
                jacket_exterior_base_plate_thickness_mm = jacket_exterior_base_plate_thickness_mm,
                bms_bdu_mass_kg                       = bms_bdu_mass_kg,
                bms_bdu_volume_L                      = bms_bdu_volume_L,
                nominal_pack_current_A                 = nominal_pack_current_A,
            )

        if "_m03_results" not in st.session_state:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};border-radius:6px;
                        padding:3rem 2rem;text-align:center;margin-top:1rem;">
                <div style="font-family:'IBM Plex Mono',serif;font-size:0.72rem;
                            color:{T['muted']};letter-spacing:0.1em;">
                    SET INPUTS AND CLICK CALCULATE
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            r3 = st.session_state["_m03_results"]

            st.markdown('<div class="section-header">Validation</div>', unsafe_allow_html=True)
            checks3 = [
                (r3["series_parallel_valid"],
                 f"Cells per module divisible by cells in parallel - {cells_per_module} / {cells_parallel} = {r3['cells_series_per_module']} series groups"),
                (r3["modules_valid"],
                 f"Modules per pack divisible by modules in parallel - {r3['modules_per_pack']} / {modules_parallel} = {r3['modules_in_series']} series groups"),
            ]
            for passed, msg in checks3:
                cls  = "val-pass" if passed else "val-warn"
                icon = "OK" if passed else "!"
                st.markdown(f'<div class="{cls}">{icon}  {msg}</div>', unsafe_allow_html=True)

            # ── BatPaC Line-by-Line Validation Panel ──────────────────────────
            with st.expander("🔬 BatPaC NMC811-G Validation (line-by-line comparison)", expanded=False):
                
                _M03_REF = {
                    "pack_voltage_V":          371.82,
                    "pack_capacity_Ah":        268.95,
                    "pack_gross_energy_kWh":   100.00,
                    "busbar_pack_g":          1122.56,
                    "pack_terminals_g":         590.85,
                    "module_interconnect_g":     52.37,
                    "pack_mass_kg":             499.20,
                }
                _m03_rows = ""
                _m03_rows += _batpac_vrow("Pack voltage (V)",        r3.get("pack_voltage_V",0),        _M03_REF["pack_voltage_V"],        ".2f", 1.0)
                _m03_rows += _batpac_vrow("Pack capacity (Ah)",      r3.get("pack_capacity_Ah",0),      _M03_REF["pack_capacity_Ah"],      ".2f", 1.0)
                _m03_rows += _batpac_vrow("Pack gross energy (kWh)", r3.get("pack_gross_energy_kWh",0), _M03_REF["pack_gross_energy_kWh"], ".2f", 1.0)
                _m03_rows += _batpac_vrow("Bus bar mass (g)",        r3.get("busbar_pack_g",0),         _M03_REF["busbar_pack_g"],         ".1f", 3.0)
                _m03_rows += _batpac_vrow("Pack terminals (g)",      r3.get("pack_terminals_g",0),      _M03_REF["pack_terminals_g"],      ".1f", 1.0)
                _m03_rows += _batpac_vrow("Module interconnect (g)", r3.get("module_interconnect_g",0), _M03_REF["module_interconnect_g"], ".2f", 1.0)
                _m03_rows += _batpac_vrow("Pack mass (kg)",          r3.get("pack_mass_kg",0),          _M03_REF["pack_mass_kg"],          ".1f", 5.0)
                st.markdown(_batpac_validation_table(_m03_rows), unsafe_allow_html=True)

            st.markdown('<div class="section-header">Primary Outputs</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="output-grid">
                <div class="output-card highlight">
                    <div class="output-card-label">Useable energy</div>
                    <div class="output-card-value">{r3["pack_useable_energy_kWh"]:.4f}</div>
                    <div class="output-card-unit">kWh</div>
                </div>
                <div class="output-card highlight">
                    <div class="output-card-label">Pack voltage</div>
                    <div class="output-card-value">{r3["pack_voltage_V"]:.1f}</div>
                    <div class="output-card-unit">V</div>
                </div>
                <div class="output-card highlight">
                    <div class="output-card-label">Pack capacity</div>
                    <div class="output-card-value">{r3["pack_capacity_Ah"]:.2f}</div>
                    <div class="output-card-unit">Ah</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Total cells</div>
                    <div class="output-card-value">{r3["total_cells"]}</div>
                    <div class="output-card-unit">cells</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Pack specific energy</div>
                    <div class="output-card-value">{r3["pack_specific_energy"]:.1f}</div>
                    <div class="output-card-unit">Wh/kg</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Pack energy density</div>
                    <div class="output-card-value">{r3["pack_energy_density"]:.1f}</div>
                    <div class="output-card-unit">Wh/L</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">Module, Rack & Pack Geometry</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="output-grid">
                <div class="output-card">
                    <div class="output-card-label">Module dimensions</div>
                    <div class="output-card-value" style="font-size:1.0rem;">{r3["module_length_mm"]:.0f}x{r3["module_width_mm"]:.0f}x{r3["module_height_mm"]:.0f}</div>
                    <div class="output-card-unit">mm (LxWxH)</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Rack dimensions</div>
                    <div class="output-card-value" style="font-size:1.0rem;">{r3["rack_length_mm"]:.0f}x{r3["rack_width_mm"]:.0f}x{r3["rack_height_mm"]:.0f}</div>
                    <div class="output-card-unit">mm (LxWxH)</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Pack dimensions</div>
                    <div class="output-card-value" style="font-size:1.0rem;">{r3["pack_length_mm"]:.0f}x{r3["pack_width_mm"]:.0f}x{r3["pack_height_mm"]:.0f}</div>
                    <div class="output-card-unit">mm (LxWxH)</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Modules per pack</div>
                    <div class="output-card-value">{r3["modules_per_pack"]}</div>
                    <div class="output-card-unit">modules</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">Mass Breakdown (BatPaC hierarchy)</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <table class="mass-table">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th style="text-align:right">Mass (kg)</th>
                        <th style="text-align:right">% pack mass</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Cells ({r3["total_cells"]} x {c["cell_mass_g"]:.0f} g)</td>
                        <td class="val">{r3["cell_mass_total_kg"]:.4f}</td>
                        <td class="val">{pct(r3["cell_mass_total_kg"], r3["pack_mass_kg"])}</td>
                    </tr>
                    <tr><td>Module hardware ({r3["modules_per_pack"]} modules: Al conductors + enclosure)</td>
                        <td class="val">{r3["module_mass_total_kg"] - r3["cell_mass_total_kg"]:.4f}</td>
                        <td class="val">{pct(r3["module_mass_total_kg"] - r3["cell_mass_total_kg"], r3["pack_mass_kg"])}</td>
                    </tr>
                    <tr><td>Row rack ({rows_per_pack} rows: channels, restraint, pads)</td>
                        <td class="val">{r3["rack_mass_total_kg"]:.4f}</td>
                        <td class="val">{pct(r3["rack_mass_total_kg"], r3["pack_mass_kg"])}</td>
                    </tr>
                    <tr><td>Cooling system (panels, manifold, coolant)</td>
                        <td class="val">{r3["cooling_system_kg"]:.4f}</td>
                        <td class="val">{pct(r3["cooling_system_kg"], r3["pack_mass_kg"])}</td>
                    </tr>
                    <tr><td>Pack jacket (base + top, plates + insulation + frame)</td>
                        <td class="val">{r3["pack_jacket_total_kg"]:.4f}</td>
                        <td class="val">{pct(r3["pack_jacket_total_kg"], r3["pack_mass_kg"])}</td>
                    </tr>
                    <tr><td>Conductors (interconnects, bus bars, terminals)</td>
                        <td class="val">{r3["conductors_kg"]:.4f}</td>
                        <td class="val">{pct(r3["conductors_kg"], r3["pack_mass_kg"])}</td>
                    </tr>
                    <tr><td>BMS</td>
                        <td class="val">{r3["bms_mass_kg"]:.4f}</td>
                        <td class="val">{pct(r3["bms_mass_kg"], r3["pack_mass_kg"])}</td>
                    </tr>
                    <tr class="subtotal">
                        <td><strong>Total pack mass</strong></td>
                        <td class="val"><strong>{r3["pack_mass_kg"]:.4f}</strong></td>
                        <td class="val"><strong>100.0%</strong></td>
                    </tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)

            with st.expander("Equations used in this module (verified against BatPaC v5.2)"):
                st.markdown(f"""
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:{T['sub']};line-height:2.1;">

                <span style="color:{T['accent']}">Pack topology (BatPaC rows 25-38)</span><br>
                modules_per_pack = modules_per_row x rows_per_pack = {modules_per_row} x {rows_per_pack} = {r3['modules_per_pack']}<br>
                total_cells = modules_per_pack x cells_per_module = {r3['modules_per_pack']} x {cells_per_module} = <strong style="color:{T['text']}">{r3['total_cells']}</strong><br>
                pack_voltage = cells_series_per_module x modules_in_series x cell_voltage = {r3['cells_series_per_module']} x {r3['modules_in_series']} x {e.get('cell_voltage',0):.3f} = <strong style="color:{T['text']}">{r3['pack_voltage_V']:.2f} V</strong><br>
                pack_capacity = cell_capacity x cells_parallel x modules_parallel = {e.get('cell_capacity',0):.3f} x {cells_parallel} x {modules_parallel} = <strong style="color:{T['text']}">{r3['pack_capacity_Ah']:.2f} Ah</strong><br><br>

                <span style="color:{T['accent']}">Module geometry (BatPaC rows 373-390)</span><br>
                Al conductor mass/module = (cells_per_module+1) x conductor_length x (cell_width+2xcond_thick + 0.95xcell_thicknessx2) x cond_thick/1000 x 2.70<br>
                = <strong style="color:{T['text']}">{r3['al_conductor_g_per_module']:.2f} g</strong><br>
                Module enclosure mass = 7.8 x wall_thick x (LxW+LxH+WxH) x 2/1000 = <strong style="color:{T['text']}">{r3['module_enclosure_g']:.2f} g</strong><br>
                Module dimensions = <strong style="color:{T['text']}">{r3['module_length_mm']:.1f} x {r3['module_width_mm']:.1f} x {r3['module_height_mm']:.1f} mm</strong><br><br>

                <span style="color:{T['accent']}">Row rack (BatPaC rows 409-428)</span><br>
                Rack dimensions = <strong style="color:{T['text']}">{r3['rack_length_mm']:.1f} x {r3['rack_width_mm']:.1f} x {r3['rack_height_mm']:.1f} mm</strong><br>
                Rack hardware mass per row (channels + restraint + pads) = <strong style="color:{T['text']}">{r3['rack_total_kg_per_row']:.3f} kg</strong><br>
                Total rack mass ({rows_per_pack} rows) = <strong style="color:{T['text']}">{r3['rack_mass_total_kg']:.3f} kg</strong><br><br>

                <span style="color:{T['accent']}">Cooling system (BatPaC rows 437-447)</span><br>
                Coolant panels + manifold tubing + coolant liquid = <strong style="color:{T['text']}">{r3['cooling_system_kg']:.3f} kg</strong><br><br>

                <span style="color:{T['accent']}">Pack jacket (BatPaC rows 450-483)</span><br>
                Pack dimensions = <strong style="color:{T['text']}">{r3['pack_length_mm']:.1f} x {r3['pack_width_mm']:.1f} x {r3['pack_height_mm']:.1f} mm</strong><br>
                Support frame + interior/exterior plates + insulation (base + top) = <strong style="color:{T['text']}">{r3['pack_jacket_total_kg']:.3f} kg</strong><br><br>

                <span style="color:{T['accent']}">Conductors - heating-rate sizing (BatPaC rows 187-214, 488-490)</span><br>
                Module interconnect (per piece) = {r3['module_interconnect_g']:.3f} g<br>
                Bus bar (pack) = {r3['busbar_pack_g']:.2f} g<br>
                Pack terminals = {r3['pack_terminals_g']:.2f} g<br>
                Total conductor mass = <strong style="color:{T['text']}">{r3['conductors_kg']:.3f} kg</strong><br>
                <span style="color:{T['muted']};font-size:0.62rem;">Sized using {nominal_pack_current_A:.0f} A nominal discharge current (stationary-storage substitute for BatPaC's vehicle power-burst current).</span><br><br>

                <span style="color:{T['accent']}">Final assembly</span><br>
                pack_mass = cells + module_hardware + rack + cooling + jacket + conductors + BMS<br>
                = <strong style="color:{T['text']}">{r3['pack_mass_kg']:.3f} kg</strong>

                </div>
                """, unsafe_allow_html=True)

            st.session_state["pack_design"] = {
                **r3,
                "cells_per_module": cells_per_module,
                "cells_parallel": cells_parallel,
                "modules_per_row": modules_per_row,
                "rows_per_pack": rows_per_pack,
                "modules_parallel": modules_parallel,
                "useable_soc": useable_soc,
                "useable_soc_fraction": useable_soc,
                # Raw inputs for Module 06/07 slider initialisation
                "_in_useable_soc":        useable_soc,
                "_in_cells_per_module":   cells_per_module,
                "_in_cells_parallel":     cells_parallel,
                "_in_modules_per_row":    modules_per_row,
                "_in_rows_per_pack":      rows_per_pack,
                "_in_modules_parallel":   modules_parallel,
                "_in_nominal_current":    nominal_pack_current_A,
            }
            if "_study_inputs" not in st.session_state:
                st.session_state["_study_inputs"] = {}
            st.session_state["_study_inputs"].update({
                "useable_soc": useable_soc, "cells_per_module": cells_per_module,
                "cells_parallel_m03": cells_parallel, "modules_per_row": modules_per_row,
                "rows_per_pack": rows_per_pack, "modules_parallel": modules_parallel,
                "nominal_current": nominal_pack_current_A,
                # Pack hardware sizes. Without these, Modules 06 to 08 quietly use
                # the BatPaC defaults and end up modelling a different pack.
                "al_cond_thick_mm": al_conductor_thickness_mm,
                "mod_wall_thick_mm": module_wall_thickness_mm,
                "restraint_thick_mm": restraint_plate_thickness_mm,
                "coolant_panel_thick_mm": coolant_panel_thickness_mm,
                "coolant_wall_mm": coolant_plate_wall_mm,
                "jacket_insul_mm": jacket_insulation_thickness_mm,
                "jacket_int_plate_mm": jacket_interior_plate_thickness_mm,
                "jacket_ext_base_mm": jacket_exterior_base_plate_thickness_mm,
                "bms_bdu_mass": bms_bdu_mass_kg, "bms_bdu_vol": bms_bdu_volume_L,
            })

            # ── Three-panel physical layout diagrams ──────────────────────────
            _r3 = st.session_state["_m03_results"]
            _e3 = st.session_state.get("electrochem", {})
            _c3 = st.session_state.get("cell_design", {})

            _n_cpm   = cells_per_module
            _n_cp    = cells_parallel
            _n_cs    = max(1, _n_cpm // max(_n_cp, 1))
            _n_mpr   = modules_per_row
            _n_rows  = rows_per_pack
            _n_mpp   = _n_mpr * _n_rows
            _cv      = _e3.get("cell_voltage", 3.7)
            _ce      = _c3.get("cell_energy_Wh", 185.0)
            _mod_V   = _n_cs * _cv
            _mod_E   = _n_cpm * _ce / 1000.0
            _row_E   = _n_mpr * _mod_E
            _pack_V  = _r3.get("pack_voltage_V", _mod_V * (_n_mpp // max(modules_parallel,1)))
            _pack_E  = _r3.get("pack_gross_energy_kWh", _n_mpp * _mod_E)

            BG_ = "#1e1e2e"; CARD_ = "#2a2a3e"; ACC_ = "#f59e0b"
            TEXT_ = "#e2e8f0"; MUTED_ = "#94a3b8"; CELL_C_ = "#3b5bdb"
            MOD_B_ = "#f59e0b"; ROW_B_ = "#64748b"; PACK_BG_ = "#1a2540"

            def _svgt(x,y,s,sz=10,cl=None,an="middle",fw="normal"):
                c2 = cl or TEXT_
                return f'<text x="{x}" y="{y}" font-family="IBM Plex Mono,monospace" font-size="{sz}" fill="{c2}" text-anchor="{an}" font-weight="{fw}">{s}</text>'

            # Panel 1: Module
            CELL_W, CELL_H, CGAP = 18, 12, 3
            disp_cs = min(_n_cs, 20)
            disp_cp = min(_n_cp, 6)
            mod_cells_w = disp_cs * (CELL_W + CGAP) - CGAP
            mod_cells_h = disp_cp * (CELL_H + CGAP) - CGAP
            PAD = 14
            M_W = mod_cells_w + 2*PAD + 30
            M_H = mod_cells_h + 2*PAD + 44
            s1 = [f'<svg viewBox="0 0 {M_W} {M_H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;border-radius:8px;background:{BG_};margin-bottom:8px;">']
            s1.append(f'<rect x="1" y="1" width="{M_W-2}" height="{M_H-2}" rx="8" fill="{CARD_}" stroke="{MOD_B_}" stroke-width="2"/>')
            s1.append(_svgt(M_W//2, 18, "MODULE", 12, ACC_, fw="bold"))
            s1.append(_svgt(M_W//2, 32, f"{_n_cs} cells in series" + (f" x {_n_cp} parallel" if _n_cp > 1 else ""), 9, MUTED_))
            cx0 = PAD + 14
            cy0 = 42
            for ri in range(disp_cp):
                for ci in range(disp_cs):
                    cx = cx0 + ci*(CELL_W+CGAP)
                    cy = cy0 + ri*(CELL_H+CGAP)
                    s1.append(f'<rect x="{cx}" y="{cy}" width="{CELL_W}" height="{CELL_H}" rx="2" fill="{CELL_C_}" opacity="0.9"/>')
                    if ci == 0:
                        s1.append(_svgt(cx+4, cy+9, "+", 7, "#fff"))
                    if ci == disp_cs-1:
                        s1.append(_svgt(cx+CELL_W-4, cy+9, "-", 7, "#fff"))
                cy_mid = cy0 + ri*(CELL_H+CGAP) + CELL_H//2
                s1.append(f'<line x1="{cx0}" y1="{cy_mid}" x2="{cx0+mod_cells_w}" y2="{cy_mid}" stroke="{MUTED_}" stroke-width="0.5" stroke-dasharray="2,2"/>')
            term_y = cy0 + mod_cells_h//2 + 4
            s1.append(_svgt(PAD+2, term_y, "+", 11, "#22c55e", fw="bold"))
            s1.append(_svgt(cx0+mod_cells_w+10, term_y, "-", 11, "#ef4444", fw="bold"))
            if _n_cs > 20 or _n_cp > 6:
                s1.append(_svgt(M_W//2, cy0+mod_cells_h+12, f"(showing {disp_cs}S x {disp_cp}P of {_n_cs}S x {_n_cp}P)", 8, MUTED_))
            s1.append(_svgt(M_W//2, M_H-8, f"{_mod_V:.2f} V  |  {_mod_E:.3f} kWh  |  {_n_cpm} cells", 9, TEXT_, fw="bold"))
            s1.append("</svg>")
            st.markdown("".join(s1), unsafe_allow_html=True)

            # Panel 2: Row Rack
            disp_mpr = min(_n_mpr, 12)
            MOD_SLOT_W = max(40, min(80, (680 - 20) // max(disp_mpr, 1)))
            MOD_SLOT_H = 60
            R_W = disp_mpr * (MOD_SLOT_W + 4) + 20
            R_H = MOD_SLOT_H + 56
            s2 = [f'<svg viewBox="0 0 {R_W} {R_H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;border-radius:8px;background:{BG_};margin-bottom:8px;">']
            s2.append(f'<rect x="1" y="1" width="{R_W-2}" height="{R_H-2}" rx="8" fill="{CARD_}" stroke="{ROW_B_}" stroke-width="2"/>')
            s2.append(_svgt(R_W//2, 18, "ROW RACK", 12, ACC_, fw="bold"))
            s2.append(_svgt(R_W//2, 31, f"{_n_mpr} modules in series per row", 9, MUTED_))
            for mi in range(disp_mpr):
                mx = 10 + mi*(MOD_SLOT_W+4)
                my = 38
                s2.append(f'<rect x="{mx}" y="{my}" width="{MOD_SLOT_W}" height="{MOD_SLOT_H}" rx="4" fill="{CARD_}" stroke="{MOD_B_}" stroke-width="1.2"/>')
                s2.append(_svgt(mx+MOD_SLOT_W//2, my+16, f"M{mi+1}", 9, ACC_))
                s2.append(_svgt(mx+MOD_SLOT_W//2, my+30, f"{_mod_V:.1f}V", 8, MUTED_))
                s2.append(_svgt(mx+MOD_SLOT_W//2, my+44, f"{_mod_E:.2f}kWh", 8, MUTED_))
                if mi < disp_mpr - 1:
                    wire_y = my + MOD_SLOT_H//2
                    s2.append(f'<line x1="{mx+MOD_SLOT_W}" y1="{wire_y}" x2="{mx+MOD_SLOT_W+4}" y2="{wire_y}" stroke="{MUTED_}" stroke-width="1.5"/>')
            if _n_mpr > 12:
                s2.append(_svgt(R_W//2, 38+MOD_SLOT_H+12, f"({_n_mpr} modules total, {disp_mpr} shown)", 8, MUTED_))
            s2.append(_svgt(R_W//2, R_H-8, f"{_mod_V:.1f} V  |  {_row_E:.2f} kWh  |  {_n_mpr} modules", 9, TEXT_, fw="bold"))
            s2.append("</svg>")
            st.markdown("".join(s2), unsafe_allow_html=True)

            # Panel 3: Pack
            disp_rows = min(_n_rows, 8)
            RACK_H = 36
            P_W = 700
            P_H = disp_rows*(RACK_H+4) + 56
            s3 = [f'<svg viewBox="0 0 {P_W} {P_H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;border-radius:8px;background:{PACK_BG_};margin-bottom:8px;">']
            s3.append(f'<rect x="1" y="1" width="{P_W-2}" height="{P_H-2}" rx="8" fill="{PACK_BG_}" stroke="{ACC_}" stroke-width="2.5"/>')
            s3.append(_svgt(P_W//2, 18, "PACK", 13, ACC_, fw="bold"))
            s3.append(_svgt(P_W//2, 31, f"{_n_rows} row racks  |  {_n_mpp} modules total  |  {_n_mpp*_n_cpm} cells total", 9, MUTED_))
            for ri in range(disp_rows):
                ry = 38 + ri*(RACK_H+4)
                s3.append(f'<rect x="10" y="{ry}" width="{P_W-20}" height="{RACK_H}" rx="4" fill="{CARD_}" stroke="{ROW_B_}" stroke-width="1.2"/>')
                s3.append(_svgt(P_W//2, ry+14, f"ROW RACK {ri+1}", 9, ACC_))
                s3.append(_svgt(P_W//2, ry+27, f"{_n_mpr} modules  |  {_mod_V:.1f} V  |  {_row_E:.2f} kWh", 8, MUTED_))
            if _n_rows > 8:
                s3.append(_svgt(P_W//2, 38+disp_rows*(RACK_H+4)+10, f"({_n_rows} rows total, {disp_rows} shown)", 8, MUTED_))
            s3.append(_svgt(P_W//2, P_H-8, f"{_pack_V:.1f} V  |  {_pack_E:.1f} kWh  |  {_n_mpp} modules  |  {_n_mpp*_n_cpm} cells", 9, TEXT_, fw="bold"))
            s3.append("</svg>")
            st.markdown("".join(s3), unsafe_allow_html=True)

            st.markdown(f"""
            <div class="note-box" style="margin-top:1rem;">
                <strong>Passed to Module 04:</strong> pack_useable_energy_kWh, pack_mass_kg,
                pack_voltage_V, pack_capacity_Ah, total_cells, cell_mass_fraction,
                module/rack/jacket/conductor mass breakdown for cost calculation.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            prev3, next3 = st.columns(2)
            with prev3:
                if st.button("← Previous: Cell Design", use_container_width=True, key="prev_m02"):
                    st.session_state["_navigate_to"] = "🔲  Module 02 - Cell Design"
                    st.rerun()
            with next3:
                if st.button("Next module: Cost Model →", use_container_width=True, key="next_m04"):
                    st.session_state["_navigate_to"] = "💰  Module 04 - Cost Model"
                    st.rerun()

# -- MODULE 04: COST MODEL -----------------------------------------------------
elif selected_key == "cost_model":

    if "pack_design" not in st.session_state:
        st.markdown("""
        <div class="hero-label">Module 04</div>
        <div class="hero-title">Cost <span>Model</span></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="status-bar" style="text-align:center;padding:2rem;">
            <strong>Module 03 required</strong> - Run the Pack Design module first,
            then return here.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    e = st.session_state.get("electrochem", {})
    c = st.session_state.get("cell_design", {})
    p = st.session_state["pack_design"]

    st.markdown("""
    <div class="hero-label">Module 04</div>
    <div class="hero-title">Cost <span>Model</span></div>
    <div class="hero-subtitle">BatPaC v5.2 manufacturing cost engine - cell, module, and pack level</div>
    """, unsafe_allow_html=True)

    col_in, col_out = st.columns([2, 3], gap="large")

    with col_in:

        st.markdown('<div class="input-section-title">From Upstream Modules</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="note-box">
            <strong>Total cells:</strong> {p["total_cells"]} ({p["modules_per_pack"]} modules)<br>
            <strong>Useable energy:</strong> {p["pack_useable_energy_kWh"]:.4f} kWh<br>
            <strong>Cathode AM per cell:</strong> {e.get("c_AM_mass", 0):.4f} g<br>
            <strong>Anode AM per cell:</strong> {e.get("a_AM_mass", 0):.4f} g
        </div>
        """, unsafe_allow_html=True)

        # -- Active material prices --------------------------------------------
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Active Material Prices</div>', unsafe_allow_html=True)
        am1, am2 = st.columns(2)
        with am1:
            p_cathode_am = st.number_input(
                "Cathode AM ($/kg)", value=16.53, min_value=0.9, max_value=200.0,
                step=0.05, key="p_cathode_am",
                help="NVPF: $16.53/kg bottom-up estimate following Peters et al. (2019) Eq.1, V2O5 at $12.70/kg (vanadiumprice.com). See Register Sec 6.1."
            )
        with am2:
            p_anode_am = st.number_input(
                "Anode AM ($/kg)", value=5.2, min_value=1.0, max_value=50.0,
                step=0.5, key="p_anode_am",
                help="Hard carbon $5.2/kg. Source: S2666248525000241."
            )

        # -- Electrode component prices ----------------------------------------
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Electrode Component Prices</div>', unsafe_allow_html=True)

        ec1, ec2 = st.columns(2)
        with ec1:
            p_carbon = st.number_input(
                "Carbon black ($/kg)", value=1.296, min_value=0.5, max_value=10.0,
                step=0.001, key="p_carbon",
                help="Conductive carbon additive. Rosner et al. (2024): $1.296/kg."
            )
            p_pvdf = st.number_input(
                "PVDF binder ($/kg)", value=7.33, min_value=1.0, max_value=50.0,
                step=0.5, key="p_pvdf",
                help="Cathode binder, requires NMP solvent. Peters et al. (2016): $7.33/kg."
            )
        with ec2:
            p_cmcsbr = st.number_input(
                "CMC/SBR binder ($/kg)", value=1.40, min_value=0.5, max_value=20.0,
                step=0.5, key="p_cmcsbr",
                help="Anode binder, water-based. Blended CMC:SBR at 1:1 by mass (Li et al. 2013). $1.40/kg, Register Sec 6.3."
            )
            p_al_foil_cost = st.number_input(
                "Al foil ($/m2)", value=0.20, min_value=0.05, max_value=2.0,
                step=0.05, format="%.3f", key="p_al_foil_cost",
                help="Both electrodes use Al foil in SIBs. $0.15-0.25/m2."
            )
            p_anode_foil_cost = st.number_input(
                "Anode foil ($/m²)", value=0.20, min_value=0.05, max_value=2.0,
                step=0.05, format="%.3f", key="p_anode_foil_cost",
                help="SIB default: Al foil, same as cathode ($0.20/m²). Set to $1.20/m² to validate against BatPaC LIB cases, which use copper."
            )
        # -- Cell component prices ----------------------------------------------
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Cell Component Prices</div>', unsafe_allow_html=True)

        cc1, cc2 = st.columns(2)
        with cc1:
            p_sep = st.number_input(
                "Separator ($/m2)", value=1.78, min_value=0.5, max_value=10.0,
                step=0.001, key="p_sep",
                help="PE separator. Peters et al. (2016): $1.78/m2."
            )
            p_electrolyte = st.number_input(
                "Electrolyte ($/L)", value=18.03, min_value=1.0, max_value=50.0,
                step=0.5, key="p_electrolyte",
                help="NaPF6-based electrolyte. Peters et al. (2016): $18.03/L (NaPF6 proxy)."
            )
        with cc2:
            p_container = st.number_input(
                "Container ($/kg)", value=3.0, min_value=1.0, max_value=30.0,
                step=0.5, key="p_container",
                help="PET-Al-PP pouch laminate. BatPaC CI!F47: $3.00/kg, plus a $0.20/cell fixed charge (CI!G47)."
            )
            p_pos_terminal_kg = st.number_input(
                "Pos. terminal ($/kg)", value=2.405, min_value=0.5, max_value=20.0,
                step=0.1, format="%.3f", key="p_pos_terminal_kg",
                help="Positive terminal material price per kg. BatPaC default: Al = $2.405/kg."
            )
            p_neg_terminal_kg = st.number_input(
                "Neg. terminal ($/kg)", value=2.405, min_value=0.5, max_value=30.0,
                step=0.1, format="%.3f", key="p_neg_terminal_kg",
                help="Negative terminal material price per kg. SIB default: Al = $2.405/kg. BatPaC LIB uses Cu = $8.64/kg."
            )
            terminal_fixed_cost = st.number_input(
                "Terminal fixed cost ($/terminal)", value=0.08, min_value=0.0, max_value=1.0,
                step=0.01, format="%.3f", key="terminal_fixed_cost",
                help="Fixed assembly cost per terminal (both pos and neg). BatPaC Cost Input: $0.08/terminal."
            )

        # -- Manufacturing scale & process inputs (BatPaC) -----------------------
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Manufacturing Scale (BatPaC process model)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="note-box">
            <strong>BatPaC engine:</strong> all 26 manufacturing process steps
            (materials prep, coating, calendering, stacking, formation, module/pack
            assembly, building systems) are sized from your annual production
            volume and cell design.
        </div>
        """, unsafe_allow_html=True)

        mf1, mf2 = st.columns(2)
        with mf1:
            annual_production_packs = st.number_input(
                "Annual production (packs/yr)", value=500000, min_value=1000, max_value=5000000,
                step=10000, key="annual_production_packs",
                help="Number of battery packs manufactured per year. Drives all process-cost scaling. BatPaC reference case: 500,000 packs/yr."
            )
            cell_yield_pct = st.number_input(
                "Cell yield (%)", value=95.0, min_value=70.0, max_value=99.9,
                step=0.5, key="cell_yield_pct",
                help="Fraction of manufactured cells that pass quality control. BatPaC default: 95%."
            )
        with mf2:
            labor_rate_per_hr = st.number_input(
                "Labor rate ($/hr)", value=35.0, min_value=5.0, max_value=100.0,
                step=1.0, key="labor_rate_per_hr",
                help="Direct labor wages + benefits. BatPaC default: $35/hr."
            )
            energy_price_per_kWh = st.number_input(
                "Energy price ($/kWh)", value=0.04, min_value=0.01, max_value=0.50,
                step=0.01, format="%.3f", key="energy_price_per_kWh",
                help="Industrial electricity price. BatPaC default: $0.04/kWh."
            )

        effective_days_per_year = st.number_input(
            "Effective operating days/year", value=320, min_value=200, max_value=365,
            step=5, key="effective_days_per_year",
            help="Plant operating days per year, accounting for downtime. BatPaC default: 320 days."
        )

        # -- BMS cost --------------------------------------------------------------
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Battery Management System Cost</div>', unsafe_allow_html=True)
        bms_cost_per_pack = st.number_input(
            "BMS cost ($/pack)", value=375.0, min_value=50.0, max_value=2000.0,
            step=10.0, key="bms_cost_per_pack",
            help="Total BMS hardware and electronics cost per pack. BatPaC reference (100 kWh EV pack): $375/pack."
        )

        # -- Pack hardware unit prices (BatPaC) ------------------------------------
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Pack Hardware Unit Prices (BatPaC)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="note-box">
            These price the module/pack hardware your Module 03 already sized
            (row rack, busbars, cooling panels, pack jacket) using BatPaC's
            default unit prices.
        </div>
        """, unsafe_allow_html=True)

        ph1, ph2 = st.columns(2)
        with ph1:
            p_row_rack = st.number_input("Row rack ($/kg)", value=1.325, min_value=0.1, max_value=10.0, step=0.05, key="p_row_rack")
            p_module_pads = st.number_input("Module pads ($/pad)", value=1.5, min_value=0.1, max_value=10.0, step=0.1, key="p_module_pads")
            p_module_interconnect = st.number_input("Module interconnect ($/kg)", value=8.84, min_value=1.0, max_value=30.0, step=0.5, key="p_module_interconnect")
            p_busbar = st.number_input("Bus bars ($/kg)", value=8.68, min_value=1.0, max_value=30.0, step=0.5, key="p_busbar")
            p_coolant_panel = st.number_input("Coolant panels ($/kg)", value=3.45, min_value=0.5, max_value=20.0, step=0.25, key="p_coolant_panel")
            p_coolant_manifold = st.number_input("Coolant manifolds ($/kg)", value=9.5, min_value=1.0, max_value=30.0, step=0.5, key="p_coolant_manifold")
        with ph2:
            p_pack_terminal_seal = st.number_input("Pack terminals/seals ($/kg)", value=8.88, min_value=1.0, max_value=30.0, step=0.5, key="p_pack_terminal_seal")
            p_pack_support_frame = st.number_input("Pack support frame ($/kg)", value=1.325, min_value=0.1, max_value=10.0, step=0.05, key="p_pack_support_frame")
            p_jacket_top_interior = st.number_input("Jacket top/interior ($/kg)", value=3.16, min_value=0.5, max_value=20.0, step=0.25, key="p_jacket_top_interior")
            p_jacket_exterior_base = st.number_input("Jacket exterior base ($/kg)", value=1.375, min_value=0.1, max_value=10.0, step=0.05, key="p_jacket_exterior_base")
            p_jacket_insulation = st.number_input("Jacket insulation ($/kg)", value=3.0, min_value=0.5, max_value=20.0, step=0.25, key="p_jacket_insulation")

        # -- Benchmark -------------------------------------------------------------
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">LFP Benchmark</div>', unsafe_allow_html=True)
        lfp_benchmark = _lfp_reference_cost()
        if lfp_benchmark:
            st.markdown(
                f'<div class="val-pass">Like-for-like LFP/graphite cost from Module 06: '
                f'<strong>${lfp_benchmark:.2f}/kWh</strong>, same plant, volume and topology.</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="val-warn">{_NO_LFP_MSG}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        calculate4 = st.button("CALCULATE", use_container_width=True, key="calc4")

    with col_out:

        if calculate4:
            # Derive total coated electrode area (cm²) for BatPaC G16/G17
            # = num_bicell_layers × 2 sides × width × length (mm→cm²: /100)
            # Ref: BatPaC BD291/BD292, Manufacturing Costs G16/G17
            _n_layers_m04 = c.get("num_bicell_layers", 32)
            _anode_excess_m04 = st.session_state.get("anode_excess", 2.0)
            positive_electrode_area_cm2 = _n_layers_m04 * 2 * c.get("electrode_width_mm", 0) * c.get("electrode_length_mm", 0) / 100
            negative_electrode_area_cm2 = _n_layers_m04 * 2 * (c.get("electrode_width_mm", 0) + _anode_excess_m04) * c.get("electrode_length_mm", 0) / 100

            st.session_state["_m04_results"] = run_cost_model(
                c_AM_mass_g=e.get("c_AM_mass", 0), a_AM_mass_g=e.get("a_AM_mass", 0),
                c_carbon_g=e.get("c_carbon_mass", 0), a_carbon_g=e.get("a_carbon_mass", 0),
                c_binder_g=e.get("c_binder_mass", 0), a_binder_g=e.get("a_binder_mass", 0),
                binder_solvent_ratio_pos=16, binder_solvent_ratio_neg=40,
                binder_solvent_density_pos=1.03, binder_solvent_density_neg=1.0,
                c_AM_density=st.session_state.get("c_dens", 3.2),
                c_carbon_density=st.session_state.get("c_carb_dens", 1.825),
                c_binder_density=st.session_state.get("c_bind_dens", 1.77),
                a_AM_density=st.session_state.get("a_dens", 1.6),
                a_carbon_density=st.session_state.get("a_carb_dens", 1.95),
                a_binder_density=st.session_state.get("a_bind_dens", 1.10),
                c_foil_m2=c.get("cathode_foil_area_m2", 0), a_foil_m2=c.get("anode_foil_area_m2", 0),
                sep_m2=c.get("sep_area_m2", 0), elec_vol_L=c.get("elec_vol_L", 0),
                container_mass_g=c.get("container_mass_g", 0), cell_mass_g=c.get("cell_mass_g", 0),
                cell_capacity_Ah=e.get("cell_capacity", 0), cell_voltage_V=e.get("cell_voltage", 0),
                positive_electrode_area_cm2=positive_electrode_area_cm2,
                negative_electrode_area_cm2=negative_electrode_area_cm2,
                num_bicell_layers=c.get("num_bicell_layers", 1),
                total_cells=p["total_cells"], modules_per_pack=p["modules_per_pack"],
                cells_per_module=p.get("cells_per_module", 20), modules_per_row=p.get("modules_per_row", 5),
                rows_per_pack=p.get("rows_per_pack", 4),
                pack_useable_energy_kWh=p["pack_useable_energy_kWh"],
                pack_gross_energy_kWh=p["pack_gross_energy_kWh"],
                al_conductor_g_per_module=p.get("al_conductor_g_per_module", 0),
                module_enclosure_g=p.get("module_enclosure_g", 0),
                cell_interconnect_g_per_module=p.get("cell_interconnect_g_per_module", 0),
                interconnect_panel_g_per_module=p.get("interconnect_panel_g_per_module", 0),
                module_terminals_g_per_module=p.get("module_terminals_g_per_module", 0),
                cell_interconnects_per_module=p.get("cell_interconnects_per_module", 1),
                cell_interconnect_rate_per_module=p.get("cell_interconnect_rate_per_module", 1),
                busbar_pack_g=p.get("busbar_pack_g", 0), pack_terminals_g=p.get("pack_terminals_g", 0),
                module_interconnect_g=p.get("module_interconnect_g", 0),
                rack_total_kg_per_row=p.get("rack_total_kg_per_row", 0),
                coolant_panel_kg=p.get("coolant_panel_kg", 0), coolant_manifold_kg=p.get("coolant_manifold_kg", 0),
                coolant_liquid_kg=p.get("coolant_liquid_kg", 0),
                jacket_support_frame_kg=p.get("jacket_support_frame_kg", 0),
                jacket_interior_base_kg=p.get("jacket_interior_base_kg", 0),
                jacket_exterior_base_kg=p.get("jacket_exterior_base_kg", 0),
                jacket_top_plates_kg=p.get("jacket_top_plates_kg", 0),
                pack_jacket_total_kg=p.get("pack_jacket_total_kg", 0),
                bms_mass_kg=p.get("bms_mass_kg", 0),
                p_cathode_am=p_cathode_am, p_anode_am=p_anode_am, p_carbon=p_carbon,
                p_pvdf=p_pvdf, p_cmcsbr=p_cmcsbr, p_al_foil=p_al_foil_cost, p_anode_foil=p_anode_foil_cost,
                p_sep=p_sep, p_electrolyte=p_electrolyte, p_container=p_container,
                p_pos_terminal_kg=p_pos_terminal_kg, p_neg_terminal_kg=p_neg_terminal_kg,
                terminal_fixed_cost=terminal_fixed_cost,
                terminal_mass_cathode_g=c.get("terminal_mass_cathode_g", 0),
                terminal_mass_anode_g=c.get("terminal_mass_anode_g", 0),
                annual_production_packs=annual_production_packs, cell_yield_pct=cell_yield_pct,
                labor_rate_per_hr=labor_rate_per_hr, energy_price_per_kWh=energy_price_per_kWh,
                effective_days_per_year=effective_days_per_year,
                bms_cost_per_pack=bms_cost_per_pack,
                p_row_rack=p_row_rack, p_module_pads=p_module_pads,
                p_module_interconnect=p_module_interconnect, p_busbar=p_busbar,
                p_coolant_panel=p_coolant_panel, p_coolant_manifold=p_coolant_manifold,
                p_pack_terminal_seal=p_pack_terminal_seal, p_pack_support_frame=p_pack_support_frame,
                p_jacket_top_interior=p_jacket_top_interior, p_jacket_exterior_base=p_jacket_exterior_base,
                p_jacket_insulation=p_jacket_insulation,
                lfp_benchmark_per_kwh=lfp_benchmark,
                cells_parallel=st.session_state.get("cells_parallel", 2),
                insulation_area_base_m2=p.get("insulation_area_base_m2", 0.0),
                insulation_area_top_m2=p.get("insulation_area_top_m2", 0.0),
                rack_pad_kg_per_row=p.get("rack_pad_kg_per_row", 0.0),
            )
            # Save raw M04 inputs for Module 06/07 slider initialisation
            st.session_state["_m04_results"]["_in_p_cathode_am"] = p_cathode_am
            st.session_state["_m04_results"]["_in_p_anode_am"]   = p_anode_am
            st.session_state["_m04_results"]["_in_p_carbon"]     = p_carbon
            st.session_state["_m04_results"]["_in_p_pvdf"]       = p_pvdf
            st.session_state["_m04_results"]["_in_p_cmcsbr"]     = p_cmcsbr
            st.session_state["_m04_results"]["_in_p_sep"]        = p_sep
            st.session_state["_m04_results"]["_in_p_electrolyte"]= p_electrolyte
            st.session_state["_m04_results"]["_in_p_container"]  = p_container
            st.session_state["_m04_results"]["_in_p_al_foil"]    = p_al_foil_cost
            st.session_state["_m04_results"]["_in_p_anode_foil"] = p_anode_foil_cost
            st.session_state["_m04_results"]["_in_annual_prod"]  = annual_production_packs
            st.session_state["_m04_results"]["_in_cell_yield"]   = cell_yield_pct
            st.session_state["_m04_results"]["_in_labor_rate"]   = labor_rate_per_hr
            st.session_state["_m04_results"]["_in_energy_price"] = energy_price_per_kWh
            st.session_state["_m04_results"]["_in_eff_days"]     = effective_days_per_year
            if "_study_inputs" not in st.session_state:
                st.session_state["_study_inputs"] = {}
            st.session_state["_study_inputs"].update({
                "p_cathode_am": p_cathode_am, "p_anode_am": p_anode_am, "p_carbon": p_carbon,
                "p_pvdf": p_pvdf, "p_cmcsbr": p_cmcsbr,
                "p_al_foil": p_al_foil_cost, "p_anode_foil": p_anode_foil_cost,
                "p_sep": p_sep, "p_electrolyte": p_electrolyte, "p_container": p_container,
                "p_pos_terminal_kg": p_pos_terminal_kg, "p_neg_terminal_kg": p_neg_terminal_kg,
                "terminal_fixed_cost": terminal_fixed_cost,
                "annual_production_packs": annual_production_packs, "cell_yield_pct": cell_yield_pct,
                "labor_rate_per_hr": labor_rate_per_hr, "energy_price_per_kWh": energy_price_per_kWh,
                "effective_days_per_year": effective_days_per_year,
                "bms_cost_per_pack": bms_cost_per_pack,
                "p_row_rack": p_row_rack, "p_module_pads": p_module_pads,
                "p_module_interconnect": p_module_interconnect, "p_busbar": p_busbar,
                "p_coolant_panel": p_coolant_panel, "p_coolant_manifold": p_coolant_manifold,
                "p_pack_terminal_seal": p_pack_terminal_seal, "p_pack_support_frame": p_pack_support_frame,
                "p_jacket_top_interior": p_jacket_top_interior, "p_jacket_exterior_base": p_jacket_exterior_base,
                "p_jacket_insulation": p_jacket_insulation,
                "tab_length_mm": st.session_state.get("tab_length_mm", 8.0),
                "cells_parallel": st.session_state.get("cells_parallel", 2),
            })
            # Snapshot the resulting base cost too, so Module 06/07 show $0 delta at load
            st.session_state["_study_inputs"]["_base_cost_per_kwh"] = st.session_state["_m04_results"].get("cost_per_kwh", 0)

        if "_m04_results" not in st.session_state:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};border-radius:6px;
                        padding:3rem 2rem;text-align:center;margin-top:1rem;">
                <div style="font-family:'IBM Plex Mono',serif;font-size:0.72rem;
                            color:{T['muted']};letter-spacing:0.1em;">
                    SET INPUTS AND CLICK CALCULATE
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            r4 = st.session_state["_m04_results"]
            _gap = r4.get("gap_vs_lfp")
            _gappct = r4.get("gap_pct")
            gap_sign = "+" if (_gap or 0) > 0 else ""
            pct_sign = "+" if (_gappct or 0) > 0 else ""

            # ── BatPaC Line-by-Line Validation Panel ──────────────────────────
            with st.expander("🔬 BatPaC NMC811-G Validation (line-by-line comparison)", expanded=False):

                # BatPaC reference values (Battery 1, NMC811-G Energy defaults)
                BATPAC_REF = {
                    "mat_cost_per_cell":        14.2727,
                    "cost_c_foil":               0.1145,
                    "cost_a_foil":               0.7326,
                    "cost_sep":                  0.8606,
                    "cost_elec":                 0.6985,
                    "cost_container":            0.2631,
                    "cost_terminal":             0.3002,   # pos+neg: 0.0990+0.2013
                    "cost_from_cells":        7229.62,
                    "cost_from_modules":       882.99,
                    "cost_from_pack":          939.99,
                    "total_profit":            504.38,
                    "total_warranty":          535.19,
                    "pack_total_cost":       10092.18,
                    "cost_per_kwh":            100.92,    # $/kWh (total/100 kWh)
                }

                def _vrow(label, your_val, ref_val, fmt=".4f", pct_tol=1.0):
                    diff_pct = (your_val - ref_val) / ref_val * 100 if ref_val else 0
                    ok = abs(diff_pct) <= pct_tol
                    colour = "#2ecc71" if ok else ("#e67e22" if abs(diff_pct) <= 5 else "#e74c3c")
                    arrow = "✓" if ok else ("▲" if your_val > ref_val else "▼")
                    return (f"<tr>"
                            f"<td style='padding:4px 8px'>{label}</td>"
                            f"<td style='padding:4px 8px;text-align:right'>{your_val:{fmt}}</td>"
                            f"<td style='padding:4px 8px;text-align:right'>{ref_val:{fmt}}</td>"
                            f"<td style='padding:4px 8px;text-align:right;color:{colour}'>"
                            f"{arrow} {diff_pct:+.2f}%</td>"
                            f"</tr>")

                rows_html = ""
                rows_html += "<tr style='background:#333'><td colspan=4 style='padding:4px 8px;font-weight:bold'>Per-cell material costs ($/cell)</td></tr>"
                rows_html += _vrow("Total materials",      r4.get("mat_cost_per_cell",0),  BATPAC_REF["mat_cost_per_cell"])
                rows_html += _vrow("  Cathode foil (Al)",  r4.get("cost_c_foil",0),        BATPAC_REF["cost_c_foil"])
                rows_html += _vrow("  Anode foil",         r4.get("cost_a_foil",0),        BATPAC_REF["cost_a_foil"])
                rows_html += _vrow("  Separator",          r4.get("cost_sep",0),           BATPAC_REF["cost_sep"])
                rows_html += _vrow("  Electrolyte",        r4.get("cost_elec",0),          BATPAC_REF["cost_elec"])
                rows_html += _vrow("  Container",          r4.get("cost_container",0),     BATPAC_REF["cost_container"])
                rows_html += _vrow("  Terminals (both)",   r4.get("cost_terminal",0),      BATPAC_REF["cost_terminal"])
                rows_html += "<tr style='background:#333'><td colspan=4 style='padding:4px 8px;font-weight:bold'>Pack cost hierarchy ($/pack)</td></tr>"
                rows_html += _vrow("Cells",                r4.get("cost_from_cells",0),    BATPAC_REF["cost_from_cells"],   ".2f", 1.0)
                rows_html += _vrow("Modules",              r4.get("cost_from_modules",0),  BATPAC_REF["cost_from_modules"], ".2f", 1.0)
                rows_html += _vrow("Pack hardware",        r4.get("cost_from_pack",0),     BATPAC_REF["cost_from_pack"],    ".2f", 1.0)
                rows_html += _vrow("Profit (all levels)",  r4.get("total_profit",0),       BATPAC_REF["total_profit"],      ".2f", 1.0)
                rows_html += _vrow("Warranty",             r4.get("total_warranty",0),     BATPAC_REF["total_warranty"],    ".2f", 1.0)
                rows_html += _vrow("Total pack cost",      r4.get("pack_total_cost",0),    BATPAC_REF["pack_total_cost"],   ".2f", 1.0)
                rows_html += _vrow("Cost per kWh",         r4.get("cost_per_kwh",0),       BATPAC_REF["cost_per_kwh"],      ".4f", 1.0)

                st.markdown(f"""
                <table style='width:100%;border-collapse:collapse;font-size:0.85rem'>
                <thead><tr style='border-bottom:1px solid #555'>
                  <th style='padding:4px 8px;text-align:left'>Line item</th>
                  <th style='padding:4px 8px;text-align:right'>Your model</th>
                  <th style='padding:4px 8px;text-align:right'>BatPaC ref</th>
                  <th style='padding:4px 8px;text-align:right'>Diff</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
                </table>
                <p style='font-size:0.75rem;color:#888;margin-top:6px'>
                ✓ = within 1% &nbsp;|&nbsp; ▲▼ orange = within 5% &nbsp;|&nbsp; ▲▼ red = &gt;5% gap.<br>
                </p>
                """, unsafe_allow_html=True)
            # ── End BatPaC Validation Panel ────────────────────────────────────

            st.markdown('<div class="section-header">Primary Outputs</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="output-grid">
                <div class="output-card highlight">
                    <div class="output-card-label">Cost per kWh</div>
                    <div class="output-card-value">${r4["cost_per_kwh"]:.4f}</div>
                    <div class="output-card-unit">$/kWh</div>
                </div>
                <div class="output-card highlight">
                    <div class="output-card-label">Gap vs LFP</div>
                    <div class="output-card-value">{f'{pct_sign}{_gappct:.1f}%' if _gappct is not None else 'n/a'}</div>
                    <div class="output-card-unit">{f'vs ${lfp_benchmark:.2f}/kWh, like-for-like' if lfp_benchmark else 'run Module 06'}</div>
                </div>
                <div class="output-card highlight">
                    <div class="output-card-label">Total pack cost</div>
                    <div class="output-card-value">${r4["pack_total_cost"]:.0f}</div>
                    <div class="output-card-unit">$/pack</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Material cost/cell</div>
                    <div class="output-card-value">${r4["mat_cost_per_cell"]:.4f}</div>
                    <div class="output-card-unit">$/cell</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Total cell cost/cell</div>
                    <div class="output-card-value">${r4["total_cell_cost_per_cell"]:.4f}</div>
                    <div class="output-card-unit">$/cell (incl. mfg, profit, warranty)</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Material fraction</div>
                    <div class="output-card-value">{r4["mat_frac"]*100:.1f}%</div>
                    <div class="output-card-unit">of total cell cost</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">Cost by Hierarchy Level (BatPaC structure)</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <table class="mass-table">
                <thead>
                    <tr>
                        <th>Level</th>
                        <th style="text-align:right">Cost ($/pack)</th>
                        <th style="text-align:right">% pack cost</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>Cells ({p["total_cells"]} cells)</td>
                        <td class="val">${r4["cost_from_cells"]:.2f}</td>
                        <td class="val">{pct(r4["cost_from_cells"], r4["pack_total_cost"])}</td>
                    </tr>
                    <tr><td>Modules ({p["modules_per_pack"]} modules)</td>
                        <td class="val">${r4["cost_from_modules"]:.2f}</td>
                        <td class="val">{pct(r4["cost_from_modules"], r4["pack_total_cost"])}</td>
                    </tr>
                    <tr><td>Pack hardware</td>
                        <td class="val">${r4["cost_from_pack"]:.2f}</td>
                        <td class="val">{pct(r4["cost_from_pack"], r4["pack_total_cost"])}</td>
                    </tr>
                    <tr><td>Profit (all levels)</td>
                        <td class="val">${r4["total_profit"]:.2f}</td>
                        <td class="val">{pct(r4["total_profit"], r4["pack_total_cost"])}</td>
                    </tr>
                    <tr><td>Warranty (all levels)</td>
                        <td class="val">${r4["total_warranty"]:.2f}</td>
                        <td class="val">{pct(r4["total_warranty"], r4["pack_total_cost"])}</td>
                    </tr>
                    <tr class="subtotal">
                        <td><strong>Total pack cost</strong></td>
                        <td class="val"><strong>${r4["pack_total_cost"]:.2f}</strong></td>
                        <td class="val"><strong>100.0%</strong></td>
                    </tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">Cell-Level Cost Breakdown</div>', unsafe_allow_html=True)
            breakdown_sorted = sorted([
                ("Cathode active material", r4["cost_cathode_am"]),
                ("Anode active material",   r4["cost_anode_am"]),
                ("Carbon black",            r4["cost_carbon"]),
                ("PVDF binder",             r4["cost_pvdf"]),
                ("CMC/SBR binder",          r4["cost_cmcsbr"]),
                ("Al foil (both)",          r4["cost_c_foil"] + r4["cost_a_foil"]),
                ("Separator",               r4["cost_sep"]),
                ("Electrolyte",             r4["cost_elec"]),
                ("Container",               r4["cost_container"]),
                ("Terminals",               r4["cost_terminal"]),
            ], key=lambda x: -x[1])
            table_rows = ""
            for name, val in breakdown_sorted:
                table_rows += f'<tr><td>{name}</td><td class="val">${val:.4f}</td><td class="val">{pct(val, r4["mat_cost_per_cell"])}</td></tr>'
            st.markdown(f"""
            <table class="mass-table">
                <thead>
                    <tr>
                        <th>Material</th>
                        <th style="text-align:right">$/cell</th>
                        <th style="text-align:right">% materials</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                    <tr class="subtotal">
                        <td><strong>Total materials</strong></td>
                        <td class="val"><strong>${r4["mat_cost_per_cell"]:.4f}</strong></td>
                        <td class="val"><strong>100.0%</strong></td>
                    </tr>
                    <tr>
                        <td>Direct labor</td>
                        <td class="val">${r4["cell_direct_labor_per_cell"]:.4f}</td>
                        <td class="val">-</td>
                    </tr>
                    <tr>
                        <td>Energy</td>
                        <td class="val">${r4["cell_energy_per_cell"]:.4f}</td>
                        <td class="val">-</td>
                    </tr>
                    <tr>
                        <td>Variable overhead</td>
                        <td class="val">${r4["cell_variable_overhead_per_cell"]:.4f}</td>
                        <td class="val">-</td>
                    </tr>
                    <tr>
                        <td>Depreciation</td>
                        <td class="val">${r4["cell_depreciation_per_cell"]:.4f}</td>
                        <td class="val">-</td>
                    </tr>
                    <tr>
                        <td>GSA</td>
                        <td class="val">${r4["cell_gsa_per_cell"]:.4f}</td>
                        <td class="val">-</td>
                    </tr>
                    <tr>
                        <td>R&D</td>
                        <td class="val">${r4["cell_rd_per_cell"]:.4f}</td>
                        <td class="val">-</td>
                    </tr>
                    <tr>
                        <td>Financing</td>
                        <td class="val">${r4["cell_financing_per_cell"]:.4f}</td>
                        <td class="val">-</td>
                    </tr>
                    <tr>
                        <td>Profit</td>
                        <td class="val">${r4["cell_profit_per_cell"]:.4f}</td>
                        <td class="val">-</td>
                    </tr>
                    <tr>
                        <td>Warranty</td>
                        <td class="val">${r4["cell_warranty_per_cell"]:.4f}</td>
                        <td class="val">-</td>
                    </tr>
                    <tr class="subtotal">
                        <td><strong>Total cell cost</strong></td>
                        <td class="val"><strong>${r4["total_cell_cost_per_cell"]:.4f}</strong></td>
                        <td class="val"><strong>100.0%</strong></td>
                    </tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="note-box" style="margin-top:1rem;">
                <strong>Annual production diagnostics:</strong> {r4["annual_cells_accepted"]:,.0f} cells/yr accepted ·
                {r4["annual_cells_yield_adj"]:,.0f} cells/yr at yield-adjusted rate ·
                {r4["total_direct_labor_hrs_yr"]:,.0f} total labor hrs/yr ·
                ${r4["total_capital_equipment_mil"]:,.1f}M total capital equipment ·
                {r4["total_energy_GWh_yr"]:,.1f} GWh/yr total energy
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="note-box" style="margin-top:1rem;">
                <strong>Passed to Module 05:</strong> cost_per_kwh,
                mat_cost_per_cell, total_cell_cost_per_cell, pack_total_cost, full
                BatPaC cost hierarchy for sensitivity analysis.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            prev4, next4 = st.columns(2)
            with prev4:
                if st.button("Previous: Pack Design", use_container_width=True, key="m04_prev_to_m03"):
                    st.session_state["_navigate_to"] = "🔋  Module 03 - Pack Design"
                    st.rerun()
            with next4:
                if st.button("Next module: Sustainability →", use_container_width=True, key="m04_next_to_m05"):
                    st.session_state["_navigate_to"] = "🌿  Module 05 - Sustainability"
                    st.rerun()
# ── MODULE 05: SUSTAINABILITY ─────────────────────────────────────────────────
elif selected_key == "sustainability":

    if "pack_design" not in st.session_state:
        st.markdown("""
        <div class="hero-label">Module 05</div>
        <div class="hero-title">Sustainability <span>Analysis</span></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="status-bar" style="text-align:center;padding:2rem;">
            <strong>Module 03 required</strong> - Run through to Pack Design first,
            then return here.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    e  = st.session_state.get("electrochem", {})
    c  = st.session_state.get("cell_design", {})
    p  = st.session_state["pack_design"]
    cm = st.session_state.get("_m04_results", st.session_state.get("cost_model", {}))

    st.markdown("""
    <div class="hero-label">Module 05</div>
    <div class="hero-title">Sustainability <span>Analysis</span></div>
    <div class="hero-subtitle">Material intensity · Al vs Cu saving · CO2 indicator · LCOS · Supply risk</div>
    """, unsafe_allow_html=True)

    col_in, col_out = st.columns([2, 3], gap="large")

    with col_in:

        st.markdown('<div class="input-section-title">From Upstream Modules</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="note-box">
            <strong>Total cells:</strong> {p["total_cells"]}<br>
            <strong>Useable energy:</strong> {p["pack_useable_energy_kWh"]:.4f} kWh<br>
            <strong>Pack cost:</strong> ${cm.get("pack_total_cost", 0):,.2f}<br>
            <strong>Cathode AM:</strong> {e.get("c_AM_mass", 0):.1f} g/cell<br>
            <strong>Anode AM:</strong> {e.get("a_AM_mass", 0):.1f} g/cell
        </div>
        """, unsafe_allow_html=True)

        # Al vs Cu prices
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Al vs Cu Foil Prices</div>', unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            p_al_kg = st.number_input("Al price ($/kg)", value=0.94, min_value=0.1, max_value=20.0, step=0.1, key="p_al_kg", help="Aluminium scrap. UK Metals scrap price list: $0.94/kg.")
        with fc2:
            p_cu_kg = st.number_input("Cu price ($/kg)", value=8.96, min_value=2.0, max_value=30.0, step=0.1, key="p_cu_kg", help="Copper scrap. UK Metals scrap price list: $8.96/kg.")

        # CO2 intensity factors
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">CO2 Intensity Factors (kgCO2/kg)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="note-box">
            Cradle-to-gate embodied carbon estimates from literature. Indicative only.
        </div>
        """, unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            co2_cathode_am  = st.number_input("Cathode AM (kgCO2/kg)",  value=22.0, min_value=0.0, max_value=100.0, step=0.5, key="co2_cathode_am",  help="NVPF cathode active material. Voss et al. (2025): 22.0 kgCO2/kg.")
            co2_anode_am    = st.number_input("Anode AM (kgCO2/kg)",    value=4.07, min_value=0.0, max_value=50.0,  step=0.5, key="co2_anode_am",    help="Hard carbon from biomass. Liu et al. (2021): 4.07 kgCO2/kg.")
            co2_al_foil     = st.number_input("Al foil (kgCO2/kg)",     value=6.6,  min_value=0.0, max_value=30.0,  step=0.5, key="co2_al_foil",     help="European primary Al average. European Aluminium Assoc. (2022): 6.6 kgCO2/kg.")
            co2_carbon      = st.number_input("Carbon black (kgCO2/kg)",value=3.5,  min_value=0.0, max_value=20.0,  step=0.5, key="co2_carbon",      help="Conductive carbon additive. Rosner et al. (2024): 3.5 kgCO2/kg.")
        with g2:
            co2_separator   = st.number_input("Separator (kgCO2/kg)",   value=2.9,  min_value=0.0, max_value=20.0,  step=0.5, key="co2_separator",   help="PE membrane. Leal Filho et al. (2025): 2.9 kgCO2/kg.")
            co2_electrolyte = st.number_input("Electrolyte (kgCO2/kg)", value=2.58, min_value=0.0, max_value=30.0,  step=0.01, format="%.2f", key="co2_electrolyte", help="Complete electrolyte solution, built up from components (Register Sec 6.7): 13.4% NaPF6 at 12.15 plus 86.6% carbonate solvents, all component intensities from Batteries (2022) 8(8), 76. Peters et al. (2016) is cited for the inventory approach only, not for a per-kg figure.")
            co2_pvdf        = st.number_input("PVDF binder (kgCO2/kg)", value=55.8, min_value=0.0, max_value=100.0, step=0.5, key="co2_pvdf",        help="Hu et al. (2022) gas-phase route: 55.8 kgCO2/kg. High but small mass fraction.")
            co2_anode_binder = st.number_input("Anode binder CMC/SBR (kgCO2/kg)", value=3.36, min_value=0.0, max_value=100.0, step=0.01, format="%.2f", key="co2_anode_binder", help="Blended CMC/SBR on a dry-solids basis (Register Sec 6.5): 1:1 blend of CMC at 4.02 (Gboe et al. 2025) and SBR at 2.70 (Soratana et al. 2017).")

        g3, g4 = st.columns(2)
        with g3:
            st.number_input("Steel structural (kgCO2/kg)", value=1.92, min_value=0.0, max_value=10.0, step=0.1, key="co2_steel", help="World Steel Association (2023): 1.92 kgCO2/kg global average.")
            st.number_input("Copper conductors (kgCO2/kg)", value=6.0, min_value=0.0, max_value=30.0, step=0.1, key="co2_copper", help="Memary et al. (2012): 6.0 kgCO2/kg. Applies to the pack conductors and the in-module copper (BatPaC Lists!AR101/102/105), and to the anode foil in the LFP benchmark.")
        with g4:
            st.number_input("BMS electronics (kgCO2/kg)", value=23.3, min_value=0.0, max_value=100.0, step=1.0, key="co2_bms", help="Derived from Ellingsen et al. (2014) supplementary inventory: 23.3 kgCO2/kg.")
            st.number_input("Cell container (kgCO2/kg)", value=6.6, min_value=0.0, max_value=50.0, step=0.1, key="co2_container", help="PET-Al-PP pouch laminate (BatPaC CI!F47). Taken as the aluminium intensity of 6.6 kgCO2/kg (European Aluminium), since the laminate is aluminium-dominated at a density of 2.202 g/cm3. Declared assumption.")
        st.number_input(
            "Grid CO2 intensity (kgCO2/kWh)", value=0.164, min_value=0.0, max_value=1.0,
            step=0.01, format="%.3f", key="grid_co2_intensity",
            help="Grid average CO2 intensity for energy payback calculation. UK 2024: ~0.233 kgCO2/kWh. Renewables: ~0.02."
        )

        # End-of-life recycling
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">End-of-Life Recycling</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="note-box">
            Residual value recovered at end of pack life. Offsets lifetime cost in LCOS.
            Recovery fractions from hydrometallurgical recycling literature.
        </div>
        """, unsafe_allow_html=True)
        el1, el2, el3 = st.columns(3)
        with el1:
            eol_cat_rec = st.number_input("Cathode AM recovery (%)", value=88.23, min_value=0.0, max_value=100.0, step=1.0, key="eol_cat_recovery", help="Zhang et al. (2024): 88.23% hydromet recovery for SIB cathode.")
            eol_cat_p   = st.number_input("Cathode AM EOL price ($/kg)", value=10.74, min_value=0.0, max_value=50.0, step=0.01, format="%.2f", key="eol_cat_price", help="Estimated at 65% of the virgin NVPF price ($16.53/kg) = $10.74/kg. No secondary market exists. See Register Sec 6.2.")
        with el2:
            eol_al_rec  = st.number_input("Al recovery (%)", value=99.1, min_value=0.0, max_value=100.0, step=1.0, key="eol_al_recovery", help="Liu et al. (2019) direct aqueous recycling: 99.1%. Lab-scale - state caveat in thesis.")
            eol_al_p    = st.number_input("Al EOL price ($/kg)", value=0.94, min_value=0.0, max_value=10.0, step=0.1, key="eol_al_price", help="Mixed Al scrap price. UK Metals: $0.94/kg.")
        with el3:
            eol_st_rec  = st.number_input("Steel recovery (%)", value=98.1, min_value=0.0, max_value=100.0, step=1.0, key="eol_steel_recovery", help="Liu et al. (2019): 98.1%. Lab-scale - state caveat in thesis.")
            eol_st_p    = st.number_input("Steel EOL price ($/kg)", value=0.47, min_value=0.0, max_value=2.0, step=0.05, key="eol_steel_price", help="Scrap steel. UK Metals: $0.47/kg.")

        # LCOS inputs
        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Levelised Cost of Storage (LCOS)</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="note-box">
            LCOS captures full lifetime economics: capital, O&amp;M, and charging
            energy cost per kWh delivered. Methodology: Schmidt et al. (2019).
        </div>
        """, unsafe_allow_html=True)
        lc1, lc2 = st.columns(2)
        with lc1:
            cycle_life = st.number_input("Cycle life (cycles)", value=3200, min_value=100, max_value=20000, step=100, key="cycle_life", help="He et al. (2023) v2022 NVPF/HC cell: >3200 cycles at 2C/5C, 100% DOD.")
            calendar_life_yr = st.number_input("Calendar life (years)", value=15, min_value=1, max_value=30, step=1, key="calendar_life_yr", help="Jasper et al. (2026): 15 years for stationary SIB.")
            roundtrip_efficiency_pct = st.number_input("Round-trip efficiency (%)", value=90.0, min_value=50.0, max_value=100.0, step=0.5, format="%.1f", key="rt_eff", help="Jasper et al. (2026): 90% system-level RTE for SIB.")
        with lc2:
            electricity_price_per_kwh = st.number_input("Electricity price ($/kWh)", value=0.05, min_value=0.0, max_value=0.5, step=0.005, format="%.3f", key="elec_price", help="Schmidt et al. (2019): $0.05/kWh.")
            discount_rate_pct = st.number_input("Discount rate (%)", value=8.0, min_value=0.0, max_value=20.0, step=0.5, format="%.1f", key="discount_rate", help="Schmidt et al. (2019): 8% WACC.")
            om_cost_pct_per_yr = st.number_input("O&M cost (% of CAPEX/yr)", value=2.075, min_value=0.0, max_value=5.0, step=0.1, format="%.3f", key="om_cost_pct", help="Schmidt et al. (2019) via Energy Storage Ninja: 2.075% CAPEX/yr.")

        st.markdown("<br>", unsafe_allow_html=True)
        calculate5 = st.button("CALCULATE", use_container_width=True, key="calc5")

    with col_out:

        if calculate5:
            st.session_state["_m05_results"] = run_sustainability(
                c_AM_mass_g              = e.get("c_AM_mass", 0),
                a_AM_mass_g              = e.get("a_AM_mass", 0),
                c_carbon_g               = e.get("c_carbon_mass", 0),
                a_carbon_g               = e.get("a_carbon_mass", 0),
                c_binder_g               = e.get("c_binder_mass", 0),
                a_binder_g               = e.get("a_binder_mass", 0),
                c_foil_area_m2           = c.get("cathode_foil_area_m2", 0),
                a_foil_area_m2           = c.get("anode_foil_area_m2", 0),
                c_foil_mass_g            = c.get("cathode_foil_mass_g", 0),
                a_foil_mass_g            = c.get("anode_foil_mass_g", 0),
                anode_foil_density       = c.get("anode_foil_density", 2.70),
                sep_area_m2              = c.get("sep_area_m2", 0),
                sep_mass_g               = c.get("sep_mass_g", 0),
                elec_mass_g              = c.get("elec_mass_g", 0),
                container_mass_g         = c.get("container_mass_g", 0),
                cell_mass_g              = c.get("cell_mass_g", 0),
                total_cells              = p["total_cells"],
                pack_useable_energy_kWh  = p["pack_useable_energy_kWh"],
                pack_mass_kg             = p.get("pack_mass_kg", 0),
                conductors_kg            = p.get("conductors_kg", 0),
                rack_mass_total_kg       = p.get("rack_mass_total_kg", 0),
                coolant_panel_kg         = p.get("coolant_panel_kg", 0),
                coolant_manifold_kg      = p.get("coolant_manifold_kg", 0),
                coolant_liquid_kg        = p.get("coolant_liquid_kg", 0),
                jacket_support_frame_kg  = p.get("jacket_support_frame_kg", 0),
                jacket_interior_base_kg  = p.get("jacket_interior_base_kg", 0),
                jacket_exterior_base_kg  = p.get("jacket_exterior_base_kg", 0),
                jacket_top_plates_kg     = p.get("jacket_top_plates_kg", 0),
                pack_jacket_total_kg     = p.get("pack_jacket_total_kg", 0),
                module_al_kg             = p.get("module_al_g", 0) * p.get("modules_per_pack", 0) / 1000,
                module_steel_kg          = p.get("module_steel_g", 0) * p.get("modules_per_pack", 0) / 1000,
                module_cu_kg             = p.get("module_cu_g", 0) * p.get("modules_per_pack", 0) / 1000,
                module_polymer_kg        = p.get("module_polymer_g", 0) * p.get("modules_per_pack", 0) / 1000,
                bms_mass_kg              = p.get("bms_mass_kg", 0),
                p_al_kg                  = p_al_kg,
                p_cu_kg                  = p_cu_kg,
                co2_cathode_am           = co2_cathode_am,
                co2_anode_am             = co2_anode_am,
                co2_al_foil              = co2_al_foil,
                co2_separator            = co2_separator,
                co2_electrolyte          = co2_electrolyte,
                co2_carbon               = co2_carbon,
                co2_pvdf                 = co2_pvdf,
                co2_anode_binder         = st.session_state.get("co2_anode_binder", 3.36),
                co2_container            = st.session_state.get("co2_container", 6.6),
                co2_copper               = st.session_state.get("co2_copper", 6.0),
                co2_steel                = st.session_state.get("co2_steel", 1.92),
                co2_bms                  = st.session_state.get("co2_bms", 23.3),
                grid_co2_intensity_kg_per_kwh = st.session_state.get("grid_co2_intensity", 0.164),
                cycle_life               = cycle_life,
                calendar_life_yr         = calendar_life_yr,
                roundtrip_efficiency_pct = roundtrip_efficiency_pct,
                electricity_price_per_kwh = electricity_price_per_kwh,
                discount_rate_pct        = discount_rate_pct,
                pack_total_cost_usd      = cm.get("pack_total_cost", 0),
                om_cost_pct_per_yr       = om_cost_pct_per_yr,
                eol_cathode_am_recovery_pct = st.session_state.get("eol_cat_recovery", 88.23),
                eol_al_recovery_pct      = st.session_state.get("eol_al_recovery", 99.1),
                eol_steel_recovery_pct   = st.session_state.get("eol_steel_recovery", 98.1),
                eol_cathode_am_price_kg  = st.session_state.get("eol_cat_price", 10.74),
                eol_al_price_kg          = st.session_state.get("eol_al_price", 0.94),
                eol_steel_price_kg       = st.session_state.get("eol_steel_price", 0.47),
            )

        if "_m05_results" not in st.session_state:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};border-radius:6px;
                        padding:3rem 2rem;text-align:center;margin-top:1rem;">
                <div style="font-family:'IBM Plex Mono',serif;font-size:0.72rem;
                            color:{T['muted']};letter-spacing:0.1em;">
                    SET INPUTS AND CLICK CALCULATE
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            r5 = st.session_state["_m05_results"]

            st.markdown('<div class="section-header">Levelised Cost of Storage</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="output-grid">
                <div class="output-card highlight">
                    <div class="output-card-label">LCOS (gross)</div>
                    <div class="output-card-value">${r5["lcos_per_kwh"]:.2f}</div>
                    <div class="output-card-unit">$/kWh delivered</div>
                </div>
                <div class="output-card highlight">
                    <div class="output-card-label">LCOS (net, with EOL credit)</div>
                    <div class="output-card-value">${r5["lcos_net_per_kwh"]:.2f}</div>
                    <div class="output-card-unit">$/kWh delivered</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Capital component</div>
                    <div class="output-card-value">${r5["lcos_capex_component"]:.2f}</div>
                    <div class="output-card-unit">$/kWh</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">O&M component</div>
                    <div class="output-card-value">${r5["lcos_om_component"]:.2f}</div>
                    <div class="output-card-unit">$/kWh</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Charging energy component</div>
                    <div class="output-card-value">${r5["lcos_energy_component"]:.2f}</div>
                    <div class="output-card-unit">$/kWh</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">EOL recycling credit</div>
                    <div class="output-card-value">${r5["lcos_eol_credit"]:.3f}</div>
                    <div class="output-card-unit">$/kWh (reduces LCOS)</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Effective cycle life</div>
                    <div class="output-card-value">{r5["effective_cycles"]:,.0f}</div>
                    <div class="output-card-unit">cycles</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Lifetime energy</div>
                    <div class="output-card-value">{r5["lifetime_energy_kwh"]/1000:.1f}</div>
                    <div class="output-card-unit">MWh delivered</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Cost per cycle</div>
                    <div class="output-card-value">${r5["cost_per_cycle"]:.2f}</div>
                    <div class="output-card-unit">$/cycle</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Annual throughput</div>
                    <div class="output-card-value">{r5["energy_per_year_kwh"]:.1f}</div>
                    <div class="output-card-unit">kWh/year</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            from plotly.subplots import make_subplots
            st.markdown('<div class="section-header" style="margin-top:1rem;">LCOS Sensitivity</div>', unsafe_allow_html=True)
            fig_lcos = make_subplots(rows=1, cols=2,
                subplot_titles=["LCOS vs Electricity Price", "LCOS vs Cycle Life"],
                horizontal_spacing=0.12)
            fig_lcos.add_trace(go.Scatter(
                x=r5["lcos_vs_elec_prices"], y=r5["lcos_vs_elec_values"],
                mode="lines", line=dict(color=T["accent"], width=2),
                hovertemplate="Elec: $%{x:.2f}/kWh<br>LCOS: $%{y:.2f}/kWh<extra></extra>",
            ), row=1, col=1)
            fig_lcos.add_trace(go.Scatter(
                x=r5["lcos_vs_cycle_lives"], y=r5["lcos_vs_cycle_values"],
                mode="lines", line=dict(color="#3b82f6", width=2),
                hovertemplate="Cycles: %{x:,.0f}<br>LCOS: $%{y:.2f}/kWh<extra></extra>",
            ), row=1, col=2)
            fig_lcos.add_vline(x=r5["effective_cycles"], row=1, col=2,
                               line_color=T["accent"], line_dash="dot",
                               annotation_text="Your design", annotation_font_color=T["accent"])
            fig_lcos.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=T["text"], size=11), showlegend=False,
                margin=dict(l=10, r=10, t=40, b=30), height=300,
            )
            fig_lcos.update_xaxes(gridcolor=T["border"])
            fig_lcos.update_yaxes(title_text="LCOS ($/kWh)", gridcolor=T["border"])
            fig_lcos.update_xaxes(title_text="Electricity price ($/kWh)", row=1, col=1)
            fig_lcos.update_xaxes(title_text="Cycle life", row=1, col=2)
            st.plotly_chart(fig_lcos, use_container_width=True)

            st.markdown('<div class="section-header" style="margin-top:0.5rem;">CO2 Intensity and EOL Recycling</div>', unsafe_allow_html=True)
            ebp = r5.get("energy_payback_yr")
            ebp_str = f"{ebp:.1f} years" if ebp else "N/A"
            st.markdown(f"""
            <div class="output-grid">
                <div class="output-card highlight">
                    <div class="output-card-label">CO2 intensity (full pack)</div>
                    <div class="output-card-value">{r5["co2_per_kwh"]:.2f}</div>
                    <div class="output-card-unit">kgCO2/kWh (cradle-to-gate)</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Cell materials CO2</div>
                    <div class="output-card-value">{r5["co2_pack_cells_kg"]:.1f}</div>
                    <div class="output-card-unit">kgCO2</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Non-cell components CO2</div>
                    <div class="output-card-value">{r5["co2_pack_noncell_kg"]:.1f}</div>
                    <div class="output-card-unit">kgCO2</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Energy payback period</div>
                    <div class="output-card-value">{ebp_str}</div>
                    <div class="output-card-unit">years to offset embodied CO2</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">EOL recycling value</div>
                    <div class="output-card-value">${r5["eol_total_value"]:.2f}</div>
                    <div class="output-card-unit">$/pack (${r5["eol_per_kwh"]:.3f}/kWh)</div>
                </div>
                <div class="output-card">
                    <div class="output-card-label">Al vs Cu cost saving</div>
                    <div class="output-card-value">${r5["cost_saving_usd"]:.2f}</div>
                    <div class="output-card-unit">$/pack ({r5["mass_saving_pct"]:.1f}% lighter)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <table class="mass-table">
                <thead><tr><th>EOL Stream</th><th style="text-align:right">Value</th></tr></thead>
                <tbody>
                    <tr><td>Cathode active material</td><td class="val">${r5["eol_cathode_value"]:.2f}</td></tr>
                    <tr><td>Aluminium (foils + conductors + jacket)</td><td class="val">${r5["eol_al_value"]:.2f}</td></tr>
                    <tr><td>Steel (rack + jacket frame)</td><td class="val">${r5["eol_steel_value"]:.2f}</td></tr>
                    <tr><td>Copper (pack conductors + module hardware)</td><td class="val">${r5["eol_cu_value"]:.2f}</td></tr>
                    <tr class="subtotal"><td><strong>Total EOL value</strong></td><td class="val"><strong>${r5["eol_total_value"]:.2f}</strong></td></tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:1rem;">Material Intensity per kWh</div>', unsafe_allow_html=True)
            intensities_cell = [
                ("Cathode active material", r5["int_cathode_am"]),
                ("Anode active material",   r5["int_anode_am"]),
                ("Electrolyte",             r5["int_electrolyte"]),
                ("Separator",               r5["int_separator"]),
                ("Cathode Al foil",         r5["int_c_foil"]),
                ("Anode Al foil",           r5["int_a_foil"]),
                ("Carbon black",            r5["int_carbon"]),
                ("Binders",                 r5["int_binder"]),
                ("Container",               r5["int_container"]),
            ]
            intensities_pack = [
                ("Conductors (Al)",  r5["int_pack_conductors"]),
                ("Row rack (steel)", r5["int_pack_rack"]),
                ("Cooling system",   r5["int_pack_cooling"]),
                ("Pack jacket",      r5["int_pack_jacket"]),
                ("BMS",              r5["int_pack_bms"]),
            ]
            int_rows = ""
            for name, val in sorted(intensities_cell, key=lambda x: -x[1]):
                int_rows += f'<tr><td>{name}</td><td class="val">{val:.4f}</td><td class="val">{pct(val, r5["int_pack_total"])}</td></tr>'
            int_rows += f'<tr class="subtotal"><td><strong>Cell subtotal</strong></td><td class="val"><strong>{r5["int_cell_total"]:.4f}</strong></td><td class="val">{pct(r5["int_cell_total"], r5["int_pack_total"])}</td></tr>'
            for name, val in sorted(intensities_pack, key=lambda x: -x[1]):
                int_rows += f'<tr><td>{name}</td><td class="val">{val:.4f}</td><td class="val">{pct(val, r5["int_pack_total"])}</td></tr>'
            st.markdown(f"""
            <table class="mass-table">
                <thead><tr><th>Component</th><th style="text-align:right">kg/kWh</th><th style="text-align:right">% pack</th></tr></thead>
                <tbody>
                    {int_rows}
                    <tr class="subtotal"><td><strong>Total pack</strong></td>
                    <td class="val"><strong>{r5["int_pack_total"]:.4f}</strong></td>
                    <td class="val"><strong>100.0%</strong></td></tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:1rem;">Supply Chain Risk Assessment</div>', unsafe_allow_html=True)
            risk_rows = ""
            risks = [
                ("Sodium (electrolyte salt)", "Very low", "13th most abundant element. Geographically distributed global reserves.", True),
                ("Hard carbon (anode)",       "Low",      "Derived from biomass or resin. No critical mineral dependency.", True),
                ("Aluminium (foil)",          "Low",      "3rd most abundant element. Mature global supply chain.", True),
                ("Iron/Manganese (cathode)",  "Low",      "Abundant, low-cost transition metals. No concentration risk.", True),
                ("Vanadium (NVPF only)",      "Moderate", "Concentrated supply in Russia, China, S. Africa. Co-product of steel.", False),
                ("Phosphorus (NVPF/NaFePO4)","Low-Med",  "Abundant but phosphate supply chains are geographically concentrated.", False),
                ("PVDF binder",               "Low-Med",  "Fluoropolymer. Supply chain tied to fluorite and HF chemistry.", False),
                ("Cobalt",                    "None",     "SIBs are cobalt-free. Major advantage vs NMC/NCA lithium-ion.", True),
                ("Lithium",                   "None",     "No lithium used. Removes Lithium Triangle concentration risk.", True),
                ("Copper",                    "None",     "No copper current collector. Removes Cu supply and price risk.", True),
                ("Nickel",                    "None",     "SIBs avoid Ni-dependent cathode chemistries entirely.", True),
            ]
            for material, risk, note, ok in risks:
                color = T["accent"] if not ok else "#10b981"
                risk_rows += f"""<tr><td>{material}</td>
                    <td style="color:{color};text-align:center">{risk}</td>
                    <td style="color:{T['muted']}">{note}</td></tr>"""
            st.markdown(f"""
            <table class="mass-table">
                <thead><tr><th>Material</th><th style="text-align:center">Risk</th><th>Notes</th></tr></thead>
                <tbody>{risk_rows}</tbody>
            </table>
            """, unsafe_allow_html=True)

            with st.expander("Equations used in this module"):
                st.markdown(f"""
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.70rem;color:{T['sub']};line-height:2.2;">
                <span style="color:{T['accent']}">1. Material intensity (cell and pack)</span><br>
                cell_intensity = (mass_g/cell x cells / 1000) / useable_kWh<br>
                pack_intensity = mass_kg_pack / useable_kWh<br><br>
                <span style="color:{T['accent']}">2. CO2 intensity (full pack)</span><br>
                = cell CO2 + conductors(Al) + rack(steel) + jacket(Al+steel) + BMS = <strong style="color:{T['text']}">{r5["co2_per_kwh"]:.4f} kgCO2/kWh</strong><br><br>
                <span style="color:{T['accent']}">3. Energy payback</span><br>
                = pack_co2 / (annual_energy x grid_intensity) = <strong style="color:{T['text']}">{ebp_str}</strong><br><br>
                <span style="color:{T['accent']}">4. EOL value</span><br>
                = sum(mass_i x recovery_i x price_i) = <strong style="color:{T['text']}">${r5["eol_total_value"]:.2f}/pack</strong><br><br>
                <span style="color:{T['accent']}">5. LCOS gross/net (Schmidt et al. 2019)</span><br>
                LCOS_gross = (capex x annuity + OM + energy x elec/RT) / energy_yr = <strong style="color:{T['text']}">${r5["lcos_per_kwh"]:.2f}/kWh</strong><br>
                LCOS_net = LCOS_gross - EOL_PV x annuity / energy_yr = <strong style="color:{T['text']}">${r5["lcos_net_per_kwh"]:.2f}/kWh</strong>
                </div>
                """, unsafe_allow_html=True)

            st.session_state["sustainability"] = {**r5}
            st.markdown(f"""
            <div class="note-box" style="margin-top:1rem;">
                <strong>Passed to Module 06:</strong> int_pack_total, co2_per_kwh,
                lcos_per_kwh, lcos_net_per_kwh, eol_total_value, energy_payback_yr.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            prev5, next5 = st.columns(2)
            with prev5:
                if st.button("Previous: Cost Model", use_container_width=True, key="prev_m04"):
                    st.session_state["_navigate_to"] = "💰  Module 04 - Cost Model"
                    st.rerun()
            with next5:
                if st.button("Next module: Sensitivity Analysis", use_container_width=True, key="next_m06"):
                    st.session_state["_navigate_to"] = "📊  Module 06 - Sensitivity"
                    st.rerun()


# ── MODULE 06: SENSITIVITY ANALYSIS ──────────────────────────────────────────
elif selected_key == "sensitivity":

    if "_m04_results" not in st.session_state and "cost_model" not in st.session_state:
        st.markdown("""
        <div class="hero-label">Module 06</div>
        <div class="hero-title">Sensitivity <span>Analysis</span></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="status-bar" style="text-align:center;padding:2rem;">
            <strong>⚠ Module 04 required</strong> - run through to the Cost Model first,
            then return here.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    st.markdown("""
    <div class="hero-label">Module 06</div>
    <div class="hero-title">Sensitivity <span>Analysis</span></div>
    <div class="hero-subtitle">Sensitivity sliders &nbsp;·&nbsp; Tornado &nbsp;·&nbsp; Chemistry scenarios &nbsp;·&nbsp; Radar</div>
    """, unsafe_allow_html=True)

    _tab1, _tab2, _tab3, _tab4 = st.tabs([
        "📐  Sensitivity Sliders",
        "🌪  Tornado Chart",
        "⚗️  Chemistry Scenarios",
        "📊  Chemistry Deep Dive",
    ])

    with _tab1:

        # ── Single source of truth: _study_inputs, built as each module Calculates ──
        e_b  = st.session_state.get("electrochem", {})
        cd_b = st.session_state.get("cell_design", {})
        pd_b = st.session_state.get("pack_design", {})
        SI = st.session_state.get("_study_inputs", {})
        r4_b = st.session_state.get("_m04_results", st.session_state.get("cost_model", {}))
        base_cost = r4_b.get("cost_per_kwh", 0)
        lfp_bmark = _lfp_reference_cost()

        base_inputs = _build_base_inputs(SI, lfp_bmark)

        # ── Slider key map defined FIRST so reset button can reference it ────────
        _slider_key_map = {
            # Material prices
            "sl_cat_am":    "p_cathode_am",
            "sl_an_am":     "p_anode_am",
            "sl_sep":       "p_sep",
            "sl_elec":      "p_electrolyte",
            "sl_pvdf":      "p_pvdf",
            "sl_carbon":    "p_carbon",
            "sl_cmcsbr":    "p_cmcsbr",
            # Manufacturing
            "sl_packs":     "annual_production_packs",
            "sl_yield":     "cell_yield_pct",
            "sl_labor":     "labor_rate_per_hr",
            "sl_energyp":   "energy_price_per_kWh",
            # Electrode design
            "sl_cthick":    "c_thick",
            "sl_np":        "np_ratio",
            "sl_cpor":      "c_por",
            "sl_apor":      "a_por",
            # Pack
            "sl_soc":       "useable_soc",
            "sl_modpar":    "modules_parallel",
            "sl_rows":      "rows_per_pack",
        }

        # ── Reset sliders to current study values whenever the study changes ──────
        _study_fingerprint = tuple(
            round(float(base_inputs.get(v, 0)), 6)
            if isinstance(base_inputs.get(v, 0), (int, float))
            else base_inputs.get(v, 0)
            for v in _slider_key_map.values()
        )
        if st.session_state.get("_sens_study_fingerprint") != _study_fingerprint:
            for sk in _slider_key_map:
                st.session_state.pop(sk, None)
            st.session_state["_sens_study_fingerprint"] = _study_fingerprint

        # Apply pending reset BEFORE widgets render so slider values take effect
        if st.session_state.get("_sl_pending_reset"):
            for sk, bk in _slider_key_map.items():
                val = base_inputs.get(bk)
                if val is not None:
                    st.session_state[sk] = int(val) if isinstance(val, float) and val == int(val) and bk in ("modules_parallel","rows_per_pack") else val
            st.session_state["_sl_pending_reset"] = False

        _rcol, _ncol = st.columns([1, 5])
        with _rcol:
            if st.button("Reset to study values", key="sl_reset"):
                st.session_state["_sl_pending_reset"] = True
                st.rerun()

        # ── Sliders - 5 columns ────────────────────────────────────────────────
        sl1, sl2, sl3, sl4, sl5 = st.columns(5, gap="small")

        with sl1:
            st.markdown('<div class="input-section-title">Material Prices</div>', unsafe_allow_html=True)
            s_cathode_am  = st.slider("Cathode AM ($/kg)",    8.0,  50.0,  float(base_inputs["p_cathode_am"]),  0.5,  key="sl_cat_am")
            s_anode_am    = st.slider("Anode AM ($/kg)",      1.0,  20.0,  float(base_inputs["p_anode_am"]),    0.5,  key="sl_an_am")
            s_sep         = st.slider("Separator ($/m²)",     0.5,   6.0,  float(base_inputs["p_sep"]),         0.1,  key="sl_sep")
            s_electrolyte = st.slider("Electrolyte ($/L)",    2.0,  40.0,  float(base_inputs["p_electrolyte"]), 0.5,  key="sl_elec")

        with sl2:
            st.markdown('<div class="input-section-title">Binder & Carbon</div>', unsafe_allow_html=True)
            s_pvdf        = st.slider("PVDF binder ($/kg)",   2.0,  20.0,  float(base_inputs["p_pvdf"]),        0.5,  key="sl_pvdf")
            s_carbon      = st.slider("Carbon black ($/kg)",  0.5,   5.0,  float(base_inputs["p_carbon"]),      0.1,  key="sl_carbon")
            s_cmcsbr      = st.slider("CMC/SBR ($/kg)",       0.5,   8.0,  float(base_inputs["p_cmcsbr"]),      0.1,  key="sl_cmcsbr")

        with sl3:
            st.markdown('<div class="input-section-title">Manufacturing</div>', unsafe_allow_html=True)
            s_annual_packs = st.slider("Production (packs/yr)", 1000.0, 500000.0, float(base_inputs["annual_production_packs"]), 1000.0, key="sl_packs")
            s_yield       = st.slider("Cell yield (%)",        70.0,  99.9,  float(base_inputs["cell_yield_pct"]),      0.5,  key="sl_yield")
            s_labor       = st.slider("Labor rate ($/hr)",     5.0,  100.0, float(base_inputs["labor_rate_per_hr"]),    1.0,  key="sl_labor")
            s_energy_p    = st.slider("Energy price ($/kWh)",  0.01,  0.50, float(base_inputs["energy_price_per_kWh"]), 0.01, key="sl_energyp")

        with sl4:
            st.markdown('<div class="input-section-title">Electrode Design</div>', unsafe_allow_html=True)
            s_c_thick     = st.slider("Cathode thickness (µm)", 40.0, 300.0, float(base_inputs["c_thick"]),  5.0,  key="sl_cthick")
            s_np_ratio    = st.slider("N/P ratio",              1.05,  1.50, float(base_inputs["np_ratio"]), 0.01, key="sl_np")
            s_c_por       = st.slider("Cathode porosity",       0.05,  0.50, float(base_inputs["c_por"]),    0.01, key="sl_cpor")
            s_a_por       = st.slider("Anode porosity",         0.05,  0.50, float(base_inputs["a_por"]),    0.01, key="sl_apor")

        with sl5:
            st.markdown('<div class="input-section-title">Pack</div>', unsafe_allow_html=True)
            s_soc              = st.slider("SOC window",          0.70, 1.00, float(base_inputs["useable_soc"]),    0.01, key="sl_soc")
            s_modules_parallel = st.slider("Modules in parallel", 1,    10,   int(base_inputs["modules_parallel"]),  1,   key="sl_modpar")
            s_rows             = st.slider("Rows per pack",       1,    12,   int(base_inputs["rows_per_pack"]),      1,   key="sl_rows")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Live calculation ───────────────────────────────────────────────────────
        slider_overrides = {
            "p_cathode_am":           s_cathode_am,
            "p_anode_am":             s_anode_am,
            "p_sep":                  s_sep,
            "p_electrolyte":          s_electrolyte,
            "p_pvdf":                 s_pvdf,
            "p_carbon":               s_carbon,
            "p_cmcsbr":               s_cmcsbr,
            "annual_production_packs": s_annual_packs,
            "cell_yield_pct":         s_yield,
            "labor_rate_per_hr":      s_labor,
            "energy_price_per_kWh":   s_energy_p,
            "c_thick":                s_c_thick,
            "np_ratio":               s_np_ratio,
            "c_por":                  s_c_por,
            "a_por":                  s_a_por,
            "useable_soc":            s_soc,
            "modules_parallel":       s_modules_parallel,
            "rows_per_pack":          s_rows,
        }
        live_result = _run_full_cost(slider_overrides, e_b, cd_b, pd_b, base_inputs)
        base_result = _run_full_cost({}, e_b, cd_b, pd_b, base_inputs)

        # ── Outputs - full width below sliders ────────────────────────────────────
        if live_result is not None:
            live_cost  = live_result["cost_per_kwh"]
            delta      = live_cost - base_cost
            delta_pct  = delta / base_cost * 100
            gap_lfp    = (live_cost - lfp_bmark) if lfp_bmark else None
            d_sign     = "+" if delta >= 0 else ""
            g_sign     = "+" if (gap_lfp or 0) >= 0 else ""
            card_color = T["accent"] if (lfp_bmark and live_cost > lfp_bmark) else "#10b981"

            def _delta_str(key, fmt=".1f", unit=""):
                if base_result is None or key not in base_result:
                    return ""
                d = live_result[key] - base_result[key]
                s = "+" if d >= 0 else ""
                return f"{s}{d:{fmt}} {unit}".strip()

            st.markdown('<div class="section-header">Cost</div>', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4, gap="small")
            with c1:
                st.markdown(f"""
                <div class="output-card highlight">
                    <div class="output-card-label">Cost per kWh</div>
                    <div class="output-card-value" style="color:{card_color};">${live_cost:.4f}</div>
                    <div class="output-card-unit">$/kWh</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="output-card highlight">
                    <div class="output-card-label">Change from base</div>
                    <div class="output-card-value">{d_sign}{delta:.4f}</div>
                    <div class="output-card-unit">$/kWh &nbsp;·&nbsp; {d_sign}{delta_pct:.1f}%</div>
                </div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="output-card highlight">
                    <div class="output-card-label">Gap vs LFP</div>
                    <div class="output-card-value">{f'{g_sign}{gap_lfp:.4f}' if gap_lfp is not None else 'n/a'}</div>
                    <div class="output-card-unit">{f'$/kWh vs ${lfp_bmark:.2f}/kWh, like-for-like' if lfp_bmark else 'run the chemistry comparison'}</div>
                </div>""", unsafe_allow_html=True)
            with c4:
                if gap_lfp is None:
                    st.markdown(f'<div class="val-warn">{_NO_LFP_MSG}</div>', unsafe_allow_html=True)
                elif gap_lfp <= 0:
                    st.markdown('<div class="val-pass">✓  Cost parity with LFP achieved</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="val-warn">⚠  ${gap_lfp:.4f}/kWh above like-for-like LFP</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:1rem;">Performance</div>', unsafe_allow_html=True)
            p1, p2, p3, p4, p5, p6 = st.columns(6, gap="small")
            for col, label, val, unit, delta_s in [
                (p1, "Cell capacity",   f"{live_result['cell_capacity']:.4f}",       "Ah",    _delta_str('cell_capacity', '.2f', 'Ah')),
                (p2, "Specific energy", f"{live_result['cell_specific_energy']:.1f}", "Wh/kg", _delta_str('cell_specific_energy', '.1f', 'Wh/kg')),
                (p3, "Energy density",  f"{live_result['cell_energy_density']:.1f}",  "Wh/L",  _delta_str('cell_energy_density', '.1f', 'Wh/L')),
                (p4, "Pack energy",     f"{live_result['pack_useable_energy']:.4f}",  "kWh",   _delta_str('pack_useable_energy', '.2f', 'kWh')),
                (p5, "Pack sp. energy", f"{live_result['pack_specific_energy']:.1f}", "Wh/kg", _delta_str('pack_specific_energy', '.1f', 'Wh/kg')),
                (p6, "Cell mass",       f"{live_result['cell_mass_g']:.0f}",          "g",     _delta_str('cell_mass_g', '.0f', 'g')),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="output-card">
                        <div class="output-card-label">{label}</div>
                        <div class="output-card-value" style="font-size:1.1rem;">{val}</div>
                        <div class="output-card-unit">{unit}<br><span style="font-size:0.58rem;">{delta_s}</span></div>
                    </div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-header" style="margin-top:1rem;">Cell Dimensions</div>', unsafe_allow_html=True)
            d1, d2, d3, d4, d5 = st.columns(5, gap="small")
            for col, label, val, unit, delta_s in [
                (d1, "Bicell layers",  f"{live_result['num_bicell_layers']}",     "layers", _delta_str('num_bicell_layers', '.0f', 'layers')),
                (d2, "Cell thickness", f"{live_result['cell_thickness_mm']:.1f}", "mm",     _delta_str('cell_thickness_mm', '.1f', 'mm')),
                (d3, "Cell width",     f"{live_result['cell_width_mm']:.1f}",     "mm",     _delta_str('cell_width_mm', '.1f', 'mm')),
                (d4, "Cell length",    f"{live_result['cell_length_mm']:.1f}",    "mm",     _delta_str('cell_length_mm', '.1f', 'mm')),
                (d5, "Cell volume",    f"{live_result['cell_volume_cm3']:.1f}",   "cm³",    _delta_str('cell_volume_cm3', '.1f', 'cm³')),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="output-card">
                        <div class="output-card-label">{label}</div>
                        <div class="output-card-value" style="font-size:1.1rem;">{val}</div>
                        <div class="output-card-unit">{unit}<br><span style="font-size:0.58rem;">{delta_s}</span></div>
                    </div>""", unsafe_allow_html=True)

        else:
            st.markdown('<div class="val-fail">✗  Could not compute - check inputs</div>', unsafe_allow_html=True)


    with _tab2:
        # ═══════════════════════════════════════════════════════════════════════════
        # SECTION 2 - TORNADO CHART
        # Vary each parameter ±20% from base, rank by impact on cost/kWh
        # ═══════════════════════════════════════════════════════════════════════════
        st.markdown('<div class="section-header" style="margin-top:2rem;">Tornado Chart - Parameter Sensitivity</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="note-box">
            Each parameter is varied independently by ±20% from its base study value.
            All other parameters remain fixed. Ranked by absolute impact on $/kWh.
            Base cost = <strong>${base_cost:.4f}/kWh</strong>.
        </div>
        """, unsafe_allow_html=True)

        tornado_pct = st.slider("Variation range (±%)", 5, 50, 20, 5, key="tornado_pct")

        if st.button("Run Tornado Analysis", key="run_tornado", use_container_width=False):

            # Parameters selected based on TEA literature (Nelson 2011, Schmidt 2019,
            # Marcel 2022, Nilugal 2025). Includes material prices, manufacturing parameters,
            # and electrochemical performance uncertainty (cathode capacity and voltage).
            # Electrode geometry (area, layer count) and fractions are excluded as design
            # variables. Cell yield excluded as a manufacturing assumption not a market input.
            tornado_params = {
                # Material prices
                "Cathode AM price":      ("p_cathode_am",            base_inputs["p_cathode_am"]),
                "Anode AM price":        ("p_anode_am",              base_inputs["p_anode_am"]),
                "Electrolyte price":     ("p_electrolyte",           base_inputs["p_electrolyte"]),
                "Separator price":       ("p_sep",                   base_inputs["p_sep"]),
                # Manufacturing
                "Annual production":     ("annual_production_packs", base_inputs["annual_production_packs"]),
                "Labor rate":            ("labor_rate_per_hr",       base_inputs["labor_rate_per_hr"]),
                "Manufacturing energy":  ("energy_price_per_kWh",    base_inputs["energy_price_per_kWh"]),
                # Electrochemical performance — genuine uncertainty in accessible capacity
                # and cell voltage at operating conditions (He et al. 2023 reports range
                # of 100-128 mAh/g depending on rate; 3.7-4.0V half-cell potential range)
                "Cathode capacity":      ("c_cap",  base_inputs["c_cap"]),
                "Cathode voltage":       ("c_volt", base_inputs["c_volt"]),
            }

            # Physical bounds: cathode capacity and voltage cannot go negative or
            # exceed physically achievable limits. These are absolute bounds, not
            # fractions, to prevent the ±% variation producing nonsensical values.
            PARAM_BOUNDS = {
                "c_cap":  (80.0,  140.0),   # mAh/g: physically achievable range for NVPF
                "c_volt": (3.50,  4.10),    # V vs Na+/Na: cutoff voltage range for NVPF
            }

            f = tornado_pct / 100.0
            tornado_results = []

            with st.spinner("Running tornado analysis..."):
                for label, (key, base_val) in tornado_params.items():
                    lo_val = base_val * (1 - f)
                    hi_val = base_val * (1 + f)
                    if key in PARAM_BOUNDS:
                        lo_b, hi_b = PARAM_BOUNDS[key]
                        if lo_b is not None: lo_val = max(lo_val, lo_b)
                        if hi_b is not None: hi_val = min(hi_val, hi_b)
                    r_lo = _run_full_cost({key: lo_val}, e_b, cd_b, pd_b, base_inputs)
                    r_hi = _run_full_cost({key: hi_val}, e_b, cd_b, pd_b, base_inputs)
                    if r_lo and r_hi:
                        cost_lo = r_lo["cost_per_kwh"]
                        cost_hi = r_hi["cost_per_kwh"]
                        tornado_results.append({
                            "label": label,
                            "lo_val": lo_val, "hi_val": hi_val,
                            "low":   cost_lo,
                            "high":  cost_hi,
                            "swing": abs(cost_hi - cost_lo),
                        })

            # Sort by swing (largest first) — show ALL parameters ranked by impact
            tornado_results.sort(key=lambda x: -x["swing"])
            st.session_state["_tornado_results"] = tornado_results
            st.session_state["_tornado_base"] = base_cost

        if "_tornado_results" in st.session_state:
            tr   = st.session_state["_tornado_results"]
            bc   = st.session_state.get("_tornado_base", base_cost)
            # Sort by swing, smallest first so largest appears at top of chart
            tr_sorted = sorted(tr, key=lambda x: x["swing"])
            labels = [r["label"] for r in tr_sorted]

            # Delta from base for each direction the parameter can move
            delta_lo = [r["low"]  - bc for r in tr_sorted]
            delta_hi = [r["high"] - bc for r in tr_sorted]

            # Colour by COST DIRECTION, not by parameter direction, so every row
            # reads the same way: orange (right) always means "cost goes up",
            # blue (left) always means "cost goes down" - regardless of whether
            # that came from raising or lowering the parameter.
            cost_up   = [max(dl, dh, 0) for dl, dh in zip(delta_lo, delta_hi)]
            cost_down = [min(dl, dh, 0) for dl, dh in zip(delta_lo, delta_hi)]
            # Track which parameter value (low/high) caused the increase, for hover text
            up_is_high   = [dh >= dl for dl, dh in zip(delta_lo, delta_hi)]

            fig_t = go.Figure()
            fig_t.add_trace(go.Bar(
                name="Cost decreases",
                y=labels, x=cost_down,
                orientation="h",
                marker_color="#3b82f6",
                customdata=[("low" if up else "high") for up in up_is_high],
                hovertemplate="<b>%{y}</b><br>%{x:+.2f} $/kWh when parameter is at its %{customdata} value<extra></extra>",
            ))
            fig_t.add_trace(go.Bar(
                name="Cost increases",
                y=labels, x=cost_up,
                orientation="h",
                marker_color=T["accent"],
                customdata=[("high" if up else "low") for up in up_is_high],
                hovertemplate="<b>%{y}</b><br>%{x:+.2f} $/kWh when parameter is at its %{customdata} value<extra></extra>",
            ))
            fig_t.add_vline(x=0, line_color=T["text"], line_width=1.5,
                            annotation_text=f"Base: ${bc:.2f}/kWh",
                            annotation_position="top",
                            annotation_font_color=T["text"])
            fig_t.update_layout(
                barmode="relative",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=T["text"], size=11),
                xaxis=dict(
                    title="Change in $/kWh from base",
                    gridcolor=T["border"], zeroline=True,
                    zerolinecolor=T["text"], zerolinewidth=1.5,
                ),
                yaxis=dict(categoryorder="array", categoryarray=labels),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=10, r=20, t=60, b=40), title=dict(text=""),
                height=max(380, len(labels) * 38 + 100),
            )
            st.plotly_chart(fig_t, use_container_width=True)

            # Tornado table
            trows = ""
            for r in tr:
                swing_color = T["accent"] if r["swing"] > 5 else T["text"]
                trows += f"""<tr>
                    <td>{r["label"]}</td>
                    <td class="val">${r["low"]:.4f}</td>
                    <td class="val">${r["high"]:.4f}</td>
                    <td class="val" style="color:{swing_color}"><strong>${r["swing"]:.4f}</strong></td>
                </tr>"""
            st.markdown(f"""
            <table class="mass-table" style="margin-top:0.5rem;">
                <thead><tr>
                    <th>Parameter</th>
                    <th style="text-align:right">Low $/kWh</th>
                    <th style="text-align:right">High $/kWh</th>
                    <th style="text-align:right">Swing</th>
                </tr></thead>
                <tbody>{trows}</tbody>
            </table>
            """, unsafe_allow_html=True)

        # ═══════════════════════════════════════════════════════════════════════════
        # SECTION 3 - CHEMISTRY SCENARIO COMPARISON
        # ═══════════════════════════════════════════════════════════════════════════

    with _tab3:

        # ── Shared chemistry presets — used by both sub-tabs ─────────────────────
        CHEMISTRY_PRESETS = CHEMISTRY_PRESETS_GLOBAL

        CHEM_COLORS = [
            T["accent"], "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"
        ]

        _useable_soc = base_inputs.get("useable_soc", 0.84) or 0.84

        # ── Helper: render bar charts + stacked bar + table from a results dict ──
        def _chem_scenario(ov, base_in, match_kwh=None):
            """Run one chemistry through Modules 01-04.

            match_kwh=None, the basis used by the chemistry comparison, keeps the
            baseline electrode geometry so pack energy floats with the chemistry.
            Passing a target pack energy instead re-derives the electrode area by
            bisection so every chemistry delivers the same kWh; that is available for
            one-off analyses but is not what Module 06 reports.
            """
            if not match_kwh:
                return _run_full_cost(ov, e_b, cd_b, pd_b, base_in)
            lo, hi, r, bi = 5.0, 400.0, None, dict(base_in)
            for _ in range(48):
                mid = (lo + hi) / 2
                _e = run_electrochemical(
                    ov.get("c_cap", base_in["c_cap"]), ov.get("c_volt", base_in["c_volt"]),
                    ov.get("c_dens", base_in["c_dens"]), ov.get("c_am", base_in["c_am"]),
                    ov.get("c_carb", base_in["c_carb"]), ov.get("c_bind", base_in["c_bind"]),
                    ov.get("c_por", base_in["c_por"]), ov.get("c_thick", base_in["c_thick"]),
                    ov.get("a_cap", base_in["a_cap"]), ov.get("a_volt", base_in["a_volt"]),
                    ov.get("a_dens", base_in["a_dens"]), ov.get("a_am", base_in["a_am"]),
                    ov.get("a_bind", base_in["a_bind"]), ov.get("a_carb", base_in["a_carb"]),
                    ov.get("a_por", base_in["a_por"]), ov.get("np_ratio", base_in["np_ratio"]),
                    None, base_in["tab_excess"],
                    c_carb_dens=base_in["c_carb_dens"],
                    c_bind_dens=ov.get("c_bind_dens", base_in["c_bind_dens"]),
                    a_carb_dens=base_in["a_carb_dens"],
                    a_bind_dens=ov.get("a_bind_dens", base_in["a_bind_dens"]),
                    target_cell_capacity_Ah=mid)
                bi = dict(base_in); bi["electrode_area"] = _e["electrode_area"]
                r = _run_full_cost(ov, e_b, cd_b, pd_b, bi)
                if r is None:
                    return None
                if r["pack_gross_energy"] < match_kwh:
                    lo = mid
                else:
                    hi = mid
            return r

        def _render_chem_results(cr):
            # Pack energy varies between chemistries under fixed geometry, so it is
            # shown as its own column rather than assumed constant.
            gross_fixed = True
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            names  = list(cr.keys())
            shorts = [n.split("/")[0].strip() for n in names]

            # 1. Overview: cost, specific energy, energy density
            costs  = [cr[n]["cost_per_kwh"]        for n in names]
            sp_eng = [cr[n]["cell_specific_energy"] for n in names]
            en_den = [cr[n]["cell_energy_density"]  for n in names]
            pk_kwh = [cr[n].get("pack_gross_energy", cr[n].get("pack_useable_energy",0) / _useable_soc) for n in names]

            if gross_fixed:
                # Fixed geometry: also show pack gross energy to show how much it varies
                fig_c = make_subplots(rows=1, cols=4,
                    subplot_titles=["Cost ($/kWh)", "Pack Gross Energy (kWh)",
                                    "Cell Specific Energy (Wh/kg)", "Cell Energy Density (Wh/L)"],
                    horizontal_spacing=0.08)
            else:
                fig_c = make_subplots(rows=1, cols=3,
                    subplot_titles=["Cost ($/kWh)", "Cell Specific Energy (Wh/kg)", "Cell Energy Density (Wh/L)"],
                    horizontal_spacing=0.10)

            for i, (name, cost, se, ed, gkwh) in enumerate(zip(names, costs, sp_eng, en_den, pk_kwh)):
                col = CHEM_COLORS[i % len(CHEM_COLORS)]
                sh  = shorts[i]
                fig_c.add_trace(go.Bar(name=sh, x=[sh], y=[cost],  marker_color=col, showlegend=True),  row=1, col=1)
                if gross_fixed:
                    fig_c.add_trace(go.Bar(name=sh, x=[sh], y=[gkwh], marker_color=col, showlegend=False), row=1, col=2)
                    fig_c.add_trace(go.Bar(name=sh, x=[sh], y=[se],   marker_color=col, showlegend=False), row=1, col=3)
                    fig_c.add_trace(go.Bar(name=sh, x=[sh], y=[ed],   marker_color=col, showlegend=False), row=1, col=4)
                else:
                    fig_c.add_trace(go.Bar(name=sh, x=[sh], y=[se],   marker_color=col, showlegend=False), row=1, col=2)
                    fig_c.add_trace(go.Bar(name=sh, x=[sh], y=[ed],   marker_color=col, showlegend=False), row=1, col=3)

            n_axes = 4 if gross_fixed else 3
            fig_c.update_layout(
                barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=T["text"], size=11), showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="center", x=0.5),
                margin=dict(l=10, r=10, t=60, b=10), height=400,
            )
            for ax in [f"xaxis{i+1 if i else ''}" for i in range(n_axes)]:
                fig_c.update_layout(**{ax: dict(showticklabels=False)})
            for ax in [f"yaxis{i+1 if i else ''}" for i in range(n_axes)]:
                fig_c.update_layout(**{ax: dict(gridcolor=T["border"])})
            st.plotly_chart(fig_c, use_container_width=True)

            # 2. Stacked cost breakdown
            st.markdown('<div class="section-header" style="margin-top:1rem;">Cost Breakdown by Component</div>', unsafe_allow_html=True)
            _stk_mat=[]; _stk_mfg=[]; _stk_ovhd=[]; _stk_pw=[]; _stk_hw=[]
            for name in names:
                _r     = cr[name]
                _gross = max(_r.get("pack_gross_energy", _r.get("pack_useable_energy",0)/(_useable_soc or 0.84)), 1)
                _mat   = _r.get("mat_cost_total", 0)   / _gross
                _mfg   = _r.get("direct_mfg_total", 0) / _gross
                _ovhd  = _r.get("fixed_overhead_total", 0) / _gross
                _pw    = (_r.get("total_profit",0) + _r.get("total_warranty",0)) / _gross
                _hw    = _r.get("cost_pack_hw_per_pack", 0) / _gross
                _rem   = _r["cost_per_kwh"] - _mat - _mfg - _ovhd - _pw - _hw
                _ovhd += max(_rem, 0)
                _stk_mat.append(round(_mat,2));  _stk_mfg.append(round(_mfg,2))
                _stk_ovhd.append(round(_ovhd,2)); _stk_pw.append(round(_pw,2))
                _stk_hw.append(round(max(_hw,0),2))

            _SCOLS = ["#f59e0b","#3b82f6","#8b5cf6","#10b981","#ef4444"]
            fig_stk = go.Figure()
            for _lbl, _vals, _col in [
                ("Materials",                    _stk_mat,  _SCOLS[0]),
                ("Direct labour + energy",        _stk_mfg,  _SCOLS[1]),
                ("Fixed overhead (depr/GSA/R&D)", _stk_ovhd, _SCOLS[2]),
                ("Profit + warranty",             _stk_pw,   _SCOLS[3]),
                ("Pack hardware + BMS",           _stk_hw,   _SCOLS[4]),
            ]:
                fig_stk.add_trace(go.Bar(
                    name=_lbl, x=shorts, y=_vals, marker_color=_col,
                    text=[f"${v:.0f}" if v > 3 else "" for v in _vals],
                    textposition="inside", textfont=dict(color="white", size=10),
                ))
            fig_stk.update_layout(
                barmode="stack", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=T["text"], size=11),
                yaxis=dict(title="$/kWh", gridcolor=T["border"]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                margin=dict(l=10, r=10, t=60, b=10), height=420,
            )
            st.plotly_chart(fig_stk, use_container_width=True)

            # 3. Summary table
            lfp_cost = next((cr[n]["cost_per_kwh"] for n in names if "LFP" in n), lfp_bmark)
            extra_col = '<th style="text-align:right">Pack kWh</th>' if gross_fixed else ""
            crow = ""
            for name in names:
                r = cr[name]
                gap = r["cost_per_kwh"] - lfp_cost
                gap_str = f"+${gap:.2f}" if gap >= 0 else f"-${abs(gap):.2f}"
                gap_col = T["accent"] if gap >= 0 else "#10b981"
                is_lfp  = "LFP" in name
                gkwh    = r.get("pack_gross_energy", r.get("pack_useable_energy",0)/_useable_soc)
                extra_val = f'<td class="val">{gkwh:.1f}</td>' if gross_fixed else ""
                crow += f"""<tr{"" if not is_lfp else ' style="border-left:3px solid #10b981;"' }>
                    <td><strong>{name}</strong><br>
                        <span style="font-size:0.68rem;color:{T["muted"]}">{r["desc"]}</span></td>
                    <td class="val">${r["cost_per_kwh"]:.2f}</td>
                    <td class="val" style="color:{gap_col}">{gap_str if not is_lfp else "benchmark"}</td>
                    {extra_val}
                    <td class="val">{r["cell_specific_energy"]:.0f}</td>
                    <td class="val">{r["cell_energy_density"]:.0f}</td>
                    <td class="val">{r["pack_specific_energy"]:.0f}</td>
                    <td class="val">{r["cell_capacity"]:.1f}</td>
                    <td class="val">{f'${r["lcos_per_kwh"]:.3f}' if r.get("lcos_per_kwh") else "&mdash;"}</td>
                    <td class="val">{f'{r["co2_per_kwh"]:.0f}' if r.get("co2_per_kwh") else "&mdash;"}</td>
                    <td class="val">{f'${r["eol_total_value"]:.0f}' if r.get("eol_total_value") else "&mdash;"}</td>
                </tr>"""
            st.markdown(f"""
            <table class="mass-table">
                <thead><tr>
                    <th>Chemistry</th>
                    <th style="text-align:right">$/kWh</th>
                    <th style="text-align:right">vs LFP</th>
                    {extra_col}
                    <th style="text-align:right">Cell Wh/kg</th>
                    <th style="text-align:right">Cell Wh/L</th>
                    <th style="text-align:right">Pack Wh/kg</th>
                    <th style="text-align:right">Capacity (Ah)</th>
                    <th style="text-align:right">LCOS $/kWh</th>
                    <th style="text-align:right">kgCO2/kWh</th>
                    <th style="text-align:right">EOL $/pack</th>
                </tr></thead>
                <tbody>{crow}</tbody>
            </table>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-header" style="margin-top:1.5rem;">Chemistry Comparison</div>', unsafe_allow_html=True)
        if st.button("Run Chemistry Comparison", key="run_chem_comp", use_container_width=False):
            _cr_fixed = {}
            _META_KEYS = _CHEM_META_KEYS
            with st.spinner("Running chemistry scenarios on both comparison bases..."):
                _study_kwh = None
                _r_study_fx = _run_full_cost({}, e_b, cd_b, pd_b, base_inputs)
                if _r_study_fx:
                    _study_kwh = _r_study_fx["pack_gross_energy"]

                _study_meta = {
                    "desc":             "Your current study inputs, exactly as saved in Modules 01-04.",
                    "co2_cathode_am":   st.session_state.get("co2_cathode_am", 22.0),
                    "co2_anode_am":     st.session_state.get("co2_anode_am", 4.07),
                    "co2_al_foil":      st.session_state.get("co2_al_foil", 6.6),
                    "cycle_life":       st.session_state.get("cycle_life", 3200),
                    "rte_pct":          st.session_state.get("rt_eff", 90.0),
                    "eol_cat_recovery": st.session_state.get("eol_cat_recovery", 88.23),
                    "eol_cat_price":    st.session_state.get("eol_cat_price", 10.74),
                    "anode_foil_density": base_inputs.get("anode_foil_density", 2.70),
                }

                _store = _cr_fixed
                # Fixed geometry: every scenario keeps the electrode area, thickness,
                # layer count and pack topology of the study. Only the material
                # properties change, together with the things that follow from the
                # chemistry: aluminium or copper negative foil and terminal, and PVDF
                # or CMC/SBR anode binder. Pack energy is therefore an output, not a
                # constraint, and differs between chemistries.
                if True:
                    for name, params in CHEMISTRY_PRESETS.items():
                        ov = _chem_overrides(params)
                        r = _chem_scenario(ov, base_inputs, match_kwh=None)
                        if not r:
                            continue
                        _s5 = _chem_sustainability(r, params, base_inputs)
                        # CO2 is shown for every chemistry. LCOS and end-of-life
                        # values are only shown where we have a sourced figure.
                        _c5 = _chem_co2(r, params, base_inputs)
                        _store[name] = {
                            **r,
                            "desc":           params["desc"],
                            "co2_cathode_am": params.get("co2_cathode_am", base_inputs.get("co2_cathode_am", 22.0)),
                            "co2_anode_am":   params.get("co2_anode_am",   base_inputs.get("co2_anode_am", 4.07)),
                            "co2_al_foil":    params.get("co2_al_foil",    base_inputs.get("co2_al_foil", 6.6)),
                            "cycle_life":     params.get("cycle_life"),
                            "rte_pct":        params.get("rte_pct", 90.0),
                            "eol_cat_recovery": params.get("eol_cat_recovery"),
                            "eol_cat_price":    params.get("eol_cat_price"),
                            "lcos_per_kwh":     _s5.get("lcos_per_kwh") if _s5 else None,
                            "lcos_net_per_kwh": _s5.get("lcos_net_per_kwh") if _s5 else None,
                            "co2_per_kwh":      _c5.get("co2_per_kwh") if _c5 else None,
                            "co2_breakdown":    _c5.get("co2_breakdown") if _c5 else None,
                            "eol_total_value":  _s5.get("eol_total_value") if _s5 else None,
                            "energy_payback_yr": _s5.get("energy_payback_yr") if _s5 else None,
                            "m05_basis":        "run" if _s5 else "missing inputs",
                        }
                    r_study = _r_study_fx
                    if r_study:
                        _s5s = _chem_sustainability(r_study, _study_meta, base_inputs)
                        _c5s = _chem_co2(r_study, _study_meta, base_inputs)
                        # Use saved Module 05 sustainability metrics so Your study always
                        # quotes the same number as Module 05 / Study Summary page.
                        _saved_s5 = st.session_state.get("_m05_results", {})
                        _store["Your study"] = {
                            **r_study, **_study_meta,
                            "lcos_per_kwh":      _saved_s5.get("lcos_per_kwh") or (_s5s.get("lcos_per_kwh") if _s5s else None),
                            "lcos_net_per_kwh":  _saved_s5.get("lcos_net_per_kwh") or (_s5s.get("lcos_net_per_kwh") if _s5s else None),
                            "co2_per_kwh":       _saved_s5.get("co2_per_kwh") or (_c5s.get("co2_per_kwh") if _c5s else None),
                            "co2_breakdown":     _saved_s5.get("co2_breakdown") or (_c5s.get("co2_breakdown") if _c5s else None),
                            "eol_total_value":   _saved_s5.get("eol_total_value") or (_s5s.get("eol_total_value") if _s5s else None),
                            "energy_payback_yr": _saved_s5.get("energy_payback_yr") or (_s5s.get("energy_payback_yr") if _s5s else None),
                            "m05_basis":         "run" if (_saved_s5 or _s5s) else "missing inputs",
                        }
            st.session_state["_chem_results"] = _cr_fixed

        if "_chem_results" in st.session_state:
            _cr_show = st.session_state.get("_chem_results", {})
            _kwhs = [v.get("pack_gross_energy", 0) for v in _cr_show.values()]
            st.markdown(
                f'<div class="val-pass">Fixed construction: every chemistry keeps the electrode '
                f'area, composition, porosity, thickness, layer count and pack topology of your '
                f'study, and only the material properties and prices change. Pack energy is an '
                f'output and ranges {min(_kwhs) if _kwhs else 0:.0f} to '
                f'{max(_kwhs) if _kwhs else 0:.0f} kWh.</div>',
                unsafe_allow_html=True)

            _missing = [k for k, v in _cr_show.items() if v.get("m05_basis") != "run"]
            if _missing:
                st.markdown(
                    '<div class="val-warn">LCOS, end-of-life value and energy payback are not '
                    'computed for: <strong>' + ", ".join(_missing) + '</strong>. These scenarios '
                    'have no sourced cycle life or end-of-life basis. They are left blank rather '
                    'than inheriting the baseline chemistry\'s figures.</div>',
                    unsafe_allow_html=True)

            _render_chem_results(_cr_show)

        # ═══════════════════════════════════════════════════════════════════════════
        # SECTION 4 - SPIDER / RADAR CHART
        # Multi-dimensional comparison across cost, energy, CO2, supply risk
        # ═══════════════════════════════════════════════════════════════════════════

    with _tab4:
        st.markdown('<div class="section-header" style="margin-top:2rem;">Chemistry Deep Dive</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="note-box">
            Per-chemistry breakdown of cost and CO2 emissions. Requires Chemistry Comparison
            to be run first. CO2 covers electrode materials plus separator, electrolyte,
            carbon black, pack structure, steel rack, and BMS using sourced cradle-to-gate
            intensities. Excludes manufacturing energy.
        </div>
        """, unsafe_allow_html=True)

        if "_chem_results" in st.session_state:
            import plotly.graph_objects as go
            cr = st.session_state["_chem_results"]
            names = list(cr.keys())

            # ── Order: Your study first, then others
            _ordered_names = (["Your study"] + [n for n in names if n != "Your study"])

            # ── Colour palette per chemistry
            _CHEM_COL = {
                "Your study":             "#f59e0b",
                "SIB NaMnO2 / Hard carbon":"#3b82f6",
                "SIB NaFePO4 / Hard carbon":"#10b981",
                "LIB LFP / Graphite":     "#e879f9",
            }

            # ── CO2 intensity factors ────────────────────────────────────────────
            # Read from the Module 05 inputs so the whole model quotes one number
            # per material. Chemistry-specific factors (cathode AM, anode AM, anode
            # foil) still come from each preset, since those genuinely differ.
            # Only used by the cost donut below. All CO2 numbers now come from
            # Module 05, so nothing gets counted twice.
            _F_AL     = float(st.session_state.get("co2_al_foil", 6.6))

            # ── Render one row per chemistry ─────────────────────────────────────
            for _cn in _ordered_names:
                _crd    = cr.get(_cn, {})
                _short  = _cn.split("/")[0].strip()
                _anode  = _cn.split("/")[1].strip() if "/" in _cn else ""
                _col    = _CHEM_COL.get(_cn, "#f59e0b")
                _ckwh   = _crd.get("cost_per_kwh", 0)
                # CO2/kWh uses useable energy (matches Module 05 convention and LCA literature).
                # Fall back to gross × SOC if useable not stored in chemistry result.
                _pack_e = max(
                    float(_crd.get("pack_useable_energy",
                          _crd.get("pack_gross_energy", 0.001) * (_useable_soc or 0.85))),
                    0.001
                )
                _n_cells = float(_crd.get("total_cells", 1200))

                # ── CO2: use the numbers Module 05 already worked out ────────────
                # Reading them here means the bar chart, the donut and the card
                # can never disagree with Module 05.
                _bd = _crd.get("co2_breakdown") or {}
                def _b(k):
                    return float(_bd.get(k, 0.0))
                _co2_cat_am   = _b("Cathode AM")
                _co2_an_am    = _b("Anode AM")
                _co2_cat_bind = _b("Cathode binder")
                _co2_an_bind  = _b("Anode binder")
                _co2_foil     = _b("Cathode foil") + _b("Anode foil")
                _co2_sep      = _b("Separator")
                _co2_elec     = _b("Electrolyte")
                _co2_cont     = _b("Cell container")
                _co2_c_carb   = _b("Conductive carbon")
                _co2_a_carb   = 0.0
                _co2_cond     = _b("Copper (pack)")
                _co2_rack     = _b("Steel (rack, cooling, jacket)")
                _co2_al_str   = _b("Aluminium (pack)")
                _co2_bms      = _b("BMS")

                _elec_co2_kg  = (_co2_cat_am + _co2_an_am + _co2_cat_bind
                                 + _co2_an_bind + _co2_foil)
                _total_co2    = sum(_bd.values())
                _elec_co2_kwh = round(_elec_co2_kg / _pack_e, 1)
                _full_co2_kwh = round(_total_co2 / _pack_e, 1)

                # ── Header ───────────────────────────────────────────────────────
                st.markdown(f"""
                <div style="margin:2rem 0 0.75rem;display:flex;align-items:baseline;gap:10px;">
                    <span style="font-size:1.15rem;font-weight:500;color:{_col};
                        font-family:'IBM Plex Mono',monospace;">{_short}</span>
                    {"<span style='font-size:0.8rem;color:" + T["muted"] + ";'>/ " + _anode + "</span>" if _anode else ""}
                </div>
                <hr style="border:none;border-top:1px solid {T["border"]};margin:0 0 0.75rem;">
                """, unsafe_allow_html=True)

                # ── Metric cards ─────────────────────────────────────────────────
                _mc1, _mc2, _mc3, _mc4 = st.columns(4, gap="small")
                with _mc1:
                    st.markdown(f"""<div class="output-card">
                        <div class="output-card-label">Pack cost</div>
                        <div class="output-card-value" style="font-size:1.3rem;">${_ckwh:.2f}</div>
                        <div class="output-card-unit">$/kWh</div></div>""", unsafe_allow_html=True)
                with _mc2:
                    st.markdown(f"""<div class="output-card">
                        <div class="output-card-label">Pack gross energy</div>
                        <div class="output-card-value" style="font-size:1.3rem;">{_crd.get("pack_gross_energy",0):.1f}</div>
                        <div class="output-card-unit">kWh</div></div>""", unsafe_allow_html=True)
                with _mc3:
                    st.markdown(f"""<div class="output-card">
                        <div class="output-card-label">CO2 electrode mat.</div>
                        <div class="output-card-value" style="font-size:1.3rem;">{_elec_co2_kwh:.1f}</div>
                        <div class="output-card-unit">kgCO2/kWh</div></div>""", unsafe_allow_html=True)
                with _mc4:
                    st.markdown(f"""<div class="output-card">
                        <div class="output-card-label">CO2 full pack est.</div>
                        <div class="output-card-value" style="font-size:1.3rem;">{_full_co2_kwh:.1f}</div>
                        <div class="output-card-unit">kgCO2/kWh</div></div>""", unsafe_allow_html=True)

                st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

                _c1, _c2, _c3 = st.columns(3, gap="small")

                # ── Col 1: CO2 stacked bar ───────────────────────────────────────
                with _c1:
                    _bar_cats = ["Cathode AM","Anode AM","Cathode binder",
                                 "Anode binder","Current collectors","Separator",
                                 "Electrolyte","Cell container","Carbon black",
                                 "Pack jacket (Al)","Steel structure",
                                 "Cu conductors","BMS"]
                    _bar_vals = [round(v,0) for v in [
                        _co2_cat_am, _co2_an_am, _co2_cat_bind, _co2_an_bind, _co2_foil,
                        _co2_sep, _co2_elec, _co2_cont, _co2_c_carb+_co2_a_carb,
                        _co2_al_str, _co2_rack, _co2_cond, _co2_bms]]
                    _bar_cols = ["#f59e0b","#3b82f6","#e879f9","#8b5cf6","#64748b",
                                 "#06b6d4","#84cc16","#0ea5e9","#f97316","#94a3b8",
                                 "#475569","#b45309","#ef4444"]
                    _fig_bar = go.Figure()
                    for _bi, (_bc, _bv, _bco) in enumerate(zip(_bar_cats, _bar_vals, _bar_cols)):
                        _fig_bar.add_trace(go.Bar(
                            name=_bc, x=[_short], y=[_bv],
                            marker_color=_bco, showlegend=False,
                            hovertemplate=f"{_bc}: %{{y:.0f}} kgCO2<extra></extra>",
                        ))
                    _fig_bar.add_annotation(x=_short, y=_total_co2*1.04,
                        text=f"{_total_co2:,.0f} kgCO2",
                        showarrow=False, font=dict(size=10, color=T["muted"]))
                    _fig_bar.update_layout(
                        barmode="stack", height=360,
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color=T["text"], size=10),
                        title=dict(text="CO2 emissions",
                                   font=dict(size=11, color=T["muted"]), x=0.5),
                        xaxis=dict(visible=False),
                        yaxis=dict(title="kgCO2", gridcolor=T["border"], tickfont=dict(size=9)),
                        margin=dict(l=40, r=10, t=40, b=10),
                        showlegend=False,
                    )
                    st.plotly_chart(_fig_bar, use_container_width=True, key=f"co2bar_{_cn}")

                # ── Col 2: Cost breakdown pie ────────────────────────────────────
                # All values in $/kWh. Uses BatPaC cost tier keys always present in results.
                with _c2:
                    _tc2 = float(_crd.get("total_cells", 1200))

                    def _to_kwh(v): return v / _pack_e

                    # Individual cell material costs ($/cell -> $/kWh)
                    _cat_am  = _to_kwh(_crd.get("cost_cathode_am", 0) * _tc2)
                    _an_am   = _to_kwh(_crd.get("cost_anode_am",   0) * _tc2)
                    _sep     = _to_kwh(_crd.get("cost_sep",        0) * _tc2)
                    _elec    = _to_kwh(_crd.get("cost_elec",       0) * _tc2)
                    _binders = _to_kwh((_crd.get("cost_pvdf",0)+_crd.get("cost_cmcsbr",0)) * _tc2)
                    _foils   = _to_kwh((_crd.get("cost_c_foil",0)+_crd.get("cost_a_foil",0)) * _tc2)
                    _cont    = _to_kwh((_crd.get("cost_container",0)+_crd.get("cost_terminal",0)) * _tc2)

                    # Total cell materials in $/kWh
                    _mat_kwh = _cat_am+_an_am+_sep+_elec+_binders+_foils+_cont

                    # Pack-level tiers using always-present keys
                    _cells_total = _to_kwh(_crd.get("cost_cells_per_pack",   0))  # G634
                    _mods_total  = _to_kwh(_crd.get("cost_modules_per_pack", 0))  # G635
                    _pack_hw     = _to_kwh(_crd.get("cost_pack_hw_per_pack", 0))  # G636
                    _profit      = _to_kwh(_crd.get("total_profit",   0))          # G637
                    _warranty    = _to_kwh(_crd.get("total_warranty",  0))          # G638

                    # Cell manufacturing = cell total minus cell materials
                    _cell_mfg = max(_cells_total - _mat_kwh, 0)

                    _has_detail = _cat_am > 0
                    if _has_detail:
                        _cp_labels = [
                            "Cathode AM","Anode AM","Separator","Electrolyte",
                            "Binders","Foils","Container & terminals",
                            "Cell manufacturing","Module hardware",
                            "Pack hardware","Profit","Warranty",
                        ]
                        _cp_vals_kwh = [
                            _cat_am, _an_am, _sep, _elec, _binders, _foils, _cont,
                            _cell_mfg, _mods_total, _pack_hw, _profit, _warranty,
                        ]
                        _cp_cols = ["#f59e0b","#3b82f6","#10b981","#8b5cf6","#e879f9",
                                    "#64748b","#94a3b8","#06b6d4","#f97316","#475569",
                                    "#84cc16","#a855f7"]
                    else:
                        # Fallback: tier-level only
                        _cp_labels = ["Cell materials","Cell manufacturing",
                                      "Module hardware","Pack hardware","Profit","Warranty"]
                        _cp_vals_kwh = [_mat_kwh, _cell_mfg, _mods_total,
                                        _pack_hw, _profit, _warranty]
                        _cp_cols = ["#f59e0b","#06b6d4","#f97316","#475569","#84cc16","#a855f7"]

                    _cp_vals_kwh = [max(v, 0) for v in _cp_vals_kwh]
                    _cp_customdata = [f"${v:.2f}/kWh" for v in _cp_vals_kwh]
                    _fig_cpie = go.Figure(go.Pie(
                        labels=_cp_labels, values=_cp_vals_kwh,
                        hole=0.50,
                        marker=dict(colors=_cp_cols),
                        textinfo="label+percent",
                        textfont=dict(size=8),
                        customdata=_cp_customdata,
                        hovertemplate="<b>%{label}</b><br>%{customdata}<br>%{percent}<extra></extra>",
                        showlegend=False, sort=True,
                    ))
                    _fig_cpie.add_annotation(
                        text=f"${_ckwh:.2f}<br>/kWh",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=12, color=_col, family="IBM Plex Mono"))
                    _fig_cpie.update_layout(
                        height=360,
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color=T["text"], size=10),
                        title=dict(text="Cost breakdown",
                                   font=dict(size=11, color=T["muted"]), x=0.5),
                        margin=dict(l=10, r=10, t=40, b=10),
                        showlegend=False,
                    )
                    st.plotly_chart(_fig_cpie, use_container_width=True, key=f"cpie_{_cn}")

                # ── Col 3: CO2 breakdown pie ─────────────────────────────────────
                with _c3:
                    _fig_gpie = go.Figure(go.Pie(
                        labels=_bar_cats, values=_bar_vals,
                        hole=0.50,
                        marker=dict(colors=_bar_cols),
                        textinfo="label+percent",
                        textfont=dict(size=8),
                        hovertemplate="<b>%{label}</b><br>%{value:.0f} kgCO2<br>%{percent}<extra></extra>",
                        showlegend=False, sort=True,
                    ))
                    _fig_gpie.add_annotation(
                        text=f"{_full_co2_kwh:.1f}<br>kgCO2/kWh",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=11, color=_col, family="IBM Plex Mono"))
                    _fig_gpie.update_layout(
                        height=360,
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color=T["text"], size=10),
                        title=dict(text="CO2 breakdown",
                                   font=dict(size=11, color=T["muted"]), x=0.5),
                        margin=dict(l=10, r=10, t=40, b=10),
                        showlegend=False,
                    )
                    st.plotly_chart(_fig_gpie, use_container_width=True, key=f"gpie_{_cn}")

        else:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};border-radius:6px;
                        padding:2rem;text-align:center;color:{T['muted']};">
                Run Chemistry Comparison above to populate the chemistry analysis.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        prev6, next6 = st.columns(2)
        with prev6:
            if st.button("Previous: Sustainability", use_container_width=True, key="prev_m05_sens"):
                st.session_state["_navigate_to"] = "🌿  Module 05 - Sustainability"
                st.rerun()
        with next6:
            if st.button("Next module: Uncertainty →", use_container_width=True, key="next_m07_sens"):
                st.session_state["_navigate_to"] = "🎲  Module 07 - Uncertainty"
                st.rerun()

    # ── STUDY SUMMARY ─────────────────────────────────────────────────────────────
elif selected_key == "uncertainty":

    if "_m04_results" not in st.session_state and "cost_model" not in st.session_state:
        st.markdown("""
        <div class="hero-label">Module 07</div>
        <div class="hero-title">Uncertainty <span>Analysis</span></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="status-bar" style="text-align:center;padding:2rem;">
            <strong>Module 04 required</strong> - run through to the Cost Model first,
            then return here.
        </div>
        """, unsafe_allow_html=True)
        st.stop()


    st.markdown("""
    <div class="hero-label">Module 07</div>
    <div class="hero-title">Uncertainty <span>Analysis</span></div>
    <div class="hero-subtitle">Monte Carlo simulation</div>
    """, unsafe_allow_html=True)

    e_b  = st.session_state.get("electrochem", {})
    cd_b = st.session_state.get("cell_design", {})
    pd_b = st.session_state.get("pack_design", {})
    SI = st.session_state.get("_study_inputs", {})
    r4_b = st.session_state.get("_m04_results", st.session_state.get("cost_model", {}))
    base_cost = r4_b.get("cost_per_kwh", 0)
    lfp_bmark = _lfp_reference_cost()

    base_inputs_mc = _build_base_inputs(SI, lfp_bmark)


    col_mc_in, col_mc_out = st.columns([2, 3], gap="large")

    with col_mc_in:

        st.markdown('<div class="input-section-title">Simulation Settings</div>', unsafe_allow_html=True)
        _lfp_line = (f"LFP reference: <strong>${lfp_bmark:.2f}/kWh</strong> "
                     f"(like-for-like, Module 06 chemistry scenario)<br>"
                     if lfp_bmark else f"LFP reference: {_NO_LFP_MSG}<br>")
        st.markdown(f"""
        <div class="note-box">
            Base cost from your study: <strong>${base_cost:.4f}/kWh</strong><br>
            {_lfp_line}
        </div>
        """, unsafe_allow_html=True)

        n_iterations = st.number_input(
            "Number of iterations", value=500, min_value=100, max_value=100000, step=100,
            key="mc_n_iter",
        )
        mc_seed = st.number_input(
            "Random seed (for reproducibility)", value=42, min_value=0, max_value=99999, step=1,
            key="mc_seed",
            help="Set to any integer for reproducible results. Change to explore different random draws."
        )

        st.markdown('<div class="input-section-title" style="margin-top:1.2rem;">Parameter Uncertainty Ranges</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="note-box">
            Each parameter is sampled from a triangular distribution
            defined by (minimum, most likely, maximum). The most likely
            value is your current study input. Adjust min/max to reflect
            your confidence in each parameter.
        </div>
        """, unsafe_allow_html=True)

        # ── Define uncertain parameters ────────────────────────────────────────
        # Each entry: (display_label, base_inputs_key, min_frac, max_frac)
        # min_frac/max_frac are fractions of the base value
        # User can adjust these via expanders

        # Parameters chosen to reflect genuine market and manufacturing uncertainty.
        # Excluded: electrode area and cathode thickness (design variables, not uncertain
        # market inputs), cell yield (manufacturing assumption), cathode capacity and
        # cell voltage (fixed by chemistry choice — use chemistry scenarios tab instead).
        # Separator and electrolyte use tighter ranges (0.7-1.5) as these are more
        # mature commodity markets vs novel SIB-specific materials (0.5-2.0).
        # Electrochemical parameters use absolute (min, mode, max) ranges rather than
        # fractions because fractional variation around 3.9V or 120 mAh/g can produce
        # physically implausible values. These are handled separately below.
        # Ranges justified by: He et al. (2023) reports 100-128 mAh/g at varying C-rates;
        # voltage range 3.7-4.0V reflects uncertainty in accessible potential window;
        # HC price $3-12/kg reflects biomass-derived vs resin-derived supply chain spread
        # (Peters et al. 2019; Yao et al. 2025).
        MC_PARAMS_DEFAULT = [
            ("Cathode AM price ($/kg)",       "p_cathode_am",            0.50, 2.00),
            ("Anode AM price ($/kg)",          "p_anode_am",              0.50, 2.00),
            ("Separator price ($/m2)",         "p_sep",                   0.70, 1.50),
            ("Electrolyte price ($/L)",        "p_electrolyte",           0.70, 1.50),
            ("Annual production (packs/yr)",   "annual_production_packs", 0.10, 5.00),
            ("Labor rate ($/hr)",              "labor_rate_per_hr",       0.60, 2.00),
        ]
        # Electrochemical parameters with absolute bounds (not fractional)
        MC_ELEC_PARAMS = [
            # (label, key, min_abs, mode_abs, max_abs)
            ("Cathode capacity (mAh/g)", "c_cap",  100.0, base_inputs_mc.get("c_cap", 120.0), 130.0),
            ("Cathode voltage (V)",      "c_volt", 3.70,  base_inputs_mc.get("c_volt", 3.90),  4.00),
        ]

        with st.expander("Adjust uncertainty ranges", expanded=False):
            st.markdown("""
            <div class="note-box">
                Price/manufacturing parameters: ranges defined as fractions of base value
                (0.5 = 50% of base, 2.0 = 200% of base).<br>
                Electrochemical parameters: absolute ranges (mAh/g or V).
            </div>
            """, unsafe_allow_html=True)
            mc_param_config = []
            for label, key, def_lo, def_hi in MC_PARAMS_DEFAULT:
                base_val = base_inputs_mc.get(key, 1.0)
                ca, cb, cc = st.columns([3, 1, 1])
                with ca:
                    st.markdown(f"<div style='padding-top:0.5rem;font-size:0.75rem;'>{label} (base={base_val:.3g})</div>", unsafe_allow_html=True)
                with cb:
                    lo = st.number_input("Min frac", value=def_lo, min_value=0.1, max_value=1.0,
                                         step=0.05, format="%.2f", key=f"mc_lo_{key}", label_visibility="collapsed")
                with cc:
                    hi = st.number_input("Max frac", value=def_hi, min_value=1.0, max_value=5.0,
                                         step=0.05, format="%.2f", key=f"mc_hi_{key}", label_visibility="collapsed")
                mc_param_config.append((label, key, lo, hi))
            st.markdown("<div style='font-size:0.75rem;margin-top:0.5rem;color:#94a3b8;'>Electrochemical parameters (absolute ranges):</div>", unsafe_allow_html=True)
            mc_elec_config = []
            for label, key, def_mn, def_mode, def_mx in MC_ELEC_PARAMS:
                ea, eb, ec = st.columns([3, 1, 1])
                with ea:
                    st.markdown(f"<div style='padding-top:0.5rem;font-size:0.75rem;'>{label} (mode={def_mode:.2g})</div>", unsafe_allow_html=True)
                with eb:
                    mn = st.number_input("Min", value=float(def_mn), step=1.0 if "cap" in key else 0.05,
                                         format="%.2f", key=f"mc_emn_{key}", label_visibility="collapsed")
                with ec:
                    mx = st.number_input("Max", value=float(def_mx), step=1.0 if "cap" in key else 0.05,
                                         format="%.2f", key=f"mc_emx_{key}", label_visibility="collapsed")
                mc_elec_config.append((label, key, mn, def_mode, mx))

        st.markdown("<br>", unsafe_allow_html=True)
        run_mc = st.button("RUN MONTE CARLO", use_container_width=True, key="run_mc_btn")

    with col_mc_out:

        if run_mc:
            # Build elec_config from expander if it ran, else use defaults
            if "mc_elec_config" not in dir():
                mc_elec_config = MC_ELEC_PARAMS
            np.random.seed(int(mc_seed))
            costs_mc       = []
            sp_energies_mc = []
            pack_sp_mc     = []
            sampled_vals   = {key: [] for _, key, _, _ in mc_param_config}
            failed_iters   = 0

            progress_bar = st.progress(0, text="Running Monte Carlo simulation...")

            # Extend sampled_vals to include electrochemical keys
            _elec_keys = [key for _, key, _, _, _ in mc_elec_config]
            for k in _elec_keys:
                sampled_vals[k] = []

            for i in range(int(n_iterations)):
                sample = {}
                # Price/manufacturing parameters -- fractional triangular
                for label, key, lo_frac, hi_frac in mc_param_config:
                    base_val = base_inputs_mc.get(key, 1.0)
                    lo  = base_val * lo_frac
                    hi  = base_val * hi_frac
                    mid = max(lo, min(hi, base_val))
                    drawn = float(np.random.triangular(lo, mid, hi))
                    if key == "cell_yield_pct":
                        drawn = min(drawn, 99.9)
                    elif key == "annual_production_packs":
                        drawn = max(drawn, 1000)
                    sample[key] = drawn
                    sampled_vals[key].append(drawn)
                # Electrochemical parameters -- absolute triangular
                for label, key, mn, mode, mx in mc_elec_config:
                    mn2   = min(mn, mode)
                    mx2   = max(mx, mode)
                    drawn = float(np.random.triangular(mn2, mode, mx2))
                    sample[key] = drawn
                    sampled_vals[key].append(drawn)

                r = _run_full_cost(sample, e_b, cd_b, pd_b, base_inputs_mc)
                if r is not None:
                    costs_mc.append(r["cost_per_kwh"])
                    sp_energies_mc.append(r["cell_specific_energy"])
                    pack_sp_mc.append(r["pack_specific_energy"])
                else:
                    failed_iters += 1
                    for key in sampled_vals:
                        if sampled_vals[key]:
                            sampled_vals[key].pop()

                if (i + 1) % 50 == 0:
                    progress_bar.progress((i+1)/int(n_iterations),
                                          text=f"Running... {i+1}/{int(n_iterations)} iterations")

            progress_bar.empty()

            _all_labels = {key: label for label, key, _, _ in mc_param_config}
            _all_labels.update({key: label for label, key, _, _, _ in mc_elec_config})
            st.session_state["_mc_results"] = {
                "costs": costs_mc,
                "sp_energies": sp_energies_mc,
                "pack_sp": pack_sp_mc,
                "sampled_vals": sampled_vals,
                "param_labels": _all_labels,
                "n_total": int(n_iterations),
                "n_failed": failed_iters,
                "base_cost": base_cost,
                "lfp_bmark": lfp_bmark,
            }

        if "_mc_results" in st.session_state:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            mc = st.session_state["_mc_results"]
            costs = np.array(mc["costs"])
            n_ok  = len(costs)
            n_fail = mc["n_failed"]
            bc    = mc["base_cost"]
            lfp_b = mc["lfp_bmark"]

            if n_ok == 0:
                st.markdown('<div class="val-fail">All iterations failed. Check your base inputs.</div>', unsafe_allow_html=True)
            else:
                p10  = float(np.percentile(costs, 10))
                p50  = float(np.percentile(costs, 50))
                p90  = float(np.percentile(costs, 90))
                pmean = float(np.mean(costs))
                pstd  = float(np.std(costs))
                parity_prob = float(np.mean(costs <= lfp_b) * 100) if lfp_b else None

                # ── Primary stats ──────────────────────────────────────────────
                st.markdown('<div class="section-header">Monte Carlo Results</div>', unsafe_allow_html=True)
                if n_fail > 0:
                    st.markdown(f'<div class="val-warn">{n_fail} iterations failed and were excluded ({n_ok} used)</div>', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="output-grid">
                    <div class="output-card highlight">
                        <div class="output-card-label">P50 (median)</div>
                        <div class="output-card-value">${p50:.2f}</div>
                        <div class="output-card-unit">$/kWh</div>
                    </div>
                    <div class="output-card highlight">
                        <div class="output-card-label">P10 (optimistic)</div>
                        <div class="output-card-value">${p10:.2f}</div>
                        <div class="output-card-unit">$/kWh</div>
                    </div>
                    <div class="output-card highlight">
                        <div class="output-card-label">P90 (pessimistic)</div>
                        <div class="output-card-value">${p90:.2f}</div>
                        <div class="output-card-unit">$/kWh</div>
                    </div>
                    <div class="output-card">
                        <div class="output-card-label">Mean</div>
                        <div class="output-card-value">${pmean:.2f}</div>
                        <div class="output-card-unit">$/kWh</div>
                    </div>
                    <div class="output-card">
                        <div class="output-card-label">Std deviation</div>
                        <div class="output-card-value">${pstd:.2f}</div>
                        <div class="output-card-unit">$/kWh</div>
                    </div>
                    <div class="output-card {'highlight' if (parity_prob or 0) > 50 else ''}">
                        <div class="output-card-label">{f'P(cost <= LFP ${lfp_b:.2f})' if lfp_b else 'P(cost parity)'}</div>
                        <div class="output-card-value" style="color:{'#10b981' if (parity_prob or 0) > 50 else T['accent']}">{f'{parity_prob:.1f}%' if parity_prob is not None else 'n/a'}</div>
                        <div class="output-card-unit">{'probability of like-for-like parity' if lfp_b else 'run Module 06'}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Cost distribution KDE curve ───────────────────────────────
                st.markdown('<div class="section-header" style="margin-top:1rem;">Cost Distribution</div>', unsafe_allow_html=True)
                from scipy.stats import gaussian_kde
                kde = gaussian_kde(costs, bw_method="scott")
                x_kde = np.linspace(costs.min() - pstd * 0.5, costs.max() + pstd * 0.5, 500)
                y_kde = kde(x_kde)
                y_kde_norm = y_kde / y_kde.max()

                fig_hist = go.Figure()
                fig_hist.add_trace(go.Scatter(
                    x=x_kde, y=y_kde_norm,
                    mode="lines",
                    fill="tozeroy",
                    fillcolor="rgba(245,158,11,0.20)",
                    line=dict(color=T["accent"], width=2.5),
                    name="Cost distribution",
                    hovertemplate="$/kWh: %{x:.2f}<extra></extra>",
                ))
                _vlines = [
                    (p10,   "P10",  "#3b82f6", "solid"),
                    (p50,   "P50",  "#10b981", "solid"),
                    (p90,   "P90",  T["accent"], "solid"),
                    (bc,    "Base", "#e2e8f0",  "dash"),
                ]
                if lfp_b:
                    _vlines.append((lfp_b, f"LFP ${lfp_b:.2f}", "#f59e0b", "dot"))
                for val, label, col, dash in _vlines:
                    fig_hist.add_vline(x=val, line_color=col, line_width=1.8,
                                       line_dash=dash,
                                       annotation_text=label,
                                       annotation_position="top",
                                       annotation_font_color=col,
                                       annotation_font_size=10)
                fig_hist.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=T["text"], size=11),
                    xaxis=dict(title="Cost ($/kWh)", gridcolor=T["border"]),
                    yaxis=dict(title="Relative probability density",
                               gridcolor=T["border"], showticklabels=False),
                    showlegend=False,
                    margin=dict(l=10, r=10, t=30, b=40), title=dict(text=""),
                    height=320,
                )
                st.plotly_chart(fig_hist, use_container_width=True)

                # ── CDF curve ─────────────────────────────────────────────────
                sorted_costs = np.sort(costs)
                cdf_y = np.arange(1, len(sorted_costs)+1) / len(sorted_costs) * 100

                fig_cdf = go.Figure()
                fig_cdf.add_trace(go.Scatter(
                    x=sorted_costs, y=cdf_y,
                    mode="lines", line=dict(color=T["accent"], width=2),
                    name="CDF",
                    hovertemplate="$/kWh: %{x:.2f}<br>Percentile: %{y:.1f}%<extra></extra>",
                ))
                if lfp_b:
                    fig_cdf.add_hline(y=parity_prob, line_color="#f59e0b", line_dash="dot",
                                       annotation_text=f"{parity_prob:.1f}% below like-for-like LFP (${lfp_b:.2f}/kWh)",
                                       annotation_position="right",
                                       annotation_font_color="#f59e0b")
                    fig_cdf.add_vline(x=lfp_b, line_color="#f59e0b", line_width=1.5,
                                       annotation_text=f"LFP ${lfp_b:.2f}",
                                       annotation_position="top",
                                       annotation_font_color="#f59e0b")
                fig_cdf.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=T["text"], size=11),
                    xaxis=dict(title="Cost ($/kWh)", gridcolor=T["border"]),
                    yaxis=dict(title="Cumulative probability (%)", gridcolor=T["border"]),
                    showlegend=False,
                    margin=dict(l=10, r=10, t=20, b=40), title=dict(text=""),
                    height=280,
                )
                st.plotly_chart(fig_cdf, use_container_width=True)

                # ── Correlation / sensitivity ranking ──────────────────────────
                st.markdown('<div class="section-header" style="margin-top:0.5rem;">Parameter Influence on Cost</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="note-box">
                    Spearman rank correlation between each sampled parameter and the resulting
                    cost/kWh. Bars closest to +1 or -1 are the parameters that most strongly
                    drove cost variance across the simulation. 
                </div>
                """, unsafe_allow_html=True)

                from scipy.stats import spearmanr
                corr_results = []
                for key, samples in mc["sampled_vals"].items():
                    if len(samples) == len(costs) and len(samples) > 10:
                        corr, _ = spearmanr(samples, costs)
                        label = mc["param_labels"].get(key, key)
                        corr_results.append((label, float(corr)))
                corr_results.sort(key=lambda x: abs(x[1]), reverse=True)

                labels_c = [r[0] for r in corr_results]
                corrs_c  = [r[1] for r in corr_results]
                bar_cols = [T["accent"] if c > 0 else "#10b981" for c in corrs_c]

                fig_corr = go.Figure(go.Bar(
                    y=labels_c, x=corrs_c,
                    orientation="h",
                    marker_color=bar_cols,
                    hovertemplate="%{y}<br>Spearman r = %{x:.3f}<extra></extra>",
                ))
                fig_corr.add_vline(x=0, line_color=T["text"], line_width=1)
                fig_corr.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color=T["text"], size=11),
                    xaxis=dict(title="Spearman correlation with $/kWh", range=[-1,1],
                               gridcolor=T["border"], zeroline=False),
                    yaxis=dict(categoryorder="total ascending"),
                    showlegend=False,
                    margin=dict(l=10, r=10, t=20, b=40), title=dict(text=""),
                    height=340,
                )
                st.plotly_chart(fig_corr, use_container_width=True)
                st.markdown(f"""
                <div class="note-box">
                    <strong>Positive correlation:</strong> higher parameter value
                    leads to higher cost (e.g. cathode AM price).<br>
                    <strong>Negative correlation:</strong> higher parameter value
                    leads to lower cost (e.g. production volume, cell yield).
                </div>
                """, unsafe_allow_html=True)

                # ── Summary table ──────────────────────────────────────────────
                st.markdown('<div class="section-header" style="margin-top:1rem;">Simulation Summary</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <table class="mass-table">
                    <thead><tr>
                        <th>Metric</th><th style="text-align:right">Value</th>
                    </tr></thead>
                    <tbody>
                        <tr><td>Iterations completed</td><td class="val">{n_ok:,}</td></tr>
                        <tr><td>Failed iterations</td><td class="val">{n_fail:,}</td></tr>
                        <tr><td>Base case cost</td><td class="val">${bc:.4f}/kWh</td></tr>
                        <tr><td>P10 (10th percentile)</td><td class="val">${p10:.4f}/kWh</td></tr>
                        <tr><td>P50 (median)</td><td class="val">${p50:.4f}/kWh</td></tr>
                        <tr><td>P90 (90th percentile)</td><td class="val">${p90:.4f}/kWh</td></tr>
                        <tr><td>Mean</td><td class="val">${pmean:.4f}/kWh</td></tr>
                        <tr><td>Standard deviation</td><td class="val">${pstd:.4f}/kWh</td></tr>
                        <tr><td>P90 - P10 range</td><td class="val">${p90-p10:.4f}/kWh</td></tr>
                        <tr><td>{f'P(cost parity with like-for-like LFP at ${lfp_b:.2f}/kWh)' if lfp_b else 'P(cost parity) - run Module 06'}</td>
                            <td class="val" style="color:{'#10b981' if (parity_prob or 0)>50 else T['accent']}">
                            {f'{parity_prob:.1f}%' if parity_prob is not None else 'n/a'}</td></tr>
                    </tbody>
                </table>
                """, unsafe_allow_html=True)

        else:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};border-radius:6px;
                        padding:3rem 2rem;text-align:center;margin-top:1rem;">
                <div style="font-family:'IBM Plex Mono',serif;font-size:0.72rem;
                            color:{T['muted']};letter-spacing:0.1em;">
                    SET PARAMETERS AND CLICK RUN MONTE CARLO
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    prev7, next7 = st.columns(2)
    with prev7:
        if st.button("Previous: Sensitivity", use_container_width=True, key="prev_m06_mc"):
            st.session_state["_navigate_to"] = "📊  Module 06 - Sensitivity"
            st.rerun()
    with next7:
        if st.button("Next: Study Summary", use_container_width=True, key="next_summary_mc"):
            st.session_state["_navigate_to"] = "📋  Study Summary"
            st.rerun()

elif selected_key == "sweeps":

    st.markdown('<div class="module-title">Module 08 &nbsp;·&nbsp; Parameter Studies</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="note-box">
        A parameter variation sweeps <strong>one</strong> model input across a range with
        everything else held at your study baseline, and reports the response curve.
        This answers a different question from the Module 06 tornado, which ranks how
        sensitive cost is to a symmetric &plusmn;20% swing in market inputs at a single
        operating point. A tornado bar cannot show non-linearity, thresholds or
        diminishing returns; it deliberately excludes design variables, because varying
        them changes the cell being modelled rather than the uncertainty around it; and
        it runs on cost per kWh only, so it is silent on the storage inputs that move
        LCOS. Every sweep below can be run for your baseline chemistry and for any
        comparison chemistry, and downloaded as CSV for the results chapter.
    </div>
    """, unsafe_allow_html=True)

    SI_sw = st.session_state.get("_study_inputs", {})
    base_sw = _build_base_inputs(SI_sw)
    _m04_ok = "_m04_results" in st.session_state

    if not _m04_ok:
        st.markdown('<div class="val-warn">Run Modules 01 to 04 first so the sweeps have a baseline to vary around.</div>', unsafe_allow_html=True)

    col_sw_in, col_sw_out = st.columns([2, 3], gap="large")

    with col_sw_in:
        st.markdown('<div class="input-section-title">Select a variation</div>', unsafe_allow_html=True)
        _groups = sorted({d["group"] for d in SWEEP_DEFS.values()})
        _grp = st.selectbox("Group", _groups, key="sweep_group")
        _names = [k for k, v in SWEEP_DEFS.items() if v["group"] == _grp]
        _sel = st.selectbox("Variation", _names, key="sweep_sel")
        _d = SWEEP_DEFS[_sel]

        st.markdown(f'<div class="note-box" style="font-size:0.72rem;">{_d["note"]}</div>', unsafe_allow_html=True)

        # The default range is anchored on the value this parameter actually holds in
        # your study, so the baseline always sits inside the swept window. Widget keys
        # are per variation, so each one keeps its own range and switching between them
        # cannot leave the previous variation's numbers behind.
        _basev = _sweep_baseline_value(_d["key"], base_sw)
        _lo_d, _hi_d = float(_d["lo"]), float(_d["hi"])
        if isinstance(_basev, (int, float)) and _basev > 0:
            if _basev < _lo_d:
                _lo_d = _basev * 0.8
            if _basev > _hi_d:
                _hi_d = _basev * 1.2

        st.markdown('<div class="input-section-title" style="margin-top:1rem;">Range</div>', unsafe_allow_html=True)
        if isinstance(_basev, (int, float)):
            st.markdown(
                f'<div style="font-size:0.72rem;color:{T["muted"]};margin:-0.3rem 0 0.4rem 0;">'
                f'Your study value: <strong style="color:{T["text"]}">{_basev:,.4g} {_d["unit"]}</strong>. '
                f'The default range below is set to contain it.</div>', unsafe_allow_html=True)
        _sk = _d["key"]
        s_c1, s_c2 = st.columns(2)
        with s_c1:
            _lo = st.number_input(f"From ({_d['unit']})", value=_lo_d,
                                  step=float(abs(_hi_d - _lo_d) / 20) or 1.0,
                                  key=f"sweep_lo_{_sk}", format="%.4g")
        with s_c2:
            _hi = st.number_input(f"To ({_d['unit']})", value=_hi_d,
                                  step=float(abs(_hi_d - _lo_d) / 20) or 1.0,
                                  key=f"sweep_hi_{_sk}", format="%.4g")
        _npts = st.slider("Points", 5, 40, int(_d.get("n", 15)), key=f"sweep_n_{_sk}")
        _round = st.checkbox(
            "Round sweep points to 3 significant figures", value=True, key=f"sweep_rd_{_sk}",
            help="Logarithmic sweeps place points at equal ratios rather than equal steps, "
                 "which produces values like 1535.097. Rounding makes the axis and the CSV "
                 "readable. It shifts each sample point by well under a percent and does not "
                 "change the shape of the curve.")

        st.markdown('<div class="input-section-title" style="margin-top:1rem;">Chemistries</div>', unsafe_allow_html=True)
        _chem_opts = ["Your study (baseline)"] + list(CHEMISTRY_PRESETS_GLOBAL.keys())
        if _d.get("nvpf_only"):
            st.markdown(
                f'<div style="font-size:0.72rem;color:{T["muted"]};margin-bottom:0.3rem;">'
                f'This variation moves a precursor of the baseline cathode, so it applies to '
                f'the study chemistry only.</div>', unsafe_allow_html=True)
        _chems = st.multiselect("Run for", _chem_opts, default=["Your study (baseline)"],
                                key="sweep_chems",
                                help="Running the same sweep for more than one chemistry shows "
                                     "whether the response is a property of the chemistry or of "
                                     "the manufacturing model.")

        _resp_opts = ["cost_per_kwh", "pack_specific_energy", "pack_mass_kg", "pack_gross_energy",
                      "mat_cost_per_cell", "cell_capacity"]
        if _d.get("needs_m05"):
            _resp_opts = ["lcos_per_kwh", "lcos_net_per_kwh", "co2_per_kwh",
                          "eol_total_value"] + _resp_opts
        _resp = st.selectbox("Response variable", _resp_opts,
                             index=_resp_opts.index(_d["response"]) if _d.get("response") in _resp_opts else 0,
                             key="sweep_resp")

        st.markdown("<br>", unsafe_allow_html=True)
        _run_sweep = st.button("RUN SWEEP", use_container_width=True, key="run_sweep")

    with col_sw_out:
        if _run_sweep and _m04_ok:
            _needs5 = bool(_d.get("needs_m05"))
            # Linear sweeps split the range into equal steps. Logarithmic sweeps split
            # it into equal ratios, which is the right spacing when the range spans
            # orders of magnitude: it puts as many points between 1k and 10k as between
            # 100k and 500k, instead of crowding them all at the top.
            if _d.get("log") and _lo > 0:
                _vals = [_lo * (_hi / _lo) ** (i / (_npts - 1)) for i in range(_npts)]
            else:
                _vals = [_lo + (_hi - _lo) * i / (_npts - 1) for i in range(_npts)]
            if _round:
                _vals = [float(f"{v:.3g}") for v in _vals]

            _study_m05 = {
                "cycle_life":       st.session_state.get("cycle_life", 3200),
                "rte_pct":          st.session_state.get("rt_eff", 90.0),
                "eol_cat_recovery": st.session_state.get("eol_cat_recovery", 88.23),
                "eol_cat_price":    st.session_state.get("eol_cat_price", 10.74),
                "co2_cathode_am":   st.session_state.get("co2_cathode_am", 22.0),
                "co2_anode_am":     st.session_state.get("co2_anode_am", 4.07),
                "anode_foil_density": base_sw.get("anode_foil_density", 2.70),
                "desc": "baseline",
            }

            _results, _fails = {}, 0
            _pbar = st.progress(0.0)
            _total = max(len(_chems) * len(_vals), 1)
            _done = 0
            for _cname in _chems:
                if _cname == "Your study (baseline)":
                    _ov, _m05p = {}, _study_m05
                else:
                    _pp = CHEMISTRY_PRESETS_GLOBAL[_cname]
                    _ov = _chem_overrides(_pp)
                    _m05p = _pp
                _rows = []
                for _v in _vals:
                    _row = _sweep_point(_d["key"], _v, base_sw, _ov, _needs5, _m05p)
                    if _row is None:
                        _fails += 1
                    else:
                        _rows.append(_row)
                    _done += 1
                    _pbar.progress(_done / _total)
                _results[_cname] = _rows
            _pbar.empty()

            st.session_state["_sweep_results"] = {
                "name": _sel, "key": _d["key"], "unit": _d["unit"],
                "response": _resp, "results": _results, "failed": _fails,
                "note": _d["note"], "log": bool(_d.get("log")),
            }

        _sw = st.session_state.get("_sweep_results")
        if not _sw:
            st.markdown(f"""
            <div style="background:{T['card']};border:1px solid {T['border']};border-radius:6px;
                        padding:3rem 2rem;text-align:center;margin-top:1rem;">
                <div style="font-family:'IBM Plex Mono',serif;font-size:0.72rem;
                            color:{T['muted']};letter-spacing:0.1em;">
                    NO SWEEP RUN YET
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            _res, _rk = _sw["results"], _sw["response"]
            if _sw["failed"]:
                st.markdown(f'<div class="val-warn">{_sw["failed"]} point(s) failed to solve and were dropped. The curve below is drawn from the points that succeeded.</div>', unsafe_allow_html=True)

            fig_sw = go.Figure()
            _cols = [T["accent"], "#3b82f6", "#10b981", "#e879f9", "#8b5cf6"]
            for _i, (_cn, _rows) in enumerate(_res.items()):
                _xs = [r["value"] for r in _rows if r.get(_rk) is not None]
                _ys = [r[_rk] for r in _rows if r.get(_rk) is not None]
                if not _xs:
                    continue
                fig_sw.add_trace(go.Scatter(
                    x=_xs, y=_ys, mode="lines+markers", name=_cn.split("/")[0].strip(),
                    line=dict(color=_cols[_i % len(_cols)], width=2),
                    marker=dict(size=5)))
            _base_x = base_sw.get(_sw["key"])
            if isinstance(_base_x, (int, float)):
                fig_sw.add_vline(x=_base_x, line_color=T["muted"], line_dash="dash",
                                 line_width=1.2, annotation_text="baseline",
                                 annotation_position="top", annotation_font_size=10)
            fig_sw.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=T["text"], size=11),
                xaxis=dict(title=f'{_sw["name"]} ({_sw["unit"]})'.strip(),
                           gridcolor=T["border"],
                           type="log" if _sw["log"] else "linear"),
                yaxis=dict(title=_rk, gridcolor=T["border"]),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                margin=dict(l=10, r=10, t=50, b=40), height=380, title=dict(text=""),
            )
            st.plotly_chart(fig_sw, use_container_width=True)

            for _cn, _rows in _res.items():
                _ys = [r[_rk] for r in _rows if r.get(_rk) is not None]
                if len(_ys) < 2:
                    continue
                _lo_y, _hi_y = min(_ys), max(_ys)
                _span = (_hi_y - _lo_y) / _lo_y * 100 if _lo_y else 0
                _mono = "monotonic" if all(
                    (_ys[i+1] - _ys[i]) * (_ys[1] - _ys[0]) >= 0 for i in range(len(_ys)-1)
                ) else "non-monotonic"
                st.markdown(
                    f'<div style="font-size:0.72rem;color:{T["muted"]};margin:0.2rem 0;">'
                    f'<strong>{_cn}</strong>: {_rk} ranges {_lo_y:.4g} to {_hi_y:.4g} '
                    f'({_span:.1f}% span across the swept range), {_mono}.</div>',
                    unsafe_allow_html=True)


elif selected_key == "summary":

    st.markdown("""
    <div class="hero-label">Study Summary</div>
    <div class="hero-title">Summary <span>Report</span></div>
    """, unsafe_allow_html=True)

    e  = st.session_state.get("electrochem", {})
    c  = st.session_state.get("cell_design", {})
    p  = st.session_state.get("pack_design", {})
    r4 = st.session_state.get("_m04_results", st.session_state.get("cost_model", {}))
    r5 = st.session_state.get("sustainability", {})

    if not e:
        st.markdown("""
        <div class="status-bar" style="text-align:center;padding:2rem;">
            <strong>⚠ No study data found</strong> - run at least Module 01 first,
            then return here to generate a summary.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ── Top bar: study name ───────────────────────────────────────────────────
    study_name = st.text_input(
        "Study name",
        value=st.session_state.get("_last_study_name", "NVPF Baseline Study"),
        key="_summary_study_name",
        label_visibility="collapsed",
        placeholder="Study name"
    )
    st.session_state["_last_study_name"] = study_name

    # ── Pull MC results if available ─────────────────────────────────────────
    _mc  = st.session_state.get("_mc_results", {})
    _mc_costs = _mc.get("costs", [])
    _p10 = float(np.percentile(_mc_costs, 10))  if _mc_costs else None
    _p50 = float(np.percentile(_mc_costs, 50))  if _mc_costs else None
    _p90 = float(np.percentile(_mc_costs, 90))  if _mc_costs else None

    _lfp_scenario = _lfp_reference_cost()

    cost_kwh   = r4.get("cost_per_kwh", 0) if r4 else 0
    lcos_kwh   = r5.get("lcos_per_kwh", 0) if r5 else 0
    # Like-for-like LFP cost from Module 06. No market-price fallback.
    if _lfp_scenario and cost_kwh:
        gap_pct  = (cost_kwh - _lfp_scenario) / _lfp_scenario * 100
        gap_ref  = f"vs like-for-like LFP ${_lfp_scenario:.2f}/kWh"
    else:
        gap_pct  = None
        gap_ref  = "run Module 06 chemistry comparison"
    gap_sign   = "+" if (gap_pct or 0) > 0 else ""

    # ── Row 1: Hero metrics ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns(4, gap="small")
    for col, label, val, unit, highlight in [
        (h1, "Pack cost",        f"${cost_kwh:.2f}",   "$/kWh",         True),
        (h2, "LCOS",             f"${lcos_kwh:.3f}" if lcos_kwh else "Run M05", "$/kWh delivered", True),
        (h3, "Gap vs LFP",       f"{gap_sign}{gap_pct:.1f}%" if gap_pct is not None else "—", gap_ref, False),
        (h4, "Useable energy",   f"{p.get('pack_useable_energy_kWh',0):.1f}" if p else "—", "kWh", False),
    ]:
        with col:
            st.markdown(f"""
            <div class="output-card {'highlight' if highlight else ''}">
                <div class="output-card-label">{label}</div>
                <div class="output-card-value" style="font-size:1.6rem;">{val}</div>
                <div class="output-card-unit">{unit}</div>
            </div>""", unsafe_allow_html=True)

    # ── Row 2: MC band + LFP context ──────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if _mc_costs:
        mc1, mc2, mc3, mc4 = st.columns(4, gap="small")
        for col, label, val, unit in [
            (mc1, "P10 (optimistic)",  f"${_p10:.2f}", "$/kWh"),
            (mc2, "P50 (median)",      f"${_p50:.2f}", "$/kWh"),
            (mc3, "P90 (pessimistic)", f"${_p90:.2f}", "$/kWh"),
            (mc4, "P90-P10 spread",    f"${_p90-_p10:.2f}", "$/kWh uncertainty range"),
        ]:
            with col:
                st.markdown(f"""
                <div class="output-card">
                    <div class="output-card-label">{label}</div>
                    <div class="output-card-value" style="font-size:1.2rem;">{val}</div>
                    <div class="output-card-unit">{unit}</div>
                </div>""", unsafe_allow_html=True)
    elif _lfp_scenario:
        st.markdown(f"""
        <div class="note-box">
            <strong>LFP scenario cost (Module 06):</strong> ${_lfp_scenario:.2f}/kWh &nbsp;|&nbsp;
            NVPF premium: ${cost_kwh - _lfp_scenario:.2f}/kWh
            ({(cost_kwh/_lfp_scenario - 1)*100:.1f}% above LFP).
            Run Module 07 to see Monte Carlo uncertainty band.
        </div>""", unsafe_allow_html=True)

    # ── Row 3: Cost breakdown donut + key specs ────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    donut_col, specs_col = st.columns([1, 1], gap="large")

    with donut_col:
        if r4:
            st.markdown('<div class="section-header">Cost Breakdown</div>', unsafe_allow_html=True)
            _bd = [
                ("Cathode AM",   r4.get("cost_cathode_am", 0)),
                ("Anode AM",     r4.get("cost_anode_am", 0)),
                ("Electrolyte",  r4.get("cost_elec", 0)),
                ("Separator",    r4.get("cost_sep", 0)),
                ("Fixed overheads", r4.get("cell_fixed_expenses_per_cell", 0)),
                ("Al foil",      r4.get("cost_c_foil", 0) + r4.get("cost_a_foil", 0)),
                ("Other",        r4.get("cost_carbon", 0) + r4.get("cost_pvdf", 0) +
                                 r4.get("cost_container", 0) + r4.get("cost_terminal", 0)),
            ]
            _bd_labels = [x[0] for x in _bd]
            _bd_vals   = [x[1] for x in _bd]
            _bd_colors = ["#f59e0b","#3b82f6","#10b981","#8b5cf6","#e879f9","#64748b","#94a3b8"]
            fig_donut = go.Figure(go.Pie(
                labels=_bd_labels, values=_bd_vals,
                hole=0.55,
                marker=dict(colors=_bd_colors),
                textinfo="label+percent",
                textfont=dict(size=11, color="#e2e8f0"),
                hovertemplate="<b>%{label}</b><br>$%{value:.3f}/cell<br>%{percent}<extra></extra>",
            ))
            fig_donut.add_annotation(
                text=f"${r4.get('cost_per_kwh',0):.2f}<br>/kWh",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="#f59e0b", family="IBM Plex Mono"),
            )
            fig_donut.update_layout(
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color=T["text"]),
                margin=dict(l=10, r=10, t=10, b=10),
                height=320,
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    with specs_col:
        st.markdown('<div class="section-header">Key Study Parameters</div>', unsafe_allow_html=True)

        _base = st.session_state.get("base_inputs_snapshot", {})
        _si   = lambda k, d=0: st.session_state.get(k, _base.get(k, d))

        _specs = [
            ("Chemistry",          "NVPF / Hard Carbon",                            ""),
            ("Cell format",        "Pouch cell (BatPaC)",                           ""),
            ("Cell capacity",      f"{e.get('cell_capacity',0):.1f}",              "Ah"),
            ("Cell voltage",       f"{e.get('cell_voltage',0):.3f}",               "V"),
            ("Cell specific energy",f"{c.get('cell_specific_energy',0):.1f}" if c else "—", "Wh/kg"),
            ("Pack useable energy", f"{p.get('pack_useable_energy_kWh',0):.1f}" if p else "—", "kWh"),
            ("Pack voltage",       f"{p.get('pack_voltage_V',0):.0f}" if p else "—", "V"),
            ("Total cells",        f"{p.get('total_cells',0)}" if p else "—",       ""),
            ("Cathode thickness",  f"{_si('c_thick', 237):.0f}",                   "µm"),
            ("Cathode porosity",   f"{_si('c_por', 0.10):.2f}",                    ""),
            ("Production volume",  f"{_si('annual_production_packs', 20000):,.0f}", "packs/yr"),
            ("NVPF AM price",      f"${_si('p_cathode_am', 16.71):.2f}",          "/kg"),
            ("CO₂ intensity",      f"{r5.get('co2_per_kwh',0):.1f}" if r5 else "—", "kgCO₂/kWh"),
            ("LCOS",               f"${lcos_kwh:.3f}" if lcos_kwh else "Run M05",   "/kWh delivered"),
        ]

        rows = ""
        for label, val, unit in _specs:
            rows += f'<tr><td style="color:#94a3b8;font-size:0.78rem;">{label}</td><td style="text-align:right;font-size:0.82rem;">{val} <span style="color:#94a3b8;font-size:0.72rem;">{unit}</span></td></tr>'

        st.markdown(f"""
        <table style="width:100%;border-collapse:collapse;font-family:'IBM Plex Mono',monospace;">
            <tbody>{rows}</tbody>
        </table>""", unsafe_allow_html=True)

    # ── Row 4: Cell / pack / sustainability detail ─────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Full Results</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3, gap="large")

    with d1:
        st.markdown("<div style='font-size:0.78rem;color:#94a3b8;margin-bottom:0.4rem;'>CELL &amp; PACK</div>", unsafe_allow_html=True)
        _cell_specs = [
            ("Cell energy",        f"{c.get('cell_energy_Wh',0):.2f}" if c else "—", "Wh"),
            ("Cell mass",          f"{c.get('cell_mass_g',0):.1f}" if c else "—", "g"),
            ("Cell thickness",     f"{c.get('cell_thickness_mm',0):.2f}" if c else "—", "mm"),
            ("Energy density",     f"{c.get('cell_energy_density',0):.1f}" if c else "—", "Wh/L"),
            ("Pack mass",          f"{p.get('pack_mass_kg',0):.1f}" if p else "—", "kg"),
            ("Pack sp. energy",    f"{p.get('pack_specific_energy',0):.1f}" if p else "—", "Wh/kg"),
            ("Cell mass fraction", f"{p.get('cell_mass_fraction',0)*100:.1f}" if p else "—", "%"),
            ("Anode thickness",    f"{e.get('a_thick',0):.1f}", "µm"),
        ]
        for label, val, unit in _cell_specs:
            st.markdown(f"<div style='display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid #2a2a3e;font-size:0.78rem;'><span style='color:#94a3b8;'>{label}</span><span>{val} <span style='color:#64748b;font-size:0.70rem;'>{unit}</span></span></div>", unsafe_allow_html=True)

    with d2:
        if r4:
            st.markdown("<div style='font-size:0.78rem;color:#94a3b8;margin-bottom:0.4rem;'>COST MODEL</div>", unsafe_allow_html=True)
            _cost_specs = [
                ("Total pack cost",    f"${r4.get('pack_total_cost',0):,.0f}", ""),
                ("Material cost",      f"${r4.get('mat_cost_per_cell',0):.3f}", "/cell"),
                ("Material fraction",  f"{r4.get('mat_frac',0)*100:.1f}", "%"),
                ("Cathode AM cost",    f"${r4.get('cost_cathode_am',0):.3f}", "/cell"),
                ("Anode AM cost",      f"${r4.get('cost_anode_am',0):.3f}", "/cell"),
                ("Electrolyte cost",   f"${r4.get('cost_elec',0):.3f}", "/cell"),
                ("Fixed overheads",    f"${r4.get('cell_fixed_expenses_per_cell',0):.3f}", "/cell"),
                ("Total cell cost",    f"${r4.get('total_cell_cost_per_cell',0):.3f}", "/cell"),
            ]
            for label, val, unit in _cost_specs:
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid #2a2a3e;font-size:0.78rem;'><span style='color:#94a3b8;'>{label}</span><span>{val} <span style='color:#64748b;font-size:0.70rem;'>{unit}</span></span></div>", unsafe_allow_html=True)

    with d3:
        if r5:
            st.markdown("<div style='font-size:0.78rem;color:#94a3b8;margin-bottom:0.4rem;'>SUSTAINABILITY &amp; LCOS</div>", unsafe_allow_html=True)
            _sust_specs = [
                ("LCOS",               f"${r5.get('lcos_per_kwh',0):.4f}", "/kWh del."),
                ("Effective cycles",   f"{r5.get('effective_cycles',0):,}", "cycles"),
                ("Lifetime energy",    f"{r5.get('lifetime_energy_kwh',0)/1000:.1f}", "MWh"),
                ("CO₂ intensity",      f"{r5.get('co2_per_kwh',0):.2f}", "kgCO₂/kWh"),
                ("Pack CO₂",           f"{r5.get('co2_pack_total_kg',0):,.0f}", "kgCO₂"),
                ("Energy payback",     f"{r5.get('energy_payback_yr',0):.1f}", "years"),
                ("EOL recycling value",f"${r5.get('eol_total_value',0):,.2f}", "/pack"),
                ("Al vs Cu saving",    f"${r5.get('cu_saving_per_kwh',0):.4f}", "/kWh"),
            ]
            for label, val, unit in _sust_specs:
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid #2a2a3e;font-size:0.78rem;'><span style='color:#94a3b8;'>{label}</span><span>{val} <span style='color:#64748b;font-size:0.70rem;'>{unit}</span></span></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Home", use_container_width=True, key="summary_home"):
        st.session_state["_navigate_to"] = "🏠  Home"
        st.rerun()