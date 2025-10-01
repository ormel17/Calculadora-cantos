import streamlit as st
import math
import pandas as pd
import os
from pathlib import Path

# ========= Config básica =========
st.set_page_config(page_title="Calculadora de Canto LAMIRED", layout="centered")
st.title("🧮 Calculadora de Longitud de Canto - LAMIRED")
st.write("Busca el ítem por **código** o **color** y calcula la **longitud** (usando el área del anillo).")

CATALOGO_PATH = Path("Data-cantos.xlsx")  # según tu repo
REQ_COLS = ["Ítem", "Nombre del producto", "Color"]

# ========= Estado =========
if "historial" not in st.session_state:
    st.session_state.historial = []

# ========= UTIL: cargar Excel con mensajes claros =========
def cargar_catalogo():
    # Debug opcional
    with st.sidebar.expander("🛠️ Debug (opcional)"):
        st.caption(f"cwd: {os.getcwd()}")
        try:
            st.caption(f"Archivos en cwd: {os.listdir('.')}")
        except Exception:
            pass

    df_local = None
    # 1) Intento leer del repo
    if CATALOGO_PATH.exists():
        try:
            # openpyxl es el motor recomendado para .xlsx
            df_local = pd.read_excel(CATALOGO_PATH, engine="openpyxl")
        except Exception as e:
            st.warning("No pude leer 'Data-cantos.xlsx' del repositorio.")
            st.caption(f"Detalle: {e}")

    # 2) Si no se pudo, permitir subir
    if df_local is None:
        with st.sidebar:
            st.header("📁 Catálogo")
            st.warning("No se pudo cargar automáticamente el Excel. Sube el archivo aquí:")
            up = st.file_uploader("Subir catálogo (.xlsx)", type=["xlsx"])
            if up is not None:
                try:
                    df_local = pd.read_excel(up, engine="openpyxl")
                except Exception as e:
                    st.error(f"No pude abrir el Excel subido: {e}")

    # 3) Validar columnas esperadas (con limpieza básica)
    if df_local is not None:
        # Limpia espacios en encabezados
        df_local.columns = [str(c).strip() for c in df_local.columns]
        # Revisa columnas
        faltan = [c for c in REQ_COLS if c not in df_local.columns]
        if faltan:
            st.error(f"El Excel se abrió pero faltan estas columnas: {', '.join(faltan)}")
            st.caption(f"Encabezados detectados: {list(df_local.columns)}")
            return None
        # Fuerza string para búsquedas
        for c in REQ_COLS:
            df_local[c] = df_local[c].astype(str)
    return df_local

# ========= Carga catálogo =========
df_catalog = cargar_catalogo()

# ========= Búsqueda por cód/color =========
if df_catalog is not None:
    st.subheader("🔎 Buscar ítem en el catálogo")
    c1, c2 = st.columns([2, 1])
    with c1:
        q_codigo = st.text_input("Código (Ítem) contiene…")
    with c2:
        colores = ["(Todos)"] + sorted(df_catalog["Color"].unique().tolist())
        q_color = st.selectbox("Color", options=colores)

    mask = pd.Series([True] * len(df_catalog))
    if q_codigo:
        mask &= df_catalog["Ítem"].str.lower().str.contains(q_codigo.lower())
    if q_color != "(Todos)":
        mask &= df_catalog["Color"] == q_color

    df_view = df_catalog.loc[mask].reset_index(drop=True)
    st.write("**Resultados del catálogo**")
    st.dataframe(df_view, use_container_width=True)

    # Seleccionar ítem para asociar al cálculo
    options = [f"{r['Ítem']} — {r['Nombre del producto']} — {r['Color']}" for _, r in df_view.iterrows()]
    sel_opt = st.selectbox("Selecciona el ítem a asociar (opcional)", options=["(Sin selección)"] + options)
else:
    df_view, options, sel_opt = None, [], "(Sin selección)"
    st.info("Sube o corrige el archivo para habilitar la búsqueda.")

st.markdown("---")

# ========= Entradas y cálculo =========
col1, col2, col3 = st.columns(3)
with col1:
    d_ext = st.number_input("Diámetro externo (cm):", min_value=0.0, format="%.2f")
with col2:
    d_int = st.number_input("Diámetro interno (cm):", min_value=0.0, format="%.2f")
with col3:
    espesor = st.number_input("Espesor (mm):", min_value=0.0, format="%.2f")

if st.button("Calcular longitud"):
    if d_ext <= 0 or d_int < 0 or espesor <= 0:
        st.error("Todos los valores deben ser > 0 (y el diámetro interno puede ser 0).")
    elif d_ext <= d_int:
        st.error("El diámetro externo debe ser mayor que el diámetro interno.")
    else:
        area_cm2 = math.pi * (((d_ext / 2.0) ** 2) - ((d_int / 2.0) ** 2))
        longitud_m = area_cm2 / (espesor * 10.0)  # m

        st.success(f"👉 Longitud aproximada: **{longitud_m:.2f} m**")

        # Metadatos del ítem seleccionado
        item = desc = color = ""
        if df_view is not None and options and sel_opt != "(Sin selección)":
            i = options.index(sel_opt)
            item  = df_view.loc[i, "Ítem"]
            desc  = df_view.loc[i, "Nombre del producto"]
            color = df_view.loc[i, "Color"]

        st.session_state.historial.append({
            "Ítem": item,
            "Nombre del producto": desc,
            "Color": color,
            "d_ext (cm)": round(d_ext, 2),
            "d_int (cm)": round(d_int, 2),
            "Espesor (mm)": round(espesor, 2),
            "Longitud (m)": round(longitud_m, 2),
        })

# ========= Historial =========
if st.button("🧹 Limpiar historial"):
    st.session_state.historial.clear()
    st.success("Historial limpiado.")

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
