import streamlit as st
from data_loader import cargar_datos
from tabs import resumen, por_via, buscar_rut, por_carrera, analisis_pace, por_colegio
from PIL import Image

st.set_page_config(page_title="Alerta Temprana UCM", layout="centered" )


# Cargar datos una sola vez
df = cargar_datos()

st.title("🎓 Sistema De Alerta Temprana UCM")

# Filtrar por "Vía de Ingreso" (Solo estudiantes PACE)
df_pace = df[df['Via de Ingreso'] == 'PACE']  # Filtramos solo los estudiantes PACE

    # Métrica del total de estudiantes PACE
st.metric("👨‍🎓 Total de estudiantes registrados (PACE)", len(df_pace))

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Resumen General", 
    "🔍 Análisis por Vía de Ingreso", 
    "🔎 Buscar por RUT", 
    "📊 Estadísticas por carrera",
    "📈 Estadísticas PACE",
    "📊 Análisis por colegio"
])

with tab1:
    resumen.mostrar(df)

with tab2:
    por_via.mostrar(df)

with tab3:
    buscar_rut.mostrar(df)

with tab4:
    por_carrera.mostrar(df)

with tab5:
    analisis_pace.mostrar(df)

with tab6:
    por_colegio.mostrar(df)