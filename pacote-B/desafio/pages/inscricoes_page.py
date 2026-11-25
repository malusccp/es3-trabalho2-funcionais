from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


class InscricoesPage:
    NOME = (By.ID, "nome")
    EMAIL = (By.ID, "email")
    CURSO = (By.ID, "curso")
    CONFIRMAR = (By.ID, "confirmar")
    ERRO = (By.ID, "erro")
    SUCESSO = (By.ID, "sucesso")
    ITENS = (By.CSS_SELECTOR, "#lista li")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 5)

    def abrir(self):
        self.driver.get(f"{self.base_url}/inscricoes")
        self.wait.until(EC.element_to_be_clickable(self.CONFIRMAR))
        return self

    def inscrever(self, nome, email, curso=""):
        self.driver.find_element(*self.NOME).send_keys(nome)
        self.driver.find_element(*self.EMAIL).send_keys(email)
        if curso:
            Select(self.driver.find_element(*self.CURSO)).select_by_value(curso)
        self.driver.find_element(*self.CONFIRMAR).click()

    def cancelar(self, id_inscricao):
        botao = self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f'[data-testid="cancelar-{id_inscricao}"]')))
        botao.click()

    def erro(self):
        # o texto só aparece depois da resposta do servidor
        return self.wait.until(lambda d: d.find_element(*self.ERRO).text or False)

    def sucesso(self):
        return self.wait.until(lambda d: d.find_element(*self.SUCESSO).text or False)

    def aguardar_itens(self, quantidade):
        # a lista é atualizada depois da mensagem, então espera a quantidade certa
        self.wait.until(lambda d: len(d.find_elements(*self.ITENS)) == quantidade)

    def textos_da_lista(self):
        return [li.text for li in self.driver.find_elements(*self.ITENS)]
