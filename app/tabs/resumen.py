import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Calcular índice de riesgo
def calcular_indice_riesgo(row):
    try:
        reprobadas = float(row.get('Cantidad de veces Reprobadas', 0)) or 0
    except:
        reprobadas = 0

    try:
        ramos_repetidos = float(row.get('Ramo Repetido mas de una vez', 0)) or 0
    except:
        ramos_repetidos = 0

    try:
        anio_ingreso = int(row.get('AÑO', 0))
        anio_actual = datetime.now().year
        años_cursados = int(row.get('Año cursado actual', 0))
        desfase = (anio_actual - anio_ingreso) - años_cursados
        desfase = max(0, desfase)
    except:
        desfase = 0

    riesgo = 0
    riesgo += reprobadas * 1.5
    riesgo += ramos_repetidos * 3
    riesgo += desfase * 2

    if riesgo < 5:
        nivel_riesgo = "🟢 Bajo"
        color_riesgo = "green"
    elif riesgo < 10:
        nivel_riesgo = "🟡 Medio"
        color_riesgo = "orange"
    else:
        nivel_riesgo = "🔴 Alto"
        color_riesgo = "red"

    return pd.Series([nivel_riesgo, color_riesgo, riesgo])

# Mostrar la información en Streamlit
def mostrar(df):
    st.title("📊 Resumen General de Estudiantes")

    # Asegurar tipo de dato correcto en columna 'AÑO'
    df['AÑO'] = pd.to_numeric(df['AÑO'], errors='coerce')
    df = df.dropna(subset=['AÑO'])
    df['AÑO'] = df['AÑO'].astype(int)

    # Aplicar índice de riesgo
    df[['Nivel Riesgo', 'Color Riesgo', 'Índice de Riesgo']] = df.apply(calcular_indice_riesgo, axis=1)

    # Filtrar por año de ingreso
    anios_disponibles = sorted(df['AÑO'].unique())
    anio_seleccionado = st.selectbox("📅 Filtrar por año de ingreso", anios_disponibles)

    df_ano = df[df['AÑO'] == anio_seleccionado].copy()

    # Filtrar por "Vía de Ingreso" (Solo estudiantes PACE)
    df_ano = df_ano[df_ano['Via de Ingreso'] == 'PACE']

    # Recuadros de resumen (filtrados)
    total_alto = df_ano[df_ano['Nivel Riesgo'].str.contains("Alto")].shape[0]
    total_medio = df_ano[df_ano['Nivel Riesgo'].str.contains("Medio")].shape[0]
    total_bajo = df_ano[df_ano['Nivel Riesgo'].str.contains("Bajo")].shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 Alto Riesgo", total_alto)
    col2.metric("🟡 Riesgo Medio", total_medio)
    col3.metric("🟢 Bajo Riesgo", total_bajo)

    # Orden personalizado para riesgo
    nivel_riesgo_orden = {
        "🔴 Alto": 0,
        "🟡 Medio": 1,
        "🟢 Bajo": 2
    }
    df_ano['orden'] = df_ano['Nivel Riesgo'].map(nivel_riesgo_orden)
    df_ano = df_ano.sort_values(by=['orden', 'Índice de Riesgo'], ascending=[True, False])

    # Mostrar tabla usando pandas

    st.markdown("### 📋 Detalle de Estudiantes Filtrados")
    columnas_a_mostrar = ['RUT', 'NOMBRE COMPLETO', 'AÑO', 'Via de Ingreso', 'Texto Plan Estudio', 'Nivel Riesgo']
    st.dataframe(df_ano[columnas_a_mostrar])
    #st.dataframe(df_ano.drop(columns=['orden']))

    st.markdown("### 📥 Descargar datos por nivel de riesgo")

    # Filtrar por nivel de riesgo
    alto_riesgo_df = df_ano[df_ano['Nivel Riesgo'] == '🔴 Alto']
    medio_riesgo_df = df_ano[df_ano['Nivel Riesgo'] == '🟡 Medio']
    bajo_riesgo_df = df_ano[df_ano['Nivel Riesgo'] == '🟢 Bajo']

    def generar_excel_download(df, nombre):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Estudiantes')
        st.download_button(
            label=f"📥 Descargar {nombre}",
            data=output.getvalue(),
            file_name=f"{nombre.lower().replace(' ', '_')}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    # Botones para descarga
    generar_excel_download(alto_riesgo_df, "Alto Riesgo")
    generar_excel_download(medio_riesgo_df, "Riesgo Medio")
    generar_excel_download(bajo_riesgo_df, "Bajo Riesgo")
