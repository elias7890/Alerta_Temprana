import pandas as pd
import streamlit as st

@st.cache_data
def cargar_datos():
    df = pd.read_excel('data/DatosUCM.xlsx', header=0, dtype=str)
    df['RUT'] = df['RUT'].astype(str)
    return df
