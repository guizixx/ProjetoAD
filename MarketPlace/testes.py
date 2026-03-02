import unittest
import servidor.processador as processador
import re


# USO:  python -m unittest testes.py

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.prc = processador.Processador()
        self.prc.reset()

    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

    def normalizar_texto(self, nome): 
        # remove espaços extremos
        nome = nome.strip()

        nome = nome.replace('"', '').replace("'", '')

        # substitui múltiplos espaços por 1 só
        nome = re.sub(r'\s+', ' ', nome)

        # lower case
        return nome
    
    def assert_msg(self, resp, contains=""):
        if contains is not None:
            self.assertIn(contains, resp, f"\n\nMensagem devia conter '{contains}', mas foi: {resp}") 
        return resp
    
    def assert_ok(self, resp):
        ok_nok = resp.upper()
        self.assertIn("OK", ok_nok, f"\n\nEsperado 'OK', mas recebeu: {resp}")
        return resp
    
    def assert_nok(self, resp):
        ok_nok = resp.upper()
        self.assertIn("NOK", ok_nok, f"\n\nEsperado 'NOK', mas recebeu: {resp}")
        return resp
    
    def cria_categoria(self, nome): 
        return self.prc.processar_comando(f'CRIA_CATEGORIA {nome}')



class TesteCriaCategoria(BaseTestCase):

    # Testes funcionais

    def teste_funcional_cria_categoria_validar_ok(self):
        resp = self.cria_categoria('Livros')
        self.assert_ok(resp)

    def teste_funcional_cria_categoria_validar_msg(self):
        resp = self.cria_categoria('Livros')
        self.assert_msg(resp, contains="Categoria Livros criada com sucesso")

    def teste_funcional_cria_categoria_validar_msg_avancado(self):
        resp = self.cria_categoria('Livros')
        self.assert_msg(resp, contains="Categoria Livros criada com sucesso")

    # Testes de Formatacao

    def teste_formatacao_cria_categoria_por_normalizar_validar_ok(self):
        resp = self.cria_categoria('livros')
        self.assert_ok(resp)

    def teste_formatacao_cria_categoria_por_normalizar_validar_msg(self):
        resp = self.cria_categoria('livros')
        self.assert_msg(resp, contains="Categoria Livros criada com sucesso")

    def teste_formatacao_cria_categoria_com_espacos_validar_ok(self):
        resp = self.cria_categoria('"Electrodomésticos Pequenos"')
        self.assert_ok(resp)

    def teste_formatacao_cria_categoria_com_espacos_validar_msg(self):
        resp = self.cria_categoria('"Electrodomésticos Pequenos"')
        self.assert_msg(resp, contains="Categoria Electrodomésticos Pequenos criada com sucesso")
    
    def teste_formatacao_cria_categoria_com_espacos_redundantes_validar_ok(self):
        resp = self.cria_categoria('"Electrodomésticos  Pequenos"')
        self.assert_ok(resp)

    def teste_formatacao_cria_categoria_com_espacos_redundantes_validar_msg(self):
        resp = self.cria_categoria('"Electrodomésticos  Pequenos"')
        self.assert_msg(resp, contains="Categoria Electrodomésticos Pequenos criada com sucesso")
    
    def teste_formatacao_cria_categoria_preposicoes_minusculas_validar_ok(self):
        resp = self.cria_categoria('"Electrodomésticos de Venda"')
        self.assert_ok(resp)
    
    def teste_formatacao_cria_categoria_preposicoes_minusculas_validar_msg(self):
        resp = self.cria_categoria('"Electrodomésticos de Venda"')
        self.assert_msg(resp, contains="Categoria Electrodomésticos De Venda criada com sucesso")

