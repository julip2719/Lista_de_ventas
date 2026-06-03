import streamlit as st
import pandas as pd

# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN — edita solo esta sección
# ═══════════════════════════════════════════════════════════════════════════════

APP_TITULO       = "Mi App de Datos"
APP_ICONO        = "📊"
APP_KICKER       = "Secretaría Seccional de Salud de Antioquia"   # texto pequeño sobre el título
APP_SUBTITULO    = "Consulta y filtra los registros de la base de datos."

SHEET_URL        = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQH1h7L5laiWJIg1cgxc0QpVvUqikHmmW7HstXTZgc1uMVGFNXkK7R-pyLMZnBLzjBiBC1c5rADEVts/pub?output=csv"

COLUMNAS_FILTRO  = ["AÑO", "COMPONENTE", "MUNICIPIO"]   # ej: ["MUNICIPIO", "COMPONENTE"] — vacío = auto-detectar
COLUMNAS_TABLA   = []   # vacío = mostrar todas
MAX_FILTROS_AUTO = 4
CACHE_TTL        = 60

# ═══════════════════════════════════════════════════════════════════════════════
#  DISEÑO CSS  — no necesitas tocar esto salvo para cambiar colores
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title=APP_TITULO, page_icon=APP_ICONO, layout="wide")

st.markdown("""
<style>
    /* ── Fondo general ─────────────────────────────────────────────────────── */
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(0, 104, 55, 0.12), transparent 28%),
            linear-gradient(180deg, #f4f8f4 0%, #eef4ef 100%);
    }

    /* ── Contenedor central ─────────────────────────────────────────────────── */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }

    /* ── Panel de encabezado verde ──────────────────────────────────────────── */
    .header-panel {
        background: linear-gradient(135deg, #006837 0%, #0b8f4a 100%);
        padding: 28px 32px;
        border-radius: 22px;
        color: white;
        box-shadow: 0 18px 40px rgba(0, 104, 55, 0.18);
        margin-bottom: 24px;
    }
    .header-kicker {
        text-transform: uppercase;
        letter-spacing: 0.18em;
        font-size: 0.8rem;
        font-weight: 700;
        opacity: 0.85;
        margin-bottom: 12px;
    }
    .header-title {
        font-size: 2.2rem;
        line-height: 1.2;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.95;
        max-width: 780px;
    }

    /* ── Tarjeta de filtros ─────────────────────────────────────────────────── */
    .selector-card {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid rgba(0, 104, 55, 0.12);
        border-radius: 20px;
        padding: 22px 22px 10px 22px;
        box-shadow: 0 14px 34px rgba(24, 39, 75, 0.08);
        margin: 10px 0 22px 0;
        backdrop-filter: blur(6px);
    }
    .selector-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0d4728;
        margin-bottom: 6px;
    }
    .selector-help {
        font-size: 0.95rem;
        color: #527060;
        margin-bottom: 14px;
    }

    /* ── Selectbox nativos de Streamlit ─────────────────────────────────────── */
    div[data-baseweb="select"] > div {
        border-radius: 14px !important;
        border: 1px solid rgba(0, 104, 55, 0.18) !important;
        min-height: 54px !important;
        box-shadow: none !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #0b8f4a !important;
    }

    /* ── Tarjeta principal de contenido ─────────────────────────────────────── */
    .equipo-hero {
        background: linear-gradient(135deg, #ffffff 0%, #f7fbf8 100%);
        border-radius: 24px;
        padding: 26px 30px;
        border: 1px solid rgba(0, 104, 55, 0.10);
        box-shadow: 0 18px 38px rgba(20, 33, 61, 0.09);
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .equipo-hero::after {
        content: "";
        position: absolute;
        inset: auto -40px -40px auto;
        width: 170px;
        height: 170px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 104, 55, 0.14), rgba(0, 104, 55, 0));
    }
    .equipo-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: #5c7668;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .equipo-title {
        font-size: 2rem;
        font-weight: 800;
        color: #073b22;
        margin-bottom: 8px;
    }
    .equipo-caption {
        font-size: 1rem;
        color: #587061;
        max-width: 750px;
    }

    /* ── Tarjetas de información ─────────────────────────────────────────────── */
    .card {
        background: rgba(255, 255, 255, 0.94);
        padding: 18px 20px;
        border-radius: 16px;
        border: 1px solid rgba(0, 104, 55, 0.09);
        box-shadow: 0 10px 28px rgba(24, 39, 75, 0.07);
        margin-bottom: 15px;
    }
    .card-title {
        font-weight: 700;
        font-size: 1rem;
        color: #006837;
        margin-bottom: 8px;
    }
    .bullet-list {
        margin: 0;
        padding-left: 1.35rem;
    }
    .bullet-list li {
        margin-bottom: 0.5rem;
        line-height: 1.55;
        color: #24352c;
    }

    /* ── Pestañas ────────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 10px 16px;
        background: rgba(255, 255, 255, 0.7);
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  CARGA DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=CACHE_TTL)
def cargar_datos(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df = df.dropna(how="all")
    return df

try:
    df = cargar_datos(SHEET_URL)
except Exception as e:
    st.error(f"❌ No se pudieron cargar los datos. Verifica que el Google Sheet esté publicado.\n\nError: `{e}`")
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
#  ENCABEZADO  (usa la clase .header-panel del CSS)
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="header-panel">
    <div class="header-kicker">{APP_KICKER}</div>
    <div class="header-title">{APP_ICONO} {APP_TITULO}</div>
    <div class="header-subtitle">{APP_SUBTITULO}</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MÉTRICAS
# ═══════════════════════════════════════════════════════════════════════════════

col1, col2, col3 = st.columns(3)
col1.metric("Total de registros", f"{len(df):,}")
col2.metric("Columnas", len(df.columns))
col3.metric("Filas con datos completos", int(df.notna().all(axis=1).sum()))


# ═══════════════════════════════════════════════════════════════════════════════
#  FILTROS  (dentro de la tarjeta .selector-card)
# ═══════════════════════════════════════════════════════════════════════════════

def columnas_categoricas(dataframe, max_col):
    resultado = []
    for col in dataframe.columns:
        if dataframe[col].dtype == object and 1 < dataframe[col].nunique() <= 50:
            resultado.append(col)
        if len(resultado) >= max_col:
            break
    return resultado

filtros_activos = COLUMNAS_FILTRO if COLUMNAS_FILTRO else columnas_categoricas(df, MAX_FILTROS_AUTO)
columnas_tabla  = COLUMNAS_TABLA  if COLUMNAS_TABLA  else df.columns.tolist()

st.markdown("""
<div class="selector-card">
    <div class="selector-title">🔍 Filtros</div>
    <div class="selector-help">Selecciona uno o varios criterios para filtrar la tabla.</div>
</div>
""", unsafe_allow_html=True)

selecciones = {}
if filtros_activos:
    cols_filtros = st.columns(len(filtros_activos))
    for i, col in enumerate(filtros_activos):
        opciones = ["Todos"] + sorted(df[col].dropna().unique().tolist())
        selecciones[col] = cols_filtros[i].selectbox(col.title(), opciones)

busqueda = st.text_input("🔎 Búsqueda libre en cualquier columna", placeholder="Escribe para buscar…")


# ═══════════════════════════════════════════════════════════════════════════════
#  APLICAR FILTROS
# ═══════════════════════════════════════════════════════════════════════════════

df_filtrado = df.copy()

for col, valor in selecciones.items():
    if valor != "Todos":
        df_filtrado = df_filtrado[df_filtrado[col] == valor]

if busqueda:
    mascara = df_filtrado.apply(
        lambda c: c.astype(str).str.contains(busqueda, case=False, na=False)
    ).any(axis=1)
    df_filtrado = df_filtrado[mascara]


# ═══════════════════════════════════════════════════════════════════════════════
#  TABLA  (dentro de .equipo-hero)
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown(f"""
<div class="equipo-hero">
    <div class="equipo-label">Resultados</div>
    <div class="equipo-title">{len(df_filtrado):,} registros encontrados</div>
    <div class="equipo-caption">Usa los filtros de arriba para refinar la búsqueda.</div>
</div>
""", unsafe_allow_html=True)

columnas_mostrar = [c for c in columnas_tabla if c in df_filtrado.columns]
st.dataframe(df_filtrado[columnas_mostrar], use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  GRÁFICO
# ═══════════════════════════════════════════════════════════════════════════════

if filtros_activos:
    st.markdown('<div class="card"><div class="card-title">📊 Distribución por columna</div>', unsafe_allow_html=True)
    col_grafico = st.selectbox("Selecciona columna", options=filtros_activos, label_visibility="collapsed")
    conteo = df_filtrado[col_grafico].value_counts().reset_index()
    conteo.columns = [col_grafico, "Cantidad"]
    st.bar_chart(conteo.set_index(col_grafico))
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  DESCARGA
# ═══════════════════════════════════════════════════════════════════════════════

csv_exportar = df_filtrado[columnas_mostrar].to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Descargar resultados como CSV",
    data=csv_exportar,
    file_name="datos_filtrados.csv",
    mime="text/csv",
)

st.caption(f"Datos desde Google Sheets · Caché {CACHE_TTL}s · {APP_TITULO}")
