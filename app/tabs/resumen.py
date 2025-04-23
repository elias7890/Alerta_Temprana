import streamlit as st
import plotly.express as px

def mostrar(df):
    st.header("Resumen general")
    st.markdown("Análisis de distribución por carrera y ciudad de origen.")

    df_carreras = df['Texto Plan Estudio'].value_counts().reset_index()
    df_carreras.columns = ['Carrera', 'Cantidad']
    fig1 = px.bar(df_carreras, x='Carrera', y='Cantidad', title="Estudiantes por carrera",
                  color='Cantidad', color_continuous_scale='Tealgrn')
    fig1.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig1, use_container_width=True)

    df_ciudad = df['Ciudad'].value_counts().reset_index()
    df_ciudad.columns = ['Ciudad', 'Cantidad']
    fig2 = px.pie(df_ciudad, names='Ciudad', values='Cantidad', title='Ciudad de origen',
                  color_discrete_sequence=px.colors.sequential.RdBu)
    fig2.update_layout(title_x=0.5)
    st.plotly_chart(fig2, use_container_width=True)
