from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginMatriculaPage:
    MATRICULA = (By.ID, "matricula")
    SENHA = (By.ID, "senha")
    ENTRAR = (By.ID, "btn-entrar")
    ERRO = (By.ID, "mensagem-erro")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 5)

    def abrir(self):
        self.driver.get(f"{self.base_url}/matricula/login")
        return self

    def entrar(self, matricula, senha):
        self.wait.until(EC.visibility_of_element_located(self.MATRICULA)).send_keys(matricula)
        self.driver.find_element(*self.SENHA).send_keys(senha)
        self.driver.find_element(*self.ENTRAR).click()

    def erro(self):
        return self.wait.until(EC.visibility_of_element_located(self.ERRO)).text


class DisciplinasPage:
    TABELA = (By.ID, "tabela-disciplinas")
    CONFIRMAR = (By.ID, "btn-confirmar")
    ERRO = (By.ID, "mensagem-erro")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 5)

    def abrir(self):
        self.driver.get(f"{self.base_url}/matricula/disciplinas")
        return self

    def esta_aberta(self):
        return self.wait.until(EC.visibility_of_element_located(self.TABELA)).is_displayed()

    def tabela_aparece(self):
        return len(self.driver.find_elements(*self.TABELA)) > 0

    def selecionar(self, codigos):
        for codigo in codigos:
            self.wait.until(EC.element_to_be_clickable((By.ID, f"chk-{codigo}"))).click()

    def confirmar(self):
        self.driver.find_element(*self.CONFIRMAR).click()

    def erro(self):
        return self.wait.until(EC.visibility_of_element_located(self.ERRO)).text

    def vagas(self):
        self.esta_aberta()
        vagas = {}
        for linha in self.driver.find_elements(By.CSS_SELECTOR, "[data-testid^='disc-']"):
            codigo = linha.get_attribute("data-testid").replace("disc-", "")
            vagas[codigo] = int(linha.find_element(By.CSS_SELECTOR, ".vagas").text)
        return vagas


class ComprovantePage:
    SUCESSO = (By.ID, "mensagem-sucesso")
    COMPROVANTE = (By.ID, "comprovante")
    DISCIPLINAS = (By.ID, "disciplinas-matriculadas")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

    def mensagem(self):
        return self.wait.until(EC.visibility_of_element_located(self.SUCESSO)).text

    def numero(self):
        return self.driver.find_element(*self.COMPROVANTE).text

    def disciplinas(self):
        return self.driver.find_element(*self.DISCIPLINAS).text.split(", ")
