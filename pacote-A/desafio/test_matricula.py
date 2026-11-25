import re

import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.matricula_pages import ComprovantePage, DisciplinasPage, LoginMatriculaPage

MSG_LOGIN = "Matrícula ou senha inválidas."


def entrar_como_aluno(driver, base_url, matricula="20260001"):
    LoginMatriculaPage(driver, base_url).abrir().entrar(matricula, "senha123")
    oferta = DisciplinasPage(driver, base_url)
    oferta.esta_aberta()
    return oferta


def test_ct01_login_valido(driver, base_url):
    LoginMatriculaPage(driver, base_url).abrir().entrar("20260001", "senha123")
    assert DisciplinasPage(driver, base_url).esta_aberta()
    assert driver.current_url.endswith("/matricula/disciplinas")


@pytest.mark.parametrize("matricula, senha", [("20260001", "senha-errada"),
                                              ("20269999", "senha123"),
                                              ("", "")],
                         ids=["senha-errada", "matricula-inexistente", "vazios"])
def test_login_invalido(driver, base_url, matricula, senha):
    login = LoginMatriculaPage(driver, base_url).abrir()
    login.entrar(matricula, senha)
    assert login.erro() == MSG_LOGIN
    assert driver.current_url.endswith("/matricula/login")
    assert not DisciplinasPage(driver, base_url).tabela_aparece()


def test_ct05_oferta_exige_login(driver, base_url):
    DisciplinasPage(driver, base_url).abrir()
    WebDriverWait(driver, 5).until(EC.url_contains("/matricula/login"))
    assert driver.current_url.endswith("/matricula/login")
    assert not DisciplinasPage(driver, base_url).tabela_aparece()


@pytest.mark.parametrize("codigos, erro", [
    ([], "Selecione ao menos uma disciplina."),
    (["ES3"], None),
    (["ES3", "BD2", "PW2", "IHC", "EMP"], None),
    (["ES3", "BD2", "PW2", "IHC", "EMP", "MOB"], "Máximo de 5 disciplinas por semestre."),
], ids=["0", "1", "5", "6"])
def test_quantidade_de_disciplinas(driver, base_url, codigos, erro):
    oferta = entrar_como_aluno(driver, base_url)
    antes = oferta.vagas()
    oferta.selecionar(codigos)
    oferta.confirmar()
    if erro:
        assert oferta.erro() == erro
        assert oferta.vagas() == antes
    else:
        comprovante = ComprovantePage(driver)
        assert comprovante.mensagem() == "Matrícula realizada com sucesso!"
        assert re.fullmatch(r"COMP-\d{6}", comprovante.numero())
        assert comprovante.disciplinas() == codigos


def test_ct10_choque_de_horario(driver, base_url):
    oferta = entrar_como_aluno(driver, base_url)
    antes = oferta.vagas()
    oferta.selecionar(["ES3", "RED"])
    oferta.confirmar()
    assert oferta.erro() == "Choque de horário entre disciplinas selecionadas."
    assert oferta.vagas() == antes


def test_ct11_vagas_esgotadas(driver, base_url, matricular_pela_api):
    for n in range(5):
        matricular_pela_api(f"2026010{n + 1}", ["MOB"])
    oferta = entrar_como_aluno(driver, base_url)
    antes = oferta.vagas()
    oferta.selecionar(["MOB"])
    oferta.confirmar()
    assert oferta.erro() == "Vagas esgotadas: MOB."
    assert oferta.vagas() == antes


def test_ct12_matricula_unica(driver, base_url, matricular_pela_api):
    matricular_pela_api("20260001", ["ES3"])
    oferta = entrar_como_aluno(driver, base_url)
    antes = oferta.vagas()
    oferta.selecionar(["BD2"])
    oferta.confirmar()
    assert oferta.erro() == "Aluno já possui matrícula neste semestre."
    assert oferta.vagas() == antes


def test_ct13_matricula_com_sucesso(driver, base_url):
    oferta = entrar_como_aluno(driver, base_url)
    antes = oferta.vagas()
    oferta.selecionar(["ES3", "BD2"])
    oferta.confirmar()

    comprovante = ComprovantePage(driver)
    assert comprovante.mensagem() == "Matrícula realizada com sucesso!"
    assert re.fullmatch(r"COMP-\d{6}", comprovante.numero())
    assert comprovante.disciplinas() == ["ES3", "BD2"]

    depois = oferta.abrir().vagas()
    assert depois["ES3"] == antes["ES3"] - 1
    assert depois["BD2"] == antes["BD2"] - 1
    assert depois["PW2"] == antes["PW2"]
