import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="Calculadora de Canto LAMIRED", layout="centered")
st.title("🧮 Calculadora de Longitud de Canto - LAMIRED")

st.write("Ingresa los valores para calcular la longitud aproximada del canto usando el perímetro medio.")

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

# Cálculo
if st.button("Calcular longitud"):
    if d_ext > 0 and d_int >= 0 and espesor > 0 and d_ext > d_int:
        longitud = (math.pi * (((d_ext/2)**2) - ((d_int/2)**2))) / (espesor*10)  # conversión mm->cm
        st.success(f"👉 La longitud aproximada del canto es: **{longitud:.2f} metros**")

        # Guardar en historial
        st.session_state.historial.append({
            "Diámetro externo (cm)": d_ext,
            "Diámetro interno (cm)": d_int,
            "Espesor (mm)": espesor,
            "Longitud (cm)": round(longitud, 1)
        })

    else:
        st.error("Verifica que todos los valores sean válidos y que el diámetro externo sea mayor al interno.")

# Mostrar historial
if st.session_state.historial:
    st.subheader("📊 Historial de cálculos")
    df = pd.DataFrame(st.session_state.historial)
    st.table(df)
    st.download_button("📥 Descargar historial en CSV", df.to_csv(index=False), "historial_cantos.csv", "text/csv")
