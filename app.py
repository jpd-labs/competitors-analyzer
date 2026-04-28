"""
Getlinko · Competitive Intelligence Dashboard
=============================================
Streamlit app — single file, no external DB needed.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import datetime, re

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Getlinko · Intelligence Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<meta name="robots" content="noindex, nofollow">',
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# THEME / CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

:root {
    /* Sidebar palette */
    --sb-bg:      #261a4b;
    --sb-text:    #ffffff;
    --sb-muted:   rgba(255,255,255,0.6);
    --sb-border:  rgba(255,255,255,0.12);
    --sb-accent:  #f3006e;

    /* Main area palette */
    --g-bg:       #FFFCF9;
    --g-ink:      #261a4b;
    --g-card:     #ffffff;
    --g-border:   #e2ddf5;
    --g-accent:   #f3006e;
    --g-green:    #0dab6a;
    --g-red:      #e05260;
    --g-amber:    #d4820a;
    --g-text:     #261a4b;
    --g-muted:    #7a6fa8;

    /* Header palette */
    --hd-bg:      #CBCBCB;
    --hd-text:    #261a4b;

    --g-font:     'Syne', sans-serif;
    --g-mono:     'DM Mono', monospace;
}

/* ── MAIN BACKGROUND ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
section.main > div {
    background: var(--g-bg) !important;
    color: var(--g-text) !important;
    font-family: var(--g-font) !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background: var(--sb-bg) !important;
    border-right: 1px solid var(--sb-border);
}

/* All text inside sidebar */
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] div {
    color: var(--sb-text) !important;
}

/* Sidebar muted/helper text */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] small,
[data-testid="stSidebar"] .st-emotion-cache-1xw8zd0,
[data-testid="stSidebar"] .st-emotion-cache-qcqlej {
    color: var(--sb-muted) !important;
}

/* Sidebar file uploader text (uploaded filenames) */
[data-testid="stSidebar"] [data-testid="stFileUploaderFileName"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFileData"],
[data-testid="stSidebar"] .uploadedFileName,
[data-testid="stSidebar"] small {
    color: #ffffff !important;
}

/* Sidebar inputs background & placeholder */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="input"] input {
    background: rgba(255,255,255,0.08) !important;
    color: #ffffff !important;
    border-color: var(--sb-border) !important;
}
[data-testid="stSidebar"] input::placeholder,
[data-testid="stSidebar"] textarea::placeholder {
    color: var(--sb-bg) !important;
    opacity: 1 !important;
}

/* Sidebar multiselect pills */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: var(--sb-accent) !important;
    border-color: var(--sb-accent) !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span,
[data-testid="stSidebar"] [data-baseweb="tag"] svg {
    color: #ffffff !important;
    fill: #ffffff !important;
}

/* Sidebar multiselect dropdown container */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08) !important;
    border-color: var(--sb-border) !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span {
    color: #ffffff !important;
}

/* Sidebar slider track & thumb */
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
    background: var(--sb-accent) !important;
    border-color: var(--sb-accent) !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div > div {
    background: var(--sb-accent) !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="progressbar"] {
    background: var(--sb-accent) !important;
}

/* Sidebar expander */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    border-color: var(--sb-border) !important;
    background: rgba(255,255,255,0.05) !important;
}
/* Expander summary (header bar) → #f3006e */
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpander"] summary > div,
[data-testid="stSidebar"] [data-testid="stExpander"] summary p {
    background: #f3006e !important;
    color: #ffffff !important;
    border-radius: 6px !important;
    padding: 0.3rem 0.6rem !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}

/* Expander — ✅/⬜ badge pills */
[data-testid="stSidebar"] [data-testid="stExpander"] td:last-child,
[data-testid="stSidebar"] [data-testid="stExpander"] strong {
    background: transparent !important;
}
/* Pills on "Obligatorias" and "Opcionales" inline code / emphasis */
[data-testid="stSidebar"] [data-testid="stExpander"] code {
    background: #f3006e !important;
    color: #ffffff !important;
    border-radius: 4px !important;
    padding: 1px 6px !important;
    font-size: 0.72rem !important;
    border: none !important;
}
            

/* SQL code block → rgba(255,255,255,0.08) */
[data-testid="stSidebar"] [data-testid="stExpander"] pre,
[data-testid="stSidebar"] [data-testid="stExpander"] pre code,
[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stCode"],
[data-testid="stSidebar"] [data-testid="stExpander"] .stCode,
[data-testid="stSidebar"] [data-testid="stExpander"] .stCodeBlock {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 6px !important;
    color: #ffffff !important;
}

/* Sidebar file uploader — dropzone inner container */
[data-testid="stSidebar"] .st-emotion-cache-h2yu1l {
    background-color: rgba(255,255,255,0.08) !important;
}

/* Sidebar file uploader box */
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] * {
    color: #ffffff !important;
}
/* Browse files button → #f3006e */
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] button,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] button,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
[data-testid="stSidebar"] .stFileUploader button {
    background: #f3006e !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: var(--g-mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploadDropzone"] button:hover,
[data-testid="stSidebar"] .stFileUploader button:hover {
    background: #c8005a !important;
}
/* Drag & drop text and helper text */
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] * {
    color: rgba(255,255,255,0.75) !important;
}
/* Uploaded file name row (rgb 49,51,63 fix) */
[data-testid="stSidebar"] [data-testid="stFileUploaderFileName"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFileName"] *,
[data-testid="stSidebar"] [data-testid="stFileUploaderFileData"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFileData"] *,
[data-testid="stSidebar"] .st-emotion-cache-9ycgxx,
[data-testid="stSidebar"] .st-emotion-cache-1gulkj5 {
    color: #ffffff !important;
}
/* File uploader delete/X button */
[data-testid="stSidebar"] [data-testid="stFileUploaderDeleteBtn"] button {
    background: transparent !important;
    color: rgba(255,255,255,0.6) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDeleteBtn"] button:hover {
    background: rgba(243,0,110,0.2) !important;
    color: #f3006e !important;
    border-color: #f3006e !important;
}

/* ── HEADER STRIP ── */
.gl-header {
    background: var(--hd-bg);
    border-bottom: 2px solid #b0b0b0;
    padding: 1.5rem 2rem 1rem;
    margin: -1rem -1rem 1.5rem;
}
.gl-title {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--hd-text) !important;
    margin: 0;
}
.gl-subtitle {
    font-family: var(--g-mono);
    font-size: 0.72rem;
    color: #555 !important;
    margin: 0.2rem 0 0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── MAIN TEXT ── */
h1, h2, h3, h4 {
    font-family: var(--g-font) !important;
    color: var(--g-text) !important;
}
p, li { color: var(--g-text) !important; }
.stMarkdown p, .stMarkdown li { color: var(--g-text) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--g-border) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--g-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--g-muted) !important;
    padding: 0.6rem 1.2rem !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--g-text) !important;
    border-bottom: 2px solid var(--g-accent) !important;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: var(--g-card);
    border: 1px solid var(--g-border);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    box-shadow: 0 1px 4px rgba(38,26,75,0.06);
}
[data-testid="stMetricLabel"] {
    font-family: var(--g-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--g-muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--g-font) !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em !important;
    color: var(--g-text) !important;
}
[data-testid="stMetricDelta"] { color: var(--g-muted) !important; }

/* Dataframe */
.stDataFrame {
    border: 1px solid var(--g-border) !important;
    border-radius: 8px;
}

/* Buttons (main area) */
.stDownloadButton button, .stButton button {
    background: var(--g-ink) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: var(--g-mono) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
}
.stDownloadButton button:hover, .stButton button:hover {
    background: var(--g-accent) !important;
    color: #ffffff !important;
}

/* Radio & select in main */
[data-testid="stRadio"] label, [data-testid="stSelectbox"] label {
    color: var(--g-text) !important;
}

/* KPI / opp / alert cards */
.kpi-card {
    background: var(--g-card);
    border: 1px solid var(--g-border);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    flex: 1; min-width: 160px;
    position: relative; overflow: hidden;
    box-shadow: 0 1px 4px rgba(38,26,75,0.06);
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--g-accent);
}
.kpi-label {
    font-family: var(--g-mono); font-size: 0.65rem;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--g-muted); margin-bottom: 0.4rem;
}
.kpi-value {
    font-size: 1.9rem; font-weight: 800;
    color: var(--g-text); line-height: 1; letter-spacing: -0.04em;
}
.kpi-delta { font-family: var(--g-mono); font-size: 0.72rem; margin-top: 0.3rem; }
.kpi-delta.up   { color: var(--g-green); }
.kpi-delta.down { color: var(--g-red); }
.kpi-delta.flat { color: var(--g-muted); }

.alert-card {
    background: var(--g-card);
    border: 1px solid var(--g-border);
    border-left: 3px solid var(--level-color, var(--g-accent));
    border-radius: 8px; padding: 0.8rem 1rem;
    margin-bottom: 0.6rem; font-size: 0.85rem;
    color: var(--g-text) !important;
}
.alert-card .tag {
    font-family: var(--g-mono); font-size: 0.62rem;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--level-color, var(--g-accent)); margin-bottom: 0.2rem;
}
.alert-card b, .alert-card strong { color: var(--g-text) !important; }

.opp-card {
    background: var(--g-card);
    border: 1px solid var(--g-border);
    border-radius: 10px; padding: 1rem 1.2rem;
    flex: 1; min-width: 220px;
    box-shadow: 0 1px 4px rgba(38,26,75,0.06);
}
.opp-card .opp-url {
    font-family: var(--g-mono); font-size: 0.72rem;
    color: var(--g-accent) !important; margin-bottom: 0.3rem; word-break: break-all;
}
.opp-card .opp-score { font-size: 1.4rem; font-weight: 800; color: var(--g-green) !important; }
.opp-card .opp-meta  { font-size: 0.76rem; color: var(--g-muted) !important; margin-top: 0.2rem; }
.opp-card b, .opp-card div { color: var(--g-text) !important; }

.sec-header {
    font-size: 0.7rem; font-family: var(--g-mono);
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--g-muted) !important;
    border-bottom: 1px solid var(--g-border);
    padding-bottom: 0.4rem; margin: 1.5rem 0 0.8rem;
}

.badge {
    display: inline-block; font-family: var(--g-mono); font-size: 0.6rem;
    letter-spacing: 0.06em; text-transform: uppercase;
    padding: 2px 7px; border-radius: 20px;
    background: var(--g-border); color: var(--g-muted);
}
.badge.green { background: rgba(13,171,106,.12); color: var(--g-green); }
.badge.red   { background: rgba(224,82,96,.12);  color: var(--g-red); }
.badge.amber { background: rgba(212,130,10,.12); color: var(--g-amber); }
.badge.blue  { background: rgba(243,0,110,.10);  color: var(--g-accent); }

/* Captions */
.stCaptionContainer, [data-testid="stCaptionContainer"] { color: var(--g-muted) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
COLS_OBLIGATORIAS = ['URL', 'Precio']
COLS_NUMERICAS    = ['DA', 'PA', 'DR', 'CF', 'TF', 'Tráfico', 'Precio']
PRICE_ALERT_PCT   = 15   # % sobre mercado para alerta roja de precio
PRIORITY_COLS     = ['DR', 'Tráfico', 'Precio']

PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Mono, monospace', color='#261a4b', size=11),
    xaxis=dict(gridcolor='#e2ddf5', zerolinecolor='#e2ddf5', color='#261a4b'),
    yaxis=dict(gridcolor='#e2ddf5', zerolinecolor='#e2ddf5', color='#261a4b'),
    colorway=['#f3006e','#261a4b','#7a6fa8','#0dab6a','#d4820a','#5b3fa8'],
    margin=dict(l=40, r=20, t=40, b=40),
)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def limpiar_numeros(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(
                df[c].astype(str).str.replace(r'[^\d.]', '', regex=True),
                errors='coerce').fillna(0)
    return df

def normalizar_url(s):
    return s.astype(str).str.strip().str.lower().str.rstrip('/')

def leer_csv(f):
    for sep in [',', ';', '\t']:
        try:
            f.seek(0)
            df = pd.read_csv(f, sep=sep)
            if df.shape[1] > 1:
                df.columns = df.columns.str.strip()
                return df
        except Exception:
            pass
    f.seek(0)
    df = pd.read_csv(f)
    df.columns = df.columns.str.strip()
    return df

def leer_archivo(f):
    if f.name.lower().endswith(('.xlsx', '.xls')):
        df = pd.read_excel(f)
    else:
        df = leer_csv(f)
    df.columns = df.columns.str.strip()
    return df

def validar(df, nombre):
    faltan = [c for c in COLS_OBLIGATORIAS if c not in df.columns]
    return faltan

def enrich_ahrefs(df, ahrefs):
    """Merge Ahrefs DR/traffic into df by URL key."""
    if ahrefs is None or ahrefs.empty:
        return df
    ah = ahrefs.copy()
    ah['_key'] = normalizar_url(ah.iloc[:, 0])  # first col = URL
    # detect DR / traffic cols
    dr_col  = next((c for c in ah.columns if 'dr' in c.lower()), None)
    tr_col  = next((c for c in ah.columns if 'traffic' in c.lower() or 'tráfico' in c.lower() or 'visits' in c.lower()), None)
    merge_cols = {'_key': '_key'}
    if dr_col:  merge_cols[dr_col]  = '_ah_dr'
    if tr_col:  merge_cols[tr_col]  = '_ah_tr'
    ah = ah.rename(columns={k: v for k, v in merge_cols.items() if k != '_key'})[list(merge_cols.values())]
    df = df.merge(ah, on='_key', how='left')
    if '_ah_dr' in df.columns:
        df['DR'] = df['_ah_dr'].combine_first(df.get('DR', pd.Series(0, index=df.index))).fillna(0)
        df.drop(columns=['_ah_dr'], inplace=True)
    if '_ah_tr' in df.columns:
        df['Tráfico'] = df['_ah_tr'].combine_first(df.get('Tráfico', pd.Series(0, index=df.index))).fillna(0)
        df.drop(columns=['_ah_tr'], inplace=True)
    return df

def score_oportunidad(row):
    dr  = row.get('DR', 0) or 0
    tr  = row.get('Tráfico', 0) or 0
    pr  = row.get('Precio', 1) or 1
    return round((dr * 0.5 + min(tr / 1000, 50) * 0.5) / max(pr / 100, 1), 2)

def to_csv_bytes(df):
    return df.to_csv(index=False).encode('utf-8')

def fmt_num(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(n))

def plotly_fig(fig):
    fig.update_layout(**PLOTLY_THEME)
    return fig

def drop_aux(df):
    return df.drop(columns=[c for c in ['_key','_es_nueva','Origen'] if c in df.columns], errors='ignore')

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="gl-header">
  <p class="gl-title">📡 Getlinko Intelligence</p>
  <p class="gl-subtitle">Competitive Marketplace Dashboard · {datetime.datetime.now().strftime('%d %b %Y, %H:%M')}</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR — DATA UPLOAD
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Fuentes de datos")

    with st.expander("ℹ️ Formato CSV requerido", expanded=False):
        st.markdown("""
