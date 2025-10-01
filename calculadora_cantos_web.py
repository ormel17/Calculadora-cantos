import streamlit as st
import pandas as pd
import math
import io
import matplotlib.pyplot as plt

# ------------------------ Configuración básica ------------------------
st.set_page_config(page_title="Calculadora de Canto LAMIRED", layout="wide")
st.title("🧮 Calculadora de Longitud de Canto - LAMIRED")
st.caption("Busca el producto por Item ERP o Color, selecciona el ítem y registra las medidas del rollo para calcular la longitud.")

CATALOGO_PATH = "Data-cantos.xlsx"
COL_ITEM = "Item ERP"
COL_DESC = "Descripción LAMIRED"
COL_COLOR = "Apariencia"

# ------------------------ Utilidades ------------------------
@st.cache_data(show_spinner=False)
def cargar_catalogo(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    faltantes = [c for c in (COL_ITEM, COL_DESC, COL_COLOR) if c not in df.columns]
    if faltantes:
        raise ValueError(f"Al catálogo le faltan columnas: {', '.join(faltantes)}")
    # Asegurar string para búsquedas robustas
    for c in (COL_ITEM, COL_DESC, COL_COLOR):
        df[c] = df[c].astype(str)
    return df

def calcular_longitud(d_ext_cm: float, d_int_cm: float, espesor_mm: float) -> float | None:
    """
    Longitud (cm) = Área del anillo (cm²) / espesor (cm)
    Área = π * [ (d_ext/2)^2 - (d_int/2)^2 ]
    espesor (cm) = espesor_mm / 10
    """
    if d_ext_cm <= 0 or d_int_cm < 0 or espesor_mm <= 0 or d_ext_cm <= d_int_cm:
        return None
    area_cm2 = math.pi * (((d_ext_cm / 2) ** 2) - ((d_int_cm / 2) ** 2))
    espesor_cm = espesor_mm / 10.0
    return area_cm2 / espesor_cm

def render_diagrama(d_ext_cm: float, d_int_cm: float):
    """
    Dibuja dos círculos concéntricos representando d_ext y d_int,
    y anota los valores para apoyar la comprensión visual.
    """
    if d_ext_cm <= 0 or d_int_cm < 0 or d_ext_cm <= d_int_cm:
        return None

    # Radio externos / internos en "unidades" arbitrarias (escala relativa)
    R_ext = d_ext_cm / 2.0
    R_int = d_int_cm / 2.0

    fig, ax = plt.subplots(figsize=(5, 5))
    # Círculos
    ext = plt.Circle((0, 0), R_ext, fill=False, linewidth=2)
    inte = plt.Circle((0, 0), R_int, fill=False, linewidth=2, linestyle="--")

    ax.add_patch(ext)
    ax.add_patch(inte)

    # Flechas para marcar diámetros
    ax.annotate(
        "", xy=(R_ext, 0), xytext=(-R_ext, 0),
        arrowprops=dict(arrowstyle="<->", linewidth=1.5)
    )
    ax.text(0, 0.3 * R_ext, f"d_ext = {d_ext_cm:.2f} cm", ha="center", va="bottom")

    ax.annotate(
        "", xy=(R_int, 0), xytext=(-R_int, 0),
        arrowprops=dict(arrowstyle="<->", linewidth=1.5, linestyle="--")
    )
    ax.text(0, -0.3 * R_ext, f"d_int = {d_int_cm:.2f} cm", ha="center", va="top")

    # Estética
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-R_ext * 1.2, R_ext * 1.2)
    ax.set_ylim(-R_ext * 1.2, R_ext * 1.2)
    ax.set_xlabel("Vista esquemática: dos círculos concéntricos (anillo del rollo)")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    return fig

# ------------------------ Carga catálogo ------------------------
try:
    df = cargar_catalogo(CATALOGO_PATH)
except Exception as e:
    st.error(
        f"No pude cargar el catálogo en **{CATALOGO_PATH}**.\n\n"
        f"Detalle: {e}\n\n"
        f"Verifica que el archivo exista y que tenga las columnas "
        f"**{COL_ITEM}**, **{COL_DESC}** y **{COL_COLOR}**."
    )
    st.stop()

# ------------------------ Búsqueda y filtros ------------------------
with st.sidebar:
    st.header("🔎 Búsqueda en catálogo")
    q_text = st.text_input("Búsqueda libre (Item/Descripción/Color)")
    sel_item = st.selectbox(
        "Filtrar por Item ERP",
        options=["(Todos)"] + sorted(df[COL_ITEM].unique().tolist())
    )
    sel_color = st.selectbox(
        "Filtrar por Color (Apariencia)",
        options=["(Todos)"] + sorted(df[COL_COLOR].unique().tolist())
    )

