import streamlit as st
import pandas as pd
import plotly.express as px

def mostrar(df):
    st.header("🏫 Análisis de Puntajes de Ingreso por Colegio (Estudiantes PACE)")

    df_pace = df[df['Via de Ingreso'] == 'PACE'].copy()

    columnas_puntajes = [
        'Puntaje_pond', 'P.MATEMATICAS', 'P.Lecto-Leng',
        'P.Historia', 'P.Ciencias', 'Puntaje NEM', 'Ranking'
    ]

    # Validar columna de colegio
    if 'Colegio de Origen' not in df_pace.columns:
        st.warning("No se encontró la columna 'Colegio de Origen'.")
        return

    # Limpiar y convertir datos
    reemplazos_invalidos = ['Sin Datos', 'No Rendida', 'No rindio', 'No riindio']
    for col in columnas_puntajes:
        if col in df_pace.columns:
            df_pace[col] = df_pace[col].astype(str).replace(reemplazos_invalidos, None)
            df_pace[col] = df_pace[col].str.replace(",", ".")
            df_pace[col] = pd.to_numeric(df_pace[col], errors='coerce')

    # Filtrar colegios con nombre
    df_pace = df_pace[df_pace['Colegio de Origen'].notna() & (df_pace['Colegio de Origen'] != '')]

    if df_pace.empty:
        st.info("No hay datos suficientes para mostrar.")
        return

    # Ranking general por puntaje ponderado
    st.subheader("🏆 Top Colegios por Puntaje Ponderado Promedio")
    ranking = df_pace.groupby('Colegio de Origen')['Puntaje_pond'].mean().reset_index()
    ranking.columns = ['Colegio', 'Puntaje Promedio']
    ranking = ranking.sort_values(by='Puntaje Promedio', ascending=False)

    fig1 = px.bar(ranking.head(10), x='Colegio', y='Puntaje Promedio',
                  title='Top 10 Colegios - Puntaje Ponderado Promedio',
                  color='Puntaje Promedio', color_continuous_scale='Plasma')
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico de los 10 colegios con peor puntaje ponderado
    st.subheader("📉 Colegios con Puntajes Más Bajos")
    # Filtrar colegios con puntaje no nulo
    ranking_bajos = ranking.dropna(subset=['Puntaje Promedio'])

    # Asegurarme de que tengamos al menos 10 colegios para mostrar
    if len(ranking_bajos) > 10:
        ranking_bajos = ranking_bajos.tail(10)
    else:
        ranking_bajos = ranking_bajos.head(10)  # Si hay menos de 10, mostrar los disponibles

    fig2 = px.bar(ranking_bajos, x='Colegio', y='Puntaje Promedio',
                title='10 Colegios con Puntaje Ponderado Más Bajo',
                color='Puntaje Promedio', color_continuous_scale='reds')
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)


    # Mejores colegios por cada tipo de prueba
    st.subheader("🥇 Mejores Colegios por Tipo de Puntaje")
    for col in columnas_puntajes:
        if col in df_pace.columns:
            top = df_pace.groupby('Colegio de Origen')[col].mean().reset_index()
            top = top.sort_values(by=col, ascending=False).head(5)
            fig = px.bar(top, x='Colegio de Origen', y=col,
                         title=f'Top 5 Colegios - {col}', color=col, color_continuous_scale='viridis')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
