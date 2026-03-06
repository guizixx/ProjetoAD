# Grupo: 47
# Guilherme Pinto - nº 60260
# Tiago Telha - nº 60261
# Descrição: Testes adicionais para todos os comandos do sistema MarketCenter

import unittest
import servidor.processador as processador
import re

# USO: python -m unittest testes2.py


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.prc = processador.Processador()
        self.prc.reset()

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

    def assert_ok(self, resp):
        self.assertIn("OK", resp.upper(), f"\n\nEsperado 'OK', mas recebeu: {resp}")
        return resp

    def assert_nok(self, resp):
        self.assertIn("NOK", resp.upper(), f"\n\nEsperado 'NOK', mas recebeu: {resp}")
        return resp

    def assert_msg(self, resp, contains=""):
        if contains is not None:
            self.assertIn(contains, resp, f"\n\nMensagem devia conter '{contains}', mas foi: {resp}")
        return resp

    # --- Helpers ---

    def cria_categoria(self, nome):
        return self.prc.processar_comando(f'CRIA_CATEGORIA {nome}')

    def remove_categoria(self, nome):
        return self.prc.processar_comando(f'REMOVE_CATEGORIA {nome}')

    def lista_categorias(self):
        return self.prc.processar_comando('LISTA_CATEGORIAS')

    def cria_produto(self, nome, categoria, preco, quantidade):
        return self.prc.processar_comando(f'CRIA_PRODUTO "{nome}" "{categoria}" {preco} {quantidade}')

    def lista_produtos(self):
        return self.prc.processar_comando('LISTA_PRODUTOS')

    def aumenta_stock(self, nome, delta):
        return self.prc.processar_comando(f'AUMENTA_STOCK_PRODUTO "{nome}" {delta}')

    def atualiza_preco(self, nome, preco):
        return self.prc.processar_comando(f'ATUALIZA_PRECO_PRODUTO "{nome}" {preco}')

    def cria_cliente(self, nome, email, pw):
        return self.prc.processar_comando(f'CRIA_CLIENTE "{nome}" {email} {pw}')

    def lista_clientes(self):
        return self.prc.processar_comando('LISTA_CLIENTES')

    def adiciona_carrinho(self, id_cliente, nome_produto, quantidade):
        return self.prc.processar_comando(f'ADICIONA_PRODUTO_CARRINHO {id_cliente} "{nome_produto}" {quantidade}')

    def remove_carrinho(self, id_cliente, nome_produto):
        return self.prc.processar_comando(f'REMOVE_PRODUTO_CARRINHO {id_cliente} "{nome_produto}"')

    def lista_carrinho(self, id_cliente):
        return self.prc.processar_comando(f'LISTA_CARRINHO {id_cliente}')

    def checkout_carrinho(self, id_cliente):
        return self.prc.processar_comando(f'CHECKOUT_CARRINHO {id_cliente}')

    def lista_encomendas(self, id_cliente):
        return self.prc.processar_comando(f'LISTA_ENCOMENDAS {id_cliente}')


# -------------------------------------------------------
# LISTA_CATEGORIAS
# -------------------------------------------------------

class TesteListaCategorias(BaseTestCase):

    def teste_lista_categorias_sem_categorias(self):
        resp = self.lista_categorias()
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Sem Categorias")

    def teste_lista_categorias_com_categorias(self):
        self.cria_categoria('Fruta')
        self.cria_categoria('Legumes')
        resp = self.lista_categorias()
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Total Categorias: 2")
        self.assert_msg(resp, contains="Fruta")
        self.assert_msg(resp, contains="Legumes")


# -------------------------------------------------------
# REMOVE_CATEGORIA
# -------------------------------------------------------

class TesteRemoveCategoria(BaseTestCase):

    def teste_remove_categoria_ok(self):
        self.cria_categoria('Fruta')
        resp = self.remove_categoria('Fruta')
        self.assert_ok(resp)
        self.assert_msg(resp, contains="removida com sucesso")

    def teste_remove_categoria_inexistente(self):
        resp = self.remove_categoria('Fruta')
        self.assert_nok(resp)

    def teste_remove_categoria_com_produtos_com_stock(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.0, 10)
        resp = self.remove_categoria('Fruta')
        self.assert_nok(resp)


# -------------------------------------------------------
# CRIA_PRODUTO
# -------------------------------------------------------