**Obligatorias:** `URL`, `Precio`  
**Opcionales:** `País`, `Temática`, `DR`, `DA`, `PA`, `CF`, `TF`, `Tráfico`

---
**Query Getlinko:**
```sql
SELECT m.url as "URL", m.url_canonical as "Url canónica",
  t.name as "Temática", m.price as "Precio", c.code as "País",
  mm.da as "DA", mm.pa as "PA", mm.dr as "DR",
  mm.cf as "CF", mm.tf as "TF",
  mm.visits as "Tráfico web/mes"
FROM medias m
INNER JOIN countries c ON c.id = m.country_id
INNER JOIN topics t ON t.id = m.main_topic_id
INNER JOIN (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY media_id ORDER BY created_at DESC) AS rn
    FROM media_metrics
) mm ON mm.media_id = m.id AND mm.rn = 1
WHERE m.type IN ('blog', 'newspaper')
  AND m.status = 'APPROVED'
  AND m.deleted_at IS NULL
  AND m.hidden = 0
```
        """)

    file_getlinko = st.file_uploader("🟣 Catálogo Getlinko", type=["csv","xlsx"])
    files_comp    = st.file_uploader("🔵 Competidores (uno o varios)", type=["csv","xlsx"], accept_multiple_files=True)
    file_ahrefs   = st.file_uploader("📊 Métricas Ahrefs (opcional)", type=["csv","xlsx"])

    st.markdown("---")
    st.markdown("### 🔧 Filtros globales")

# ─────────────────────────────────────────────
# LOAD & VALIDATE DATA
# ─────────────────────────────────────────────
df_gl   = None
df_comp = None
df_ah   = None
errors  = []

if file_getlinko:
    raw = leer_archivo(file_getlinko)
    missing = validar(raw, file_getlinko.name)
    if missing:
        errors.append(f"❌ **{file_getlinko.name}** — faltan columnas: {', '.join(missing)}")
    else:
        df_gl = limpiar_numeros(raw.copy(), COLS_NUMERICAS)
        df_gl['_key'] = normalizar_url(df_gl['URL'])
        df_gl['Marketplace'] = 'Getlinko'

if file_ahrefs:
    df_ah = leer_archivo(file_ahrefs)
    df_ah = limpiar_numeros(df_ah, ['DR','Tráfico','visits','traffic'])

if files_comp:
    dfs = []
    for f in files_comp:
        raw = leer_archivo(f)
        missing = validar(raw, f.name)
        if missing:
            errors.append(f"❌ **{f.name}** — faltan columnas: {', '.join(missing)}")
        else:
            tmp = limpiar_numeros(raw.copy(), COLS_NUMERICAS)
            tmp['_key']        = normalizar_url(tmp['URL'])
            tmp['Marketplace'] = f.name.rsplit('.',1)[0]
            dfs.append(tmp)
    if dfs:
        df_comp = pd.concat(dfs, ignore_index=True)

# Show errors
for e in errors:
    st.error(e)

# ─────────────────────────────────────────────
# NO DATA STATE
# ─────────────────────────────────────────────
if df_gl is None or df_comp is None:
    st.markdown("""
