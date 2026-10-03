# Consulta SQL com Streamlit

![Testes](https://github.com/bits-98/consulta-sql-streamlit/actions/workflows/tests.yml/badge.svg)

> Front-end em que o usuário escolhe filtros em uma tela e o sistema monta a consulta SQL de forma segura, devolvendo a base pronta para análise e download em Excel ou CSV.

<!-- Coloque aqui um print ou GIF do app: ![Demonstração](docs/demo.gif) -->

## Problema

Pedir uma base de dados para a área de dados costuma significar abrir uma solicitação, esperar alguém escrever a consulta e receber o resultado horas depois. Esse processo é lento, depende de uma pessoa e tem risco de erro manual.

## Solução

O usuário escolhe os filtros (período, área, status, canal, faixa de valor, responsável) e o app:

1. Valida os filtros.
2. Monta uma consulta SQL **parametrizada**, sem concatenar texto do usuário.
3. Executa no banco e mostra a tabela, os totais e o SQL gerado.
4. Permite baixar o resultado em Excel ou CSV.

Este projeto é uma demonstração com **dados fictícios** (SQLite). O mesmo padrão aplicado em um ambiente corporativo (com Databricks no lugar do SQLite) reduziu um relatório diário de 3–5 horas para 3–4 minutos.

## Segurança

- Valores digitados **nunca** entram no texto do SQL: vão como parâmetros (`?`).
- Nomes de colunas e ordem de classificação passam por lista de permitidos.
- Os curingas do `LIKE` são escapados e o limite de linhas tem teto.
- Há testes automatizados que simulam tentativas de SQL injection.

## Tecnologias

Python · Streamlit · Pandas · SQLite · openpyxl · pytest · GitHub Actions

## Como rodar

```bash
# 1. Clone o repositório
git clone https://github.com/bits-98/consulta-sql-streamlit.git
cd consulta-sql-streamlit

# 2. Crie o ambiente virtual e instale as dependências
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt

# 3. (Opcional) configure o caminho do banco
copy .env.example .env          # Windows (Linux/Mac: cp .env.example .env)

# 4. Execute
streamlit run app.py
```

O banco com 2.000 casos fictícios é criado automaticamente na primeira execução.

## Testes

```bash
pytest
```

São 21 testes que cobrem a montagem das consultas, as validações, o banco de dados e a abertura do app. Eles rodam automaticamente a cada `push` pelo GitHub Actions.

## Estrutura do projeto

```
consulta-sql-streamlit/
├── app.py                  # interface em Streamlit
├── src/
│   ├── query_builder.py    # filtros -> SQL parametrizado
│   └── db.py               # banco SQLite e dados fictícios
├── tests/                  # testes (pytest)
├── docs/                   # prints e GIFs
├── .github/workflows/      # testes automáticos
├── .env.example
├── requirements.txt
└── README.md
```

## Próximos passos

- [ ] Trocar o SQLite por um conector para Databricks ou PostgreSQL
- [ ] Salvar e reaproveitar combinações de filtros
- [ ] Autenticação e log de quem consultou o quê

## Aviso

Este projeto usa apenas dados fictícios. Não contém código, dados ou credenciais de nenhuma empresa.

## Autor

**Lucas Guadagnini Dodo**: [LinkedIn](https://www.linkedin.com/in/lucas-dodo/) · [GitHub](https://github.com/bits-98)
# consulta-sql-streamlit
