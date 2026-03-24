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
        norm_nome = normalizar_nome(nome)
        categoria_id = self.obter_id_categoria(norm_nome)
        if categoria_id is None:
            raise ExcepcaoComandoInvalido("Categoria Inexistente")
        if self.obter_nr_produtos_categoria(norm_nome) > 0:
            raise ExcepcaoComandoInvalido(f"Categoria {norm_nome} ainda tem produtos associados.")
        self._categorias.pop(categoria_id)
        return norm_nome 
    
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
            quantidade_counter += carrinho.get(k)
            preco_counter = round(preco_counter + round(prod.obter_preco() * carrinho.get(k), 2), 2)
            linhasDePrint.append(f"{k} - {prod.obter_nome()}({self.obter_id_categoria(prod.obter_categoria())}-{prod.obter_categoria()}, {prod.obter_preco():.2f} euros, {carrinho.get(k)} unidades);")
        linhasDePrint.insert(0, f"\nTotal Produtos: {len(carrinho)}")
        linhasDePrint.insert(1, f"Total Quantidade: {quantidade_counter}")
        linhasDePrint.insert(2, f"Total Preço: {preco_counter:.2f} euros")
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

        # carrinho passa a guardar [quantidade, preço] em vez de quantidade
        # para guardar o preço do produto no momento da encomenda
        carrinho_encomenda = deepcopy(self._clientes.get(id_cliente).obter_carrinho_compras())
        for k in carrinho_encomenda.keys():
            carrinho_encomenda[k] = [carrinho_encomenda.get(k), self._produtos.get(k).obter_preco()]

        encomenda = Encomenda(datetime.now().replace(microsecond=0), carrinho_encomenda, id_cliente, total)
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
        produtos = []
        total_preco = 0
        categorias_quantidades = {}
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
                total_produtos_encomenda += 1
                quantidade_encomenda += carrinho_encomenda.get(k)[0]
                produto = self._produtos.get(k)
                if produto.obter_id() not in produtos:
                    total_produtos += 1
                    produtos.append(produto.obter_id())
                linhasDePrintProdutos.append(f"{k} - {produto.obter_nome()}({produto.obter_categoria()}, {carrinho_encomenda.get(k)[1]} euros, {carrinho_encomenda.get(k)[0]} unidades);")

                if produto.obter_categoria() not in categorias_quantidades.keys():
                    categorias_quantidades[produto.obter_categoria()] = carrinho_encomenda.get(k)[0]
                else:
                    categorias_quantidades[produto.obter_categoria()] = (categorias_quantidades.get(produto.obter_categoria()) + carrinho_encomenda.get(k)[0])
            # formataçao para cada encomenda a ser listada
            linhasDePrintEncomendas.append(f"ID Encomenda: {e.obter_id()}")
            linhasDePrintEncomendas.append(f"Data Encomenda: {e.obter_data()}")
            linhasDePrintEncomendas.append(f"Total Produtos: {total_produtos_encomenda}")
            linhasDePrintEncomendas.append(f"Total Quantidade: {quantidade_encomenda}")
            linhasDePrintEncomendas.append(f"Total Preço: {preco_encomenda} euros\n")
            for l in range(len(linhasDePrintProdutos)):
                linhasDePrintEncomendas.append(linhasDePrintProdutos[l])
                # verificaçao para quando acaba a listagem de uma encomenda serem inseridos linebreaks antes da outra encomenda
                if ( l+1 ) == len(linhasDePrintProdutos):
                    linhasDePrintEncomendas.append("\n\n")
        
        # busca categorias top
        categorias_top_ordenadas_por_valor = dict(sorted(categorias_quantidades.items(), key=itemgetter(1), reverse=True))
        first_place = ""
        second_place = ""
        valores = list(categorias_top_ordenadas_por_valor.values())
        keys = list(categorias_top_ordenadas_por_valor.keys())

        if len(keys) == 1:
            first_place = keys[0]
        elif len(keys) == 2:
            if valores[0] == valores[1]:
                first_place = sorted(keys)[0]
                second_place = sorted(keys)[1]
            else:
                first_place = keys[0]
                second_place = keys[1]
        elif len(keys) >= 3:
            if valores[0] == valores[1]:
                if valores[1] == valores[2]:
                    first_place = sorted(keys[:3])[0]
                    second_place = sorted(keys[:3])[1]
                else:
                    first_place = sorted(keys[:2])[0]
                    second_place = sorted(keys[:2])[1]
            else:
                first_place = keys[0]
                if valores[1] == valores[2]:
                    second_place = sorted(keys[1:3])[0]
                else:
                    first_place = keys[0]
                    second_place = keys[1]
        
        # formataçao inicial da lista de encomendas
        linhasDePrint.append(f"\nCliente: {cliente.obter_nome()} {cliente.obter_email()}")
        linhasDePrint.append(f"Total Encomendas: {nr_encomendas_cliente}")
        linhasDePrint.append(f"Total Produtos: {total_produtos}")
        linhasDePrint.append(f"Total Preço: {round(total_preco, 2)}")
        # verificaçao second_place para não aparecer 'first_place, '
        if second_place == "":
            linhasDePrint.append(f"Categoria Top: {first_place}")
        else:
            linhasDePrint.append(f"Categorias Top: {first_place}, {second_place}")
        linhasDePrint.append(f"--------------------------------------------------------------------------")
        for l in linhasDePrintEncomendas:
            linhasDePrint.append(l)
        return "\n".join(linhasDePrint)
    
    #-----------------
    # AUXILIARES
    #-----------------
    def validar_utilizador(self, perfil, utilizador):
        if (perfil != 0) & (utilizador not in self._clientes.keys()):
            raise excepcoes_shared.UtilizadorInvalido()
        
        if perfil != self.clientes[utilizador].permissao:
            raise excepcoes_shared.OperacaoNaoAutorizada()
        
        # de certeza que vao faltar casos a adicionar aqui para poder validar o utilizador em todas as situaçoes
