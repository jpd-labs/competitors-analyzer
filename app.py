import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Comparador SEO de Medios", layout="wide")
st.title("📊 Analizador y Comparador de Bases de Datos SEO")

# --- COLUMNAS REQUERIDAS Y OPCIONALES ---
COLS_OBLIGATORIAS = ['URL', 'Precio']
COLS_OPCIONALES = ['País', 'Temática', 'DR', 'DA', 'PA', 'CF', 'TF', 'Tráfico web/mes']
COLS_NUMERICAS = ['DA', 'PA', 'DR', 'CF', 'TF', 'Tráfico web/mes', 'Precio']

# --- HELPERS ---
def limpiar_numeros(df, columnas):
    for col in columnas:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r'[^\d.]', '', regex=True),
                errors='coerce'
            ).fillna(0)
    return df

def leer_archivo(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    return pd.read_excel(file)

def validar_columnas(df, nombre_archivo):
    """Devuelve (ok, lista_errores, lista_avisos)"""
    errores = []
    avisos = []
    cols = df.columns.tolist()

    for col in COLS_OBLIGATORIAS:
        if col not in cols:
            errores.append(f"Falta la columna obligatoria **{col}**")

    opcionales_presentes = [c for c in COLS_OPCIONALES if c in cols]
    opcionales_ausentes = [c for c in COLS_OPCIONALES if c not in cols]
    if opcionales_ausentes:
        avisos.append(f"Columnas opcionales no encontradas: {', '.join(opcionales_ausentes)}")

    return len(errores) == 0, errores, avisos

def mostrar_info_formato():
    with st.expander("ℹ️ Formato requerido de los CSV", expanded=False):
        st.markdown("""
        Todos los archivos (tu BD interna y los de competidores) deben seguir este formato:

        | Columna | Tipo | Obligatoria |
        |---|---|---|
        | **URL** | Texto | ✅ Sí |
        | **Precio** | Número | ✅ Sí |
        | País | Texto | ⬜ Opcional |
        | Temática | Texto | ⬜ Opcional |
        | DR | Número (0-100) | ⬜ Opcional |
        | DA | Número (0-100) | ⬜ Opcional |
        | PA | Número (0-100) | ⬜ Opcional |
        | CF | Número (0-100) | ⬜ Opcional |
        | TF | Número (0-100) | ⬜ Opcional |
        | Tráfico web/mes | Número | ⬜ Opcional |

        > Los nombres de columna deben coincidir **exactamente** (incluyendo mayúsculas y tildes).
        """)

# --- BARRA LATERAL: CARGA DE DATOS ---
st.sidebar.header("📂 Carga tus datos")

mostrar_info_formato()

st.sidebar.markdown("**1. Tu base de datos interna**")
file_interna = st.sidebar.file_uploader(
    "Sube tu BD Interna",
    type=["csv", "xlsx"],
    help="Obligatorio: columnas URL y Precio"
)

st.sidebar.markdown("**2. CSVs de competidores** *(puedes subir varios)*")
files_externas = st.sidebar.file_uploader(
    "Sube BD(s) de Competidores",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
    help="Puedes subir uno o varios archivos. Obligatorio: columnas URL y Precio"
)

# --- VALIDACIONES Y CARGA ---
df_int = None
df_ext = None
hay_errores = False

if file_interna:
    df_int_raw = leer_archivo(file_interna)
    ok, errores, avisos = validar_columnas(df_int_raw, file_interna.name)
    if not ok:
        st.error(f"❌ **{file_interna.name}** tiene errores:\n\n" + "\n".join(f"- {e}" for e in errores))
        hay_errores = True
    else:
        if avisos:
            st.warning(f"⚠️ **{file_interna.name}**: {avisos[0]}")
        df_int = limpiar_numeros(df_int_raw.copy(), COLS_NUMERICAS)
        df_int['Origen'] = 'Interna'

if files_externas:
    dfs_ext = []
    for f in files_externas:
        df_raw = leer_archivo(f)
        ok, errores, avisos = validar_columnas(df_raw, f.name)
        if not ok:
            st.error(f"❌ **{f.name}** tiene errores:\n\n" + "\n".join(f"- {e}" for e in errores))
            hay_errores = True
        else:
            if avisos:
                st.warning(f"⚠️ **{f.name}**: {avisos[0]}")
            df_tmp = limpiar_numeros(df_raw.copy(), COLS_NUMERICAS)
            # Nombre del competidor = nombre del archivo sin extensión
            nombre_competidor = f.name.rsplit('.', 1)[0]
            df_tmp['Competidor'] = nombre_competidor
            dfs_ext.append(df_tmp)

    if dfs_ext and not hay_errores:
        df_ext = pd.concat(dfs_ext, ignore_index=True)

# --- ANÁLISIS PRINCIPAL ---
if df_int is not None and df_ext is not None and not hay_errores:

    # Merge para cruzar URLs
    df_cruce = pd.merge(df_ext, df_int[['URL', 'Precio']], on='URL', how='left', indicator=True)

    # Nuevas oportunidades: en competidores pero NO en nuestra BD
    df_nuevas = (
        df_cruce[df_cruce['_merge'] == 'left_only']
        .drop(columns=['_merge', 'Precio_y'])
        .rename(columns={'Precio_x': 'Precio'})
        .copy()
    )

    # Repetidas: están en ambas
    df_repetidas = df_cruce[df_cruce['_merge'] == 'both'].copy()

    # Calcular métricas en df_nuevas
    if 'DA' in df_nuevas.columns and 'DR' in df_nuevas.columns:
        df_nuevas['Nota SEO (0-100)'] = ((df_nuevas['DA'] + df_nuevas['DR']) / 2).round(2)
    elif 'DR' in df_nuevas.columns:
        df_nuevas['Nota SEO (0-100)'] = df_nuevas['DR'].round(2)
    else:
        df_nuevas['Nota SEO (0-100)'] = 0

    if 'Tráfico web/mes' in df_nuevas.columns:
        df_nuevas['Índice Rentabilidad'] = (
            df_nuevas['Tráfico web/mes'] / df_nuevas['Precio'].replace(0, 0.1)
        ).round(2)
    else:
        df_nuevas['Índice Rentabilidad'] = 0

    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["📈 Resumen General", "🎯 Catálogo de Prioridades", "🔍 Comparación Detallada"])

    # --- TAB 1: RESUMEN ---
    with tab1:
        st.header("Visión General del Cruce de Datos")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("URLs BD Interna", len(df_int))
        col2.metric("URLs Competidores (total)", len(df_ext))
        col3.metric("Nuevas Oportunidades", len(df_nuevas), "No están en tu BD")
        col4.metric("URLs Coincidentes", len(df_repetidas), "Ya las tienes")

        # Desglose por competidor
        st.markdown("---")
        st.subheader("Desglose por Competidor")
        resumen_comp = (
            df_ext.groupby('Competidor')
            .agg(Total_URLs=('URL', 'count'))
            .reset_index()
        )
        nuevas_por_comp = (
            df_nuevas.groupby('Competidor')
            .agg(Nuevas_URLs=('URL', 'count'))
            .reset_index()
        )
        resumen_comp = resumen_comp.merge(nuevas_por_comp, on='Competidor', how='left').fillna(0)
        resumen_comp['Nuevas_URLs'] = resumen_comp['Nuevas_URLs'].astype(int)
        st.dataframe(resumen_comp.rename(columns={
            'Competidor': 'Competidor',
            'Total_URLs': 'Total URLs',
            'Nuevas_URLs': 'URLs Nuevas (no en tu BD)'
        }), use_container_width=True)

        st.markdown("---")
        col_graf1, col_graf2 = st.columns(2)

        with col_graf1:
            if 'Temática' in df_nuevas.columns and df_nuevas['Temática'].notna().any():
                st.subheader("Distribución de Temáticas (Nuevas)")
                fig1 = px.pie(df_nuevas, names='Temática', hole=0.3)
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("Sin columna 'Temática' para mostrar el gráfico.")

        with col_graf2:
            if 'DR' in df_nuevas.columns and 'Tráfico web/mes' in df_nuevas.columns:
                st.subheader("Calidad vs Precio (Nuevas Oportunidades)")
                color_col = 'Competidor' if 'Competidor' in df_nuevas.columns else None
                fig2 = px.scatter(
                    df_nuevas, x='Precio', y='DR',
                    size='Tráfico web/mes', color=color_col,
                    hover_name='URL'
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Sin columnas 'DR' o 'Tráfico web/mes' para mostrar el gráfico.")

    # --- TAB 2: PRIORIDADES ---
    with tab2:
        st.header("🎯 Catálogo de Prioridades (Solo URLs Nuevas)")
        st.markdown(
            "Hemos calculado un **Índice de Rentabilidad** (Tráfico / Precio) y una "
            "**Nota SEO** ((DA+DR)/2) para ordenar las mejores opciones."
        )

        st.sidebar.markdown("---")
        st.sidebar.header("Filtros de Prioridad")

        precio_max = int(df_nuevas['Precio'].max()) if df_nuevas['Precio'].max() > 0 else 1000
        presupuesto_max = st.sidebar.slider("Presupuesto Máximo (€/$)", 0, precio_max, precio_max)

        if 'DR' in df_nuevas.columns:
            dr_minimo = st.sidebar.slider("DR Mínimo", 0, 100, 20)
        else:
            dr_minimo = 0

        # Filtro por competidor
        competidores_disponibles = sorted(df_nuevas['Competidor'].unique().tolist())
        competidores_sel = st.sidebar.multiselect(
            "Filtrar por Competidor",
            options=competidores_disponibles,
            default=competidores_disponibles
        )

        df_prioridades = df_nuevas[
            (df_nuevas['Precio'] <= presupuesto_max) &
            (df_nuevas.get('DR', pd.Series(100, index=df_nuevas.index)) >= dr_minimo) &
            (df_nuevas['Competidor'].isin(competidores_sel))
        ].sort_values(by=['Índice Rentabilidad', 'Nota SEO (0-100)'], ascending=[False, False])

        st.subheader(f"Top Medios Recomendados ({len(df_prioridades)} encontrados)")

        # Mostrar solo las columnas que existen
        cols_ideales = ['URL', 'Competidor', 'Temática', 'País', 'Precio', 'Tráfico web/mes', 'Nota SEO (0-100)', 'Índice Rentabilidad', 'DR', 'DA']
        cols_mostrar = [c for c in cols_ideales if c in df_prioridades.columns]
        st.dataframe(df_prioridades[cols_mostrar], use_container_width=True)

    # --- TAB 3: COMPARACIÓN DETALLADA ---
    with tab3:
        st.header("🔍 Comparación y Búsqueda Detallada")

        opcion_ver = st.radio(
            "¿Qué datos quieres ver?",
            ["Solo Oportunidades Nuevas", "URLs Repetidas (Comparar precios)", "Ver Todo (Competidores)"]
        )

        if opcion_ver == "Solo Oportunidades Nuevas":
            df_mostrar = df_nuevas
        elif opcion_ver == "URLs Repetidas (Comparar precios)":
            df_mostrar = (
                df_repetidas
                .rename(columns={'Precio_x': 'Precio Competidor', 'Precio_y': 'Precio Interno (Tu BD)'})
                .drop(columns=['_merge'])
                .copy()
            )
            df_mostrar['Diferencia Precio'] = df_mostrar['Precio Competidor'] - df_mostrar['Precio Interno (Tu BD)']
        else:
            df_mostrar = df_ext

        st.dataframe(df_mostrar, use_container_width=True)

        csv = df_mostrar.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar esta tabla en CSV",
            data=csv,
            file_name='analisis_seo_medios.csv',
            mime='text/csv',
        )

elif not file_interna and not files_externas:
    mostrar_info_formato()
    st.info("👈 Sube tu BD Interna y al menos un CSV de competidor en el menú lateral para comenzar.")
elif not file_interna:
    st.warning("⬅️ Falta subir tu BD Interna.")
elif not files_externas:
    st.warning("⬅️ Falta subir al menos un CSV de competidor.")