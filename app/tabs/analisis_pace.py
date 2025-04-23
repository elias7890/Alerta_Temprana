import streamlit as st
import pandas as pd
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io

def generar_pdf(df_reprobaciones, carrera_seleccionada, año_seleccionado):
    # Crear un buffer en memoria
    buffer = io.BytesIO()
    
    # Crear el objeto PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Establecer fuentes
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, 750, f"Informe de Reprobaciones - Vía PACE")
    
    # Agregar filtros seleccionados
    c.setFont("Helvetica", 12)
    c.drawString(30, 730, f"Carrera seleccionada: {carrera_seleccionada}")
    c.drawString(30, 710, f"Año de Ingreso: {año_seleccionado}")
    
    # Texto de introducción
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(30, 690, "Este informe presenta el análisis de las reprobaciones de estudiantes vía PACE.")
    
    # Linea divisoria
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(30, 680, 580, 680)
    
    # Título de la tabla
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, 660, "Resumen de Reprobaciones por Año de Ingreso:")
    
    # Agregar la tabla con los datos de reprobaciones
    c.setFont("Helvetica", 10)
    
    # Encabezado de la tabla
    c.drawString(30, 640, "Año de Ingreso")
    c.drawString(150, 640, "Prom. Reprobaciones")
    c.drawString(300, 640, "Total Reprobaciones")
    c.drawString(450, 640, "Cantidad de Estudiantes")
    
    # Dibujar filas con los datos
    y_position = 620
    for index, row in df_reprobaciones.iterrows():
        c.drawString(30, y_position, str(row['Año de Ingreso']))
        c.drawString(150, y_position, f"{row['Promedio Reprobaciones']:.2f}")
        c.drawString(300, y_position, str(row['Total Reprobaciones']))
        c.drawString(450, y_position, str(row['Cantidad de Estudiantes']))
        y_position -= 20
    
    # Agregar gráfico si es necesario (por ejemplo, podrías incluir imágenes de gráficos generados previamente)
    # Aquí simplemente hacemos un espacio para mencionar que podría haber gráficos.
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(30, y_position, "Nota: Los gráficos generados pueden ser insertados aquí si es necesario.")
    
    # Finalizar y guardar el PDF
    c.showPage()
    c.save()
    
    # Mover el buffer al inicio para poder leerlo
    buffer.seek(0)
    
    return buffer

def mostrar(df):
    st.markdown("## 📈 Análisis de Reprobaciones - Vía PACE")
    st.markdown("Filtra por carrera y año para visualizar el desempeño de estudiantes que ingresaron por la vía PACE.")

    # 🔍 Filtrar estudiantes PACE
    df_pace = df[df['Via de Ingreso'].str.upper() == 'PACE']

    if df_pace.empty:
        st.warning("No se encontraron estudiantes con vía de ingreso PACE.")
        return

    # Normalizar las columnas para evitar problemas con mayúsculas/minúsculas y espacios
    df_pace['Texto Plan Estudio'] = df_pace['Texto Plan Estudio'].str.strip().str.upper()
    df_pace['AÑO'] = df_pace['AÑO'].astype(str).str.strip()

    # 📌 Opciones únicas
    carreras = sorted(df_pace['Texto Plan Estudio'].dropna().unique())
    años = sorted(df_pace['AÑO'].dropna().unique())

    # 🎯 Filtros
    col1, col2 = st.columns(2)
    with col1:
        carrera_seleccionada = st.selectbox("🎓 Selecciona una carrera:", ["Todas"] + list(carreras))
    with col2:
        año_seleccionado = st.selectbox("📅 Selecciona un año de ingreso:", ["Todos"] + list(años))

    # Aplicar filtros
    if carrera_seleccionada != "Todas":
        df_pace = df_pace[df_pace['Texto Plan Estudio'] == carrera_seleccionada]

    if año_seleccionado != "Todos":
        df_pace = df_pace[df_pace['AÑO'] == año_seleccionado]

    if df_pace.empty:
        st.info("No hay datos que coincidan con los filtros seleccionados.")
        return

    # Asegurarse de que las columnas numéricas sean correctamente interpretadas
    df_pace['Cantidad de veces Reprobadas'] = pd.to_numeric(df_pace['Cantidad de veces Reprobadas'], errors='coerce')

    # Agrupar por Año de Ingreso
    df_reprobaciones = df_pace.groupby('AÑO').agg({
        'Cantidad de veces Reprobadas': ['mean', 'sum', 'count']
    }).reset_index()

    # Renombrar columnas
    df_reprobaciones.columns = ['Año de Ingreso', 'Promedio Reprobaciones', 'Total Reprobaciones', 'Cantidad de Estudiantes']

    # Mostrar tabla resumen
    with st.expander("📋 Ver tabla resumen"):
        st.dataframe(df_reprobaciones, use_container_width=True)

    # 🎨 Gráficos separados

    # Gráfico para Promedio de Reprobaciones
    if not df_reprobaciones.empty:
        fig_promedio = px.bar(
            df_reprobaciones,
            x='Año de Ingreso',
            y='Promedio Reprobaciones',
            text='Promedio Reprobaciones',
            color='Promedio Reprobaciones',
            color_continuous_scale='Reds',
            title='Promedio de Reprobaciones por Año - Estudiantes Vía PACE'
        )
        fig_promedio.update_layout(
            xaxis_title='Año de Ingreso',
            yaxis_title='Promedio de Reprobaciones',
            template='plotly_white',
            title_x=0.5
        )
        st.plotly_chart(fig_promedio, use_container_width=True)

    # Gráfico para Total de Reprobaciones
    if not df_reprobaciones.empty:
        fig_total = px.bar(
            df_reprobaciones,
            x='Año de Ingreso',
            y='Total Reprobaciones',
            text='Total Reprobaciones',
            color='Total Reprobaciones',
            color_continuous_scale='Blues',
            title='Total de Reprobaciones por Año - Estudiantes Vía PACE'
        )
        fig_total.update_layout(
            xaxis_title='Año de Ingreso',
            yaxis_title='Total de Reprobaciones',
            template='plotly_white',
            title_x=0.5
        )
        st.plotly_chart(fig_total, use_container_width=True)

    # Gráfico para Cantidad de Estudiantes
    if not df_reprobaciones.empty:
        fig_cantidad = px.bar(
            df_reprobaciones,
            x='Año de Ingreso',
            y='Cantidad de Estudiantes',
            text='Cantidad de Estudiantes',
            color='Cantidad de Estudiantes',
            color_continuous_scale='Greens',
            title='Cantidad de Estudiantes por Año - Estudiantes Vía PACE'
        )
        fig_cantidad.update_layout(
            xaxis_title='Año de Ingreso',
            yaxis_title='Cantidad de Estudiantes',
            template='plotly_white',
            title_x=0.5
        )
        st.plotly_chart(fig_cantidad, use_container_width=True)

    # Botón para descargar el informe en PDF
    if st.button("📥 Descargar Informe PDF"):
        pdf_buffer = generar_pdf(df_reprobaciones, carrera_seleccionada, año_seleccionado)
        st.download_button(
            label="Descargar Informe PDF",
            data=pdf_buffer,
            file_name="informe_reprobaciones_via_pace.pdf",
            mime="application/pdf"
        )
