import streamlit as st
import plotly.express as px

def mostrar(df):
    st.header("Análisis por vía de ingreso")
    via = st.selectbox('Selecciona la vía de ingreso', df['Via de Ingreso'].unique())

    df_filtrado = df[df['Via de Ingreso'] == via]
    df_carreras = df_filtrado['Texto Plan Estudio'].value_counts().reset_index()
    df_carreras.columns = ['Carrera', 'Cantidad']

    fig = px.bar(df_carreras, x='Carrera', y='Cantidad',
                 title=f"Carreras por vía de ingreso: {via}",
                 color='Cantidad', color_continuous_scale='Blues')
    fig.update_layout(xaxis_tickangle=-45, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📄 Ver tabla de estudiantes por vía seleccionada"):
        st.dataframe(df_filtrado, use_container_width=True)
