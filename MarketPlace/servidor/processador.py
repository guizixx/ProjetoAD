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
from shared.excepcoes_shared import OpCodes
import shared.excepcoes_shared
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
        
                        # opcode:  [ handler, permissão mínima para poder executar a operação ]
        self.HANDLERS = {
            OpCodes.CRIA_CATEGORIA: [self._cmd_cria_categoria, 3],
            OpCodes.LISTA_CATEGORIAS: [self._cmd_lista_categorias, 3],
            OpCodes.REMOVE_CATEGORIA: [self._cmd_remove_categoria, 3],
            OpCodes.CRIA_PRODUTO: [self._cmd_cria_produto, 2],
            OpCodes.LISTA_PRODUTOS: [self._cmd_lista_produtos, 2],
            OpCodes.AUMENTA_STOCK: [self._cmd_aumenta_stock_produto, 2],
            OpCodes.ATUALIZA_PRECO: [self._cmd_atualiza_preco_produto, 2],
            OpCodes.CRIA_CLIENTE: [self._cmd_cria_cliente, 0], 
            OpCodes.LISTA_CLIENTES: [self._cmd_lista_clientes, 2],
            OpCodes.ADICIONA_PRODUTO_CARRINHO: [self._cmd_adiciona_produto_carrinho, 1],
            OpCodes.REMOVE_PRODUTO_CARRINHO: [self._cmd_remove_produto_carrinho, 1],
            OpCodes.LISTA_CARRINHO: [self._cmd_lista_carrinho, 1],
            OpCodes.CHECKOUT_CARRINHO: [self._cmd_checkout_carrinho, 1],
            OpCodes.LISTA_ENCOMENDAS: [self._cmd_lista_encomendas, 1]
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
        
        if len(partes) == 0:
            raise ExcepcaoComandoVazio()
        elif len(partes) != 4:
            raise shared.excepcoes_shared.ExcecaoNumeroCamposInvalido()
        
        try:
            op_code = int(partes[0])
            perfil = int(partes[2])
            utilizador = int(partes[3])
        except shared.excepcoes_shared.TipoArgumentoInvalido as e:
            raise e
        if int(op_code) not in self.HANDLERS.keys():
            raise shared.excepcoes_shared.ComandoDesconhecido()
        if perfil not in [0, 1, 2, 3]:
            raise shared.excepcoes_shared.PerfilInvalido()
        
        argumentos = partes[1]
        # to-fix: ver se é a melhor maneira de verificar se o segundo argumento é uma lista
        if argumentos[0] == '[' & argumentos[-1] == ']':
            raise shared.excepcoes_shared.ExcecaoArgumentoInvalido()
        norm_argumentos = argumentos.replace("[", "").replace("]", "")
        try:
            
            partes_args = shlex.split(norm_argumentos)
        except ValueError as e:
            raise ExcepcaoComandoNaoInterpretavel(comando)
        return op_code, partes_args, perfil, utilizador
          
    def _validar_n_args(self, args, n):
        if len(args) != n:
            raise ExcepcaoComandoNumeroArgumentosIncorreto(n, len(args))
        
    def _validar_permissao(self, perfil, operacao):
        if self.HANDLERS[operacao][1] > perfil:
            raise shared.excepcoes_shared.OperacaoNaoAutorizada()
        
    def _validar_utilizador(self, perfil, utilizador, operacao):
        return self.loja.validar_utilizador(perfil, utilizador, operacao)

            
    def _obter_handler(self, opcode):
        try:
            comando = self.HANDLERS[opcode][0] 
        except KeyError:
            raise shared.excepcoes_shared.ErroInterno()
        return comando
    
    def processar_comando(self):
        try:
            comando = self.recebe()
            opcode, args, perfil, utilizador = self._dividir_comando(comando)
            self._validar_permissao(perfil, utilizador)
            handler = self._obter_handler(opcode)

            # o handler da ação lista_encomendas precisa do id_utilizador
            if opcode == OpCodes.LISTA_ENCOMENDAS:
                args.append(utilizador)
        
            resultado = handler(args)
            self.envia(resultado)
        except (ExcepcaoSupermercado, ExcepcaoComandoInvalido) as e:
            raise e
        

    #------------------------
    # _cmd_ handlers
    #------------------------

    def _cmd_cria_categoria(self, args):
        self._validar_n_args(args, 1)
        nome_categoria = normalizar_nome(args[0])
        categoria = self.loja.criar_categoria(nome_categoria)
        return [OpCodes.CRIA_CATEGORIA, [categoria.nome]]
    
    def _cmd_lista_categorias(self, args):        
        self._validar_n_args(args, 0)
        return self.loja.lista_categorias()

    def _cmd_remove_categoria(self, args):
        self._validar_n_args(args, 1)
        nome_categoria = args[0]
        nome_categoria_removida = self.loja.remover_categoria(nome_categoria)
        return [OpCodes.REMOVE_CATEGORIA, nome_categoria_removida]

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
        return [OpCodes.CRIA_PRODUTO, [produto.nome]]
    
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
        return [OpCodes.AUMENTA_STOCK, [nome_produto]]

    def _cmd_atualiza_preco_produto(self, args):
        self._validar_n_args(args, 2)
        nome_produto = normalizar_nome(args[0])
        try:
            novo_preco = float(args[1])
        except ValueError:
            raise ExcepcaoComandoInvalido("Preço inválido.")
        self.loja.atualizar_preco_produto(nome_produto, novo_preco)
        return [OpCodes.ATUALIZA_PRECO, [nome_produto]]

    def _cmd_cria_cliente(self, args):
        self._validar_n_args(args, 3)
        nome = normalizar_nome(args[0])
        email = args[1]
        pw = args[2]

        cliente = self.loja.criar_cliente(nome, email, pw)
        return [OpCodes.CRIA_CLIENTE, [cliente.nome]] 
    
    def _cmd_lista_clientes(self, args):
        self._validar_n_args(args, 0)
        return self.loja.listar_clientes()

    def _cmd_adiciona_produto_carrinho(self, args):
        self._validar_n_args(args, 2)
        try:
            quantidade = int(args[2])
        except ValueError:
            raise shared.excepcoes_shared.QuantidadeInvalida()
        nome_produto = normalizar_nome(args[1])

        self.loja.adiciona_produto_carrinho(nome_produto, quantidade)
        return [OpCodes.ADICIONA_PRODUTO_CARRINHO,[nome_produto]]
    
    def _cmd_remove_produto_carrinho(self, args):
        self._validar_n_args(args, 2)
        nome_produto = normalizar_nome(args[1])
        self.loja.remover_produto_carrinho(nome_produto)
        return [OpCodes.REMOVE_PRODUTO_CARRINHO, [nome_produto]]
    
    def _cmd_lista_carrinho(self, args):
        self._validar_n_args(args, 0)

        return self.loja.lista_carrinho_cliente()

    def _cmd_checkout_carrinho(self, args):
        self._validar_n_args(args, 0)
        encomenda = self.loja.checkout_carrinho()
        return [OpCodes.CHECKOUT_CARRINHO, [encomenda.id]]
    
    def _cmd_lista_encomendas(self, args):
        self._validar_n_args(args, 1)
        try:
            id_cliente = int(args[0])
        except ValueError:
            raise shared.excepcoes_shared.ClienteNaoExiste()

        return self.loja.lista_encomendas(id_cliente)
