# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: 

from servidor.excepcoes import ExcepcaoComandoInvalido
from servidor.excepcoes import ExcepcaoComandoDesconhecido
from servidor.excepcoes import ExcepcaoComandoNumeroArgumentosIncorreto
from servidor.excepcoes import ExcepcaoSupermercado
from servidor.excepcoes import ExcepcaoComandoNaoInterpretavel
from servidor.excepcoes import ExcepcaoComandoVazio
import shlex
from servidor.loja import Loja
from shared.utilities import normalizar_nome

class Processador:

    """
    Camada Processador:
    - interpreta comandos (parsing e dispatch)
    - valida sintaxe e número/tipo básico de argumentos (ex.: quantos args vieram)
    - chama a Loja para executar a lógica de negócio
    - NÃO faz validações de negócio (isso pertence à Loja / domínio)
    - traduz resultados/erros para mensagens (strings) para devolver à Camada Transporte
    - A função processar_comando() é o ponto único de entrada e é obrigatória para efeitos de avaliação.
    - Garantir que TODAS as respostas seguem rigorosamente o protocolo:
      "OK; <mensagem>"
      "NOK; <mensagem>"
    """

    def reset(self): 
        Loja.reset()

    def __init__(self):
        self.loja = Loja()
        
        self.HANDLERS = {
            "CRIA_CATEGORIA": self._cmd_cria_categoria,
            "LISTA_CATEGORIAS": self._cmd_lista_categorias,
            "REMOVE_CATEGORIA": self._cmd_remove_categoria,
            "CRIA_PRODUTO": self._cmd_cria_produto,
            "LISTA_PRODUTOS": self._cmd_lista_produtos,
            "AUMENTA_STOCK_PRODUTO": self._cmd_aumenta_stock_produto,
            "ATUALIZA_PRECO_PRODUTO": self._cmd_atualiza_preco_produto,
            "CRIA_CLIENTE": self._cmd_cria_cliente,
            "LISTA_CLIENTES": self._cmd_lista_clientes,
            "ADICIONA_PRODUTO_CARRINHO": self._cmd_adiciona_produto_carrinho,
            "REMOVE_PRODUTO_CARRINHO": self._cmd_remove_produto_carrinho,
            "LISTA_CARRINHO": self._cmd_lista_carrinho,
            "CHECKOUT_CARRINHO": self._cmd_checkout_carrinho,
            "LISTA_ENCOMENDAS": self._cmd_lista_encomendas,
            "EXIT": self._cmd_sai_aplicacao
        }

    def _dividir_comando(self, comando): 
        try:
            partes = shlex.split(comando)
        except ValueError as e:
            raise ExcepcaoComandoNaoInterpretavel(comando)
        
        if len(partes) == 1:
            nome_comando = partes[0].upper()
            argumentos = []
            return nome_comando, argumentos
        elif len(partes) > 1: 
            nome_comando = partes[0].upper()
            argumentos = partes[1:]
            return nome_comando, argumentos
        else: 
            raise ExcepcaoComandoVazio()
    
    def _validar_n_args(self, args, n):
        if len(args) != n:
            raise ExcepcaoComandoNumeroArgumentosIncorreto(n, len(args))

    def _obter_handler(self, nome):
        try:
            comando = self.HANDLERS[nome] 
        except KeyError:
            raise ExcepcaoComandoDesconhecido(nome)
        return comando
    
    def processar_comando(self, comando):
        try:
            nome_comando, args = self._dividir_comando(comando)
            handler = self._obter_handler(nome_comando)
        
            resultado = handler(args)
            return f"OK; {resultado}"
        except (ExcepcaoSupermercado, ExcepcaoComandoInvalido) as e:
            return f"NOK; {e}"

    #------------------------
    # _cmd_ handlers
    #------------------------
    def _cmd_cria_categoria(self, args):
        self._validar_n_args(args, 1)
        nome_categoria = normalizar_nome(args[0])
        categoria = self.loja.criar_categoria(nome_categoria)
        return f"Categoria {categoria.nome} criada com sucesso."
    
    def _cmd_lista_categorias(self, args):        
        self._validar_n_args(args, 0)
        return self.loja.lista_categorias()

    def _cmd_remove_categoria(self, args):
        self._validar_n_args(args, 1)
        nome_categoria = args[0]
        nome_categoria_removida = self.loja.remover_categoria(nome_categoria)
        return f"Categoria {nome_categoria_removida} removida com sucesso."

    def _cmd_cria_produto(self, args):
        self._validar_n_args(args, 4)
        nome_produto = normalizar_nome(args[0])
        nome_categoria = normalizar_nome(args[1])
        preco = round(int(args[2]), 2)
        quantidade = int(args[3])

        produto = self.loja.criar_produto(nome_produto, nome_categoria, preco, quantidade)    
        return f"Produto {produto.nome} criado com sucesso."
    
    def _cmd_lista_produtos(self, args):
        self._validar_n_args(args, 0)
        return self.loja.listar_produtos()

    def _cmd_aumenta_stock_produto(self, args):
        self._validar_n_args(args, 2)
        nome_produto = normalizar_nome(args[0])
        quantidade_delta = args[1]

        self.loja.aumentar_stock_produto(nome_produto, quantidade_delta)
        return f"Stock do produto {nome_produto} aumentado em {quantidade_delta} unidades com sucesso."

    def _cmd_atualiza_preco_produto(self, args):
        self._validar_n_args(args, 2)
        nome_produto = normalizar_nome(args[0])
        novo_preco = args[1]
        
        self.loja.atualizar_preco_produto(nome_produto, novo_preco)
        return f"Preco de {nome_produto} alterado para {novo_preco} € com sucesso."

    def _cmd_cria_cliente(self, args):
        self._validar_n_args(args, 3)
        nome = normalizar_nome(args[0])
        email = args[1]
        pw = args[2]

        cliente = self.loja.criar_cliente(nome, email, pw)
        return f"Cliente {cliente.nome} criado com sucesso com identificador único {cliente.id}."

    def _cmd_lista_clientes(self, args):
        self._validar_n_args(args, 0)
        return self.loja.listar_clientes()

    def _cmd_adiciona_produto_carrinho(self, args):
        self._validar_n_args(args, 3)
        id_cliente = args[0]
        nome_produto = normalizar_nome(args[1])
        quantidade = args[2]

        self.loja.adiciona_produto_carrinho(id_cliente, nome_produto, quantidade)
        return f"Produto {normalizar_nome(nome_produto)} adicionado com sucesso ao carrinho de compras."

    def _cmd_remove_produto_carrinho(self, args):
        self._validar_n_args(args, 2)
        id_cliente = args[0]
        nome_produto = normalizar_nome(args[1])

        self.loja.remover_produto_carrinho(id_cliente, nome_produto)
        return f"Produto {nome_produto} removido com sucesso do carrinho de compras."

    def _cmd_lista_carrinho(self, args):
        self._validar_n_args(args, 1)
        id_cliente = args[0]

        return self.loja.lista_carrinho_cliente(self, id_cliente)

    def _cmd_checkout_carrinho(self, args):
        self._validar_n_args(args, 1)
        id_cliente = args[0]

        self.loja.checkout_carrinho(id_cliente)
        return "Checkout de carrinho de compras efetuado com sucesso. Encomenda criada com sucesso a partir do carrinho"

    def _cmd_lista_encomendas(self, args):
        self._validar_n_args(args, 1)
        id_cliente = args[0]

        return self.loja.listar_encomendas(id_cliente)

    def _cmd_sai_aplicacao(self, args):
        self._validar_n_args(args, 0)
        return "Saindo da aplicação do lado do servidor."
    