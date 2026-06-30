import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página (Debe ser lo primero)
st.set_page_config(page_title="Dashboard de Citas Médicas", layout="wide")

# Cargar datos y asegurar formato de fecha
@st.cache_data # Optimiza la carga para que vaya súper rápido
def load_data():
    df = pd.read_csv('citas_medicas.csv')
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.month
    return df

df = load_data()

# --- TÍTULO PRINCIPAL ---
st.title('📊 Dashboard de Gestión de Citas Médicas')
st.markdown("Filtra la información usando la barra lateral para analizar los datos en tiempo real.")
st.write("---")

# --- 2. BARRA LATERAL INTERACTIVA (FILTROS) ---
st.sidebar.header("🎯 Filtros Disponibles")

# Filtro de Especialidad
todas_especialidades = ["Todas"] + sorted(df['especialidad'].dropna().unique().tolist())
especialidad_seleccionada = st.sidebar.selectbox("Selecciona Especialidad:", todas_especialidades)

# Filtro de Estado de Cita
todos_estados = ["Todos"] + sorted(df['estado'].dropna().unique().tolist())
estado_seleccionado = st.sidebar.selectbox("Selecciona Estado de la Cita:", todos_estados)

# --- 3. APLICAR FILTROS DINÁMICOS AL DATAFRAME ---
df_filtrado = df.copy()

if especialidad_seleccionada != "Todas":
    # Aquí es donde faltaba la 'e' al principio de 'especialidad'
    df_filtrado = df_filtrado[df_filtrado['especialidad'] == especialidad_seleccionada]

if estado_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['estado'] == estado_seleccionado]
    
# --- 4. SECCIÓN DE MÉTRICAS RÁPIDAS ---
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Total Citas Filtradas", f"{len(df_filtrado):,}")
with col_m2:
    atendidas = len(df_filtrado[df_filtrado['estado'] == 'Atendida'])
    st.metric("Citas Atendidas", f"{atendidas:,}")
with col_m3:
    porcentaje = (atendidas / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
    st.metric("Tasa de Asistencia", f"{porcentaje:.1f}%")

st.write("---")


# --- 5. GRÁFICOS EN PARALELO (DISTRIBUCIÓN EN COLUMNAS) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader('🩺 Volumen por Especialidad')
    datos_especialidad = df_filtrado['especialidad'].value_counts().reset_index()
    datos_especialidad.columns = ['Especialidad', 'Cantidad']
    
    fig1 = px.bar(
        datos_especialidad,
        x='Especialidad',
        y='Cantidad',
        color='Cantidad',
        color_continuous_scale='Blues',
        text_auto=True
    )
    fig1.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader('📌 Distribución de Estados')
    fig2 = px.pie(
        df_filtrado,
        names='estado',
        hole=0.4, # Lo convierte en un gráfico de dona moderno
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig2.update_traces(textinfo='percent+label')
    st.plotly_chart(fig2, use_container_width=True)


# --- 6. GRÁFICO DE TENDENCIA TEMPORAL ---
st.write("---")
st.subheader('📈 Tendencia de Citas por Mes')

citas_mes = df_filtrado.groupby('mes').size().reset_index(name='Cantidad')

# Diccionario para mostrar nombres de meses en vez de números
meses_dic = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
citas_mes['Mes_Nombre'] = citas_mes['mes'].map(meses_dic)

fig3 = px.line(
    citas_mes,
    x='Mes_Nombre',
    y='Cantidad',
    markers=True,
    text='Cantidad',
    labels={'Mes_Nombre': 'Mes'},
    color_discrete_sequence=['#1f77b4']
)
fig3.update_traces(textposition="top center")
fig3.update_layout(yaxis_title="Número de Citas")
st.plotly_chart(fig3, use_container_width=True)
