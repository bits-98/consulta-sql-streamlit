import pytest

from src.db import conectar, criar_base_ficticia, executar, valores_distintos
from src.query_builder import Filtros, montar_consulta


@pytest.fixture()
def conn(tmp_path):
    conexao = conectar(str(tmp_path / "teste.db"))
    criar_base_ficticia(conexao, n=500, seed=1)
    yield conexao
    conexao.close()


def test_base_ficticia_tem_o_numero_de_linhas_pedido(conn):
    assert conn.execute("SELECT COUNT(*) FROM casos").fetchone()[0] == 500


def test_mesma_seed_gera_os_mesmos_dados(tmp_path):
    a = conectar(str(tmp_path / "a.db"))
    b = conectar(str(tmp_path / "b.db"))
    criar_base_ficticia(a, n=100, seed=7)
    criar_base_ficticia(b, n=100, seed=7)
    assert a.execute("SELECT * FROM casos").fetchall() == b.execute("SELECT * FROM casos").fetchall()


def test_filtros_retornam_apenas_linhas_que_atendem(conn):
    sql, params = montar_consulta(Filtros(areas=["Tributário"], valor_min=1000, limite=1000))
    df = executar(conn, sql, params)
    assert not df.empty
    assert set(df["area"]) == {"Tributário"}
    assert (df["valor"] >= 1000).all()


def test_ordenacao_e_limite(conn):
    sql, params = montar_consulta(Filtros(ordenar_por="valor", ordem="DESC", limite=5))
    df = executar(conn, sql, params)
    assert len(df) == 5
    assert df["valor"].is_monotonic_decreasing


def test_tentativa_de_sql_injection_nao_apaga_a_tabela(conn):
    sql, params = montar_consulta(Filtros(areas=["x'; DROP TABLE casos; --"]))
    df = executar(conn, sql, params)
    assert df.empty
    assert conn.execute("SELECT COUNT(*) FROM casos").fetchone()[0] == 500


def test_valores_distintos_so_aceita_colunas_permitidas(conn):
    assert "Cível" in valores_distintos(conn, "area")
    with pytest.raises(ValueError):
        valores_distintos(conn, "valor; DROP TABLE casos")
