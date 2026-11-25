# Trabalho 2: Testes funcionais (Selenium + pytest)

Engenharia de Software III, IFPI, 4º período de ADS.

Equipe: Maria Luiza Morais e Isaac de Jesus.

O relatório está em [relatorio.md](relatorio.md). O trabalho tem três partes: Pacote A (Sabor Express e Portal de Matrícula), Pacote B (Portal e Inscrições em minicursos) e o projeto anterior da equipe (Roger's Market).

## Versões usadas

| Item | Versão |
|---|---|
| Sistema operacional | Windows 11 Pro |
| Python | 3.14.0 |
| Selenium | 4.54.0 |
| pytest | 9.2.0 |
| pytest-html | 4.2.0 |
| Google Chrome | 158.0.8127.88 (o Selenium baixa o driver sozinho no primeiro uso, então precisa de internet nessa vez) |
| Node.js | 22.20.0 (só para subir o front-end do projeto anterior) |

## Preparar o ambiente

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install flask locust selenium pytest pytest-html
```

Os sistemas testados não estão neste repositório. Eles vêm no zip do professor (`ESIII_Testes_Funcionais.zip`) e do projeto anterior da equipe.

| Sistema | Como subir | Endereço |
|---|---|---|
| Pacote A | `cd 02_Pacote_A_SaborExpress_Matricula/app` e `python app.py` | http://127.0.0.1:5000 |
| Pacote B | `cd 03_Pacote_B_Biblioteca_Minicursos` e `python app.py` | http://127.0.0.1:8000 |
| Projeto anterior (servidor) | na pasta do projeto, `python servidor/app.py` | http://127.0.0.1:5001 |
| Projeto anterior (front-end) | na pasta do projeto, `npm install` e `npm run dev -- --host 127.0.0.1` | http://127.0.0.1:5173 |

Usamos `127.0.0.1` em vez de `localhost` porque, no Windows, `localhost` deixa cada requisição cerca de 2 s mais lenta. Para o front-end do projeto, o Vite só escuta em `localhost` por padrão, por isso o `--host 127.0.0.1`.

## Como rodar

Em todos os casos, a suíte roda em sequência (nunca em paralelo, porque o estado dos sistemas é compartilhado). Cada teste zera o sistema pela API antes de começar. Para rodar sem abrir a janela do Chrome, defina `HEADLESS=1`.

```powershell
$env:HEADLESS="1"
```

**Pacote B, exemplo (login)**, na pasta `pacote-B/exemplo`:

```powershell
python -m pytest test_login.py -v --junitxml=resultado_login.xml --html=relatorio_login.html --self-contained-html
```

**Pacote B, desafio (inscrições)**, na pasta `pacote-B/desafio`:

```powershell
python -m pytest -v --junitxml=execucoes/execucao1.xml --html=execucoes/execucao1.html --self-contained-html
```

**Pacote A, exemplo (fluxo de pedido)**, na pasta `pacote-A/exemplo`. Como o padrão do professor é `localhost`, informe o endereço:

```powershell
$env:BASE_URL="http://127.0.0.1:5000"
python -m pytest -v --junitxml=resultado_execucao1.xml --html=relatorio_execucao1.html --self-contained-html
```

**Pacote A, desafio (matrícula)**, na pasta `pacote-A/desafio`:

```powershell
python -m pytest -v --junitxml=execucoes/execucao1.xml --html=execucoes/execucao1.html --self-contained-html
```

**Projeto anterior (Roger's Market)**, na pasta `projeto-anterior`, com o servidor e o front-end no ar:

```powershell
python -m pytest -v --junitxml=execucoes/execucao1.xml --html=execucoes/execucao1.html --self-contained-html
```

Para rodar 3 vezes, troque o número no nome dos arquivos (`execucao2`, `execucao3`).

Variáveis opcionais: `BASE_URL` (Pacote A e B), `FRONT_URL` e `API_URL` (projeto anterior).

## Estrutura

```
README.md
relatorio.md
pacote-A/
  exemplo/     conftest.py, pages/ e test_fluxo_pedido.py do professor, e os relatórios das 3 execuções
  desafio/     conftest.py, pages/matricula_pages.py, test_matricula.py, matriz_casos.csv, execucoes/
pacote-B/
  exemplo/     conftest.py e test_login.py do professor, e o resultado
  desafio/     conftest.py, pages/inscricoes_page.py, test_inscricoes.py, matriz_casos.csv, execucoes/
projeto-anterior/
  conftest.py, pages/loja_pages.py, test_loja.py, matriz_casos.csv, execucoes/
```

Se um teste falhar, o `conftest.py` salva um print da tela na pasta `evidencias/`.

## Observação sobre o exemplo do Pacote A

No `conftest.py` do professor acrescentamos três linhas para desligar o gerenciador de senhas do Chrome. Sem isso o exemplo oscilava nesta máquina. O motivo está no relatório.
