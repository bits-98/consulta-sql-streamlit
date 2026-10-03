"""Acesso ao banco SQLite com dados 100% fictícios."""
from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

AREAS = ["Cível", "Trabalhista", "Tributário", "Contratos", "Regulatório"]
STATUS = ["Novo", "Em análise", "Concluído", "Arquivado"]
CANAIS = ["E-mail", "Portal", "API", "Balcão"]
RESPONSAVEIS = [
    "Ana Souza", "Bruno Lima", "Carla Mendes", "Diego Rocha",
    "Elisa Ferraz", "Fábio Alves", "Gabriela Costa", "Hugo Martins",
]
COLUNAS_DISTINTAS = ("area", "status", "canal")


def conectar(caminho: str) -> sqlite3.Connection:
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(caminho, check_same_thread=False)


def criar_base_ficticia(conn: sqlite3.Connection, n: int = 2000, seed: int = 42) -> None:
    """Recria a tabela `casos` com n linhas aleatórias (reprodutíveis pela seed)."""
    rng = random.Random(seed)
    conn.execute("DROP TABLE IF EXISTS casos")
    conn.execute(
        """CREATE TABLE casos (
            id INTEGER PRIMARY KEY,
            data_abertura TEXT NOT NULL,
            area TEXT NOT NULL,
            status TEXT NOT NULL,
            canal TEXT NOT NULL,
            responsavel TEXT NOT NULL,
            valor REAL NOT NULL
        )"""
    )
    conn.execute("CREATE INDEX idx_casos_data ON casos(data_abertura)")
    inicio = date(2025, 1, 1)
    dias = (date(2026, 9, 30) - inicio).days
    linhas = [
        (
            i,
            (inicio + timedelta(days=rng.randint(0, dias))).isoformat(),
            rng.choice(AREAS),
            rng.choices(STATUS, weights=[2, 3, 4, 1])[0],
            rng.choice(CANAIS),
            rng.choice(RESPONSAVEIS),
            round(rng.lognormvariate(8, 1), 2),
        )
        for i in range(1, n + 1)
    ]
    conn.executemany("INSERT INTO casos VALUES (?, ?, ?, ?, ?, ?, ?)", linhas)
    conn.commit()


def garantir_base(conn: sqlite3.Connection) -> None:
    existe = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='casos'"
    ).fetchone()
    if not existe:
        criar_base_ficticia(conn)


def valores_distintos(conn: sqlite3.Connection, coluna: str) -> list[str]:
    if coluna not in COLUNAS_DISTINTAS:
        raise ValueError(f"Coluna não permitida: {coluna!r}")
    linhas = conn.execute(f"SELECT DISTINCT {coluna} FROM casos ORDER BY 1").fetchall()
    return [linha[0] for linha in linhas]


def executar(conn: sqlite3.Connection, sql: str, params: list) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)