<div style="text-align:center; padding: 4rem 2rem; color: #7a7f99;">
  <div style="font-size:3rem; margin-bottom:1rem;">📡</div>
  <p style="font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:700; color:#e8eaf2;">
    Sube los datos para comenzar
  </p>
  <p style="font-family:'DM Mono',monospace; font-size:0.78rem;">
    Necesitas el catálogo de Getlinko + al menos un competidor
  </p>
</div>
""", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# ENRICH WITH AHREFS
# ─────────────────────────────────────────────
if df_ah is not None:
    df_gl   = enrich_ahrefs(df_gl, df_ah)
    df_comp = enrich_ahrefs(df_comp, df_ah)

# ─────────────────────────────────────────────
# CORE ANALYSIS TABLES
# ─────────────────────────────────────────────
keys_gl   = set(df_gl['_key'])
keys_comp = set(df_comp['_key'])

# Exclusivos Getlinko
df_excl_gl   = df_gl[~df_gl['_key'].isin(keys_comp)].copy()

# Solo competencia (captación)
df_excl_comp = df_comp[~df_comp['_key'].isin(keys_gl)].copy()
df_excl_comp['Score'] = df_excl_comp.apply(score_oportunidad, axis=1)

# Compartidos — precio comparativo
df_shared_gl   = df_gl[df_gl['_key'].isin(keys_comp)].copy()
df_shared_comp = df_comp[df_comp['_key'].isin(keys_gl)].copy()

price_comp_min = df_shared_comp.groupby('_key')['Precio'].min().reset_index().rename(columns={'Precio':'PrecioCompMin'})
price_comp_avg = df_shared_comp.groupby('_key')['Precio'].mean().reset_index().rename(columns={'Precio':'PrecioCompAvg'})
mkt_cheapest   = df_shared_comp.loc[df_shared_comp.groupby('_key')['Precio'].idxmin(), ['_key','Marketplace']].rename(columns={'Marketplace':'MktMasBarato'})

df_pricing = df_shared_gl.merge(price_comp_min, on='_key', how='left') \
                          .merge(price_comp_avg, on='_key', how='left') \
                          .merge(mkt_cheapest,   on='_key', how='left')

df_pricing['DifPct'] = ((df_pricing['Precio'] - df_pricing['PrecioCompMin']) / df_pricing['PrecioCompMin'].replace(0,1) * 100).round(1)
df_pricing['Alerta'] = df_pricing['DifPct'] > PRICE_ALERT_PCT

# Combined universe
df_all = pd.concat([df_gl, df_comp], ignore_index=True)

# ─────────────────────────────────────────────
# GLOBAL FILTERS (sidebar)
# ─────────────────────────────────────────────
with st.sidebar:
    all_paises = sorted(df_all['País'].dropna().unique().tolist()) if 'País' in df_all.columns else []
    all_temas  = sorted(df_all['Temática'].dropna().unique().tolist()) if 'Temática' in df_all.columns else []
    all_mkts   = ['Getlinko'] + sorted(df_comp['Marketplace'].unique().tolist())

    sel_paises = st.multiselect("País", all_paises, default=all_paises)
    sel_temas  = st.multiselect("Temática", all_temas, default=all_temas)
    sel_mkts   = st.multiselect("Marketplace", all_mkts, default=all_mkts)

    precio_all_max = int(df_all['Precio'].max()) if df_all['Precio'].max() > 0 else 1000
    rango_precio = st.slider("Rango Precio (€)", 0, precio_all_max, (0, precio_all_max))

    dr_all_max = int(df_all['DR'].max()) if 'DR' in df_all.columns and df_all['DR'].max() > 0 else 100
    rango_dr = st.slider("Rango DR", 0, 100, (0, dr_all_max))

def apply_filters(df):
    d = df.copy()
    if sel_paises and 'País' in d.columns:
        d = d[d['País'].isin(sel_paises)]
    if sel_temas and 'Temática' in d.columns:
        d = d[d['Temática'].isin(sel_temas)]
    if sel_mkts and 'Marketplace' in d.columns:
        d = d[d['Marketplace'].isin(sel_mkts)]
    d = d[(d['Precio'] >= rango_precio[0]) & (d['Precio'] <= rango_precio[1])]
    if 'DR' in d.columns:
        d = d[(d['DR'] >= rango_dr[0]) & (d['DR'] <= rango_dr[1])]
    return d

df_gl_f      = apply_filters(df_gl)
df_comp_f    = apply_filters(df_comp)
df_pricing_f = apply_filters(df_pricing)
df_excl_comp_f = apply_filters(df_excl_comp)
df_excl_gl_f   = apply_filters(df_excl_gl)

# ─────────────────────────────────────────────
# KPI STRIP
# ─────────────────────────────────────────────
n_gl       = len(df_gl_f)
n_comp     = len(df_comp_f)
n_excl_gl  = len(df_excl_gl_f)
pct_excl   = round(n_excl_gl / n_gl * 100, 1) if n_gl else 0
avg_gl     = df_gl_f['Precio'].mean() if n_gl else 0
avg_comp   = df_comp_f['Precio'].mean() if n_comp else 0
pct_price  = round((avg_gl - avg_comp) / avg_comp * 100, 1) if avg_comp else 0
n_alertas  = int(df_pricing_f['Alerta'].sum()) if not df_pricing_f.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Medios Getlinko", f"{n_gl:,}")
col2.metric("Medios Competencia", f"{n_comp:,}")
col3.metric("Exclusivos Getlinko", f"{n_excl_gl:,}", f"{pct_excl}% del catálogo")
col4.metric("Precio medio GL vs Mercado", f"{avg_gl:,.0f}€", f"{pct_price:+.1f}% vs comp.")
col5.metric("🔴 Alertas precio", f"{n_alertas}", f">{PRICE_ALERT_PCT}% sobre mercado")

st.markdown("---")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_exec, tab_pricing, tab_excl, tab_shared, tab_captacion, tab_pais = st.tabs([
    "🧭 Resumen Ejecutivo",
    "💰 Pricing",
    "⭐ Exclusividad",
    "🔄 Compartidos",
    "🎯 Captación",
    "🗺️ País & Temática",
])

# ══════════════════════════════════════════════
# TAB 1 — RESUMEN EJECUTIVO
# ══════════════════════════════════════════════
with tab_exec:
    st.markdown('<p class="sec-header">Top 3 oportunidades accionables</p>', unsafe_allow_html=True)

    top_opp = df_excl_comp_f.sort_values('Score', ascending=False).head(3)
    opp_cols = st.columns(3)
    for i, (_, row) in enumerate(top_opp.iterrows()):
        with opp_cols[i]:
            pais  = row.get('País','—')
            tema  = row.get('Temática','—')
            dr    = row.get('DR', 0)
            tr    = row.get('Tráfico', 0)
            pr    = row.get('Precio', 0)
            mkt   = row.get('Marketplace','—')
            st.markdown(f"""
