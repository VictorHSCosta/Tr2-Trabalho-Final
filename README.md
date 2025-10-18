# Tr2-Trabalho-Final

Ambiente base para o trabalho final com Flask.

## Primeiros passos
- `chmod +x setup.sh`
- `./setup.sh`
- `source .venv/bin/activate`
- `flask --app app run --debug`

O script `setup.sh` cria a virtualenv, atualiza o `pip` e instala dependências de runtime, testes e lint.

## Estrutura
- `app/`: código principal do Flask.
- `app/templates/index.html`: página inicial simples para validação rápida.
- `app.py`: ponto de entrada para rodar o servidor localmente.
- `tests/`: testes automatizados com `pytest`.
- `requirements.txt` e `requirements-dev.txt`: requisitos de runtime e desenvolvimento.

## Ferramentas de qualidade
- `ruff check .` para linting.
- `pytest` ou `pytest --cov` para testes (inclui exemplo de teste da API).
- CI com GitHub Actions (`.github/workflows/ci.yml`) roda lint e testes em cada push/PR.

## Próximos passos sugeridos
- Adicionar blueprints ou rotas específicas do trabalho.
- Escrever mais testes para cobrir as APIs principais.
- Personalizar a página HTML conforme a necessidade do projeto.
