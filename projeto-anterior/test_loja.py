import re

import pytest

from pages.loja_pages import CarrinhoPage, CatalogoPage, PedidoPage

MSG_QUANTIDADE = "Quantidade deve ser de 1 a 10"


@pytest.fixture
def catalogo(driver, front_url):
    return CatalogoPage(driver, front_url).abrir()


@pytest.fixture
def carrinho(driver):
    return CarrinhoPage(driver)


@pytest.fixture
def pedido(driver):
    return PedidoPage(driver)


def montar_carrinho_de_30_reais(catalogo, carrinho):
    # 5 x Pistachio Cake (4,80) + 3 x Spinach (2,00) = R$ 30,00
    catalogo.adicionar(9)
    carrinho.alterar_quantidade(9, 5)
    catalogo.adicionar(4)
    carrinho.alterar_quantidade(4, 3)


def test_ct01_busca_ignora_caixa_e_espacos(catalogo):
    catalogo.buscar(" aPPle ")
    assert catalogo.ids_visiveis() == [1]
    assert catalogo.contador() == "1 produto(s)"


def test_ct02_busca_sem_resultado(catalogo):
    catalogo.buscar("xyz")
    assert catalogo.sem_resultados() == "Nenhum produto encontrado"
    assert catalogo.contador() == "0 produto(s)"
    assert catalogo.ids_visiveis() == []


def test_ct03_filtro_estoque_combina_com_busca(catalogo):
    catalogo.buscar("cake")
    catalogo.marcar_estoque()
    assert catalogo.ids_visiveis() == [7, 9]
    assert catalogo.contador() == "2 produto(s)"


def test_ct04_produto_esgotado_nao_adiciona(catalogo, carrinho):
    botao = catalogo.botao_adicionar(3)
    assert not botao.is_enabled()
    assert botao.text == "Esgotado"
    assert carrinho.vazio()


def test_ct05_adicionar_e_totais(catalogo, carrinho):
    catalogo.adicionar(1)
    assert carrinho.item_aparece(1)
    assert carrinho.totais() == {"subtotal": 100, "desconto": 0, "frete": 500, "total": 600}


@pytest.mark.parametrize("valor, aceita", [(0, False), (10, True), (11, False)], ids=["0", "10", "11"])
def test_quantidade(catalogo, carrinho, valor, aceita):
    catalogo.adicionar(1)
    carrinho.alterar_quantidade(1, valor)
    if aceita:
        assert carrinho.centavos("subtotal") == 100 * valor
        assert not carrinho.erro_aparece()
    else:
        assert carrinho.erro() == MSG_QUANTIDADE
        assert carrinho.centavos("subtotal") == 100


def test_ct09_frete_gratis_no_limite(catalogo, carrinho):
    montar_carrinho_de_30_reais(catalogo, carrinho)
    assert carrinho.totais() == {"subtotal": 3000, "desconto": 0, "frete": 0, "total": 3000}


def test_ct10_cupom_faz_perder_frete_gratis(catalogo, carrinho):
    montar_carrinho_de_30_reais(catalogo, carrinho)
    carrinho.aplicar_cupom(" promo10 ")
    assert carrinho.mensagem_cupom() == "Cupom aplicado: 10% de desconto"
    assert carrinho.totais() == {"subtotal": 3000, "desconto": 300, "frete": 500, "total": 3200}


def test_ct11_email_invalido_bloqueia_pedido(catalogo, carrinho, pedido,
                                             estoque_pela_api, status_do_pedido_pela_api):
    catalogo.adicionar(1)
    pedido.finalizar("Maria Souza", "maria.ads.local")
    assert pedido.erro() == "E-mail inválido"
    assert carrinho.item_aparece(1)
    assert not pedido.sucesso_aparece()
    assert status_do_pedido_pela_api("PED-000001") == 404
    assert estoque_pela_api(1) == 40


def test_ct12_pedido_com_sucesso(catalogo, carrinho, pedido, estoque_pela_api):
    catalogo.adicionar(1)
    pedido.finalizar("Maria Souza", "maria@ads.local")
    assert pedido.sucesso() == "Pedido realizado"
    assert re.fullmatch(r"PED-\d{6}", pedido.numero())
    assert carrinho.vazio()
    assert pedido.nome_digitado() == ""
    assert estoque_pela_api(1) == 39


def test_ct13_estoque_insuficiente(catalogo, carrinho, pedido,
                                   estoque_pela_api, status_do_pedido_pela_api):
    catalogo.adicionar(9)
    carrinho.alterar_quantidade(9, 9)
    pedido.finalizar("Maria Souza", "maria@ads.local")
    assert pedido.erro() == "Estoque insuficiente: Pistachio Cake"
    assert carrinho.item_aparece(9)
    assert estoque_pela_api(9) == 8
    assert status_do_pedido_pela_api("PED-000001") == 404