<div class="opp-card">
  <div class="opp-url">{row['URL'][:55]}…</div>
  <div class="opp-score">{row['Score']}</div>
  <div class="opp-meta">Score de prioridad</div>
  <div style="margin-top:.6rem; font-size:.78rem; line-height:1.7;">
    🌍 {pais} &nbsp;·&nbsp; 📂 {tema}<br>
    DR <b>{int(dr)}</b> &nbsp;·&nbsp; Tráfico <b>{fmt_num(tr)}</b><br>
    Precio <b>{pr:,.0f}€</b> &nbsp;·&nbsp; En <b>{mkt}</b>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<p class="sec-header">Alertas críticas de precio</p>', unsafe_allow_html=True)

    alertas = df_pricing_f[df_pricing_f['Alerta']].sort_values('DifPct', ascending=False).head(5)
    if alertas.empty:
        st.success("✅ Sin alertas críticas de precio con los filtros actuales.")
    else:
        for _, row in alertas.iterrows():
            st.markdown(f"""
<div class="alert-card" style="--level-color: #e05260;">
  <div class="tag">⚠ Precio {row['DifPct']:+.1f}% sobre mercado</div>
  <b>{row['URL']}</b> — GL: <b>{row['Precio']:,.0f}€</b> · Comp. mín: <b>{row['PrecioCompMin']:,.0f}€</b>
  · Más barato en: <b>{row.get('MktMasBarato','—')}</b>
</div>""", unsafe_allow_html=True)

    st.markdown('<p class="sec-header">Distribución del catálogo por marketplace</p>', unsafe_allow_html=True)
    dist = df_all[df_all['Marketplace'].isin(sel_mkts)].groupby('Marketplace').size().reset_index(name='URLs')
    fig_bar = px.bar(dist.sort_values('URLs', ascending=True), x='URLs', y='Marketplace',
                     orientation='h', color='Marketplace',
                     color_discrete_sequence=['#5b6af0','#28c98e','#f0a93a','#e05260','#9b6cf0','#2cc4e0'])
    fig_bar.update_layout(**PLOTLY_THEME)
    fig_bar.update_traces(showlegend=False)
    st.plotly_chart(fig_bar, width="100%")

