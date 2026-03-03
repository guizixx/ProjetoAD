# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 
# Descrição: 

from shared.utilities import normalizar_nome
from servidor.excepcoes import ExcepcaoComandoInvalido, ExcepcaoSupermercadoCategoriaJaExistente
from servidor.categoria import Categoria
from servidor.produto import Produto
from servidor.clienteLoja import ClienteLoja

class Loja:

    def __init__(self):
        self._categorias = {}
        self._produtos = {}
        self._clientes = {}

        # todos os dicionários atributo são do tipo { id : objeto }

    def reset(): 
        Categoria._contador_global = 1
        # TODO: MUITO IMPORTANTE Completar esta funcao para Testes Unitários puderem executar sem problemas

    # -----------------------------
    # Categorias
    # -----------------------------
    def criar_categoria(self, nome):
        nome = normalizar_nome(nome)
        if self.obter_id_categoria(nome) is not None:
            raise ExcepcaoSupermercadoCategoriaJaExistente(nome)
        categoria = Categoria(nome)
        self._categorias[categoria.id] = categoria
        return categoria
    
    def lista_categorias(self):
        if len(self._categorias.values()) == 0:
            return "OK; Sem Categorias."
        prints = f"OK;\nTotal Categorias: {len(self._categorias.values())}\nTotal Produtos: {self._produtos.values()}\n\n"
        for c in self._categorias.values():
            prints + f"{c.id} - {c.nome}({self.obter_nr_produtos_categoria(c.nome)});\n"
        return prints
    
    def obter_id_categoria(self, nome): 
        for c in self._categorias.values(): 
            if nome == c.nome: 
                return c.id
        return None
    
    def obter_nr_produtos_categoria(self, nome):
        counter = 0
        for p in self._produtos.values():
            if p.categoria == nome:
                counter += 1
        return counter
    
    def remover_categoria(self, nome):
        categoria_id = self.obter_id_categoria(normalizar_nome(nome))
        if categoria_id is None:
            raise ExcepcaoComandoInvalido("Categoria Inexistente")
        if self.obter_nr_produtos_categoria(nome) > 0:
            raise ExcepcaoComandoInvalido(f"Categoria {nome} ainda tem produtos associados.")
        self._categorias.pop(categoria_id)
        return nome 
    
    #-----------------------
    # Produtos
    #-----------------------
    def criar_produto(self, nome_produto, nome_categoria, preco, quantidade):

        for p in self._produtos.values():
            if nome_produto == p.nome():
                raise ExcepcaoComandoInvalido("Nome do produto já existe.")

        if self.obter_id_categoria(nome_categoria) is None:
            raise ExcepcaoComandoInvalido("Categoria não existe.")

        if preco <= 0:
            raise ExcepcaoComandoInvalido("Preço inválido.")

        if quantidade < 0:
            raise ExcepcaoComandoInvalido("Quantidade inválida.")
        produto = Produto(nome_produto, nome_categoria, preco, quantidade)
        self._produtos[produto.id] = produto
        return produto 

    def listar_produtos(self):
        if len(self._produtos.values()) == 0:
            return "OK; Sem Produtos."
        quantidade_total = 0
        for p in self._produtos.values():
            quantidade_total += p.quantidade
        prints = f"OK;\nTotal Produtos: {len(self._produtos.values())}\nTotal Quantidade: {quantidade_total}\n\n"
        for p in self._produtos.values():
            prints + f"{p.id} - {p.nome}({p.categoria}, {p.preco}, {p._quantidade} unidades);\n"
        return prints
    
    def obter_id_produto(self, nome):
        for p in self._produtos.values():
            if p.nome == nome:
                return p.id
        return None
    
    def aumentar_stock_produto(self, nome, quantidade):
        self._produtos.get(self.obter_id_produto(nome)).quantidade += quantidade

    def atualizar_preco_produto(self, nome, novo_preco):
        self._produtos.get(self.obter_id_produto(nome)).preco = novo_preco

    #---------------
    # Clientes
    #---------------

    def criar_cliente(self, nome, email, pw):
        for c in self._clientes.values():
            if c.email == email.lower():
                raise ExcepcaoComandoInvalido("NOK; Email em uso.")
        cliente = ClienteLoja(nome, email, pw)
        self._clientes[cliente.id] = cliente
        return cliente


    def listar_clientes(self):
        if len(self._clientes.values()) == 0:
            return "OK; Sem Clientes."
        
        prints = f"OK;\nTotal Clientes: {len(self._clientes.values())}\n\n"
        for c in self._clientes.values():
            prints + f"{c.id} - {c.nome}({c.email});\n"
        return prints
    
