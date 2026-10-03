"""Montagem segura de consultas SQL a partir dos filtros escolhidos pelo usuário.

Regras de segurança:
- valores do usuário NUNCA entram no texto do SQL: vão sempre como parâmetros (?);
- nomes de colunas e a ordem de classificação passam por lista de permitidos;
- o limite de linhas tem teto, para não derrubar o banco com uma consulta gigante.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

COLUNAS = ("id", "data_abertura", "area", "status", "canal", "responsavel", "valor")
LIMITE_MAXIMO = 10_000


@dataclass
class Filtros:
    data_inicio: date | None = None
    data_fim: date | None = None
    areas: list[str] = field(default_factory=list)
    status: list[str] = field(default_factory=list)
    canais: list[str] = field(default_factory=list)
    valor_min: float | None = None
    valor_max: float | None = None
    responsavel_contem: str = ""
    ordenar_por: str = "data_abertura"
    ordem: str = "DESC"
    limite: int = 500


def _escapar_like(texto: str) -> str:
    """Escapa os curingas do LIKE para o texto digitado ser tratado de forma literal."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _validar(f: Filtros) -> str:
    if f.ordenar_por not in COLUNAS:
        raise ValueError(f"Coluna de ordenação inválida: {f.ordenar_por!r}")
    ordem = f.ordem.upper()
    if ordem not in ("ASC", "DESC"):
        raise ValueError(f"Ordem inválida: {f.ordem!r}")
    if not 1 <= f.limite <= LIMITE_MAXIMO:
        raise ValueError(f"O limite deve estar entre 1 e {LIMITE_MAXIMO}")
    if f.data_inicio and f.data_fim and f.data_inicio > f.data_fim:
        raise ValueError("A data inicial não pode ser maior que a final")
    if (
        f.valor_min is not None
        and f.valor_max is not None
        and f.valor_min > f.valor_max
    ):
        raise ValueError("O valor mínimo não pode ser maior que o máximo")
    return ordem


def montar_consulta(f: Filtros) -> tuple[str, list]:
    """Traduz os filtros em (sql, parametros), prontos para o sqlite3."""
    ordem = _validar(f)
    condicoes: list[str] = []
    params: list = []

    if f.data_inicio:
        condicoes.append("data_abertura >= ?")
        params.append(f.data_inicio.isoformat())
    if f.data_fim:
        condicoes.append("data_abertura <= ?")
        params.append(f.data_fim.isoformat())

    for coluna, valores in (("area", f.areas), ("status", f.status), ("canal", f.canais)):
        if valores:
            marcadores = ", ".join("?" for _ in valores)
            condicoes.append(f"{coluna} IN ({marcadores})")
            params.extend(valores)

    if f.valor_min is not None:
        condicoes.append("valor >= ?")
        params.append(f.valor_min)
    if f.valor_max is not None:
        condicoes.append("valor <= ?")
        params.append(f.valor_max)

    texto = f.responsavel_contem.strip()
    if texto:
        condicoes.append("responsavel LIKE ? ESCAPE '\\'")
        params.append(f"%{_escapar_like(texto)}%")

    sql = f"SELECT {', '.join(COLUNAS)} FROM casos"
    if condicoes:
        sql += " WHERE " + " AND ".join(condicoes)
    sql += f" ORDER BY {f.ordenar_por} {ordem}, id LIMIT ?"
    params.append(f.limite)
    return sql, params