# ══════════════════════════════════════════════
# TAB 2 — PRICING
# ══════════════════════════════════════════════
with tab_pricing:
    p_tab1, p_tab2, p_tab3 = st.tabs(["🔴 Más caros que mercado", "🟢 Más baratos / alineados", "📉 Scatter Calidad/Precio"])

    with p_tab1:
        st.caption(f"Medios donde Getlinko está >{PRICE_ALERT_PCT}% por encima del precio mínimo de la competencia.")
        df_caros = df_pricing_f[df_pricing_f['DifPct'] > 0].sort_values('DifPct', ascending=False)
        cols_show = [c for c in ['URL','Precio','PrecioCompMin','PrecioCompAvg','DifPct','MktMasBarato','DR','Tráfico','País','Temática'] if c in df_caros.columns]
        df_show = df_caros[cols_show].rename(columns={'PrecioCompMin':'Comp. Mín','PrecioCompAvg':'Comp. Avg','DifPct':'% Dif','MktMasBarato':'Más barato en'})

        def color_row(row):
            if row.get('% Dif', 0) > PRICE_ALERT_PCT:
                return ['background-color: rgba(224,82,96,0.12)']*len(row)
            return ['']*len(row)

        st.dataframe(df_show.style.apply(color_row, axis=1), width="100%", hide_index=True)
        st.download_button("📥 Exportar", to_csv_bytes(df_show), "pricing_caros.csv", "text/csv")

    with p_tab2:
        df_baratos = df_pricing_f[df_pricing_f['DifPct'] <= 0].sort_values('DifPct')
        cols_show  = [c for c in ['URL','Precio','PrecioCompMin','DifPct','MktMasBarato','DR','Tráfico','País'] if c in df_baratos.columns]
        df_show    = df_baratos[cols_show].rename(columns={'PrecioCompMin':'Comp. Mín','DifPct':'% Dif','MktMasBarato':'Más barato en'})
        st.dataframe(df_show, width="100%", hide_index=True)
        st.download_button("📥 Exportar", to_csv_bytes(df_show), "pricing_baratos.csv", "text/csv")

    with p_tab3:
        st.caption("Eje X = DR · Eje Y = Precio · Tamaño = Tráfico. Outliers = medios con precio alto para su calidad SEO.")
        df_sc = df_gl_f.copy()
        if 'DR' in df_sc.columns and df_sc['DR'].sum() > 0:
            size_col = 'Tráfico' if 'Tráfico' in df_sc.columns and df_sc['Tráfico'].sum() > 0 else None
            color_col = 'País' if 'País' in df_sc.columns else 'Marketplace'
            fig_sc = px.scatter(df_sc, x='DR', y='Precio', size=size_col, color=color_col,
                                hover_name='URL',
                                hover_data={c: True for c in ['Temática','País','DR','Tráfico','Precio'] if c in df_sc.columns},
                                opacity=0.75, title="Calidad SEO vs Precio — Catálogo Getlinko")
            fig_sc.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig_sc, width="100%")
        else:
            st.info("Se necesita la columna DR para este gráfico. Sube el CSV de Ahrefs o asegúrate de que el CSV de Getlinko incluye DR.")

