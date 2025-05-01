
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

DATA_PATH = 'student_evals_30x6_months.csv'
@st.cache_data
def load_data(path=DATA_PATH):
    df = pd.read_csv(path, parse_dates=['created_at'])
    # extrair ano‑mês para facilitar gráficos
    df['year_month'] = df['created_at'].dt.to_period('M').astype(str)
    return df

df = load_data()

st.title('Dashboard • Jornada do Aluno (30 × 6 meses)')

# ==== Sidebar filtros globais ====
st.sidebar.header('Filtros')
months = sorted(df['year_month'].unique())
month_sel = st.sidebar.multiselect('Meses', months, default=months)
alunos = sorted(df['student_id'].unique())
alunos_sel = st.sidebar.multiselect('Alunos', alunos, default=alunos)

filt = df[df['year_month'].isin(month_sel) & df['student_id'].isin(alunos_sel)]

# ==== Tabs ====
aba1, aba2, aba3, aba4 = st.tabs(["Visão Geral", "Heatmap", "Aluno 360º", "Plano de Ação"])

# ---------- 1. VISÃO GERAL ----------
with aba1:
    st.header('Panorama Mensal')
    # % em risco por mês
    risk_month = (
        filt.groupby('year_month')['meta_prediction']
        .mean()
        .reset_index(name='perc_risco')
    )
    risk_month['perc_risco'] *= 100
    line = alt.Chart(risk_month).mark_line(point=True).encode(
        x='year_month', y='perc_risco', tooltip=['year_month','perc_risco']
    ).properties(height=300)
    st.altair_chart(line, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric('Alunos em risco (filtro)', int(filt['meta_prediction'].sum()))
    with col2:
        st.metric('% Risco', f"{filt['meta_prediction'].mean()*100:.1f}%")

# ---------- 2. HEATMAP ----------
with aba2:
    st.header('Persistência de Risco por Aluno')
    # Pivot: linhas = aluno, colunas = mês, valor = meta_prediction
    pivot = filt.pivot_table(index='student_id', columns='year_month', values='meta_prediction', fill_value=0)
    st.dataframe(pivot.style.background_gradient(cmap='RdYlGn_r'))

# ---------- 3. ALUNO 360 ----------
with aba3:
    st.header('Detalhe do Aluno')
    aluno_focus = st.selectbox('Escolha um aluno', alunos)
    df_a = df[df['student_id']==aluno_focus]
    st.subheader('Probabilidade de Engajamento Geral')
    area = alt.Chart(df_a).mark_line(point=True).encode(
        x='year_month', y='proba_indice_engajamento_geral', tooltip=['year_month','proba_indice_engajamento_geral']
    ).properties(height=300)
    st.altair_chart(area, use_container_width=True)

    st.subheader('Feedbacks ao longo do tempo')
    for _, row in df_a.iterrows():
        with st.expander(row['year_month']):
            st.write(row['feedback'])

# ---------- 4. PLANO DE AÇÃO ----------
with aba4:
    st.header('Planejamento')
    st.markdown('''### Sugestões
* **Mentoria personalizada** para alunos com risco contínuo \> 3 meses.
* **Aulas extras** focadas em KPIs mais críticos (ver Heatmap).
* **Revisão de infraestrutura** quando `infraestrutura` segue baixa.\n''')
