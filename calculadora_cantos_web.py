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

# Cálculo (resultado en METROS)
if st.button("Calcular longitud"):
    # Validaciones mínimas
    if d_ext <= 0 or d_int < 0 or espesor <= 0:
        st.error("Todos los valores deben ser > 0 (y d_int ≥ 0).")
    elif d_ext <= d_int:
        st.error("El diámetro externo debe ser mayor que el interno.")
    else:
        # Área del anillo en cm²
        area_cm2 = math.pi * (((d_ext/2.0)**2) - ((d_int/2.0)**2))
        # Resultado directo en metros: dividir por (espesor*10)
        longitud_m = area_cm2 / (espesor * 10.0)

        st.success(f"👉 Longitud aproximada del canto: **{longitud_m:,.2f} metros**")


       # Guardar en historial
        st.session_state.historial.append({
            "Diámetro externo (cm)": d_ext,
            "Diámetro interno (cm)": d_int,
            "Espesor (mm)": espesor,
            "Longitud (cm)": round(longitud, 2)
        })

    else:
        st.error("Verifica que todos los valores sean válidos y que el diámetro externo sea mayor al interno.")

# Mostrar historial
if st.session_state.historial:
    st.subheader("📊 Historial de cálculos")
    df = pd.DataFrame(st.session_state.historial)
    st.table(df)
    st.download_button("📥 Descargar historial en CSV", df.to_csv(index=False), "historial_cantos.csv", "text/csv")
