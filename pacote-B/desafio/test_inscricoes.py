import pytest

from pages.inscricoes_page import InscricoesPage

MSG_NOME = "Nome deve ter de 3 a 60 caracteres"


@pytest.fixture
def pagina(driver, base_url):
    return InscricoesPage(driver, base_url)


def test_ct01_inscricao_valida(pagina):
    pagina.abrir()
    pagina.inscrever("Ana Souza", "ana@ads.local", "1")
    assert pagina.sucesso() == "Inscrição realizada"
    pagina.aguardar_itens(1)
    assert "ana@ads.local" in pagina.textos_da_lista()[0]


def test_ct02_mesmo_email_outro_curso(pagina, inscrever_pela_api):
    inscrever_pela_api("Ana Souza", "ana@ads.local", 1)
    pagina.abrir()
    pagina.aguardar_itens(1)
    pagina.inscrever("Ana Souza", "ana@ads.local", "2")
    assert pagina.sucesso() == "Inscrição realizada"
    pagina.aguardar_itens(2)


def test_ct03_nome_vazio(pagina, inscricoes_pela_api):
    pagina.abrir()
    pagina.inscrever("", "ana@ads.local", "1")
    assert pagina.erro() == MSG_NOME
    assert pagina.textos_da_lista() == []
    assert inscricoes_pela_api() == []


def test_ct04_email_invalido(pagina, inscricoes_pela_api):
    pagina.abrir()
    pagina.inscrever("Ana Souza", "ana.ads.local", "1")
    assert pagina.erro() == "E-mail inválido"
    assert pagina.textos_da_lista() == []
    assert inscricoes_pela_api() == []


def test_ct05_curso_ausente(pagina, inscricoes_pela_api):
    pagina.abrir()
    pagina.inscrever("Ana Souza", "ana@ads.local")
    assert pagina.erro() == "Curso obrigatório"
    assert pagina.textos_da_lista() == []
    assert inscricoes_pela_api() == []


@pytest.mark.parametrize("tamanho, aceita", [(2, False), (3, True), (60, True), (61, False)],
                         ids=["2", "3", "60", "61"])
def test_limite_nome(pagina, inscricoes_pela_api, tamanho, aceita):
    pagina.abrir()
    pagina.inscrever("a" * tamanho, "ana@ads.local", "1")
    if aceita:
        assert pagina.sucesso() == "Inscrição realizada"
        pagina.aguardar_itens(1)
        assert len(inscricoes_pela_api()) == 1
    else:
        assert pagina.erro() == MSG_NOME
        assert pagina.textos_da_lista() == []
        assert inscricoes_pela_api() == []


def test_ct10_duplicidade_maiusculas_e_espacos(pagina, inscrever_pela_api, inscricoes_pela_api):
    inscrever_pela_api("Ana Souza", "ana@ads.local", 1)
    pagina.abrir()
    pagina.aguardar_itens(1)
    pagina.inscrever("Ana Souza", "  ANA@ADS.LOCAL ", "1")
    assert pagina.erro() == "Inscrição já existente"
    assert len(pagina.textos_da_lista()) == 1
    assert len(inscricoes_pela_api()) == 1


def test_ct11_curso_lotado(pagina, inscrever_pela_api, inscricoes_pela_api):
    inscrever_pela_api("Ana Souza", "ana@ads.local", 1)
    inscrever_pela_api("Bruno Lima", "bruno@ads.local", 1)
    pagina.abrir()
    pagina.aguardar_itens(2)
    pagina.inscrever("Carla Dias", "carla@ads.local", "1")
    assert pagina.erro() == "Curso sem vagas"
    assert len(pagina.textos_da_lista()) == 2
    assert len(inscricoes_pela_api()) == 2


def test_ct12_cancelar_e_inscrever_de_novo(pagina, inscrever_pela_api):
    primeira = inscrever_pela_api("Ana Souza", "ana@ads.local", 1)
    inscrever_pela_api("Bruno Lima", "bruno@ads.local", 1)
    pagina.abrir()
    pagina.aguardar_itens(2)

    pagina.cancelar(primeira["id"])
    assert pagina.sucesso() == "Inscrição cancelada"
    pagina.aguardar_itens(1)

    pagina.inscrever("Carla Dias", "carla@ads.local", "1")
    assert pagina.sucesso() == "Inscrição realizada"
    pagina.aguardar_itens(2)
