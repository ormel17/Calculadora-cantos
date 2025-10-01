import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="Calculadora de Canto LAMIRED", layout="centered")
st.title("🧮 Calculadora de Longitud de Canto - LAMIRED")
st.write("Busca el ítem por código o color y calcula la longitud (usando el área del anillo).")

# --- Config del catálogo (según tu archivo) ---
CATALOGO_PATH = "Data-cantos.xlsx"
COL_ITEM  = "Ítem"
COL_DESC  = "Nombre del producto"
COL_COLOR = "Color"

# --- Estado: historial ---
if "historial" not in st.session_state:
    st.session_state.historial = []

# ====================== CARGA Y BÚSQUEDA DE CATÁLOGO ======================
df_catalog = None
with st.sidebar:
    st.header("📁 Catálogo")
    try:
        df_catalog = pd.read_excel(CATALOGO_PATH)
    except Exception:
        st.warning("No se pudo leer 'Data-cantos.xlsx'. Sube el archivo aquí:")
        up = st.file_uploader("Subir catálogo (.xlsx)", type=["xlsx"])
        if up is not None:
            try:
                df_catalog = pd.read_excel(up)
            except Exception as e:
                st.error(f"No pude abrir el Excel: {e}")

    if df_catalog is not None:
        faltan = [c for c in (COL_ITEM, COL_DESC, COL_COLOR) if c not in df_catalog.columns]
        if faltan:
            st.error(f"Faltan columnas en el catálogo: {', '.join(faltan)}")
            df_catalog = None

if df_catalog is not None:
    # Normalizar a string para búsquedas robustas (respeta acentos)
    for c in (COL_ITEM, COL_DESC, COL_COLOR):
        df_catalog[c] = df_catalog[c].astype(str)

    st.subheader("🔎 Buscar ítem en el catálogo")
    c1, c2 = st.columns([2, 1])
    with c1:
        q_codigo = st.text_input("Código (Ítem) contiene…")
    with c2:
        colores = ["(Todos)"] + sorted(df_catalog[COL_COLOR].unique().tolist())
        q_color = st.selectbox("Color", options=colores)

    # Filtros
    mask = pd.Series([True] * len(df_catalog))
    if q_codigo:
        mask &= df_catalog[COL_ITEM].str.lower().str.contains(q_codigo.lower())
    if q_color != "(Todos)":
        mask &= df_catalog[COL_COLOR] == q_color

    df_view = df_catalog.loc[mask].reset_index(drop=True)

    # Resultados
    st.write("**Resultados del catálogo**")
    st.dataframe(df_view, use_container_width=True)

    # Selección para asociar al cálculo
    options = [
        f"{row[COL_ITEM]} — {row[COL_DESC]} — {row[COL_COLOR]}"
        for _, row in df_view.iterrows()
    ]
    sel_opt = st.selectbox("Selecciona el ítem a asociar (opcional)", options=["(Sin selección)"] + options)
else:
    df_view = None
    options = []
    sel_opt = "(Sin selección)"
    st.info("Carga el catálogo para habilitar la búsqueda por código/color.")

st.markdown("---")

# ====================== ENTRADAS Y CÁLCULO ======================
col1, col2, col3 = st.columns(3)
with col1:
    d_ext = st.number_input("Diámetro externo (cm):", min_value=0.0, format="%.2f")
with col2:
    d_int = st.number_input("Diámetro interno (cm):", min_value=0.0, format="%.2f")
with col3:
    espesor = st.number_input("Espesor (mm):", min_value=0.0, format="%.2f")

if st.button("Calcular longitud"):
    # Validaciones
    if d_ext <= 0 or d_int < 0 or espesor <= 0:
        st.error("Todos los valores deben ser > 0 (y el diámetro interno puede ser 0).")
    elif d_ext <= d_int:
        st.error("El diámetro externo debe ser mayor que el diámetro interno.")
    else:
        # Área del anillo en cm²
        area_cm2 = math.pi * (((d_ext / 2.0) ** 2) - ((d_int / 2.0) ** 2))
        # Resultado en METROS: cm² / (mm*0.1) = cm; cm/100 = m  ⇒ dividir entre (espesor*10)
        longitud_m = area_cm2 / (espesor * 10.0)
        st.success(f"👉 Longitud aproximada: **{longitud_m:.2f} m**")

        # Datos del ítem seleccionado (si hay)
        item = desc = color = ""
        if df_view is not None and options and sel_opt != "(Sin selección)":
            i = options.index(sel_opt)
            item  = df_view.loc[i, COL_ITEM]
            desc  = df_view.loc[i, COL_DESC]
            color = df_view.loc[i, COL_COLOR]

        # Guardar en historial
        st.session_state.historial.append({
            "Ítem": item,
            "Nombre del producto": desc,
            "Color": color,
            "d_ext (cm)": round(d_ext, 2),
            "d_int (cm)": round(d_int, 2),
            "Espesor (mm)": round(espesor, 2),
            "Longitud (m)": round(longitud_m, 2)
        })

# ====================== HISTORIAL ======================
if st.button("🧹 Limpiar historial"):
    st.session_state.historial.clear()
    st.success("Historial limpiado.")

if st.session_state.historial:
    st.subheader("📊 Historial de cálculos")
    df_hist = pd.DataFrame(st.session_state.historial)
    st.table(df_hist)
    st.download_button(
        "📥 Descargar historial en CSV",
        df_hist.to_csv(index=False).encode("utf-8"),
        "historial_cantos.csv",
        "text/csv"
    )
