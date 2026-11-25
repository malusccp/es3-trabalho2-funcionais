from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def por_testid(valor):
    return (By.CSS_SELECTOR, f'[data-testid="{valor}"]')


class CatalogoPage:
    CAMPO_BUSCA = por_testid("campo-busca")
    FILTRO_ESTOQUE = por_testid("filtro-estoque")
    CONTADOR = por_testid("contador-resultados")
    SEM_RESULTADOS = por_testid("sem-resultados")
    PRODUTOS = (By.CSS_SELECTOR, '[data-testid^="produto-"]')

    def __init__(self, driver, front_url):
        self.driver = driver
        self.front_url = front_url
        self.wait = WebDriverWait(driver, 5)

    def abrir(self):
        self.driver.get(self.front_url)
        # espera os produtos virem do servidor
        self.wait.until(EC.visibility_of_element_located(por_testid("produto-1")))
        return self

    def buscar(self, texto):
        campo = self.wait.until(EC.visibility_of_element_located(self.CAMPO_BUSCA))
        campo.clear()
        campo.send_keys(texto)

    def marcar_estoque(self):
        self.driver.find_element(*self.FILTRO_ESTOQUE).click()

    def ids_visiveis(self):
        ids = [p.get_attribute("data-testid").replace("produto-", "") for p in
               self.driver.find_elements(*self.PRODUTOS)]
        return sorted(int(i) for i in ids)

    def contador(self):
        return self.wait.until(EC.visibility_of_element_located(self.CONTADOR)).text

    def sem_resultados(self):
        return self.wait.until(EC.visibility_of_element_located(self.SEM_RESULTADOS)).text

    def botao_adicionar(self, id_produto):
        return self.wait.until(EC.visibility_of_element_located(por_testid(f"adicionar-{id_produto}")))

    def adicionar(self, id_produto):
        self.wait.until(EC.element_to_be_clickable(por_testid(f"adicionar-{id_produto}"))).click()


class CarrinhoPage:
    ERRO = por_testid("erro-carrinho")
    VAZIO = por_testid("carrinho-vazio")
    CAMPO_CUPOM = por_testid("campo-cupom")
    APLICAR_CUPOM = por_testid("aplicar-cupom")
    MENSAGEM_CUPOM = por_testid("mensagem-cupom")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

    def item_aparece(self, id_produto):
        return len(self.driver.find_elements(*por_testid(f"item-{id_produto}"))) > 0

    def vazio(self):
        return self.wait.until(EC.visibility_of_element_located(self.VAZIO)).is_displayed()

    def alterar_quantidade(self, id_produto, valor):
        campo = self.wait.until(EC.visibility_of_element_located(por_testid(f"quantidade-{id_produto}")))
        campo.send_keys(Keys.CONTROL, "a")  # troca o valor sem passar por campo vazio
        campo.send_keys(str(valor))

    def erro(self):
        return self.wait.until(EC.visibility_of_element_located(self.ERRO)).text

    def erro_aparece(self):
        return len(self.driver.find_elements(*self.ERRO)) > 0

    def centavos(self, nome):
        elemento = self.wait.until(EC.visibility_of_element_located(por_testid(nome)))
        return int(elemento.get_attribute("data-centavos"))

    def totais(self):
        return {nome: self.centavos(nome) for nome in ("subtotal", "desconto", "frete", "total")}

    def aplicar_cupom(self, cupom):
        campo = self.wait.until(EC.visibility_of_element_located(self.CAMPO_CUPOM))
        campo.send_keys(cupom)
        self.driver.find_element(*self.APLICAR_CUPOM).click()

    def mensagem_cupom(self):
        return self.wait.until(EC.visibility_of_element_located(self.MENSAGEM_CUPOM)).text


class PedidoPage:
    CAMPO_NOME = por_testid("campo-nome")
    CAMPO_EMAIL = por_testid("campo-email")
    FINALIZAR = por_testid("finalizar")
    ERRO = por_testid("erro-pedido")
    SUCESSO = por_testid("sucesso-pedido")
    NUMERO = por_testid("numero-pedido")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

    def finalizar(self, nome, email):
        self.wait.until(EC.visibility_of_element_located(self.CAMPO_NOME)).send_keys(nome)
        self.driver.find_element(*self.CAMPO_EMAIL).send_keys(email)
        self.wait.until(EC.element_to_be_clickable(self.FINALIZAR)).click()

    def erro(self):
        return self.wait.until(EC.visibility_of_element_located(self.ERRO)).text

    def sucesso(self):
        return self.wait.until(EC.visibility_of_element_located(self.SUCESSO)).text

    def sucesso_aparece(self):
        return len(self.driver.find_elements(*self.SUCESSO)) > 0

    def numero(self):
        return self.wait.until(EC.visibility_of_element_located(self.NUMERO)).text

    def nome_digitado(self):
        return self.driver.find_element(*self.CAMPO_NOME).get_attribute("value")
