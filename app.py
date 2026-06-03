import streamlit as st
import pandas as pd
import re #Ubica textos 
import unicodedata #Quita tíldes y caracteres especiales

APP_TITULO= "App de Ventas"
APP_ICONO       = "📊"              # Emoji que aparece en la pestaña del navegador
APP_DESCRIPCION = "Consulta y filtra los registros de la base de datos."

# URL de Google Sheets publicado como CSV
# Ruta: Archivo → Publicar en la web → Seleccionar hoja → CSV → Publicar → copiar URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRfSo35N4EQei0bxZgXwnEFdgYDJUsM2oDWmGtkPHaZxWDo4RPycbda5dfCHY5IEjVC9GxXoFfzVnPw/pub?gid=146860403&single=true&output=csv"

# Columnas que quieres usar como filtros desplegables (deben existir en tu hoja)
# Déjalas vacías [] para que la app las detecte automáticamente
COLUMNAS_FILTRO = []

# Columnas que quieres mostrar en la tabla (vacío = mostrar todas)
COLUMNAS_TABLA = []

# Columna numérica para mostrar en las métricas (vacío = no mostrar métrica numérica)
COLUMNA_METRICA_NUMERICA = ""

# Número máximo de columnas de filtro a generar automáticamente (si COLUMNAS_FILTRO está vacío)
MAX_FILTROS_AUTO = 4

# TTL del caché en segundos (cada cuánto recarga los datos desde Google Sheets)
CACHE_TTL = 60

# ═══════════════════════════════════════════════════════════════════════════════
#  NO NECESITAS EDITAR NADA DEBAJO DE ESTA LÍNEA
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title=APP_TITULO, page_icon=APP_ICONO, layout="wide")


@st.cache_data(ttl=CACHE_TTL)
def cargar_datos(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()          # elimina espacios en encabezados
    df = df.dropna(how="all")                    # elimina filas completamente vacías
    return df


# ── Carga ──────────────────────────────────────────────────────────────────────
try:
    df = cargar_datos(SHEET_URL)
except Exception as e:
    st.error(
        "❌ No se pudieron cargar los datos. "
        "Verifica que el Google Sheet esté publicado como CSV.\n\n"
        f"Detalle del error: `{e}`"
    )
    st.stop()


# ── Determinar columnas de filtro ──────────────────────────────────────────────
def columnas_categoricas(dataframe: pd.DataFrame, max_col: int) -> list:
    """Devuelve columnas de texto con cardinalidad baja, ideales para filtros."""
    candidatas = []
    for col in dataframe.columns:
        if dataframe[col].dtype == object:
            n_unicos = dataframe[col].nunique()
            if 1 < n_unicos <= 50:          # entre 2 y 50 valores únicos
                candidatas.append(col)
        if len(candidatas) >= max_col:
            break
    return candidatas


filtros_activos = (
    COLUMNAS_FILTRO
    if COLUMNAS_FILTRO
    else columnas_categoricas(df, MAX_FILTROS_AUTO)
)

columnas_tabla = COLUMNAS_TABLA if COLUMNAS_TABLA else df.columns.tolist()


# ── Encabezado ─────────────────────────────────────────────────────────────────
st.title(f"{APP_ICONO} {APP_TITULO}")
st.caption(APP_DESCRIPCION)
st.divider()


# ── Métricas ───────────────────────────────────────────────────────────────────
cols_metricas = st.columns(3 if not COLUMNA_METRICA_NUMERICA else 4)

cols_metricas[0].metric("Total de registros", f"{len(df):,}")
cols_metricas[1].metric("Columnas disponibles", len(df.columns))
cols_metricas[2].metric(
    "Columnas de filtro detectadas", len(filtros_activos)
)

if COLUMNA_METRICA_NUMERICA and COLUMNA_METRICA_NUMERICA in df.columns:
    total = pd.to_numeric(df[COLUMNA_METRICA_NUMERICA], errors="coerce").sum()
    cols_metricas[3].metric(COLUMNA_METRICA_NUMERICA, f"{total:,.0f}")

st.divider()


# ── Filtros ────────────────────────────────────────────────────────────────────
selecciones = {}

if filtros_activos:
    st.subheader("🔍 Filtros")
    cols_filtros = st.columns(len(filtros_activos))

    for i, col in enumerate(filtros_activos):
        opciones = ["Todos"] + sorted(df[col].dropna().unique().tolist())
        selecciones[col] = cols_filtros[i].selectbox(col.title(), opciones)

    st.divider()
else:
    st.info("No se detectaron columnas de texto con pocos valores únicos para usar como filtros.")


# ── Aplicar filtros ────────────────────────────────────────────────────────────
df_filtrado = df.copy()

for col, valor in selecciones.items():
    if valor != "Todos":
        df_filtrado = df_filtrado[df_filtrado[col] == valor]


# ── Búsqueda de texto libre ────────────────────────────────────────────────────
busqueda = st.text_input("🔎 Búsqueda en cualquier columna", placeholder="Escribe para buscar...")

if busqueda:
    mascara = df_filtrado.apply(
        lambda col: col.astype(str).str.contains(busqueda, case=False, na=False)
    ).any(axis=1)
    df_filtrado = df_filtrado[mascara]


# ── Tabla ──────────────────────────────────────────────────────────────────────
st.subheader(f"📋 Resultados: {len(df_filtrado):,} registros")

columnas_mostrar = [c for c in columnas_tabla if c in df_filtrado.columns]

st.dataframe(
    df_filtrado[columnas_mostrar],
    use_container_width=True,
    hide_index=True,
)


# ── Gráfico automático ─────────────────────────────────────────────────────────
if filtros_activos:
    st.divider()
    col_grafico = st.selectbox(
        "📊 Ver distribución por columna",
        options=filtros_activos,
        index=0,
    )

    if col_grafico:
        conteo = (
            df_filtrado[col_grafico]
            .value_counts()
            .reset_index()
        )
        conteo.columns = [col_grafico, "Cantidad"]
        st.bar_chart(conteo.set_index(col_grafico))


# ── Descarga ───────────────────────────────────────────────────────────────────
st.divider()

csv_exportar = df_filtrado[columnas_mostrar].to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Descargar resultados filtrados como CSV",
    data=csv_exportar,
    file_name="datos_filtrados.csv",
    mime="text/csv",
)

st.caption(f"Datos cargados desde Google Sheets · Caché: {CACHE_TTL}s · {APP_TITULO}")
