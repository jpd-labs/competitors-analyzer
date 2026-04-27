import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import re
import anthropic

st.set_page_config(
    page_title="Media Catalog Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #13131a;
    --surface2: #1c1c27;
    --accent: #7c6cfa;
    --accent2: #fa6c8a;
    --accent3: #6cfabd;
    --text: #e8e8f0;
    --text-muted: #7a7a9a;
    --border: #2a2a3a;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

.stApp { background-color: var(--bg); }

h1, h2, h3 { font-family: 'Space Mono', monospace; }

.main-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #7c6cfa, #fa6c8a, #6cfabd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: var(--text-muted);
    font-size: 0.95rem;
    margin-bottom: 2rem;
    font-family: 'DM Sans', sans-serif;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}

.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
}

.metric-label {
    color: var(--text-muted);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.provider-tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'Space Mono', monospace;
    margin-right: 4px;
}

.insight-box {
    background: linear-gradient(135deg, rgba(124,108,250,0.1), rgba(250,108,138,0.05));
    border: 1px solid rgba(124,108,250,0.3);
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1rem;
    font-size: 0.95rem;
    line-height: 1.7;
    white-space: pre-wrap;
}

.stButton > button {
    background: linear-gradient(135deg, #7c6cfa, #fa6c8a);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 0.85rem;
    padding: 0.6rem 1.4rem;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

.stFileUploader {
    background: var(--surface);
    border: 1px dashed var(--border);
    border-radius: 12px;
}

div[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace;
    color: var(--accent);
}

.stSelectbox > div, .stMultiSelect > div {
    background: var(--surface2);
}

section[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}

.stDataFrame { border-radius: 8px; overflow: hidden; }

hr { border-color: var(--border); margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


PROVIDER_COLORS = {
    "publisuites": "#7c6cfa",
    "getalink": "#fa6c8a",
    "prensalink": "#6cfabd",
    "unancor": "#fad46c",
    "other": "#a0a0c0"
}

def parse_price(price_str):
    if pd.isna(price_str):
        return None
    price_str = str(price_str).replace("€", "").replace(",", ".").strip()
    try:
        return float(price_str)
    except:
        return None

def parse_traffic(traffic_str):
    if pd.isna(traffic_str):
        return 0
    try:
        return int(str(traffic_str).replace(".", "").replace(",", "").strip())
    except:
        return 0

def load_csv(file, provider_name):
    df = pd.read_csv(file, encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    df["Proveedor"] = provider_name.lower()
    if "Precio" in df.columns:
        df["Precio_num"] = df["Precio"].apply(parse_price)
    if "Tráfico web/mes" in df.columns:
        df["Tráfico_num"] = df["Tráfico web/mes"].apply(parse_traffic)
    return df

def get_provider_color(provider):
    for key, color in PROVIDER_COLORS.items():
        if key in provider.lower():
            return color
    return PROVIDER_COLORS["other"]

def generate_insights(df, client):
    sample = df[["URL", "Proveedor", "DA", "DR", "Tráfico_num", "Precio_num", "Temática"]].dropna().head(40)
    stats = df.groupby("Proveedor").agg(
        medios=("URL", "count"),
        DA_medio=("DA", "mean"),
        DR_medio=("DR", "mean"),
        trafico_medio=("Tráfico_num", "mean"),
        precio_medio=("Precio_num", "mean"),
        precio_min=("Precio_num", "min"),
        precio_max=("Precio_num", "max"),
    ).round(1).to_string()

    prompt = f"""Eres un analista SEO experto en link building y medios digitales. Analiza estos datos de proveedores de medios y genera insights accionables para el equipo de catálogo.

ESTADÍSTICAS POR PROVEEDOR:
{stats}

MUESTRA DE DATOS:
{sample.to_string()}

Por favor proporciona:
1. **Resumen ejecutivo**: ¿Qué proveedor ofrece mejor relación calidad/precio?
2. **Insights por proveedor**: Fortalezas y debilidades de cada uno
3. **Oportunidades**: Medios con alto DA/DR pero precio bajo (gangas)
4. **Alertas**: Medios con métricas sospechosas o inconsistentes
5. **Recomendación para el equipo**: Qué proveedor priorizar según el objetivo (volumen vs calidad vs precio)

Sé concreto y usa los datos reales. Responde en español."""

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            yield text


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📁 Cargar CSVs")
    st.markdown("<small style='color:#7a7a9a'>El nombre del archivo se usa como proveedor</small>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Sube uno o más CSVs",
        type=["csv"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🔑 API Key")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.markdown("<small style='color:#7a7a9a'>Para generar insights con IA</small>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎛️ Filtros")


# ── MAIN ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">MEDIA CATALOG ANALYZER</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Compara proveedores · Analiza métricas · Descubre oportunidades</div>', unsafe_allow_html=True)

if not uploaded_files:
    st.info("👈 Sube uno o más CSVs desde el panel lateral para empezar. El nombre del archivo se usará como nombre del proveedor.")
    st.stop()

# Load all CSVs
dfs = []
for f in uploaded_files:
    provider_name = os.path.splitext(f.name)[0]
    provider_name = re.sub(r'[_\-]medios[_\-]?.*', '', provider_name, flags=re.IGNORECASE).strip()
    try:
        df = load_csv(f, provider_name)
        dfs.append(df)
    except Exception as e:
        st.error(f"Error cargando {f.name}: {e}")

if not dfs:
    st.stop()

all_df = pd.concat(dfs, ignore_index=True)

# Sidebar filters
with st.sidebar:
    proveedores = sorted(all_df["Proveedor"].unique().tolist())
    sel_proveedores = st.multiselect("Proveedores", proveedores, default=proveedores)

    if "DA" in all_df.columns:
        da_min, da_max = int(all_df["DA"].min()), int(all_df["DA"].max())
        da_range = st.slider("DA mínimo", da_min, da_max, da_min)

    if "Precio_num" in all_df.columns:
        p_min = float(all_df["Precio_num"].dropna().min())
        p_max = float(all_df["Precio_num"].dropna().max())
        precio_range = st.slider("Precio máximo (€)", p_min, p_max, p_max)

    tematicas = sorted(all_df["Temática"].dropna().unique().tolist()) if "Temática" in all_df.columns else []
    sel_tematicas = st.multiselect("Temáticas", tematicas)

# Apply filters
filtered = all_df[all_df["Proveedor"].isin(sel_proveedores)]
if "DA" in filtered.columns:
    filtered = filtered[filtered["DA"] >= da_range]
if "Precio_num" in filtered.columns:
    filtered = filtered[filtered["Precio_num"] <= precio_range]
if sel_tematicas and "Temática" in filtered.columns:
    mask = filtered["Temática"].apply(lambda x: any(t in str(x) for t in sel_tematicas))
    filtered = filtered[mask]


# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown("#### Resumen")
cols = st.columns(5)
metrics = [
    ("Total medios", len(filtered), ""),
    ("Proveedores", filtered["Proveedor"].nunique(), ""),
    ("DA medio", f"{filtered['DA'].mean():.1f}" if "DA" in filtered.columns else "—", ""),
    ("DR medio", f"{filtered['DR'].mean():.1f}" if "DR" in filtered.columns else "—", ""),
    ("Precio medio", f"{filtered['Precio_num'].mean():.0f}€" if "Precio_num" in filtered.columns else "—", ""),
]
for col, (label, value, _) in zip(cols, metrics):
    col.metric(label, value)

st.markdown("---")

# ── CHARTS ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Comparativa", "💰 Precio vs Calidad", "🗺️ Distribución", "📋 Tabla"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### DA medio por proveedor")
        da_by_prov = filtered.groupby("Proveedor")["DA"].mean().reset_index()
        colors = [get_provider_color(p) for p in da_by_prov["Proveedor"]]
        fig = px.bar(da_by_prov, x="Proveedor", y="DA",
                     color="Proveedor",
                     color_discrete_sequence=colors,
                     template="plotly_dark")
        fig.update_layout(paper_bgcolor="#13131a", plot_bgcolor="#13131a", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("##### DR medio por proveedor")
        if "DR" in filtered.columns:
            dr_by_prov = filtered.groupby("Proveedor")["DR"].mean().reset_index()
            fig2 = px.bar(dr_by_prov, x="Proveedor", y="DR",
                          color="Proveedor",
                          color_discrete_sequence=[get_provider_color(p) for p in dr_by_prov["Proveedor"]],
                          template="plotly_dark")
            fig2.update_layout(paper_bgcolor="#13131a", plot_bgcolor="#13131a", showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("##### Distribución de métricas por proveedor")
    metric_cols = [c for c in ["DA", "DR", "TF", "CF"] if c in filtered.columns]
    if metric_cols:
        sel_metric = st.selectbox("Métrica", metric_cols)
        fig3 = px.box(filtered, x="Proveedor", y=sel_metric, color="Proveedor",
                      color_discrete_sequence=list(PROVIDER_COLORS.values()),
                      template="plotly_dark")
        fig3.update_layout(paper_bgcolor="#13131a", plot_bgcolor="#13131a", showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.markdown("##### Precio vs DA — cada punto es un medio")
    if "Precio_num" in filtered.columns and "DA" in filtered.columns:
        scatter_df = filtered.dropna(subset=["Precio_num", "DA"])
        fig4 = px.scatter(scatter_df, x="DA", y="Precio_num",
                          color="Proveedor",
                          hover_data=["URL", "Temática", "DR"] if "DR" in scatter_df.columns else ["URL"],
                          color_discrete_sequence=list(PROVIDER_COLORS.values()),
                          template="plotly_dark",
                          labels={"Precio_num": "Precio (€)", "DA": "DA"})
        fig4.update_layout(paper_bgcolor="#13131a", plot_bgcolor="#13131a")
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("##### 🏆 Top 10 mejor relación DA/Precio")
    if "Precio_num" in filtered.columns and "DA" in filtered.columns:
        ratio_df = filtered.dropna(subset=["Precio_num", "DA"]).copy()
        ratio_df = ratio_df[ratio_df["Precio_num"] > 0]
        ratio_df["DA_por_euro"] = ratio_df["DA"] / ratio_df["Precio_num"]
        top10 = ratio_df.nlargest(10, "DA_por_euro")[["URL", "Proveedor", "DA", "DR", "Precio_num", "DA_por_euro", "Temática"]]
        top10.columns = ["URL", "Proveedor", "DA", "DR", "Precio €", "DA/€", "Temática"]
        top10["DA/€"] = top10["DA/€"].round(2)
        st.dataframe(top10, use_container_width=True, hide_index=True)

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Medios por proveedor")
        count_df = filtered.groupby("Proveedor").size().reset_index(name="count")
        fig5 = px.pie(count_df, values="count", names="Proveedor",
                      color_discrete_sequence=list(PROVIDER_COLORS.values()),
                      template="plotly_dark", hole=0.4)
        fig5.update_layout(paper_bgcolor="#13131a")
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        st.markdown("##### Medios por país")
        if "País" in filtered.columns:
            pais_df = filtered["País"].value_counts().head(10).reset_index()
            pais_df.columns = ["País", "count"]
            fig6 = px.bar(pais_df, x="count", y="País", orientation="h",
                          color_discrete_sequence=["#7c6cfa"],
                          template="plotly_dark")
            fig6.update_layout(paper_bgcolor="#13131a", plot_bgcolor="#13131a")
            st.plotly_chart(fig6, use_container_width=True)

    st.markdown("##### Temáticas más frecuentes")
    if "Temática" in filtered.columns:
        all_temas = []
        for t in filtered["Temática"].dropna():
            all_temas.extend([x.strip() for x in str(t).split(",")])
        tema_series = pd.Series(all_temas).value_counts().head(15).reset_index()
        tema_series.columns = ["Temática", "count"]
        fig7 = px.bar(tema_series, x="count", y="Temática", orientation="h",
                      color_discrete_sequence=["#fa6c8a"],
                      template="plotly_dark")
        fig7.update_layout(paper_bgcolor="#13131a", plot_bgcolor="#13131a", height=400)
        st.plotly_chart(fig7, use_container_width=True)

with tab4:
    st.markdown("##### Todos los medios filtrados")
    display_cols = [c for c in ["URL", "Proveedor", "País", "Temática", "DA", "PA", "DR", "CF", "TF", "Tráfico_num", "Precio_num"] if c in filtered.columns]
    display_df = filtered[display_cols].copy()
    if "Tráfico_num" in display_df.columns:
        display_df = display_df.rename(columns={"Tráfico_num": "Tráfico/mes", "Precio_num": "Precio €"})

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv_export = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Exportar CSV filtrado", csv_export, "medios_filtrados.csv", "text/csv")


# ── AI INSIGHTS ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 🤖 Insights con IA")

if not api_key:
    st.warning("Añade tu Anthropic API Key en el panel lateral para generar insights automáticos.")
else:
    if st.button("✨ Generar insights del catálogo"):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            insight_placeholder = st.empty()
            full_text = ""
            with st.spinner("Analizando datos..."):
                for chunk in generate_insights(filtered, client):
                    full_text += chunk
                    insight_placeholder.markdown(f'<div class="insight-box">{full_text}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error con la API: {e}")
