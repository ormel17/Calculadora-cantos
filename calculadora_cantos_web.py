import streamlit as st
import pandas as pd
import math
from pathlib import Path

# ---------------- Config de página ----------------
st.set_page_config(page_title="Calculadora de Longitud de Canto - LAMiRED", layout="centered")
st.title("🧮 Calculadora de Longitud de Canto - LAMIRED")
st.write("Busca el ítem por **código** o **color** y calcula la **longitud** (usando el área del anillo).")

# ---------------- Rutas y columnas ----------------
BASE_DIR = Path(__file__).resolve().parent
CATALOGO_PATH = BASE_DIR / "Data-cantos.xlsx"      # archivo en el repo
COL_ITEM  = "Ítem"
COL_DESC  = "Nombre del producto"
COL_COLOR = "Color"
REQ_COLS  = [COL_ITEM, COL_DESC, COL_COLOR]

# ---------------- Carga de catálogo (solo desde repo) ----------------
@st.cache_data(show_spinner=False)
def cargar_catalogo_desde_repo(path: Path) -> pd.DataFrame:
    # Necesita openpyxl para .xlsx
    df = pd.read_excel(path, engine="openpyxl")
    # Normalizar encabezados
    df.columns = [str(c).strip() for c in df.columns]
    faltan = [c for c in REQ_COLS if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas: {', '.join(faltan)}. Detectadas: {list(df.columns)}")
    for c in REQ_COLS:
        df[c] = df[c].astype(str)
    return df

try:
    if not CATALOGO_PATH.exists():
        st.error(f"No encuentro el archivo **{CATALOGO_PATH.name}** en el repositorio.\n"
                 f"Ubicación esperada: `{CATALOGO_PATH}`")
        st.stop()
    df_catalog = cargar_catalogo_desde_repo(CATALOGO_PATH)
except ImportError as e:
    # Falta openpyxl
    st.error("Falta el paquete **openpyxl** para leer el Excel del repositorio.")
    st.caption("Añade este requirements.txt en la raíz del repo y vuelve a desplegar:")
    st.code("streamlit>=1.36\npandas>=2.0\nopenpyxl>=3.1", language="bash")
    st.stop()
except Exception as e:
    st.error(f"No pude leer el catálogo del repositorio: {e}")
    st.stop()

# ---------------- Búsqueda por código / color ----------------
st.subheader("🔎 Buscar ítem en el catálogo")

c1, c2 = st.columns([2, 1])
with c1:
    q_codigo = st.text_input("Código (Ítem) contiene…")
with c2:
    colores = ["(Todos)"] + sorted(df_catalog[COL_COLOR].unique().tolist())
    q_color = st.selectbox("Color", options=colores)

mask = pd.Series(True, index=df_catalog.index)
if q_codigo:
    mask &= df_catalog[COL_ITEM].str.contains(q_codigo, case=False, na=False)
if q_color != "(Todos)":
    mask &= df_catalog[COL_COLOR] == q_color

df_view = df_catalog.loc[mask].copy()

st.write("**Resultados del catálogo**")
st.dataframe(df_view, use_container_width=True)

# Selectbox robusto usando índices reales (evita errores con duplicados)
if not df_view.empty:
    sel_idx = st.selectbox(
        "Selecciona el ítem a asociar (opcional)",
        options=df_view.index.tolist(),
        format_func=lambda i: f"{df_view.at[i, COL_ITEM]} — {df_view.at[i, COL_DESC]} — {df_view.at[i, COL_COLOR]}"
    )
else:
    sel_idx = None

st.markdown("---")

# ---------------- Entradas y cálculo ----------------
col1, col2, col3 = st.columns(3)
with col1:
    d_ext = st.number_input("Diámetro externo (cm):", min_value=0.0, format="%.2f")
with col2:
    d_int = st.number_input("Diámetro interno (cm):", min_value=0.0, format="%.2f")
with col3:
    espesor = st.number_input("Espesor (mm):", min_value=0.0, format="%.2f")

# Estado historial
if "historial" not in st.session_state:
    st.session_state.historial = []

# Calcular
if st.button("Calcular longitud"):
    if d_ext <= 0 or d_int < 0 or espesor <= 0:
        st.error("Todos los valores deben ser > 0 (y el diámetro interno puede ser 0).")
    elif d_ext <= d_int:
        st.error("El diámetro externo debe ser mayor que el diámetro interno.")
    else:
        area_cm2 = math.pi * (((d_ext / 2.0) ** 2) - ((d_int / 2.0) ** 2))
        longitud_m = area_cm2 / (espesor * 10.0)  # m (cm² / (mm*10))

        st.success(f"👉 Longitud aproximada: **{longitud_m:.2f} m**")

        item = desc = color = ""
        if sel_idx is not None:
            item  = df_view.at[sel_idx, COL_ITEM]
            desc  = df_view.at[sel_idx, COL_DESC]
            color = df_view.at[sel_idx, COL_COLOR]

        st.session_state.historial.append({
            "Ítem": item,
            "Nombre del producto": desc,
            "Color": color,
            "d_ext (cm)": round(d_ext, 2),
            "d_int (cm)": round(d_int, 2),
            "Espesor (mm)": round(espesor, 2),
            "Longitud (m)": round(longitud_m, 2),
        })

# Limpiar historial
if st.button("🧹 Limpiar historial"):
    st.session_state.historial.clear()
    st.success("Historial limpiado.")

# Mostrar historial
if st.session_state.historial:
    st.subheader("📊 Historial de cálculos")
    df_hist = pd.DataFrame(st.session_state.historial)
    st.table(df_hist)
    st.download_button(
        "📥 Descargar historial (CSV)",
        df_hist.to_csv(index=False).encode("utf-8"),
        "historial_cantos.csv",
        "text/csv"
    )

