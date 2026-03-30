# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: classe de domínio responsável pela lógica de negócio
#               responde aos pedidos do processador 
#               guarda os dados sobre as entidades (cliente, produto etc.)

from operator import itemgetter
from shared.utilities import normalizar_nome
from shared import excepcoes_shared
from servidor.excepcoes import ExcepcaoComandoInvalido, ExcepcaoSupermercadoCategoriaJaExistente
from servidor.categoria import Categoria
from servidor.produto import Produto
from servidor.clienteLoja import ClienteLoja
from servidor.encomenda import Encomenda
from datetime import datetime
from copy import deepcopy

class Loja:

    def __init__(self):
        self._categorias = {}
        self._produtos = {}
        self._clientes = {}
        self._encomendas = {}

        # todos os dicionários atributo são do tipo { id : objeto }

    def reset(self): 
        Categoria._contador_global = 1
        Produto._contador_global = 1
        Encomenda._contador_global = 1
        self._categorias = {}
        self._produtos = {}
        self._clientes = {}
        self._encomendas = {}
        # TODO: MUITO IMPORTANTE Completar esta funcao para Testes Unitários puderem executar sem problemas

    # -----------------------------
    # Categorias
    # -----------------------------
    def criar_categoria(self, nome):
        if self.obter_id_categoria(nome) is not None:
            raise excepcoes_shared.CategoriaJaExiste(nome)
        categoria = Categoria(nome)
        self._categorias[categoria.obter_id()] = categoria
        return categoria
    
    def lista_categorias(self):
        if len(self._categorias.values()) == 0:
            return [], []
        cats = [cat for cat in self._categorias.values()]
        prods =[prod for prod in self._produtos.values()]
        return cats, prods
    
    def obter_id_categoria(self, nome): 
        for c in self._categorias.values(): 
            if nome == c.obter_nome(): 
                return c.obter_id()
        return None
    
    def obter_nr_produtos_categoria(self, nome):
        counter = 0
        for p in self._produtos.values():
            if p.obter_categoria() == nome:
                counter += 1
        return counter
    
    def remover_categoria(self, nome):
        categoria_id = self.obter_id_categoria(nome)
        if categoria_id is None:
            raise excepcoes_shared.CategoriaNaoExiste()
        if self.obter_nr_produtos_categoria(nome) > 0:
            raise excepcoes_shared.CategoriaComProdutos()
        self._categorias.pop(categoria_id)
        return self._categorias.get(categoria_id)
    
    #-----------------------
    # Produtos
    #-----------------------
    def criar_produto(self, nome_produto, nome_categoria, preco, quantidade):
        for p in self._produtos.values():
            if nome_produto == p.obter_nome():
                raise excepcoes_shared.ProdutoJaExiste()
        if self.obter_id_categoria(nome_categoria) is None:
            raise excepcoes_shared.CategoriaNaoExiste()
        if preco <= 0:
            raise excepcoes_shared.PrecoInvalido()
        if quantidade < 0:
            raise excepcoes_shared.QuantidadeInvalida()
        
        produto = Produto(nome_produto, nome_categoria, preco, quantidade)
        self._produtos[produto.obter_id()] = produto
        return produto

    def listar_produtos(self):
        if len(self._produtos.values()) == 0:
            return [], []
        cats = [cat for cat in self._categorias.values()]
        prods =[prod for prod in self._produtos.values()]
        return cats, prods
    
    def obter_id_produto(self, nome):
        for p in self._produtos.values():
            if p.obter_nome() == nome:
                return p.obter_id()
        return None
    
    def aumentar_stock_produto(self, nome, quantidade):
        id_prod = self.obter_id_produto(nome)
        if id_prod is None:
            raise excepcoes_shared.ProdutoNaoExiste()
        if int(quantidade) < 0:
            raise excepcoes_shared.QuantidadeInvalida()
        self._produtos.get(id_prod).adicionar_quantidade(quantidade)
        return self._produtos.get(id_prod)

    def atualizar_preco_produto(self, nome, novo_preco):
        id_prod = self.obter_id_produto(nome)
        if id_prod is None:
            raise excepcoes_shared.ProdutoNaoExiste()
        if novo_preco < 0:
            raise excepcoes_shared.PrecoInvalido()
        
        self._produtos.get(id_prod).alterar_preco(novo_preco)
        return self._produtos.get(id_prod)
    #---------------
    # Clientes
    #---------------
    def criar_cliente(self, nome, email, pw, id_cliente, permissao):
        if id_cliente in self._clientes.keys():
            raise excepcoes_shared.UtilizadorInvalido()
        
        if permissao == 0:
            permissao = 1 # se for anónimo, passa a ser cliente registado
        
        for c in self._clientes.values():
            if c.obter_email() == email.lower():
                raise excepcoes_shared.EmailJaExiste()
        cliente = ClienteLoja(nome, email, pw, id_cliente, permissao)
        self._clientes[id_cliente] = cliente
        return cliente

    def listar_clientes(self):
        if len(self._clientes.values()) == 0:
            return []
        return [c for c in self._clientes.values()]
    
    #--------------
    # Carrinho
    #--------------
    def adiciona_produto_carrinho(self, id_cliente, nome_produto, quantidade):
        self.validar_id(id_cliente)
        if self.obter_id_produto(nome_produto) is None:
            raise excepcoes_shared.ProdutoNaoExiste()
        if quantidade <= 0:
            raise excepcoes_shared.QuantidadeInvalida()
        if self._produtos.get(self.obter_id_produto(nome_produto)).obter_quantidade() < quantidade:
            raise excepcoes_shared.StockInsuficiente()

        id_produto = self.obter_id_produto(nome_produto)
        if id_produto in self._clientes.get(id_cliente).obter_carrinho_compras().keys():
            self._clientes.get(id_cliente).obter_carrinho_compras()[id_produto] += quantidade
        else:
            self._clientes.get(id_cliente).obter_carrinho_compras()[id_produto] = quantidade
        self._produtos.get(id_produto).adicionar_quantidade(-quantidade)
        return self._produtos.get(id_produto)
    
    def remover_produto_carrinho(self, id_cliente, nome_produto):
        self.validar_id(id_cliente)
        if self.obter_id_produto(nome_produto) is None:
            raise excepcoes_shared.ProdutoNaoExiste()

        id_produto = self.obter_id_produto(nome_produto)
        carrinho = self._clientes.get(id_cliente).obter_carrinho_compras()

        if id_produto not in carrinho.keys():
            raise excepcoes_shared.ProdutoNaoNoCarrinho()

        quantidade = carrinho[id_produto]
        carrinho.pop(id_produto)
        self._produtos.get(id_produto).adicionar_quantidade(quantidade)
        return self._produtos.get(id_produto)

    def lista_carrinho_cliente(self, id_cliente):
        self.validar_id(id_cliente)
        carrinho = self._clientes.get(id_cliente).obter_carrinho_compras()
        if len(carrinho) < 1:
            return [], []
        cats = []
        prods = []
        for k in carrinho.keys():
            prod = self._produtos.get(k)
            prods.append(prod)
            cat = prod.obter_categoria()
            if cat not in cats:
                cats.append(cat)
        return cats, prods

    def checkout_carrinho(self, id_cliente):
        self.validar_id(id_cliente)
        if len(self._clientes.get(id_cliente).obter_carrinho_compras()) < 1:
            raise excepcoes_shared.CarrinhoVazio()
        total = 0
        for k in self._clientes.get(id_cliente).obter_carrinho_compras().keys():
            prod = self._produtos.get(k)
            total += (prod.obter_preco() * self._clientes.get(id_cliente).obter_carrinho_compras().get(k))

        # carrinho passa a guardar [quantidade, preço] em vez de quantidade
        # para guardar o preço do produto no momento da encomenda
        carrinho_encomenda = deepcopy(self._clientes.get(id_cliente).obter_carrinho_compras())
        for k in carrinho_encomenda.keys():
            carrinho_encomenda[k] = [carrinho_encomenda.get(k), self._produtos.get(k).obter_preco()]

        encomenda = Encomenda(datetime.now().replace(microsecond=0), carrinho_encomenda, id_cliente, total)
        self._encomendas[encomenda.obter_id()] = encomenda
        self._clientes.get(id_cliente).obter_carrinho_compras().clear()
        return encomenda

    #-----------------
    # Encomendas
    #-----------------
    def lista_encomendas(self, id_cliente):
        self.validar_id(id_cliente)
        encomendas_cliente = []
        produtos_por_encomenda = []
        nr_encomendas_cliente = 0
        for e in self._encomendas.values():
            if e.obter_cliente_id() == id_cliente:
                nr_encomendas_cliente += 1
                encomendas_cliente.append(e)

                # produtos da encomenda
                carrinho_encomenda = e.obter_carrinho_compras()
                produtos_encomenda = []

                for k in carrinho_encomenda.keys():
                    produtos_encomenda.append(self._produtos.get(k))
                produtos_por_encomenda.append(produtos_encomenda)

        return encomendas_cliente, produtos_por_encomenda
    

    #-----------------
    # AUXILIARES
    #-----------------
    def validar_utilizador(self, perfil, utilizador, operacao):
        # print("OPCODE dentro de validar_utilizador da loja: ", operacao)
        if (operacao != excepcoes_shared.OpCodes.CRIA_CLIENTE) & (utilizador not in self._clientes.keys()):
            raise excepcoes_shared.UtilizadorInvalido()
        
        if (operacao != excepcoes_shared.OpCodes.CRIA_CLIENTE) and (self._clientes.get(utilizador).obter_permissao() != perfil):
            raise excepcoes_shared.OperacaoNaoAutorizada()
        
    def validar_id(self, id_cliente):
        if id_cliente not in self._clientes.keys():
            raise excepcoes_shared.UtilizadorInvalido()
        
        # de certeza que vao faltar casos a adicionar aqui para poder validar o utilizador em todas as situaçoes

    def criar_funcionarios(self):
        f1 = ClienteLoja("f1", "f1@", "f1", 1000000, 2)
        f2 = ClienteLoja("f2", "f2@", "f2", 1000001, 2)
        a1 = ClienteLoja("a1", "a1@", "a1", 1000002, 3)
        a2 = ClienteLoja("a2", "a2@", "a2", 1000003, 3)