# ══════════════════════════════════════════════
# TAB 3 — EXCLUSIVIDAD
# ══════════════════════════════════════════════
with tab_excl:
    e_tab1, e_tab2, e_tab3 = st.tabs(["⭐ Solo Getlinko", "👥 Compartidos", "📊 Overlap"])

    with e_tab1:
        st.markdown(f"**{len(df_excl_gl_f):,}** medios que solo tiene Getlinko.")
        cols_gl = [c for c in ['URL','País','Temática','Precio','DR','DA','Tráfico'] if c in df_excl_gl_f.columns]
        st.dataframe(drop_aux(df_excl_gl_f)[cols_gl], width="100%", hide_index=True)
        st.download_button("📥 Exportar exclusivos", to_csv_bytes(drop_aux(df_excl_gl_f)[cols_gl]), "exclusivos_getlinko.csv", "text/csv")

    with e_tab2:
        overlap = df_all[df_all['_key'].isin(keys_gl & keys_comp)].copy()
        n_mkt_por_url = overlap.groupby('_key')['Marketplace'].nunique().reset_index(name='N_Marketplaces')
        overlap = overlap.merge(n_mkt_por_url, on='_key', how='left')
        cols_sh = [c for c in ['URL','Marketplace','Precio','DR','Tráfico','N_Marketplaces','País','Temática'] if c in overlap.columns]
        st.dataframe(drop_aux(overlap)[cols_sh], width="100%", hide_index=True)

    with e_tab3:
        labels = ['Solo Getlinko', 'Compartidos', 'Solo Competencia']
        values = [len(df_excl_gl_f), len(df_shared_gl), len(df_excl_comp_f)]
        fig_pie = px.pie(names=labels, values=values, hole=0.45,
                         color_discrete_sequence=['#5b6af0','#f0a93a','#e05260'],
                         title="Distribución del universo de URLs")
        fig_pie.update_layout(**PLOTLY_THEME)
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, width="100%")

