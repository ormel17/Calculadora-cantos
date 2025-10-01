import streamlit as st
import math

# Título de la aplicación
st.title("Calculadora de Longitud de Canto LAMIRED")

# Instrucciones
st.write("Ingresa los valores para calcular la longitud aproximada del canto usando el perímetro medio.")

# Entradas del usuario
d_ext = st.number_input("Diámetro externo (Cm):", min_value=0.0, format="%.2f")
d_int = st.number_input("Diámetro interno (Cm):", min_value=0.0, format="%.2f")
espesor = st.number_input("Espesor del canto (mm):", min_value=0.0, format="%.2f")

# Botón para calcular
if st.button("Calcular longitud"):
    if d_ext > 0 and d_int >= 0 and espesor > 0:
        perimetro_medio = math.pi * (d_ext + d_int) / 2
        longitud = perimetro_medio * espesor
        st.success(f"La longitud aproximada del canto es: {longitud:.2f} mm")
    else:
        st.error("Por favor ingresa valores válidos mayores que cero para todos los campos.")
