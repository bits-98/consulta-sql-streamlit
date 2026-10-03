"""Front de consultas SQL: o usuário escolhe os filtros e o app monta a consulta."""
import os
from datetime import date
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv

from src.db import conectar, executar, garantir_base, valores_distintos
from src.query_builder import COLUNAS, LIMITE_MAXIMO, Filtros, montar_consulta

load_dotenv()
CAMINHO_BANCO = os.getenv("DB_PATH", "data/casos.db")

st.set_page_config(page_title="Consulta de casos", page_icon="🔎", layout="wide")


@st.cache_resource
def obter_conexao(caminho: str):
    conn = conectar(caminho)
    garantir_base(conn)
    return conn


conn = obter_conexao(CAMINHO_BANCO)

st.title("🔎 Consulta de casos")
st.caption("Escolha os filtros e o sistema monta a consulta SQL por você. Dados fictícios.")

with st.sidebar:
    st.header("Filtros")
    with st.form("filtros"):
        periodo = st.date_input(
            "Período de abertura",
            value=(date(2026, 1, 1), date(2026, 9, 30)),
            format="DD/MM/YYYY",
        )
        areas = st.multiselect("Área", valores_distintos(conn, "area"))
        status = st.multiselect("Status", valores_distintos(conn, "status"))
        canais = st.multiselect("Canal", valores_distintos(conn, "canal"))
        col1, col2 = st.columns(2)
        valor_min = col1.number_input("Valor mín.", min_value=0.0, value=0.0, step=100.0)
        valor_max = col2.number_input("Valor máx.", min_value=0.0, value=0.0, step=100.0,
                                      help="0 = sem limite")
        responsavel = st.text_input("Responsável contém")
        ordenar_por = st.selectbox("Ordenar por", COLUNAS, index=COLUNAS.index("data_abertura"))
        ordem = st.radio("Ordem", ["DESC", "ASC"], horizontal=True)
        limite = st.number_input("Máximo de linhas", 1, LIMITE_MAXIMO, 500, step=100)
        consultar = st.form_submit_button("Consultar", use_container_width=True)

data_inicio = data_fim = None
if isinstance(periodo, tuple) and len(periodo) == 2:
    data_inicio, data_fim = periodo

filtros = Filtros(
    data_inicio=data_inicio,
    data_fim=data_fim,
    areas=areas,
    status=status,
    canais=canais,
    valor_min=valor_min or None,
    valor_max=valor_max or None,
    responsavel_contem=responsavel,
    ordenar_por=ordenar_por,
    ordem=ordem,
    limite=int(limite),
)

try:
    sql, params = montar_consulta(filtros)
except ValueError as erro:
    st.error(f"Filtro inválido: {erro}")
    st.stop()

with st.expander("Consulta SQL gerada", expanded=False):
    st.code(sql, language="sql")
    st.write("Parâmetros:", params)

df = executar(conn, sql, params)

m1, m2, m3 = st.columns(3)
m1.metric("Casos encontrados", f"{len(df):,}".replace(",", "."))
m2.metric("Valor total", f"R$ {df['valor'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
m3.metric("Valor médio", f"R$ {df['valor'].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if len(df) else "—")

st.dataframe(df, use_container_width=True, hide_index=True)

buffer = BytesIO()
df.to_excel(buffer, index=False, engine="openpyxl")
d1, d2 = st.columns(2)
d1.download_button("⬇️ Baixar Excel", buffer.getvalue(), "casos.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
d2.download_button("⬇️ Baixar CSV", df.to_csv(index=False).encode("utf-8"), "casos.csv", "text/csv")
