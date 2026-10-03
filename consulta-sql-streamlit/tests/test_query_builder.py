from datetime import date

import pytest

from src.query_builder import LIMITE_MAXIMO, Filtros, montar_consulta


def test_sem_filtros_nao_tem_where():
    sql, params = montar_consulta(Filtros())
    assert "FROM casos" in sql
    assert "WHERE" not in sql
    assert params == [500]


def test_filtro_por_area_usa_marcadores():
    sql, params = montar_consulta(Filtros(areas=["Cível", "Contratos"]))
    assert "area IN (?, ?)" in sql
    assert params[:2] == ["Cível", "Contratos"]


def test_intervalo_de_datas():
    sql, params = montar_consulta(
        Filtros(data_inicio=date(2026, 1, 1), data_fim=date(2026, 3, 31))
    )
    assert "data_abertura >= ?" in sql and "data_abertura <= ?" in sql
    assert params[:2] == ["2026-01-01", "2026-03-31"]


def test_faixa_de_valor():
    sql, params = montar_consulta(Filtros(valor_min=100, valor_max=900))
    assert "valor >= ?" in sql and "valor <= ?" in sql
    assert params[:2] == [100, 900]


def test_varios_filtros_combinam_com_and():
    sql, _ = montar_consulta(Filtros(areas=["Cível"], status=["Novo"], canais=["API"]))
    assert sql.count(" AND ") == 2


def test_curingas_do_like_sao_escapados():
    _, params = montar_consulta(Filtros(responsavel_contem="50%_"))
    assert params[0] == "%50\\%\\_%"


def test_texto_malicioso_vai_como_parametro_e_nunca_no_sql():
    ataque = "x'; DROP TABLE casos; --"
    sql, params = montar_consulta(Filtros(areas=[ataque]))
    assert "DROP" not in sql
    assert ataque in params


def test_coluna_de_ordenacao_fora_da_lista_e_rejeitada():
    with pytest.raises(ValueError):
        montar_consulta(Filtros(ordenar_por="valor; DROP TABLE casos"))


def test_ordem_invalida_e_rejeitada():
    with pytest.raises(ValueError):
        montar_consulta(Filtros(ordem="DESC; --"))


@pytest.mark.parametrize("limite", [0, -1, LIMITE_MAXIMO + 1])
def test_limite_fora_do_intervalo_e_rejeitado(limite):
    with pytest.raises(ValueError):
        montar_consulta(Filtros(limite=limite))


def test_datas_invertidas_sao_rejeitadas():
    with pytest.raises(ValueError):
        montar_consulta(Filtros(data_inicio=date(2026, 5, 1), data_fim=date(2026, 1, 1)))


def test_valores_invertidos_sao_rejeitados():
    with pytest.raises(ValueError):
        montar_consulta(Filtros(valor_min=10, valor_max=1))
