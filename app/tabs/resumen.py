import streamlit as st
import plotly.express as px
import pandas as pd

def mostrar(df):
    st.header("Resumen general")
    st.markdown("Análisis de distribución por carrera.")

    # 1️⃣ Agregamos columna de Riesgo
    def calcular_riesgo(row):
        if row['Cantidad de veces Reprobadas'] >= 3:
            return 'Alto Riesgo'
        elif row['Cantidad de veces Reprobadas'] == 2:
            return 'Medio Riesgo'
        else:
            return 'Bajo Riesgo'

    # Aseguramos que la columna 'Cantidad de veces Reprobadas' sea numérica
    df['Cantidad de veces Reprobadas'] = pd.to_numeric(df['Cantidad de veces Reprobadas'], errors='coerce')
    df['Riesgo'] = df.apply(calcular_riesgo, axis=1)

    # Filtrar los estudiantes cuyo 'Vía de Ingreso' es PACE
    df_pace = df[df['Via de Ingreso'] == 'PACE']

    # 2️⃣ Estudiantes por Carrera
    df_carreras = df_pace['Texto Plan Estudio'].value_counts().reset_index()
    df_carreras.columns = ['Carrera', 'Cantidad']
    fig1 = px.bar(df_carreras, x='Carrera', y='Cantidad', title="Estudiantes por carrera",
                color='Cantidad', color_continuous_scale='Tealgrn')
    fig1.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig1, use_container_width=True)

    # # 3️⃣ Estudiantes por Ciudad de Origen
    # df_ciudad = df_pace['Ciudad'].value_counts().reset_index()
    # df_ciudad.columns = ['Ciudad', 'Cantidad']
    # fig2 = px.pie(df_ciudad, names='Ciudad', values='Cantidad', title='Ciudad de origen',
    #             color_discrete_sequence=px.colors.sequential.RdBu)

    # # Ajustes para eliminar las líneas fuera del gráfico
    # fig2.update_traces(textinfo='label+value', pull=[0.1, 0.1, 0.1], showlegend=False, 
    #                 marker=dict(line=dict(width=0)))

    # # Eliminar las líneas de leyenda fuera del gráfico
    # fig2.update_layout(title_x=0.5)

    # # Mostrar el gráfico
    # st.plotly_chart(fig2, use_container_width=True)



    # # 4️⃣ Distribución por Nivel de Riesgo
    # df_riesgo = df['Riesgo'].value_counts().reset_index()
    # df_riesgo.columns = ['Nivel de Riesgo', 'Cantidad']
    # fig3 = px.pie(df_riesgo, names='Nivel de Riesgo', values='Cantidad',
    #               title='Distribución de Estudiantes por Nivel de Riesgo',
    #               color_discrete_sequence=['red', 'orange', 'green'])
    # fig3.update_layout(title_x=0.5)
    # st.plotly_chart(fig3, use_container_width=True)

    # 5️⃣ Top 10 Estudiantes en Mayor Riesgo de Deserción
    st.subheader("🚨 Top 10 Estudiantes en Mayor Riesgo de Deserción")

    # Filtro para el año
    anio_seleccionado = st.selectbox("Selecciona el Año", options=df['AÑO'].unique())

    # Filtramos los estudiantes con alto riesgo, que hayan repetido más de un ramo, y por el año seleccionado
    top_estudiantes = df[(df['Riesgo'] == 'Alto Riesgo') & 
                        (df['Ramo Repetido mas de una vez'].notna()) & 
                        (df['AÑO'] == anio_seleccionado)]

    # Ordenamos los resultados por cantidad de veces reprobadas y seleccionamos los 10 primeros
    top_estudiantes = top_estudiantes.sort_values('Cantidad de veces Reprobadas', ascending=False).head(10)

    # Mostramos los resultados
    st.dataframe(top_estudiantes[['RUT', 'NOMBRE COMPLETO', 'Texto Plan Estudio', 
                                'Cantidad de veces Reprobadas', 'Riesgo', 'Ramo Repetido mas de una vez']])


   
