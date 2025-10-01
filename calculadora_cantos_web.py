import streamlit as st
import math
import pandas as pd

# Intentar importar matplotlib; si no está, no rompemos la app
try:
    import matplotlib.pyplot as plt
    import io
    MATPLOTLIB_OK = True
except Exception:
    MATPLOTLIB_OK = False
    plt = None
    io = None

st.set_page_config(page_title="Calculadora de Canto LAMIRED", layout="centered")
st.title("🧮 Calculadora de Longitud de Canto - LAMIRED")
st.write("Ingresa los valores para calcular la longitud aproximada del canto (usando el área del anillo).")

# ------------------------ Función del diagrama ------------------------
def render_diagrama(d_ext_cm: float, d_int_cm: float, espesor_mm: float | None = None):
    """
    Dibuja dos círculos concéntricos d_ext y d_int.
    Si no hay matplotlib disponible o los datos no son válidos, retorna None.
    """
    if not MATPLOTLIB_OK:
        return None
    if d_ext_cm <= 0 or d_int_cm < 0 or d_ext_cm <= d_int_cm:
        return None

    R_ext = d_ext_cm / 2.0
    R_int = d_int_cm / 2.0

    fig, ax = plt.subplots(figsize=(5, 5))

    # Círculo externo e interno
    ext = plt.Circle((0, 0), R_ext, fill=False, linewidth=2)
    inte = plt.Circle((0, 0), R_int, fill=False, linewidth=2, linestyle="--")
    ax.add_patch(ext)
    ax.add_patch(inte)

    # Diámetro externo
    ax.annotate("", xy=(R_ext, 0), xytext=(-R_ext, 0),
                arrowprops=dict(arrowstyle="<->", linewidth=1.5))
    ax.text(0, 0.30 * R_ext, f"d_ext = {d_ext_cm:.2f} cm", ha="center", va="bottom")

    # Diámetro interno
    ax.annotate("", xy=(R_int, 0), xytext=(-R_int, 0),
                arrowprops=dict(arrowstyle="<->", linewidth=1.5, linestyle="--"))
    ax.text(0, -0.30 * R_ext, f"d_int = {d_int_cm:.2f} cm", ha="center", va="top")

    # Anotar espesor si viene
    if espesor_mm is not None and espesor_mm > 0:
        ax.text(0, -0.60 * R_ext, f"Espesor = {espesor_mm:.2f} mm (referencia)", ha="center")

    # Estética
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-R_ext * 1.2, R_ext * 1.2)
    ax.set_ylim(-R_ext * 1.2, R_ext * 1.2)
    ax.set_xlabel("Esquema: anillo del rollo (sólido = d_ext, punteado = d_int)")
    ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    return fig

# ------------------------ Inputs ------------------------
col1, col2, col3 = st.columns(3)
with col1:
    d_ext = st.number_input("Diámetro externo (cm):", min_value=0.0, format="%.2f")
with col2:
    d_int = st.number_input("Diámetro interno (cm):", min_value=0.0, format="%.2f")
with col3:
    espesor = st.number_input("Espesor (mm):", min_value=0.0, format="%.2f")

# ------------------------ Estado: historial ------------------------
if "historial" not in st.session_state:
    st.session_state.historial = []

# ------------------------ Cálculo ------------------------
if st.button("Calcular longitud"):
    # Validaciones
    if d_ext <= 0 or d_int < 0 or espesor <= 0:
        st.error("Todos los valores deben ser > 0 (y el diámetro interno puede ser 0).")
    elif d_ext <= d_int:
        st.error("El diámetro externo debe ser mayor que el diámetro interno.")
    else:
        # Área del anillo en cm²
        area_cm2 = math.pi * (((d_ext / 2.0) ** 2) - ((d_int / 2.0) ** 2))
        # Resultado en METROS: cm² / (mm*0.1) = cm, luego /100 = m  ⇒ dividir entre (espesor*10)
        longitud_m = area_cm2 / (espesor * 10.0)

        st.success(f"👉 La longitud aproximada del canto es: **{longitud_m:,.2f} m**")

        # Guardar en historial
        st.session_state.historial.append({
            "Diámetro externo (cm)": round(d_ext, 2),
            "Diámetro interno (cm)": round(d_int, 2),
            "Espesor (mm)": round(espesor, 2),
            "Longitud (m)": round(longitud_m, 2)
        })

        # (Opcional) Detalle de cálculo
        espesor_cm = espesor / 10.0
        longitud_cm = area_cm2 / espesor_cm
        perimetro_medio_cm = math.pi * (d_ext + d_int) / 2.0
        with st.expander("📚 Ver detalle del cálculo"):
            st.write(f"Área del anillo: **{area_cm2:,.2f} cm²**")
            st.write(f"Espesor: **{espesor:.2f} mm**  → **{espesor_cm:.3f} cm**")
            st.write(f"Perímetro medio (referencia): **{perimetro_medio_cm:,.2f} cm**")
            st.write(f"Longitud en cm (sin redondeo): **{longitud_cm:,.2f} cm**")
            st.write(f"Longitud en m (sin redondeo): **{longitud_m:,.2f} m**")

# ------------------------ Historial ------------------------
if st.session_state.historial:
    st.subheader("📊 Historial de cálculos")
    df = pd.DataFrame(st.session_state.historial)
    st.table(df)
    st.download_button(
        "📥 Descargar historial en CSV",
        df.to_csv(index=False).encode("utf-8"),
        "historial_cantos.csv",
        "text/csv"
    )

# Botón para limpiar historial
if st.button("🧹 Limpiar historial"):
    st.session_state.historial.clear()
    st.success("Historial limpiado.")

# ------------------------ Imagen explicativa ------------------------
st.markdown("---")
mostrar_img = st.checkbox("Mostrar imagen explicativa", value=True)
if mostrar_img:
    if MATPLOTLIB_OK:
        fig = render_diagrama(d_ext, d_int, espesor)
        if fig is not None:
            st.subheader("🖼️ Imagen explicativa")
            st.pyplot(fig)
            # Descarga PNG
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
            st.download_button(
                "📥 Descargar imagen (.png)",
                data=buf.getvalue(),
                file_name="diagrama_canto.png",
                mime="image/png"
            )
            plt.close(fig)  # libera memoria
        else:
            st.info("La imagen aparecerá cuando d_ext > d_int y ambos sean > 0.")
    else:
        st.info("Para ver el diagrama instala **matplotlib** (ver instrucciones en requirements.txt).")