# ══════════════════════════════════════════════
# TAB 4 — SHARED / PRECIO COMPARATIVO
# ══════════════════════════════════════════════
with tab_shared:
    st.markdown(f"**{len(df_pricing_f):,}** medios compartidos entre Getlinko y la competencia.")

    filtro_precio = st.radio("Filtro rápido", ["Todos","Más caros que mercado","Más baratos","Alineados (±5%)"], horizontal=True)
    if filtro_precio == "Más caros que mercado":
        df_p = df_pricing_f[df_pricing_f['DifPct'] > 5]
    elif filtro_precio == "Más baratos":
        df_p = df_pricing_f[df_pricing_f['DifPct'] < -5]
    elif filtro_precio == "Alineados (±5%)":
        df_p = df_pricing_f[df_pricing_f['DifPct'].abs() <= 5]
    else:
        df_p = df_pricing_f

    cols_p = [c for c in ['URL','Precio','PrecioCompMin','PrecioCompAvg','DifPct','MktMasBarato','DR','Tráfico','País','Temática'] if c in df_p.columns]
    st.dataframe(df_p[cols_p].rename(columns={'PrecioCompMin':'Comp.Mín','PrecioCompAvg':'Comp.Avg','DifPct':'%Dif','MktMasBarato':'Más barato'}).reset_index(drop=True),
                 width="100%", hide_index=True)

    st.markdown("---")
    st.subheader("Top 20 desviaciones de precio")
    top_pos = df_pricing_f.nlargest(10, 'DifPct')
    top_neg = df_pricing_f.nsmallest(10, 'DifPct')
    df_dev  = pd.concat([top_pos, top_neg]).sort_values('DifPct')
    df_dev['color'] = df_dev['DifPct'].apply(lambda x: '#e05260' if x > 0 else '#28c98e')
    fig_dev = go.Figure(go.Bar(
        x=df_dev['DifPct'], y=df_dev['URL'].str[:50],
        orientation='h',
        marker_color=df_dev['color'].tolist(),
        text=df_dev['DifPct'].apply(lambda x: f"{x:+.1f}%"),
        textposition='outside',
    ))
    fig_dev.update_layout(**PLOTLY_THEME, height=520,
                          xaxis_title="% diferencia vs precio mín. competencia",
                          yaxis_title="")
    st.plotly_chart(fig_dev, width="100%")

    st.download_button("📥 Exportar tabla completa", to_csv_bytes(df_p[cols_p]), "comparativa_precios.csv", "text/csv")

# ══════════════════════════════════════════════
# TAB 5 — CAPTACIÓN
# ══════════════════════════════════════════════
with tab_captacion:
    st.markdown(f"**{len(df_excl_comp_f):,}** medios que tiene la competencia y Getlinko no tiene.")
    st.caption("Ordenados por Score de prioridad = (DR×0.5 + Tráfico/1000×0.5) / (Precio/100)")

    col_ord, col_mkt = st.columns([2,2])
    with col_ord:
        orden = st.selectbox("Ordenar por", ['Score','DR','Tráfico','Precio'])
    with col_mkt:
        mkts_capt = sorted(df_excl_comp_f['Marketplace'].unique().tolist())
        sel_mkt_capt = st.multiselect("Marketplace", mkts_capt, default=mkts_capt, key="capt_mkt")

    df_capt = df_excl_comp_f[df_excl_comp_f['Marketplace'].isin(sel_mkt_capt)].sort_values(orden, ascending=False)
    cols_capt = [c for c in ['URL','Marketplace','Score','DR','Tráfico','Precio','País','Temática','DA','CF','TF'] if c in df_capt.columns]

    st.dataframe(drop_aux(df_capt)[cols_capt].reset_index(drop=True), width="100%", hide_index=True)
    st.download_button("📥 Exportar lista de captación", to_csv_bytes(drop_aux(df_capt)[cols_capt]), "captacion_prioritaria.csv", "text/csv")

    st.markdown("---")
    st.subheader("Distribución Score de prioridad")
    fig_hist = px.histogram(df_capt, x='Score', color='Marketplace', nbins=30, barmode='overlay', opacity=0.75)
    fig_hist.update_layout(**PLOTLY_THEME)
    st.plotly_chart(fig_hist, width="100%")

