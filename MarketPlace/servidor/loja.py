# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: 

from shared.utilities import normalizar_nome
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
        ClienteLoja._contador_global = 1
        self._categorias = {}
        self._produtos = {}
        self._clientes = {}
        self._encomendas = {}
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
            return "Sem Categorias."
        linhasDePrint = []
        linhasDePrint.append(f"\nTotal Categorias: {len(self._categorias.values())}")
        linhasDePrint.append(f"TotalProdutos: {len(self._produtos.values())}")
        # prints = f"OK;\nTotal Categorias: {len(self._categorias.values())}\nTotal Produtos: {self._produtos.values()}\n\n"
        for c in self._categorias.values():
            num_prod_categ = self.obter_nr_produtos_categoria(c.obter_nome())
            linhasDePrint.append(f"{c.obter_id()} - {c.obter_nome()} ({num_prod_categ} produtos)")
            # prints + f"{c.obter_id()} - {c.obter_nome()}({self.obter_nr_produtos_categoria(c.obter_nome())});\n"
        return "\n".join(linhasDePrint)
    
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
            if nome_produto == p.obter_nome():
                raise ExcepcaoComandoInvalido("Nome do produto já existe.")
        if self.obter_id_categoria(nome_categoria) is None:
            raise ExcepcaoComandoInvalido("Categoria não existe.")
        if preco <= 0:
            raise ExcepcaoComandoInvalido("Preço inválido.")
        if quantidade < 0:
            raise ExcepcaoComandoInvalido("Quantidade inválida.")
        
        produto = Produto(nome_produto, nome_categoria, preco, quantidade)
        self._produtos[produto.obter_id()] = produto
        return produto 

    def listar_produtos(self):
        if len(self._produtos.values()) == 0:
            return "Sem Produtos."
        linhasDePrint = []
        linhasDePrint.append(f"\nTotal Produtos: {len(self._produtos.values())}")
        
        quantidade_total = 0
        for p in self._produtos.values():
            quantidade_total += p.obter_quantidade()
        linhasDePrint.append(f"Total Quantidade: {quantidade_total}")
        for p in self._produtos.values():
            linhasDePrint.append(f"{p.obter_id()} - {p.obter_nome()}({p.obter_categoria()}, {p.obter_preco()}, {p.obter_quantidade()} unidades);")
        return "\n".join(linhasDePrint)
    
    def obter_id_produto(self, nome):
        for p in self._produtos.values():
            if p.obter_nome() == nome:
                return p.obter_id()
        return None
    
    def aumentar_stock_produto(self, nome, quantidade):
        if self.obter_id_produto(nome) is None:
            raise ExcepcaoComandoInvalido("O nome do produto não existe.")
        if int(quantidade) < 0:
            raise ExcepcaoComandoInvalido("A quantidade a aumentar tem de ser um número inteiro positivo")

        self._produtos.get(self.obter_id_produto(nome)).adicionar_quantidade(quantidade)

    def atualizar_preco_produto(self, nome, novo_preco):
        if self.obter_id_produto(nome) is None:
            raise ExcepcaoComandoInvalido("O nome do produto não existe.")
        if novo_preco < 0:
            raise ExcepcaoComandoInvalido("O preço tem de ser um número positivo.")
        
        self._produtos.get(self.obter_id_produto(nome)).alterar_preco(novo_preco)
    #---------------
    # Clientes
    #---------------

    def criar_cliente(self, nome, email, pw):
        for c in self._clientes.values():
            if c.obter_email() == email.lower():
                raise ExcepcaoComandoInvalido("Email em uso.")
        cliente = ClienteLoja(nome, email, pw)
        self._clientes[cliente.obter_id()] = cliente
        return cliente


    def listar_clientes(self):
        if len(self._clientes.values()) == 0:
            return "Sem Clientes."
        linhasDePrint = []
        linhasDePrint.append(f"\nTotal Clientes: {len(self._clientes.values())}")
        for c in self._clientes.values():
            linhasDePrint.append(f"{c.obter_id()} - {c.obter_nome()}({c.obter_email()});")
        return "\n".join(linhasDePrint)
    
    #--------------
    # Carrinho
    #--------------
    def adiciona_produto_carrinho(self, id_cliente, nome_produto, quantidade):
        if id_cliente not in self._clientes.keys():
            raise ExcepcaoComandoInvalido("Cliente não identificado.")
        if self.obter_id_produto(nome_produto) is None:
            raise ExcepcaoComandoInvalido("Produto inexistente na loja.")
        if quantidade <= 0:
            raise ExcepcaoComandoInvalido("Quantidade inválida.")
        if self._produtos.get(self.obter_id_produto(nome_produto)).obter_quantidade() < quantidade:
            raise ExcepcaoComandoInvalido("Quantidade superior ao stock disponível.")

        id_produto = self.obter_id_produto(nome_produto)
        if id_produto in self._clientes.get(id_cliente).obter_carrinho_compras().keys():
            self._clientes.get(id_cliente).obter_carrinho_compras()[id_produto] += quantidade
        else:
            self._clientes.get(id_cliente).obter_carrinho_compras()[id_produto] = quantidade
        self._produtos.get(id_produto).adicionar_quantidade(-quantidade)
    
    def remover_produto_carrinho(self, id_cliente, nome_produto):
        try:
            id_cliente = int(id_cliente)
        except ValueError:
            raise ExcepcaoComandoInvalido("Id de cliente inválido.")

        if id_cliente not in self._clientes.keys():
            raise ExcepcaoComandoInvalido("Id inválido.")
        if self.obter_id_produto(nome_produto) is None:
            raise ExcepcaoComandoInvalido("Produto inexistente na loja.")

        id_produto = self.obter_id_produto(nome_produto)
        carrinho = self._clientes.get(id_cliente).obter_carrinho_compras()

        if id_produto not in carrinho.keys():
            raise ExcepcaoComandoInvalido("O cliente não possui esse produto.")

        quantidade = carrinho[id_produto]
        carrinho.pop(id_produto)
        self._produtos.get(id_produto).adicionar_quantidade(quantidade)


    def lista_carrinho_cliente(self, id_cliente):
        if id_cliente not in self._clientes.keys():
            raise ExcepcaoComandoInvalido("Id inválido.")
        carrinho = self._clientes.get(id_cliente).obter_carrinho_compras()
        if len(carrinho) < 1:
            return "Carrinho Vazio."
        linhasDePrint = []
        preco_counter = 0
        quantidade_counter = 0
        for k in carrinho.keys():
            prod = self._produtos.get(k)
            quantidade_counter += prod.obter_quantidade()
            preco_counter += (prod.obter_preco() * carrinho.get(k))
            linhasDePrint.append(f"{k} - {prod.obter_nome()}({self.obter_id_categoria(prod.obter_categoria())}-{prod.obter_categoria()}, {prod.obter_preco()} euros, {prod.obter_quantidade()} unidades);")
        linhasDePrint.insert(0, f"\nTotal Produtos: {len(carrinho)}")
        linhasDePrint.insert(1, f"Total Quantidade: {quantidade_counter}")
        linhasDePrint.insert(2, f"Total Preço: {preco_counter} euros")
        return "\n".join(linhasDePrint)

    def checkout_carrinho(self, id_cliente):
        if id_cliente not in self._clientes.keys():
            raise ExcepcaoComandoInvalido("Id inválido.")
        if len(self._clientes.get(id_cliente).obter_carrinho_compras()) < 1:
            raise ExcepcaoComandoInvalido("Cliente sem produtos no carrinho.")

        total = 0
        for k in self._clientes.get(id_cliente).obter_carrinho_compras().keys():
            prod = self._produtos.get(k)
            total += (prod.obter_preco() * self._clientes.get(id_cliente).obter_carrinho_compras().get(k))

        encomenda = Encomenda(datetime.now(), deepcopy(self._clientes.get(id_cliente).obter_carrinho_compras()), id_cliente, total)
        self._encomendas[encomenda.obter_id()] = encomenda
        self._clientes.get(id_cliente).obter_carrinho_compras().clear()


    #-----------------
    # Encomendas
    #-----------------
    def lista_encomendas(self, id_cliente):
        if id_cliente not in self._clientes.keys():
            raise ExcepcaoComandoInvalido("Id inválido.")
        
        cliente = self._clientes.get(id_cliente)
        nr_encomendas_cliente = 0
        encomendas_cliente = []

        for e in self._encomendas.values():
            if e.obter_cliente_id() == id_cliente:
                nr_encomendas_cliente += 1
                encomendas_cliente.append(e)
        if nr_encomendas_cliente == 0:
            return f"Sem encomendas."
        
        total_produtos = 0
        total_preco = 0
        categorias = []
        categorias_quantidades = []
        linhasDePrint = []
        linhasDePrintEncomendas = []
        for e in encomendas_cliente:
            carrinho_encomenda = e.obter_carrinho_compras()
            quantidade_encomenda = 0
            preco_encomenda = e.obter_total()
            total_preco += preco_encomenda
            linhasDePrintProdutos = []
            total_produtos_encomenda = 0
            for k in carrinho_encomenda.keys():
                total_produtos += 1
                total_produtos_encomenda += 1
                quantidade_encomenda += carrinho_encomenda.get(k)
                produto = self._produtos.get(k)
                linhasDePrintProdutos.append(f"{k} - {produto.obter_nome()}({produto.obter_categoria()}, {produto.obter_preco()} euros, {carrinho_encomenda.get(k)} unidades);")

                if produto.obter_categoria() not in categorias:
                    categorias.append(produto.obter_categoria())
                    categorias_quantidades.append(carrinho_encomenda.get(k))
                else:
                    categorias_quantidades[categorias.index(produto.obter_categoria())] += carrinho_encomenda.get(k)
                    
            linhasDePrintEncomendas.append(f"ID Encomenda: {e.obter_id()}")
            linhasDePrintEncomendas.append(f"Total Produtos: {total_produtos_encomenda}")
            linhasDePrintEncomendas.append(f"Total Quantidade: {quantidade_encomenda}")
            linhasDePrintEncomendas.append(f"Total Preço: {preco_encomenda} euros\n")
            for l in linhasDePrintProdutos:
                linhasDePrintEncomendas.append(l)
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

        linhasDePrint.append(f"\nCliente: {cliente.obter_nome()} {cliente.obter_email()}")
        linhasDePrint.append(f"Total Encomendas: {nr_encomendas_cliente}")
        linhasDePrint.append(f"Total Produtos: {total_produtos}")
        linhasDePrint.append(f"Total Preço: {round(total_preco, 2)}")
        if second_place == "":
            linhasDePrint.append(f"Categoria Top: {first_place}")
        else:
            linhasDePrint.append(f"Categorias Top: {first_place}, {second_place}")
        linhasDePrint.append(f"--------------------------------------------------------------------------")
        for l in linhasDePrintEncomendas:
            linhasDePrint.append(l)
        return "\n".join(linhasDePrint)