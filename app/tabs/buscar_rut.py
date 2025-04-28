import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors


def mostrar(df):
    st.header("🔎 Buscar estudiante por RUT (sin digito verificador)")
    rut_input = st.text_input("Ingresa el RUT del estudiante", placeholder="Ej: 12448987")

    if rut_input:
        rut_input = rut_input.strip()
        df_rut = df[df['RUT'] == rut_input]

        if not df_rut.empty:
            st.success("✅ Estudiante encontrado:")
            st.dataframe(df_rut, use_container_width=True)

            st.markdown("## 🧾 Resumen del Estudiante")
            with st.container():
                st.markdown(
                    """
                    <style>
                    .resumen-box {
                        background-color: #ffffff0a; /* semi-transparente compatible con modo oscuro */
                        border-radius: 12px;
                        padding: 20px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                        font-size: 16px;
                        color: #f0f0f0; /* texto claro para modo oscuro */
                    }
                    .resumen-box p {
                        margin: 6px 0;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    <div class="resumen-box">
                    <p><strong>👤 Nombre:</strong> {df_rut.iloc[0]['NOMBRE COMPLETO']}</p>
                    <p><strong>🎓 Carrera:</strong> {df_rut.iloc[0]['Texto Plan Estudio']}</p>
                    <p><strong>📅 Año de Ingreso:</strong> {df_rut.iloc[0]['AÑO']}</p>
                    <p><strong>🏡 Ciudad de Origen:</strong> {df_rut.iloc[0]['Ciudad']}</p>
                    <p><strong>🚪 Vía de Ingreso:</strong> {df_rut.iloc[0]['Via de Ingreso']}</p>
                    <p><strong>📚 Colegio de Origen:</strong> {df_rut.iloc[0]['Colegio de Origen']}</p>
                    <p><strong>📚 Año Actual Cursado:</strong> {df_rut.iloc[0]['Año cursado actual']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="resumen-box">
                    <p><strong>📌 Estado:</strong> {df_rut.iloc[0]['Estado']}</p>
                    <p><strong>❌ Asignatura Reprobada:</strong> {df_rut.iloc[0]['Asignatura Reprobada']}</p>
                    <p><strong>🔁 Veces Reprobadas:</strong> {df_rut.iloc[0]['Cantidad de veces Reprobadas']}</p>
                    <p><strong>✅ Asignaturas Aprobadas:</strong> {df_rut.iloc[0]['Asignaturas Aprobadas']}</p>
                    <p><strong>🔄 Convalidadas:</strong> {df_rut.iloc[0]['Asignaturas convalidadas']}</p>
                    <p><strong>🔁 Ramos Repetidos más de una vez:</strong> {df_rut.iloc[0]['Ramo Repetido mas de una vez']}</p>
                    </div>
                    """, unsafe_allow_html=True)


             # 🎯 Índice de riesgo
            st.markdown("### ⚠️ Índice de Riesgo del Estudiante")

            try:
                reprobadas = int(df_rut.iloc[0]['Cantidad de veces Reprobadas'])
            except:
                reprobadas = 0

            try:
                ramos_repetidos = int(df_rut.iloc[0]['Ramo Repetido mas de una vez'])
            except:
                ramos_repetidos = 0

            try:
                anio_ingreso = int(df_rut.iloc[0]['AÑO'])
                anio_actual = datetime.now().year
                años_cursados = int(df_rut.iloc[0]['Año cursado actual'])
                desfase = (anio_actual - anio_ingreso) - años_cursados
                desfase = max(0, desfase)  # Asegurar que no sea negativo
            except:
                desfase = 0

            # Asignamos un puntaje por cada factor
            riesgo = 0
            riesgo += reprobadas * 1.5
            riesgo += ramos_repetidos * 3
            riesgo += desfase * 2

            # Clasificación del riesgo
            if riesgo < 5:
                nivel_riesgo = "🟢 Bajo"
                color_riesgo = "green"
            elif riesgo < 10:
                nivel_riesgo = "🟡 Medio"
                color_riesgo = "orange"
            else:
                nivel_riesgo = "🔴 Alto"
                color_riesgo = "red"

            # 🚦 Gauge Chart con Plotly
            titulo_riesgo = f"Índice de Riesgo<br><span style='font-size:20px'>{nivel_riesgo}</span>"

            fig_riesgo = go.Figure(go.Indicator(
                mode="gauge+number",
                value=riesgo,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': titulo_riesgo, 'font': {'size': 24}},
                gauge={
                    'axis': {'range': [0, 30], 'tickwidth': 1, 'tickcolor': "darkgray"},
                    'bar': {'color': color_riesgo},
                    'bgcolor': "white",
                    'steps': [
                        {'range': [0, 5], 'color': '#81C784'},      # Verde
                        {'range': [5, 10], 'color': '#FFD54F'},     # Amarillo
                        {'range': [10, 30], 'color': '#E57373'}     # Rojo
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': riesgo
                    }
                }
            ))

            # Mostrar en Streamlit
            st.plotly_chart(fig_riesgo, use_container_width=True)

            # 🧠 Sugerencias según el nivel de riesgo
            if riesgo < 5:
                sugerencias = "✅ **Buen rendimiento.** Mantener hábitos de estudio y considerar asistir a tutorías opcionales para reforzar lo aprendido."
            elif riesgo < 10:
                sugerencias = "⚠️ **Riesgo moderado.** Revisar sus hábitos de estudio, asiste a tutorías, y conversa con tu profesor guía para planificar tu avance."
            else:
                sugerencias = "🚨 **Riesgo alto.** Se recomienda dar apoyo académico intensivo, asesoría psicológica si es necesario, y apoyo personalizado."

            # Mostrar sugerencias en un expander
            with st.expander("🧠 Sugerencias para ayudar al estudiante"):
                st.markdown(f"**Nivel de Riesgo:** {nivel_riesgo}")
                st.markdown(sugerencias)

            

        

            # 🎯 Análisis de avance
            try:
                total_asignaturas = int(df_rut.iloc[0]['Asignaturas totales de la carrera'])
            except:
                total_asignaturas = 50  # Valor por defecto si no hay datos válidos

            try:
                aprobadas = int(df_rut.iloc[0]['Asignaturas Aprobadas'])
            except:
                aprobadas = 0  # Fallback si hay error de tipo

            faltantes = total_asignaturas - aprobadas
            porcentaje_avance = int((aprobadas / total_asignaturas) * 100) if total_asignaturas > 0 else 0

            st.markdown("### 📊 Porcentaje de avance en la carrera")

            # Datos
            labels = ['Aprobadas', 'Faltantes']
            sizes = [aprobadas, faltantes]
            colors = ['#64B5F6', '#FF7043']  
            explode = (0.1, 0)  

            # Pie chart
            fig, ax = plt.subplots(figsize=(2, 2))
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, explode=explode,
                textprops={'fontsize': 14, 'color': 'black'}, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
            ax.axis('equal')  # Asegura que el gráfico sea circular
            ax.set_title('Estado de las Asignaturas', fontsize=10, fontweight='bold', color='#333333')

            # Mostrar el gráfico
            st.pyplot(fig)

            # Barra de progreso mejorada
            st.markdown(f"### 🟩 Avance en la carrera: **{porcentaje_avance}%**")
            st.progress(porcentaje_avance / 100)

            # Obtener los datos del estudiante
            estudiante = df_rut.iloc[0]
            nombre = estudiante['NOMBRE COMPLETO']
            carrera = estudiante['Texto Plan Estudio']
            anio_ingreso = estudiante['AÑO']
            ciudad = estudiante['Ciudad']
            via_ingreso = estudiante['Via de Ingreso']
            anio_actual = estudiante['Año cursado actual']
            estado = estudiante['Estado']
            asig_reprobada = estudiante['Asignatura Reprobada']
            veces_reprobadas = estudiante['Cantidad de veces Reprobadas']
            asig_aprobadas = estudiante['Asignaturas Aprobadas']
            asig_convalidadas = estudiante['Asignaturas convalidadas']
            ramos_repetidos = estudiante['Ramo Repetido mas de una vez']
            porcentaje = f"{porcentaje_avance}%"
            riesgo_str = f"{riesgo} ({nivel_riesgo})"

            # Crear PDF
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=LETTER)
            width, height = LETTER

            # Márgenes
            margin_left = 50
            margin_top = height - 60
            line_height = 15  # Altura de las líneas de texto

            # Encabezado
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawString(margin_left, margin_top, "📚 Informe Académico del Estudiante")
            margin_top -= 30

            # Línea separadora
            pdf.setLineWidth(1)
            pdf.line(margin_left, margin_top, width - margin_left, margin_top)
            margin_top -= 10

            # Datos personales
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(margin_left, margin_top, "👤 Datos Personales")
            margin_top -= 20

            pdf.setFont("Helvetica", 12)
            pdf.drawString(margin_left, margin_top, f"🎓 Carrera: {carrera}")
            margin_top -= line_height
            pdf.drawString(margin_left, margin_top, f"📅 Año de Ingreso: {anio_ingreso}")
            margin_top -= line_height
            pdf.drawString(margin_left, margin_top, f"🏡 Ciudad de Origen: {ciudad}")
            margin_top -= line_height
            pdf.drawString(margin_left, margin_top, f"🚪 Vía de Ingreso: {via_ingreso}")
            margin_top -= line_height
            pdf.drawString(margin_left, margin_top, f"📚 Año Actual Cursado: {anio_actual}")
            margin_top -= line_height
            pdf.drawString(margin_left, margin_top, f"📌 Estado: {estado}")
            margin_top -= 30

            # Información académica
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(margin_left, margin_top, "📘 Información Académica")
            margin_top -= 20

            pdf.setFont("Helvetica", 12)
            pdf.drawString(margin_left, margin_top, f"❌ Asignatura Reprobada: {asig_reprobada}")
            margin_top -= line_height
            pdf.drawString(margin_left, margin_top, f"🔁 Veces Reprobadas: {veces_reprobadas}")
            margin_top -= line_height
            pdf.drawString(margin_left, margin_top, f"✅ Asignaturas Aprobadas: {asig_aprobadas}")
            margin_top -= line_height
            pdf.drawString(margin_left, margin_top, f"🔄 Convalidadas: {asig_convalidadas}")
            margin_top -= line_height
            pdf.drawString(margin_left, margin_top, f"🔁 Ramos Repetidos (+1 vez): {ramos_repetidos}")
            margin_top -= 30

            # Progreso
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(margin_left, margin_top, "📊 Progreso en la Carrera")
            margin_top -= 20

            pdf.setFont("Helvetica", 12)
            pdf.drawString(margin_left, margin_top, f"Avance: {porcentaje}")
            margin_top -= 30

            # Riesgo
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(margin_left, margin_top, "⚠️ Índice de Riesgo Estudiantil")
            margin_top -= 20

            pdf.setFont("Helvetica", 12)
            pdf.drawString(margin_left, margin_top, f"Índice de Riesgo: {riesgo_str}")
            margin_top -= 30

            # Footer
            pdf.setFont("Helvetica-Oblique", 9)
            pdf.drawString(margin_left, 30, f"Generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

            # Guardar PDF
            pdf.save()
            buffer.seek(0)

            # Descargar PDF
            st.download_button(
                label="📄 Descargar PDF del Estudiante",
                data=buffer,
                file_name=f"informe_{nombre.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

          
        else:
            st.warning("⚠️ No se encontró un estudiante con ese RUT.")
