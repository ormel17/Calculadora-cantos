import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="Calculadora de Canto LAMIRED", layout="centered")
st.title("🧮 Calculadora de Longitud de Canto - LAMIRED")

st.write("Ingresa los valores para calcular la longitud aproximada del canto (usando el diametro de la circunferencia).")

# Inputs organizados
col1, col2, col3 = st.columns(3)
with col1:
    d_ext = st.number_input("Diámetro externo (cm):", min_value=0.0, format="%.2f")
with col2:
    d_int = st.number_input("Diámetro interno (cm):", min_value=0.0, format="%.2f")
with col3:
    espesor = st.number_input("Espesor (mm):", min_value=0.0, format="%.2f")

# Inicializar historial
if "historial" not in st.session_state:
    st.session_state.historial = []




# Botón de cálculo
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

        st.success(f"👉 La longitud aproximada del canto es: **{longitud_m:.2f} metros**")
       

        # Guardar en historial
        st.session_state.historial.append({
            "Diámetro externo (cm)": round(d_ext, 2),
            "Diámetro interno (cm)": round(d_int, 2),
            "Espesor (mm)": round(espesor, 2),
            "Longitud (m)": round(longitud_m, 2)
        })

# Mostrar historial
if st.session_state.historial:
    st.subheader("📊 Historial de cálculos")
    df = pd.DataFrame(st.session_state.historial)
    st.table(df)
    st.download_button(
        "📥 Descargar historial en CSV",
        df.to_csv(index=False),
        "historial_cantos.csv",
        "text/csv"
    )
    
# Botón para limpiar historial
if st.button("🧹 Limpiar historial"):
    st.session_state.historial.clear()
    st.success("Historial limpiado.")