mask = pd.Series([True] * len(df))
if q_text:
    q = q_text.lower()
    mask &= (
        df[COL_ITEM].str.lower().str.contains(q) |
        df[COL_DESC].str.lower().str.contains(q) |
        df[COL_COLOR].str.lower().str.contains(q)
    )
if sel_item != "(Todos)":
    mask &= df[COL_ITEM] == sel_item
if sel_color != "(Todos)":
    mask &= df[COL_COLOR] == sel_color

df_view = df.loc[mask].reset_index(drop=True)

st.subheader("📋 Resultados del catálogo")
st.dataframe(df_view, use_container_width=True, hide_index=True)

# ------------------------ Selección de ítem ------------------------
st.markdown("**Selecciona el ítem para asociar el cálculo:**")
options = [f"{row[COL_ITEM]} — {row[COL_DESC]} — {row[COL_COLOR]}" for _, row in df_view.iterrows()]
sel_idx = st.selectbox("Ítem del catálogo", options=["(Sin selección)"] + options)

# ------------------------ Entradas del cálculo ------------------------
st.subheader("📐 Medidas del rollo")
c1, c2, c3 = st.columns(3)
with c1:
    d_ext = st.number_input("Diámetro externo (cm)", min_value=0.0, format="%.2f")
with c2:
    d_int = st.number_input("Diámetro interno (cm)", min_value=0.0, format="%.2f")
with c3:
    espesor = st.number_input("Espesor del canto (mm)", min_value=0.0, format="%.2f")

if "historial" not in st.session_state:
    st.session_state.historial = []

# ------------------------ Acciones ------------------------
colA, colB, colC = st.columns([1, 1, 1])
with colA:
    calc = st.button("Calcular longitud")
with colB:
    limpiar = st.button("Limpiar historial")
with colC:
    mostrar_graf = st.checkbox("Mostrar imagen explicativa", value=True)

if limpiar:
    st.session_state.historial = []
    st.experimental_rerun()

if calc:
    L_cm = calcular_longitud(d_ext, d_int, espesor)
    if L_cm is None:
        st.error("Verifica los datos: d_ext > d_int y todos los valores deben ser > 0.")
    else:
        st.success(f"👉 Longitud aproximada: **{L_cm:,.2f} cm**  (≈ **{L_cm/100:,.2f} m**)")

        item_erp = desc = color = ""
        if sel_idx != "(Sin selección)" and options:
            i = options.index(sel_idx)
            item_erp = df_view.loc[i, COL_ITEM]
            desc     = df_view.loc[i, COL_DESC]
            color    = df_view.loc[i, COL_COLOR]

        st.session_state.historial.append({
            "Item ERP": item_erp,
            "Descripción": desc,
            "Color": color,
            "d_ext (cm)": round(d_ext, 2),
            "d_int (cm)": round(d_int, 2),
            "Espesor (mm)": round(espesor, 2),
            "Longitud (cm)": round(L_cm, 2),
            "Longitud (m)": round(L_cm/100, 2),
        })

# ------------------------ Imagen / diagrama explicativo ------------------------
if mostrar_graf:
    fig = render_diagrama(d_ext, d_int)
    if fig is not None:
        st.subheader("🖼️ Imagen explicativa")
        st.pyplot(fig)
        with io.BytesIO() as buf:
            fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
            img_bytes = buf.getvalue()
        st.download_button("📥 Descargar imagen (.png)", data=img_bytes, file_name="diagrama_canto.png", mime="image/png")
    else:
        st.info("La imagen explicativa aparecerá cuando d_ext > d_int y ambos sean mayores a 0.")

# ------------------------ Historial y exportación ------------------------
if st.session_state.historial:
    st.subheader("🧾 Historial de cálculos")
    hist_df = pd.DataFrame(st.session_state.historial)
    st.dataframe(hist_df, use_container_width=True)
    st.download_button(
        "📥 Descargar historial (CSV)",
        hist_df.to_csv(index=False).encode("utf-8"),
        "historial_cantos.csv",
        "text/csv"
    )

# ------------------------ Información de fórmula ------------------------
with st.expander("📚 Ver fórmula y unidades"):
    st.markdown(
        """
**Fórmula**  
Longitud \\(L\\) (cm) = \\( \\dfrac{\\text{Área del anillo (cm}^2\\text{)}}{\\text{Espesor (cm)}} \\)  
\\( \\text{Área} = \\pi \\cdot \\left[ \\left(\\dfrac{d_{ext}}{2}\\right)^2 - \\left(\\dfrac{d_{int}}{2}\\right)^2 \\right] \\)

**Unidades usadas**  
- Diámetros en **cm**  
- Espesor en **mm** → convertido a **cm** dentro del cálculo (\\(1\\,\\text{mm} = 0.1\\,\\text{cm}\\))
        """
    )

