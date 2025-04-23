import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter

def mostrar(df):
    carreras_disponibles = df['Texto Plan Estudio'].dropna().unique()
    carrera_seleccionada = st.selectbox("Selecciona una carrera", sorted(carreras_disponibles))

    # Filtrar datos según la carrera seleccionada
    df_filtrado = df[df['Texto Plan Estudio'].str.contains(carrera_seleccionada, case=False)]

    
    # Gráfico de distribución de años cursados
    anio_counts = df_filtrado['Año cursado actual'].value_counts().sort_index()
    st.bar_chart(anio_counts)

    # Promedio de asignaturas aprobadas
    df_filtrado['Asignaturas Aprobadas'] = pd.to_numeric(df_filtrado['Asignaturas Aprobadas'], errors='coerce')
    prom_aprobadas = df_filtrado['Asignaturas Aprobadas'].mean()
    st.metric("📘 Promedio de asignaturas aprobadas", f"{prom_aprobadas:.1f}")
    
    # Calcular la cantidad de asignaturas reprobadas, excluyendo "Sin Ramos Reprobados"
    df_filtrado['Cantidad Reprobadas Estimada'] = df_filtrado['Asignatura Reprobada'].fillna('').apply(
        lambda x: len([s for s in str(x).split('/') if s.strip() and s != 'Sin Ramos Reprobados'])
    )
    
    # Calcular los ramos más reprobados, excluyendo "Sin Ramos Reprobados" y "Sin Datos"
    asignaturas_reprobadas = df_filtrado['Asignatura Reprobada'].dropna().apply(
    lambda x: [s.strip() for s in str(x).split('/') if s.strip() and s.strip().lower() not in ['sin ramos reprobados', 'sin datos']]
    )

    # Aplanar la lista y contar las ocurrencias
    flat_list = [item for sublist in asignaturas_reprobadas for item in sublist]
    conteo = Counter(flat_list)

    # Crear el DataFrame de las asignaturas más reprobadas
    df_top_reprobadas = pd.DataFrame(conteo.items(), columns=['Asignatura', 'Cantidad']).sort_values(by='Cantidad', ascending=False)

    # 🔴 FILTRAR "Sin Datos"
    df_top_reprobadas = df_top_reprobadas[
    ~df_top_reprobadas['Asignatura'].str.strip().str.lower().isin(['sin datos', 'sin ramos reprobados'])
    ]
    
    # Mostrar las 10 asignaturas más reprobadas
    st.markdown("### 🔝 Top 10 asignaturas más reprobadas")
    st.dataframe(df_top_reprobadas.head(10))

    # Gráfico de barras de las asignaturas más reprobadas
    top_10 = df_top_reprobadas.head(10)
    plt.figure(figsize=(10, 6))
    plt.barh(top_10['Asignatura'], top_10['Cantidad'], color='skyblue')
    plt.xlabel('Cantidad de Reprobaciones')
    plt.title(f'Top 10 Asignaturas Más Reprobadas - {carrera_seleccionada}')
    plt.gca().invert_yaxis()
    st.pyplot(plt)

    # 📉 Probabilidad de reprobación por asignatura (Top 10)
    st.markdown("### 📉 Probabilidad de Reprobación por Asignatura (Top 10)")

    # Asegurarse que esté en formato numérico
    df_filtrado_validas = df_filtrado[['Asignatura Reprobada', 'Cantidad de veces Reprobadas']].dropna()
    df_filtrado_validas['Cantidad de veces Reprobadas'] = pd.to_numeric(df_filtrado_validas['Cantidad de veces Reprobadas'], errors='coerce')

    # Separar asignaturas por "/" y limpiar
    df_filtrado_validas = df_filtrado_validas.assign(
        Asignatura=df_filtrado_validas['Asignatura Reprobada'].str.split('/')
    ).explode('Asignatura')
    df_filtrado_validas['Asignatura'] = df_filtrado_validas['Asignatura'].str.strip().str.lower()

    # Filtrar asignaturas válidas
    df_filtrado_validas = df_filtrado_validas[
        ~df_filtrado_validas['Asignatura'].isin(['sin datos', 'sin ramos reprobados'])
    ]

    # Agrupar por asignatura y sumar reprobaciones
    df_probabilidad = df_filtrado_validas.groupby('Asignatura')['Cantidad de veces Reprobadas'].sum().reset_index()
    df_probabilidad.columns = ['Asignatura', 'Total Reprobaciones']
    total_estudiantes_filtrados = len(df_filtrado)
    df_probabilidad['Probabilidad (%)'] = (df_probabilidad['Total Reprobaciones'] / total_estudiantes_filtrados) * 100

    # Top 10
    df_prob_top10 = df_probabilidad.sort_values(by='Probabilidad (%)', ascending=False).head(10)

    # Mostrar en gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df_prob_top10['Asignatura'], df_prob_top10['Probabilidad (%)'], color='salmon')
    ax.set_xlabel('Probabilidad de Reprobación (%)')
    ax.set_title(f'Probabilidad Estimada de Reprobación - {carrera_seleccionada}')
    ax.invert_yaxis()
    st.pyplot(fig)

    # 📍 Análisis según ciudad de origen: ¿Los de fuera de Talca reprueban más?
    st.markdown("### 🏘️ Reprobación según ciudad de origen (Talca vs otras)")

    # Asegurarse de que la columna Ciudad no tenga NaNs
    df_filtrado['Ciudad'] = df_filtrado['Ciudad'].fillna('').str.lower()

    # Clasificar si es de Talca o no
    df_filtrado['Es de Talca'] = df_filtrado['Ciudad'].apply(lambda x: 'Talca' if 'talca' in x else 'Otra ciudad')

    # Asegurar datos numéricos
    df_filtrado['Cantidad de veces Reprobadas'] = pd.to_numeric(df_filtrado['Cantidad de veces Reprobadas'], errors='coerce')

    # Agrupar y calcular promedio de reprobaciones
    resumen_ciudad = df_filtrado.groupby('Es de Talca')['Cantidad de veces Reprobadas'].mean().reset_index()
    resumen_ciudad.columns = ['Origen', 'Promedio de Reprobaciones']

    # Mostrar tabla
    st.dataframe(resumen_ciudad)

    # Gráfico de barras
    fig_ciudad, ax_ciudad = plt.subplots(figsize=(6, 4))
    ax_ciudad.bar(resumen_ciudad['Origen'], resumen_ciudad['Promedio de Reprobaciones'], color=['mediumseagreen', 'tomato'])
    ax_ciudad.set_title(f'Promedio de Reprobaciones por Origen - {carrera_seleccionada}')
    ax_ciudad.set_ylabel('Promedio de veces reprobadas')
    st.pyplot(fig_ciudad)
    
    # Agregar la métrica comparativa
    talca_reprobadas = resumen_ciudad[resumen_ciudad['Origen'] == 'Talca']['Promedio de Reprobaciones'].values[0]
    otra_ciudad_reprobadas = resumen_ciudad[resumen_ciudad['Origen'] == 'Otra ciudad']['Promedio de Reprobaciones'].values[0]

    if otra_ciudad_reprobadas > talca_reprobadas:
        st.metric(label="Reprobaciones de estudiantes de otras ciudades en talca", value=f"{otra_ciudad_reprobadas:.1f}", delta=f"+{otra_ciudad_reprobadas - talca_reprobadas:.1f}")
    else:
        st.metric(label="Reprobaciones en Talca", value=f"{talca_reprobadas:.1f}", delta=f"+{talca_reprobadas - otra_ciudad_reprobadas:.1f}")
