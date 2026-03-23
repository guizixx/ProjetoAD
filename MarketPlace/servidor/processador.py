# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Camada processador interpreta os comandos do cliente e faz validação de argumentos,
#            antes de chamar a loja para executar a lógica de negócio e formar as respostas necessárias

from servidor.excepcoes import ExcepcaoComandoInvalido
from servidor.excepcoes import ExcepcaoComandoDesconhecido
from servidor.excepcoes import ExcepcaoComandoNumeroArgumentosIncorreto
from servidor.excepcoes import ExcepcaoSupermercado
from servidor.excepcoes import ExcepcaoComandoNaoInterpretavel
from servidor.excepcoes import ExcepcaoComandoVazio
import shlex
from servidor.loja import Loja
from servidor.rede import TCPSocketServidor
from shared.utilities import normalizar_nome

# classe processador é o skeleton
# alterar tudo o que envolve o novo protocolo de mnsgs
#   -validaçao, estruturaçao, divisao e processamento

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
        self.loja.reset()

    def __init__(self, pontoAcesso):
        self.rede = TCPSocketServidor(pontoAcesso)
        self.loja = Loja()
        
        # alterar keys dos handlers para o novo protocolo de mnsgs
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

    def accept(self): 
        self.rede.accept()
        print("SERVIDOR> Servidor ligado a %s no porto %s" % (self.rede.ponto_acesso.endereco_ip, self.rede.ponto_acesso.port))

    def envia(self, msg_str): 
        print("Estou a enviar", msg_str)
        bytes = msg_str.encode()
        self.rede.envia(bytes)

    def recebe(self): 
        bytes = self.rede.recebe()
        resposta_str = bytes.decode()
        print(f"SERVIDOR> Comando recebido: {resposta_str}")
        return resposta_str

    def close(self): 
        self.rede.close()

    def closeall(self): 
        self.rede.closeall()

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
    
    def processar_comando(self):
        try:
            comando = self.recebe()

            nome_comando, args = self._dividir_comando(comando)
            handler = self._obter_handler(nome_comando)
        
            resultado = handler(args)
            self.rede.envia(resultado.encode())
        except (ExcepcaoSupermercado, ExcepcaoComandoInvalido) as e:
            raise e

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
        try:
            preco = round(float(args[2]), 2)
        except ValueError:
            raise ExcepcaoComandoInvalido("Preço inválido.")
        try:
            quantidade = int(args[3])
        except ValueError:
            raise ExcepcaoComandoInvalido("Quantidade inválida.")

        produto = self.loja.criar_produto(nome_produto, nome_categoria, preco, quantidade)    
        return f"Produto {produto.nome} criado com sucesso."
    
    def _cmd_lista_produtos(self, args):
        self._validar_n_args(args, 0)
        return self.loja.listar_produtos()

    def _cmd_aumenta_stock_produto(self, args):
        self._validar_n_args(args, 2)
        nome_produto = normalizar_nome(args[0])
        try:
            quantidade_delta = int(args[1])
        except ValueError:
            raise ExcepcaoComandoInvalido("Quantidade inválida.")

        self.loja.aumentar_stock_produto(nome_produto, quantidade_delta)
        return f"Stock do produto {nome_produto} aumentado em {quantidade_delta} unidades com sucesso."

    def _cmd_atualiza_preco_produto(self, args):
        self._validar_n_args(args, 2)
        nome_produto = normalizar_nome(args[0])
        try:
            novo_preco = float(args[1])
        except ValueError:
            raise ExcepcaoComandoInvalido("Preço inválido.")
        self.loja.atualizar_preco_produto(nome_produto, novo_preco)
        return f"Preco de {nome_produto} alterado para {novo_preco:.2f} € com sucesso."

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
        try:
            id_cliente = int(args[0])
        except ValueError:
            raise ExcepcaoComandoInvalido("Id de cliente inválido.")
        try:
            quantidade = int(args[2])
        except ValueError:
            raise ExcepcaoComandoInvalido("Quantidade inválida.")
        nome_produto = normalizar_nome(args[1])

        self.loja.adiciona_produto_carrinho(id_cliente, nome_produto, quantidade)
        return f"Produto {normalizar_nome(nome_produto)} adicionado com sucesso ao carrinho de compras."

    def _cmd_remove_produto_carrinho(self, args):
        self._validar_n_args(args, 2)
        try:
            id_cliente = int(args[0])
        except ValueError:
            raise ExcepcaoComandoInvalido("Id de cliente inválido.")
        nome_produto = normalizar_nome(args[1])

        self.loja.remover_produto_carrinho(id_cliente, nome_produto)
        return f"Produto {nome_produto} removido com sucesso do carrinho de compras."

    def _cmd_lista_carrinho(self, args):
        self._validar_n_args(args, 1)
        try:
            id_cliente = int(args[0])
        except ValueError:
            raise ExcepcaoComandoInvalido("Id de cliente inválido.")

        return self.loja.lista_carrinho_cliente(id_cliente)

    def _cmd_checkout_carrinho(self, args):
        self._validar_n_args(args, 1)
        try:
            id_cliente = int(args[0])
        except ValueError:
            raise ExcepcaoComandoInvalido("Id de cliente inválido.")

        self.loja.checkout_carrinho(id_cliente)
        return "Checkout de carrinho de compras efetuado com sucesso. Encomenda criada com sucesso a partir do carrinho."

    def _cmd_lista_encomendas(self, args):
        self._validar_n_args(args, 1)
        try:
            id_cliente = int(args[0])
        except ValueError:
            raise ExcepcaoComandoInvalido("Id de cliente inválido.")

        return self.loja.lista_encomendas(id_cliente)

    def _cmd_sai_aplicacao(self, args):
        self._validar_n_args(args, 0)
        return "Saindo da aplicação do lado do servidor."
    