class TesteCriaProduto(BaseTestCase):

    def teste_cria_produto_ok(self):
        self.cria_categoria('Fruta')
        resp = self.cria_produto('Banana', 'Fruta', 1.5, 10)
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Produto Banana criado com sucesso")

    def teste_cria_produto_categoria_inexistente(self):
        resp = self.cria_produto('Banana', 'Fruta', 1.5, 10)
        self.assert_nok(resp)

    def teste_cria_produto_preco_invalido(self):
        self.cria_categoria('Fruta')
        resp = self.cria_produto('Banana', 'Fruta', -1, 10)
        self.assert_nok(resp)

    def teste_cria_produto_duplicado(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        resp = self.cria_produto('Banana', 'Fruta', 2.0, 5)
        self.assert_nok(resp)


# -------------------------------------------------------
# LISTA_PRODUTOS
# -------------------------------------------------------

class TesteListaProdutos(BaseTestCase):

    def teste_lista_produtos_sem_produtos(self):
        resp = self.lista_produtos()
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Sem Produtos")

    def teste_lista_produtos_com_produtos(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        resp = self.lista_produtos()
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Total Produtos: 1")
        self.assert_msg(resp, contains="Banana")


# -------------------------------------------------------
# AUMENTA_STOCK_PRODUTO
# -------------------------------------------------------

class TesteAumentaStock(BaseTestCase):

    def teste_aumenta_stock_ok(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        resp = self.aumenta_stock('Banana', 5)
        self.assert_ok(resp)
        self.assert_msg(resp, contains="aumentado em 5 unidades")

    def teste_aumenta_stock_produto_inexistente(self):
        resp = self.aumenta_stock('Banana', 5)
        self.assert_nok(resp)

    def teste_aumenta_stock_delta_invalido(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        resp = self.aumenta_stock('Banana', -1)
        self.assert_nok(resp)


# -------------------------------------------------------
# ATUALIZA_PRECO_PRODUTO
# -------------------------------------------------------

class TesteAtualizaPreco(BaseTestCase):

    def teste_atualiza_preco_ok(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        resp = self.atualiza_preco('Banana', 2.0)
        self.assert_ok(resp)
        self.assert_msg(resp, contains="2.00")

    def teste_atualiza_preco_produto_inexistente(self):
        resp = self.atualiza_preco('Banana', 2.0)
        self.assert_nok(resp)

    def teste_atualiza_preco_invalido(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        resp = self.atualiza_preco('Banana', -1)
        self.assert_nok(resp)


# -------------------------------------------------------
# CRIA_CLIENTE
# -------------------------------------------------------

class TesteCriaCliente(BaseTestCase):

    def teste_cria_cliente_ok(self):
        resp = self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        self.assert_ok(resp)
        self.assert_msg(resp, contains="identificador único 1")

    def teste_cria_cliente_email_duplicado(self):
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        resp = self.cria_cliente('Ana Silva', 'maria@email.com', '5678')
        self.assert_nok(resp)


# -------------------------------------------------------
# LISTA_CLIENTES
# -------------------------------------------------------

class TesteListaClientes(BaseTestCase):

    def teste_lista_clientes_sem_clientes(self):
        resp = self.lista_clientes()
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Sem Clientes")

    def teste_lista_clientes_com_clientes(self):
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        resp = self.lista_clientes()
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Total Clientes: 1")
        self.assert_msg(resp, contains="Maria Silva")


# -------------------------------------------------------
# ADICIONA_PRODUTO_CARRINHO
# -------------------------------------------------------

class TesteAdicionaCarrinho(BaseTestCase):

    def teste_adiciona_carrinho_ok(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        resp = self.adiciona_carrinho(1, 'Banana', 3)
        self.assert_ok(resp)
        self.assert_msg(resp, contains="adicionado com sucesso ao carrinho")

    def teste_adiciona_carrinho_stock_insuficiente(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 2)
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        resp = self.adiciona_carrinho(1, 'Banana', 10)
        self.assert_nok(resp)

    def teste_adiciona_carrinho_cliente_inexistente(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        resp = self.adiciona_carrinho(99, 'Banana', 3)
        self.assert_nok(resp)


# -------------------------------------------------------
# REMOVE_PRODUTO_CARRINHO
# -------------------------------------------------------

class TesteRemoveCarrinho(BaseTestCase):

    def teste_remove_carrinho_ok(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        self.adiciona_carrinho(1, 'Banana', 3)
        resp = self.remove_carrinho(1, 'Banana')
        self.assert_ok(resp)
        self.assert_msg(resp, contains="removido com sucesso do carrinho")

    def teste_remove_carrinho_produto_nao_no_carrinho(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        resp = self.remove_carrinho(1, 'Banana')
        self.assert_nok(resp)


# -------------------------------------------------------
# LISTA_CARRINHO
# -------------------------------------------------------

class TesteListaCarrinho(BaseTestCase):

    def teste_lista_carrinho_vazio(self):
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        resp = self.lista_carrinho(1)
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Carrinho Vazio")

    def teste_lista_carrinho_com_produtos(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.50, 10)
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        self.adiciona_carrinho(1, 'Banana', 2)
        resp = self.lista_carrinho(1)
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Total Produtos: 1")
        self.assert_msg(resp, contains="Total Quantidade: 2")
        self.assert_msg(resp, contains="3.00 euros")
        self.assert_msg(resp, contains="Banana")


# -------------------------------------------------------
# CHECKOUT_CARRINHO
# -------------------------------------------------------

class TesteCheckoutCarrinho(BaseTestCase):

    def teste_checkout_ok(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        self.adiciona_carrinho(1, 'Banana', 3)
        resp = self.checkout_carrinho(1)
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Encomenda criada com sucesso")

    def teste_checkout_carrinho_vazio(self):
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        resp = self.checkout_carrinho(1)
        self.assert_nok(resp)

    def teste_checkout_esvazia_carrinho(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        self.adiciona_carrinho(1, 'Banana', 3)
        self.checkout_carrinho(1)
        resp = self.lista_carrinho(1)
        self.assert_msg(resp, contains="Carrinho Vazio")


# -------------------------------------------------------
# LISTA_ENCOMENDAS
# -------------------------------------------------------

class TesteListaEncomendas(BaseTestCase):

    def teste_lista_encomendas_sem_encomendas(self):
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        resp = self.lista_encomendas(1)
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Sem encomendas.")

    def teste_lista_encomendas_com_encomenda(self):
        self.cria_categoria('Fruta')
        self.cria_produto('Banana', 'Fruta', 1.5, 10)
        self.cria_cliente('Maria Silva', 'maria@email.com', '1234')
        self.adiciona_carrinho(1, 'Banana', 2)
        self.checkout_carrinho(1)
        resp = self.lista_encomendas(1)
        self.assert_ok(resp)
        self.assert_msg(resp, contains="Total Encomendas: 1")
        self.assert_msg(resp, contains="Banana")

    def teste_lista_encomendas_cliente_inexistente(self):
        resp = self.lista_encomendas(99)
        self.assert_nok(resp)


if __name__ == "__main__":
    unittest.main()