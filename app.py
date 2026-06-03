import streamlit as st
import pandas as pd

# ── CONFIGURACIÓN DE LA PÁGINA ──────────────────────────────────────────────
st.set_page_config(
    page_title="Matriz Proyectos SSSA",
    page_icon="🏥",
    layout="wide"
)

# ── URL DE GOOGLE SHEETS ─────────────────────────────────────────────────────
# Reemplaza esta URL con la que copiaste en el Paso 1
SHEET_URL = "https://docs.google.com/spreadsheets/d/TU_ID_AQUI/export?format=csv&gid=0"

# ── CARGAR DATOS ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)  # Guarda en caché por 60 segundos
def cargar_datos(url):
    df = pd.read_csv(url)
    return df

try:
    df = cargar_datos(SHEET_URL)
except Exception as e:
    st.error(f"No se pudo cargar la hoja de cálculo. Verifica que esté publicada. Error: {e}")
    st.stop()

# ── ENCABEZADO ────────────────────────────────────────────────────────────────
st.title("🏥 Matriz de Proyectos Presentados")
st.caption("Secretaría Seccional de Salud de Antioquia — Actualización automática cada 60 segundos")
st.divider()

# ── MÉTRICAS RESUMEN ──────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de proyectos", len(df))
col2.metric("Municipios únicos", df["MUNICIPIO"].nunique() if "MUNICIPIO" in df.columns else "—")
col3.metric("Radicados (SI)", (df["RADICADO (SI/NO)"] == "SI").sum() if "RADICADO (SI/NO)" in df.columns else "—")
col4.metric("Ejecutados", (df["ESTADO DE REVISIÓN"] == "EJECUTADO").sum() if "ESTADO DE REVISIÓN" in df.columns else "—")

st.divider()

# ── FILTROS ───────────────────────────────────────────────────────────────────
st.subheader("🔍 Filtros")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    municipios = ["Todos"] + sorted(df["MUNICIPIO"].dropna().unique().tolist())
    municipio_sel = st.selectbox("Municipio", municipios)

with col_f2:
    componentes = ["Todos"] + sorted(df["COMPONENTE"].dropna().unique().tolist())
    componente_sel = st.selectbox("Componente", componentes)

with col_f3:
    if "ESTADO DE REVISIÓN" in df.columns:
        estados = ["Todos"] + sorted(df["ESTADO DE REVISIÓN"].dropna().unique().tolist())
        estado_sel = st.selectbox("Estado de revisión", estados)
    else:
        estado_sel = "Todos"

with col_f4:
    if "PROFESIONAL A CARGO" in df.columns:
        profesionales = ["Todos"] + sorted(df["PROFESIONAL A CARGO"].dropna().unique().tolist())
        profesional_sel = st.selectbox("Profesional a cargo", profesionales)
    else:
        profesional_sel = "Todos"

# ── APLICAR FILTROS ───────────────────────────────────────────────────────────
df_filtrado = df.copy()

if municipio_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["MUNICIPIO"] == municipio_sel]

if componente_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["COMPONENTE"] == componente_sel]

if estado_sel != "Todos" and "ESTADO DE REVISIÓN" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["ESTADO DE REVISIÓN"] == estado_sel]

if profesional_sel != "Todos" and "PROFESIONAL A CARGO" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["PROFESIONAL A CARGO"] == profesional_sel]

# ── TABLA DE RESULTADOS ───────────────────────────────────────────────────────
st.subheader(f"📋 Proyectos encontrados: {len(df_filtrado)}")

st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True,
    column_config={
        "ID": st.column_config.TextColumn("ID Proyecto", width="medium"),
        "MUNICIPIO": st.column_config.TextColumn("Municipio", width="medium"),
        "COMPONENTE": st.column_config.TextColumn("Componente", width="medium"),
        "OBSERVACION": st.column_config.TextColumn("Observación", width="large"),
    }
)

# ── GRÁFICO: PROYECTOS POR COMPONENTE ─────────────────────────────────────────
st.divider()
st.subheader("📊 Distribución por componente")

if "COMPONENTE" in df_filtrado.columns:
    conteo = df_filtrado["COMPONENTE"].value_counts().reset_index()
    conteo.columns = ["Componente", "Cantidad"]
    st.bar_chart(conteo.set_index("Componente"))

# ── PIE DE PÁGINA ─────────────────────────────────────────────────────────────
st.divider()
st.caption("Datos cargados desde Google Sheets. Fuente: Secretaría Seccional de Salud de Antioquia.")
