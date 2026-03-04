# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 
# Descrição: 

from shared.utilities import normalizar_nome
from servidor.excepcoes import ExcepcaoComandoInvalido, ExcepcaoSupermercadoCategoriaJaExistente
from servidor.categoria import Categoria
from servidor.produto import Produto
from servidor.clienteLoja import ClienteLoja
from servidor.encomenda import Encomenda
from datetime import _Date

class Loja:

    def __init__(self):
        self._categorias = {}
        self._produtos = {}
        self._clientes = {}
        self._encomendas = {}

        # todos os dicionários atributo são do tipo { id : objeto }

    def reset(): 
        Categoria._contador_global = 1
        Produto._contador_global = 1
        Encomenda._contador_global = 1
        ClienteLoja._contador_global = 1
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
            raise ExcepcaoComandoInvalido("NOK; Categoria Inexistente")
        if self.obter_nr_produtos_categoria(nome) > 0:
            raise ExcepcaoComandoInvalido(f"NOK; Categoria {nome} ainda tem produtos associados.")
        self._categorias.pop(categoria_id)
        return nome 
    
    #-----------------------
    # Produtos
    #-----------------------
    def criar_produto(self, nome_produto, nome_categoria, preco, quantidade):
        for p in self._produtos.values():
            if nome_produto == p.nome():
                raise ExcepcaoComandoInvalido("NOK; Nome do produto já existe.")
        if self.obter_id_categoria(nome_categoria) is None:
            raise ExcepcaoComandoInvalido("NOK; Categoria não existe.")
        if preco <= 0:
            raise ExcepcaoComandoInvalido("NOK; Preço inválido.")
        if quantidade < 0:
            raise ExcepcaoComandoInvalido("NOK; Quantidade inválida.")
        
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
    
    #--------------
    # Carrinho
    #--------------
    def adiciona_produto_carrinho(self, id_cliente, nome_produto, quantidade):
        if id_cliente not in self._clientes.keys():
            raise ExcepcaoComandoInvalido("NOK; Cliente não identificado.")
        if self.obter_id_produto(nome_produto) is None:
            raise ExcepcaoComandoInvalido("NOK; Produto inexistente na loja.")
        if quantidade < 0 | self._produtos.get(self.obter_id_produto(nome_produto)).quantidade < quantidade:
            raise ExcepcaoComandoInvalido("NOK; Quantidade inválida.")
        
        produto_no_carrinho = False
        for p in self._clientes.get(id_cliente).carrinho_compras.keys():
            if p == self.obter_id_produto(nome_produto):
                produto_no_carrinho = True
        if produto_no_carrinho is True:
            self._clientes.get(id_cliente).carrinho_compras[p] += quantidade
        else:
            self._clientes.get(id_cliente).carrinho_compras[p] = quantidade
        
        self._produtos[self.obter_id_produto(nome_produto)] -= quantidade
    
    def remover_produto_carrinho(self, id_cliente, nome_produto):
        if id_cliente not in self._clientes.keys():
            raise ExcepcaoComandoInvalido("NOK; Id inválido.")
        if self.obter_id_produto(nome_produto) is None:
            raise ExcepcaoComandoInvalido("NOK; Produto inexistente na loja.")
        if nome_produto not in self._clientes.get(id_cliente).carrinho_compras().keys():
            raise ExcepcaoComandoInvalido("NOK; O cliente não possui esse produto.")
        
        self._clientes.get(id_cliente).carrinho_compras().pop(self.obter_id_produto(nome_produto))

    def lista_carrinho_cliente(self, id_cliente):
        if id_cliente not in self._clientes.keys():
            raise ExcepcaoComandoInvalido("NOK; Id inválido.")
        carrinho = self._clientes.get(id_cliente).carrinho_compras()
        if len(carrinho) < 1:
            return "OK; Carrinho Vazio."
        
        preco_counter = 0
        quantidade_counter = 0
        prints = ""
        for k in carrinho.keys():
            prod = self._produtos.get(k)
            quantidade_counter += prod.quantidade
            preco_counter += (prod.preco * prod.quantidade)
            prints + f"{k} - {prod.nome}({self.obter_id_categoria(prod.categoria)}-{prod.categoria}, {prod.preco} euros, {prod.quantidade} unidades);\n"

        return f"OK;\nTotal Produtos: {len(carrinho)}\nTotal Quantidade: {quantidade_counter}\nTotal Preço: {preco_counter} euros\n\n" + prints

    def checkout_carrinho(self, id_cliente):
        if id_cliente not in self._clientes.keys():
            raise ExcepcaoComandoInvalido("NOK; Id inválido.")
        if len(self._clientes.get(id_cliente).carrinho_compras()) < 1:
            raise ExcepcaoComandoInvalido("NOK; Cliente sem produtos no carrinho.")

        total = 0
        for k in self._clientes.get(id_cliente).carrinho_compras().keys():
            prod = self._produtos.get(k)
            total += (prod.preco * prod.quantidade)

        encomenda = Encomenda(_Date.today(), self._clientes.get(id_cliente).carrinho_compras(), id_cliente, total)

        self._clientes.get(id_cliente).carrinho_compras().clear()


    #-----------------
    # Encomendas
    #-----------------
    def listar_encomendas(self, id_cliente):
        if id_cliente not in self._clientes.keys():
            raise ExcepcaoComandoInvalido("NOK; Id inválido.")
        
        cliente = self._clientes.get(id_cliente)
        nr_encomendas_cliente = 0
        encomendas_cliente = []

        for e in self._encomendas.values():
            if e.cliente_id == id_cliente:
                nr_encomendas_cliente += 1
                encomendas_cliente.append(e)
        if nr_encomendas_cliente < 1:
            return f"OK; Sem encomendas."
        
        total_produtos = 0
        total_preco = 0
        categorias = []
        categorias_quantidades = []
        prints_3 = ""

        for e in encomendas_cliente:
            carrinho_encomenda = e.obterCarrinhoEncomenda()
            id_produtos_encomenda = []
            quantidade_encomenda = 0
            preco_encomenda = e.obterTotal()
            total_preco += preco_encomenda
            prints_2 = ""
            for k in carrinho_encomenda.keys():
                id_produtos_encomenda.append(k)
                quantidade_encomenda += carrinho_encomenda.get(k)
                produto = self._produtos.get(k)
                prints_2 + f"{k} - {produto.obterNome()}({produto.obterCategoria()}, {produto.obterPreco()} euros, {carrinho_encomenda.get(k)} unidades);"

                if produto.obterCategoria() not in categorias:
                    categorias.append(produto.obterCategoria())
                    categorias_quantidades.append(carrinho_encomenda.get(k))
                else:
                    categorias_quantidades[categorias.index(produto.obterCategoria())] += carrinho_encomenda.get(k)
            
            total_produtos += len(id_produtos_encomenda)
                    
            prints_3 + f"ID Encomenda: {e.obterId()}\nTotal Produtos: {len(id_produtos_encomenda)}\nTotal Quantidade: {quantidade_encomenda}\nTotal Preço: {preco_encomenda} euros\n\n" + prints_2
    
        # busca categorias top
        max = 0
        max_2 = 0
        first_place = ""
        second_place = ""
        for i in range(len(categorias)):
            if categorias_quantidades[i] > max:
                max = categorias_quantidades[i]
                first_place = categorias[i]
            elif categorias_quantidades[i] == max:
                ty = [first_place, categorias[i]]
                first_place = ty.sort()[0]
            elif max > categorias_quantidades[i] > max_2:
                max_2 = categorias_quantidades[i]
                second_place = categorias[i]
            elif categorias_quantidades[i] == max_2:
                ty = [second_place, categorias[i]]
                second_place = ty.sort()[0]        

        prints_1 = f"OK;\nCliente: {cliente.nome} {cliente.email}\nTotal Encomendas: {nr_encomendas_cliente}\nTotal Produtos: {total_produtos}\nTotal Preço: {round(total_preco, 2)}\nCategoria Top: {first_place}, {second_place}\n--------------------------------------------------------------------------"
        return prints_1 + prints_3