# ══════════════════════════════════════════════
# TAB 6 — PAÍS & TEMÁTICA
# ══════════════════════════════════════════════
with tab_pais:
    if 'País' not in df_all.columns and 'Temática' not in df_all.columns:
        st.info("Se necesita la columna 'País' o 'Temática' en los CSV.")
    else:
        p_tab1, p_tab2 = st.tabs(["🌍 Por País", "📂 Por Temática"])

        with p_tab1:
            if 'País' not in df_gl_f.columns and 'País' not in df_comp_f.columns:
                st.info("Ningún CSV incluye la columna 'País'.")
            else:
                # Agrupar solo los dataframes que tienen la columna
                if 'País' in df_gl_f.columns:
                    df_pais_gl = df_gl_f.groupby('País').agg(GL_URLs=('URL','count'), GL_PrecioAvg=('Precio','mean')).reset_index()
                else:
                    df_pais_gl = pd.DataFrame(columns=['País','GL_URLs','GL_PrecioAvg'])

                if 'País' in df_comp_f.columns:
                    df_pais_comp = df_comp_f.groupby('País').agg(Comp_URLs=('URL','count')).reset_index()
                else:
                    df_pais_comp = pd.DataFrame(columns=['País','Comp_URLs'])
                    st.info("Los CSV de competidores no incluyen la columna 'País'.")

                df_pais_mrg = df_pais_gl.merge(df_pais_comp, on='País', how='outer').fillna(0)
                df_pais_mrg['GL_PrecioAvg'] = df_pais_mrg['GL_PrecioAvg'].round(0)
                df_pais_mrg['Gap'] = (df_pais_mrg['Comp_URLs'] - df_pais_mrg['GL_URLs']).astype(int)
                df_pais_mrg = df_pais_mrg.sort_values('Gap', ascending=False)

                y_cols = [c for c in ['GL_URLs','Comp_URLs'] if c in df_pais_mrg.columns and df_pais_mrg[c].sum() > 0]
                fig_pais = px.bar(df_pais_mrg.head(20), x='País', y=y_cols, barmode='group',
                                  color_discrete_map={'GL_URLs':'#f3006e','Comp_URLs':'#261a4b'},
                                  title="Top 20 países: Getlinko vs Competencia")
                fig_pais.update_layout(**PLOTLY_THEME)
                st.plotly_chart(fig_pais, width="100%")

                st.markdown("**Gaps por país** (competencia tiene más medios que Getlinko)")
                st.dataframe(df_pais_mrg.rename(columns={'GL_URLs':'URLs GL','Comp_URLs':'URLs Comp','GL_PrecioAvg':'Precio Avg GL','Gap':'Gap (Comp-GL)'}),
                             width="100%", hide_index=True)

        with p_tab2:
            if 'Temática' not in df_gl_f.columns and 'Temática' not in df_comp_f.columns:
                st.info("Ningún CSV incluye la columna 'Temática'.")
            else:
                if 'Temática' in df_gl_f.columns:
                    df_tema_gl = df_gl_f.groupby('Temática').agg(GL=('URL','count'), PrecioGL=('Precio','mean')).reset_index()
                else:
                    df_tema_gl = pd.DataFrame(columns=['Temática','GL','PrecioGL'])

                if 'Temática' in df_comp_f.columns:
                    df_tema_comp = df_comp_f.groupby('Temática').agg(Comp=('URL','count')).reset_index()
                else:
                    df_tema_comp = pd.DataFrame(columns=['Temática','Comp'])
                    st.info("Los CSV de competidores no incluyen la columna 'Temática'. Se muestra solo el catálogo Getlinko.")

                df_tema_mrg = df_tema_gl.merge(df_tema_comp, on='Temática', how='outer').fillna(0)
                df_tema_mrg['Gap'] = (df_tema_mrg['Comp'] - df_tema_mrg['GL']).astype(int)

                y_cols = [c for c in ['GL','Comp'] if c in df_tema_mrg.columns and df_tema_mrg[c].sum() > 0]
                fig_tema = px.bar(df_tema_mrg.sort_values('Gap', ascending=False).head(20),
                                  x='Temática', y=y_cols, barmode='group',
                                  color_discrete_map={'GL':'#f3006e','Comp':'#261a4b'},
                                  title="Top 20 temáticas: Getlinko vs Competencia")
                fig_tema.update_layout(**PLOTLY_THEME, xaxis_tickangle=-35)
                st.plotly_chart(fig_tema, width="100%")

                if 'País' in df_gl_f.columns and 'Temática' in df_gl_f.columns:
                    st.markdown("**Heatmap País × Temática (densidad URLs Getlinko)**")
                    pivot = df_gl_f.pivot_table(index='País', columns='Temática', values='URL', aggfunc='count', fill_value=0)
                    pivot = pivot.loc[pivot.sum(axis=1).nlargest(15).index, pivot.sum(axis=0).nlargest(12).index]
                    fig_heat = px.imshow(pivot, color_continuous_scale='RdPu',
                                         title="Heatmap País × Temática (URLs Getlinko)")
                    fig_heat.update_layout(**PLOTLY_THEME)
                    st.plotly_chart(fig_heat, width="100%")