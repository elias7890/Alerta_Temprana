import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
import pandas as pd


def mostrar(df):
    st.title("Análisis por Colegio")

    # Aseguramos que la columna sea numérica
    df['Cantidad de veces Reprobadas'] = pd.to_numeric(df['Cantidad de veces Reprobadas'], errors='coerce')
    df['Asignaturas Aprobadas'] = pd.to_numeric(df['Asignaturas Aprobadas'], errors='coerce')

    # Agrupaciones
    reprobacion_por_colegio = df.groupby('Colegio de Origen')['Cantidad de veces Reprobadas'].sum() / df.groupby('Colegio de Origen')['RUT'].count()
    rendimiento_por_colegio = df.groupby('Colegio de Origen')['Asignaturas Aprobadas'].mean()

    st.subheader("📚 Tasa de Reprobación por Colegio de Origen")
    st.dataframe(reprobacion_por_colegio.reset_index().rename(columns={0: 'Tasa de Reprobación'}).sort_values('Tasa de Reprobación', ascending=False))

    st.subheader("🎓 Rendimiento Académico por Colegio de Origen")
    st.dataframe(rendimiento_por_colegio.reset_index().rename(columns={'Asignaturas Aprobadas': 'Promedio Aprobaciones'}).sort_values('Promedio Aprobaciones', ascending=False))


    st.subheader("Gráfico de Tasa de Reprobación por Colegio")
    fig, ax = plt.subplots(figsize=(10,5))
    reprobacion_por_colegio.sort_values(ascending=False).plot(kind='bar', ax=ax, color='red')
    ax.set_ylabel('Tasa de Reprobación')
    st.pyplot(fig)

    st.subheader("Gráfico de Rendimiento Académico por Colegio")
    fig2, ax2 = plt.subplots(figsize=(10,5))
    rendimiento_por_colegio.sort_values(ascending=False).plot(kind='bar', ax=ax2, color='green')
    ax2.set_ylabel('Promedio Aprobaciones')
    st.pyplot(fig2)

    st.subheader("🏆 Top 5 Colegios con Mejor Rendimiento Académico")

    top5_rendimiento = rendimiento_por_colegio.reset_index().rename(columns={'Asignaturas Aprobadas': 'Promedio Aprobaciones'})
    top5_rendimiento = top5_rendimiento.sort_values('Promedio Aprobaciones', ascending=False).head(5)

    st.dataframe(top5_rendimiento)

    st.subheader("⚠️ Top 5 Colegios con Mayor Tasa de Reprobación")

    top5_reprobacion = reprobacion_por_colegio.reset_index().rename(columns={0: 'Tasa de Reprobación'})
    top5_reprobacion = top5_reprobacion.sort_values('Tasa de Reprobación', ascending=False).head(5)

    # Opcional: mostrar como porcentaje
    top5_reprobacion['Tasa de Reprobación'] = (top5_reprobacion['Tasa de Reprobación'] * 100).round(2).astype(str) + '%'

    st.dataframe(top5_reprobacion)