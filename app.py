import streamlit as st
import pandas as pd

# ═══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN 
# ═══════════════════════════════════════════════════════════════════════════════

APP_TITULO       = "Mi App de Datos"
APP_ICONO        = "📊"
APP_KICKER       = "Seguimiento de ventas"   # texto pequeño sobre el título
APP_SUBTITULO    = "Consulta y filtra los registros de la base de datos."

SHEET_URL        = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTF_eyRoMXM1RowP9JBnnHqsrv3aEPYJof3cQ-gbwN1HRGlZKJji2Nlykl2dk9oTnq-J8n9HvhjRm5w/pub?output=csv"

COLUMNAS_FILTRO  = []   # ej: ["CIUDAD", "AÑO"] — vacío = auto-detectar
COLUMNAS_TABLA   = []   # vacío = mostrar todas
MAX_FILTROS_AUTO = 5
CACHE_TTL        = 60

# ═══════════════════════════════════════════════════════════════════════════════
#  DISEÑO CSS 
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title=APP_TITULO, page_icon=APP_ICONO, layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500&display=swap');
 
    /* ── Fondo general: pizarra oscura con destello ámbar ──────────────────── */
    .stApp {
        background:
            radial-gradient(ellipse at top right, rgba(245, 158, 11, 0.07), transparent 45%),
            radial-gradient(ellipse at bottom left, rgba(30, 58, 138, 0.10), transparent 40%),
            linear-gradient(180deg, #0f1117 0%, #131720 100%);
        font-family: 'DM Sans', sans-serif;
        color: #e2e8f0;
    }
 
    /* ── Contenedor central ─────────────────────────────────────────────────── */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }
 
    /* ── Panel de encabezado oscuro con borde ámbar izquierdo ──────────────── */
    .header-panel {
        background: #1a1f2e;
        border-left: 4px solid #f59e0b;
        padding: 28px 36px;
        border-radius: 4px 16px 16px 4px;
        color: #e2e8f0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(245,158,11,0.08);
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .header-panel::before {
        content: "";
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(245, 158, 11, 0.06), transparent 70%);
    }
    .header-kicker {
        font-family: 'DM Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 0.22em;
        font-size: 0.72rem;
        font-weight: 500;
        color: #f59e0b;
        margin-bottom: 14px;
    }
    .header-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.4rem;
        line-height: 1.15;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 10px;
    }
    .header-subtitle {
        font-size: 0.97rem;
        color: #94a3b8;
        max-width: 780px;
        line-height: 1.6;
    }
 
    /* ── Tarjeta de filtros: panel oscuro con borde tenue ───────────────────── */
    .selector-card {
        background: #1a1f2e;
        border: 1px solid rgba(245, 158, 11, 0.14);
        border-radius: 12px;
        padding: 20px 22px 8px 22px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.35);
        margin: 10px 0 22px 0;
    }
    .selector-title {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: #f59e0b;
        margin-bottom: 4px;
        letter-spacing: 0.02em;
    }
    .selector-help {
        font-size: 0.88rem;
        color: #64748b;
        margin-bottom: 14px;
    }
 
    /* ── Selectbox: bordes ámbar sobre fondo oscuro ─────────────────────────── */
    div[data-baseweb="select"] > div {
        background-color: #0f1117 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(245, 158, 11, 0.25) !important;
        min-height: 50px !important;
        box-shadow: none !important;
        color: #e2e8f0 !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #f59e0b !important;
    }
 
    /* ── Tarjeta principal con línea superior ámbar ─────────────────────────── */
    .equipo-hero {
        background: #1a1f2e;
        border-radius: 12px;
        border-top: 3px solid #f59e0b;
        padding: 24px 28px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.35);
        margin-bottom: 20px;
    }
    .equipo-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.22em;
        color: #f59e0b;
        font-weight: 500;
        margin-bottom: 10px;
    }
    .equipo-title {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #f1f5f9;
        margin-bottom: 6px;
    }
    .equipo-caption {
        font-size: 0.92rem;
        color: #64748b;
        max-width: 750px;
    }
 
    /* ── Tarjetas secundarias ───────────────────────────────────────────────── */
    .card {
        background: #1a1f2e;
        padding: 18px 20px;
        border-radius: 12px;
        border: 1px solid rgba(245, 158, 11, 0.12);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.30);
        margin-bottom: 15px;
    }
    .card-title {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        color: #f59e0b;
        margin-bottom: 8px;
    }
    .bullet-list {
        margin: 0;
        padding-left: 1.35rem;
    }
    .bullet-list li {
        margin-bottom: 0.5rem;
        line-height: 1.6;
        color: #94a3b8;
    }
 
    /* ── Pestañas ────────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 18px;
        background: #1a1f2e;
        border: 1px solid rgba(245, 158, 11, 0.12);
        color: #94a3b8;
        font-family: 'DM Mono', monospace;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(245, 158, 11, 0.12) !important;
        color: #f59e0b !important;
        border-color: #f59e0b !important;
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
    st.error(f" No se pudieron cargar los datos. Verifica que el Google Sheet esté publicado.\n\nError: `{e}`")
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
    """
    Detecta columnas útiles como filtros por cardinalidad baja,
    sin importar si son texto o numéricas.
    Excluye: IDs únicos por fila, constantes, fechas y texto libre.
    """
    PALABRAS_EXCLUIR = {"id", "fecha", "date", "código", "codigo",
                        "radicado", "observacion", "observación",
                        "descripcion", "descripción", "nombre"}
    resultado = []
    n_filas = len(dataframe)
 
    for col in dataframe.columns:
        nombre = col.lower().strip()
 
        # Saltar columnas cuyo nombre sugiere ID, fecha o texto libre
        if any(p in nombre for p in PALABRAS_EXCLUIR):
            continue
 
        n_unicos = dataframe[col].nunique(dropna=True)
 
        # Saltar columnas constantes (1 valor) o únicas por fila (IDs)
        if n_unicos <= 1 or n_unicos == n_filas:
            continue
 
        # Saltar columnas con demasiados valores únicos (texto libre)
        if n_unicos > 50:
            continue
 
        # Saltar floats con alta variabilidad (valores continuos como precios)
        if dataframe[col].dtype == "float64" and n_unicos > 20:
            continue
 
        resultado.append(col)
 
        if len(resultado) >= max_col:
            break
 
    return resultado
 
filtros_activos = COLUMNAS_FILTRO if COLUMNAS_FILTRO else columnas_categoricas(df, MAX_FILTROS_AUTO)
columnas_tabla  = COLUMNAS_TABLA  if COLUMNAS_TABLA  else df.columns.tolist()

st.markdown("""
<div class="selector-card">
    <div class="selector-title"> Filtros</div>
    <div class="selector-help">Selecciona uno o varios criterios para filtrar la tabla.</div>
</div>
""", unsafe_allow_html=True)

selecciones = {}
if filtros_activos:
    cols_filtros = st.columns(len(filtros_activos))
    for i, col in enumerate(filtros_activos):
        opciones = ["Todos"] + sorted(df[col].dropna().unique().tolist())
        selecciones[col] = cols_filtros[i].selectbox(col.title(), opciones)

busqueda = st.text_input(" Búsqueda libre en cualquier columna", placeholder="Escribe para buscar…")


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
    label=" Descargar resultados como CSV",
    data=csv_exportar,
    file_name="datos_filtrados.csv",
    mime="text/csv",
)

st.caption(f"Datos desde Google Sheets · Caché {CACHE_TTL}s · {APP_TITULO}")
