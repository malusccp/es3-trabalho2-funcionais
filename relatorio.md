# Relatório do Trabalho 2: Testes funcionais

Engenharia de Software III, IFPI. Equipe: Maria Luiza Morais e Isaac de Jesus. Data das execuções: 25/11/2026.

## 1. Resumo

Automatizamos testes funcionais, com Selenium e pytest, para três sistemas: o Portal de Matrícula do Pacote A, as Inscrições em minicursos do Pacote B e o Roger's Market, o projeto anterior da equipe. Antes de automatizar, escrevemos a matriz de casos de cada um. Cada suíte foi rodada 3 vezes, em sequência.

| Parte | Casos | Resultado nas 3 execuções | Defeitos no sistema |
|---|---|---|---|
| Pacote B, desafio (inscrições) | 12 | 12 de 12 aprovados nas três | não encontramos |
| Pacote A, desafio (matrícula) | 13 | 13 de 13 aprovados nas três | não encontramos |
| Projeto anterior (Roger's Market) | 13 | 13 de 13 aprovados nas três | não encontramos |

Nenhum teste oscilou nas suítes dos desafios e do projeto. Os dois exemplos do professor (login do Pacote B e fluxo de pedido do Pacote A) também foram rodados. O do Pacote A oscilou, e o motivo foi do navegador, não do sistema (seção 6).

## 2. Ambiente

| Item | Valor |
|---|---|
| Sistema operacional | Windows 11 Pro |
| Processador e memória | Intel Core i5-13420H, 15,7 GB |
| Python | 3.14.0 |
| Selenium | 4.54.0 |
| pytest e pytest-html | 9.2.0 e 4.2.0 |
| Chrome | 158.0.8127.88, rodado sem janela (`HEADLESS=1`) |
| Endereços | `127.0.0.1` em todos (Pacote A 5000, Pacote B 8000, projeto: front 5173 e servidor 5001) |

## 3. Como escrevemos os testes

- **Matriz antes do código.** Cada parte tem um `matriz_casos.csv` no modelo do professor, escrito antes de automatizar. O resultado esperado vem da regra (do guia ou do `REGRAS.md`), nunca do que o sistema mostra.
- **Técnicas.** Partição de equivalência, valor-limite e tabela de decisão, indicadas na coluna `tecnica` de cada matriz.
- **Localizadores.** Só `id` ou `data-testid`. Nenhum XPath.
- **Esperas.** Só `WebDriverWait`. Nenhum `sleep`. O `implicitly_wait` fica em 0.
- **Page Objects.** Uma classe por tela, com localizadores e ações. Os `assert` ficam só nos testes.
- **Testes independentes.** Uma fixture com `autouse` zera o sistema pela API antes de cada teste. A suíte roda em qualquer ordem.
- **Rejeição comprovada.** Nos casos em que o sistema recusa, conferimos também que nada foi gravado (seção 7).
- **Teste orientado a dados.** Cada suíte tem pelo menos um `pytest.mark.parametrize`.

## 4. Estrutura do código

| Parte | Fixtures (`conftest.py`) | Page Objects | Testes |
|---|---|---|---|
| Pacote B | `driver`, `base_url`, `sistema_zerado` (autouse), `inscrever_pela_api`, `inscricoes_pela_api` | `InscricoesPage` | `test_inscricoes.py` |
| Pacote A | `driver`, `base_url`, `sistema_zerado` (autouse), `matricular_pela_api` | `LoginMatriculaPage`, `DisciplinasPage`, `ComprovantePage` | `test_matricula.py` |
| Projeto | `driver`, `front_url`, `servidor_zerado` (autouse), `estoque_pela_api`, `status_do_pedido_pela_api` | `CatalogoPage`, `CarrinhoPage`, `PedidoPage` | `test_loja.py` |

**Dados de teste.** Matrícula 20260001 e senha `senha123` (Pacote A); o resto vem de valores fixos nos testes. A API só prepara o estado que a tela demoraria para montar (as vagas de MOB e a matrícula prévia no Pacote A; inscrições prévias no Pacote B). A ação avaliada e a verificação principal são pela tela.

**Opções do Chrome.** Em todo `conftest.py` desligamos o gerenciador de senhas e a detecção de senha vazada (seção 6).

## 5. Regras cobertas e matriz de casos

### 5.1 Pacote B: inscrições em minicursos (12 casos)

| ID | Regra | Caso | Resultado esperado |
|---|---|---|---|
| CT01 | Inscrição válida | Ana Souza, curso 1 | "Inscrição realizada" e 1 item na lista |
| CT02 | Mesmo e-mail em outro curso | Mesmo e-mail, curso 2 | As duas inscrições na lista |
| CT03 | Nome obrigatório | Nome vazio | "Nome deve ter de 3 a 60 caracteres" e nada gravado |
| CT04 | Formato do e-mail | `ana.ads.local` | "E-mail inválido" e nada gravado |
| CT05 | Curso obrigatório | Curso ausente | "Curso obrigatório" e nada gravado |
| CT06 a CT09 | Limites do nome | 2, 3, 60 e 61 caracteres | 2 e 61 recusam; 3 e 60 aceitam (um teste parametrizado) |
| CT10 | Duplicidade | `  ANA@ADS.LOCAL ` no mesmo curso | "Inscrição já existente" e a lista continua com 1 |
| CT11 | Lotação | Terceira inscrição no curso 1 | "Curso sem vagas" e a lista continua com 2 |
| CT12 | Cancelamento | Cancelar e inscrever de novo | "Inscrição cancelada" e depois "Inscrição realizada" |

### 5.2 Pacote A: portal de matrícula (13 casos)

| ID | Regra | Caso | Resultado esperado |
|---|---|---|---|
| CT01 | R1 | Login válido | Oferta de disciplinas aberta |
| CT02 a CT04 | R1 | Senha errada, matrícula inexistente, campos vazios | "Matrícula ou senha inválidas." (um teste parametrizado) |
| CT05 | R2 | Acesso direto à oferta sem login | Redireciona para o login |
| CT06 a CT09 | R3 | 0, 1, 5 e 6 disciplinas | 0 e 6 recusam com a mensagem da regra; 1 e 5 matriculam (um teste parametrizado) |
| CT10 | R4 | ES3 e RED (as duas em SEG-19h) | "Choque de horário entre disciplinas selecionadas." |
| CT11 | R5 | MOB sem vagas (5 ocupadas pela API) | "Vagas esgotadas: MOB." |
| CT12 | R6 | Aluno já matriculado | "Aluno já possui matrícula neste semestre." |
| CT13 | R7 | ES3 e BD2 | "Matrícula realizada com sucesso!", comprovante COMP-NNNNNN, disciplinas listadas e 1 vaga a menos em cada |

### 5.3 Projeto anterior: Roger's Market (13 casos)

| ID | Regra | Caso | Resultado esperado |
|---|---|---|---|
| CT01 | F1.4 | Busca ` aPPle ` | Só a Apple na lista e "1 produto(s)" |
| CT02 | F1.6 | Busca `xyz` | "Nenhum produto encontrado" e "0 produto(s)" |
| CT03 | F1.5 | `cake` com filtro de estoque | Bacuri e Pistachio; Black Forest some; "2 produto(s)" |
| CT04 | R1 | Produto esgotado | Botão desabilitado com "Esgotado" |
| CT05 | R3 | 1 x Apple | Subtotal 100, desconto 0, frete 500, total 600 |
| CT06 a CT08 | R2 | Quantidade 0, 10 e 11 | 0 e 11 recusam com "Quantidade deve ser de 1 a 10"; 10 aceita (um teste parametrizado) |
| CT09 | R3 | R$ 30,00 exatos | Frete R$ 0,00 |
| CT10 | R3 e R4 | Cupom ` promo10 ` sobre R$ 30,00 | Desconto R$ 3,00 e o frete volta a R$ 5,00 (total R$ 32,00) |
| CT11 | R5 | E-mail inválido | "E-mail inválido", carrinho mantido e nenhum pedido criado |
| CT12 | R5 e R6 | Pedido válido | "Pedido realizado", PED-NNNNNN, carrinho vazio, estoque da Apple 39 |
| CT13 | Servidor | 9 x Pistachio (estoque 8) | "Estoque insuficiente: Pistachio Cake" e estoque intacto |

As matrizes completas, com pré-condição, dados, passos e a função que implementa cada caso, estão nos arquivos `matriz_casos.csv` de cada pasta. Os fluxos do projeto são o catálogo (busca e filtro) e o pedido (carrinho, cupom e finalização). O projeto já tinha `data-testid` em todos os elementos, então não alteramos o sistema.

## 6. Resultado das 3 execuções

| Parte | Execução 1 | Execução 2 | Execução 3 | Algum teste oscilou? |
|---|---|---|---|---|
| Pacote B, desafio | 12 aprovados (51 s) | 12 aprovados (51 s) | 12 aprovados (49 s) | não |
| Pacote A, desafio | 13 aprovados (50 s) | 13 aprovados (51 s) | 13 aprovados (52 s) | não |
| Projeto anterior | 13 aprovados (50 s) | 13 aprovados (49 s) | 13 aprovados (49 s) | não |

Exemplos do professor, rodados para entender o modelo:

| Exemplo | Resultado |
|---|---|
| Pacote B, login (2 testes) | 2 aprovados em 13 s, rodado uma vez |
| Pacote A, fluxo de pedido (5 testes), com `127.0.0.1` e o aviso de senha desligado | Execução 1: 5 aprovados. Execução 2: 4 aprovados e 1 erro. Execução 3: 5 aprovados |

Os relatórios HTML e XML de cada execução estão nas pastas `execucoes/` (e `pacote-A/exemplo/` para o exemplo A).

### Problemas encontrados no ambiente de teste (não são defeitos dos sistemas)

**1. Aviso de senha vazada do Chrome.** Sem ajuste, o exemplo do Pacote A falhava de 30% a 50% das vezes. O clique em "Finalizar pedido" simplesmente não enviava o formulário. Com uma pausa de 1 s antes do clique, falhava em 100%. O servidor não recebia nada (conferimos o número de pedidos antes e depois). A causa é um aviso que o Chrome 158 mostra para senhas muito comuns (`123456` e `senha123`) cerca de 1 s depois do login, e que rouba o próximo clique. Desligar só o gerenciador de senhas, o autofill ou a oclusão de janela não resolveu. O que resolveu foi a opção `profile.password_manager_leak_detection` em falso: 0 falhas em 18 tentativas, inclusive com a pausa de 1 s. Está em todos os `conftest.py`. No exemplo do professor foi preciso acrescentar essa opção.

**2. Oscilação do `staleness_of` no exemplo do professor.** Na execução 2 do exemplo A houve um erro na preparação (fixture) do teste CT03: `WebDriverException: Node with given id does not belong to the document`, dentro do `staleness_of` do Page Object do cardápio. Aconteceu 1 vez em 15 testes. Não investigamos mais a fundo. Nos nossos Page Objects esperamos um elemento da página seguinte (como `#tabela-disciplinas` ou `#mensagem-erro`) e não usamos `staleness_of`.

## 7. Como provamos que nada foi gravado nas rejeições

- **Pacote B.** Descobrimos que a tela de inscrições só atualiza a lista quando a resposta é de sucesso. Se o servidor gravasse algo por engano numa rejeição, a lista na tela continuaria vazia e o teste passaria à toa. Por isso, além da lista da tela, conferimos `GET /api/inscricoes`. Isto não é um defeito, porque o guia não pede o contrário. A ação avaliada continua sendo feita pela tela.
- **Pacote A.** Lemos as vagas de todas as disciplinas antes de confirmar e conferimos que estão iguais depois. O esperado vem da regra ("não pode descontar vaga"), não de números fixos. No caso de sucesso, ES3 e BD2 têm 1 vaga a menos e as outras disciplinas não mudam.
- **Projeto.** Conferimos pela API que `GET /api/pedidos/PED-000001` retorna 404 e que o estoque do produto não mudou.

## 8. Defeitos encontrados

Não encontramos defeito de comportamento em nenhum dos três sistemas. Todos os casos da matriz passaram, e os resultados esperados vieram das regras. Registramos apenas os dois problemas do ambiente de teste da seção 6.

## 9. Dificuldades e limitações da cobertura

- **Chrome sem janela.** Todas as execuções foram com `HEADLESS=1`. Não rodamos com janela, onde o comportamento do Chrome pode ser diferente.
- **Sem teste de mutação.** Os testes passaram de primeira nos três desafios. Não quebramos o sistema de propósito para ver se a suíte reclama, então não provamos que ela detecta todo defeito possível.
- **Pacote A.** Só testamos a matrícula 20260001 e a senha `senha123`. Não cobrimos os outros alunos nem o comportamento dos módulos de lanchonete além do exemplo.
- **Pacote B.** Só um navegador (Chrome) e uma resolução de tela.
- **Projeto anterior.** Não testamos o servidor fora do ar, nem a carga de produtos com falha, nem os casos de "Carregando...". A quantidade decimal e a quantidade vazia no campo do carrinho também não foram automatizadas.
- **Exemplo do Pacote B.** Foi rodado uma vez só. O guia pede 3 execuções para as suítes dos desafios e do projeto.
- **Front-end do projeto.** O Vite escuta só em `localhost` por padrão. Subimos com `--host 127.0.0.1` para evitar o atraso de 2 s do Windows.

## 10. Tabela de contribuição

A preencher pela equipe. Não temos como saber quem fez o quê.

| Integrante | O que fez |
|---|---|
| Maria Luiza Morais | |
| Isaac de Jesus | |
