# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Camada processador interpreta os comandos do cliente e faz validação de argumentos,
#            antes de chamar a loja (via skeleton) para executar a lógica de negócio e formar as respostas necessárias

from servidor.excepcoes import ExcepcaoComandoInvalido
from servidor.excepcoes import ExcepcaoComandoDesconhecido
from servidor.excepcoes import ExcepcaoComandoNumeroArgumentosIncorreto
from servidor.excepcoes import ExcepcaoSupermercado
from servidor.excepcoes import ExcepcaoComandoNaoInterpretavel
from servidor.excepcoes import ExcepcaoComandoVazio
from servidor.skeleton import Skeleton
from shared.excepcoes_shared import OpCodes
import shared.excepcoes_shared
import shlex
from servidor.loja import Loja
from shared.utilities import normalizar_nome

OPCODES_ESCRITA = {
    OpCodes.CRIA_CATEGORIA,
    OpCodes.REMOVE_CATEGORIA,
    OpCodes.CRIA_PRODUTO,
    OpCodes.AUMENTA_STOCK,
    OpCodes.ATUALIZA_PRECO,
    OpCodes.CRIA_CLIENTE,
    OpCodes.ADICIONA_PRODUTO_CARRINHO,
    OpCodes.REMOVE_PRODUTO_CARRINHO,
    OpCodes.CHECKOUT_CARRINHO,
}

class Processador:

    """
    Camada Processador:
    - recebe a lista desserializada vinda do Skeleton
    - valida estrutura, permissões e número de argumentos
    - faz dispatch para o handler correcto
    - acede à Loja via Skeleton para executar a lógica de negócio
    - propaga escritas ao sucessor através do ZooKeeperServidor
    - devolve uma lista de resposta ao main.py
    """

    def __init__(self, pontoAcesso, cert_ficheiro=None, key_ficheiro=None, ca_ficheiro=None):
        self.skeleton = Skeleton(pontoAcesso, cert_ficheiro, key_ficheiro, ca_ficheiro)
                        # opcode:  [ handler, permissão mínima para poder executar a operação, numero_args a serem passados ]

        self.zk_servidor = None # será injetado pelo main após a inicialização do ZooKeeper

        self.HANDLERS = {
            OpCodes.CRIA_CATEGORIA: [self._cmd_cria_categoria, 3, 1],
            OpCodes.LISTA_CATEGORIAS: [self._cmd_lista_categorias, 0, 0],
            OpCodes.REMOVE_CATEGORIA: [self._cmd_remove_categoria, 3, 1],
            OpCodes.CRIA_PRODUTO: [self._cmd_cria_produto, 2, 4],
            OpCodes.LISTA_PRODUTOS: [self._cmd_lista_produtos, 0, 0],
            OpCodes.AUMENTA_STOCK: [self._cmd_aumenta_stock_produto, 2, 2],
            OpCodes.ATUALIZA_PRECO: [self._cmd_atualiza_preco_produto, 2, 2],
            OpCodes.CRIA_CLIENTE: [self._cmd_cria_cliente, 0, 5], 
            OpCodes.LISTA_CLIENTES: [self._cmd_lista_clientes, 2, 0],
            OpCodes.ADICIONA_PRODUTO_CARRINHO: [self._cmd_adiciona_produto_carrinho, 1, 4],
            OpCodes.REMOVE_PRODUTO_CARRINHO: [self._cmd_remove_produto_carrinho, 1, 3],
            OpCodes.LISTA_CARRINHO: [self._cmd_lista_carrinho, 1, 2],
            OpCodes.CHECKOUT_CARRINHO: [self._cmd_checkout_carrinho, 1, 2],
            OpCodes.LISTA_ENCOMENDAS: [self._cmd_lista_encomendas, 1, 1]
        }

    def obter_skeleton(self):
        return self.skeleton
    
    def definir_zk_servidor(self, zk_servidor):
        self.zk_servidor = zk_servidor
 
    def recebe(self, conn_sock):
        return self.obter_skeleton().recebe(conn_sock)

    def envia(self, conn_sock, msg_str):
        self.obter_skeleton().envia(conn_sock, msg_str)

    def _dividir_comando(self, comando): 
        if not isinstance(comando, list):
            print(f"SERVIDOR> Comando recebido não é uma lista: {comando}")
            raise ExcepcaoComandoNaoInterpretavel(comando)
        if len(comando) == 0:
            raise ExcepcaoComandoVazio()
        if len(comando) != 4:
            raise shared.excepcoes_shared.ExcecaoNumeroCamposInvalido()
 
        try:
            op_code = int(comando[0])
            perfil = int(comando[2])
            utilizador = int(comando[3])
        except (ValueError, TypeError):
            raise shared.excepcoes_shared.TipoArgumentoInvalido("op_code/perfil/utilizador")
 
        if op_code not in self.HANDLERS.keys():
            raise shared.excepcoes_shared.ComandoDesconhecido(op_code)
        if perfil not in [0, 1, 2, 3]:
            raise shared.excepcoes_shared.PerfilInvalido()
 
        argumentos = comando[1]
        if not isinstance(argumentos, list):
            raise shared.excepcoes_shared.ExcecaoArgumentoInvalido()
 
        return op_code, argumentos, perfil, utilizador
    
    def _validar_n_args(self, args, n, opcode):
        if opcode in {OpCodes.LISTA_ENCOMENDAS}:
            if len(args) == 0 or len(args) == 1:
                return True

        if len(args) != n:
            raise ExcepcaoComandoNumeroArgumentosIncorreto(n, len(args))
        
    def _validar_permissao(self, perfil, operacao):
        if self.HANDLERS[operacao][1] > perfil:
            raise shared.excepcoes_shared.OperacaoNaoAutorizada()
        
    def _validar_utilizador(self, perfil, utilizador, operacao):
        return self.obter_skeleton().obter_loja().validar_utilizador(perfil, utilizador, operacao)

            
    def _obter_handler(self, opcode):
        try:
            comando = self.HANDLERS.get(opcode)[0]
        except KeyError:
            raise shared.excepcoes_shared.ErroInterno()
        return comando
    
    def propagar_escrita(self, comando):
        """
        Envia o comando da escrita ao sucessor e aguarda resposta.
        Devolve a resposta do sucessor, ou None se a propagação falhar.
        """
        sock_sucessor = self.zk_servidor.obter_sock_sucessor()
        if sock_sucessor is None:
            return None
        
        lock = self.zk_servidor.obter_lock_escrita()
        with lock:
            try:
                self.obter_skeleton().envia(sock_sucessor, comando)
                resposta = self.obter_skeleton().recebe(sock_sucessor)
                return resposta
            except Exception as e:
                print(f"SERVIDOR> Falha ao propagar escrita ao sucessor: {e}")
                return None
    
    def processar_comando(self, sckt, comando):
        try:            
            opcode, args, perfil, utilizador = self._dividir_comando(comando)
            #print(f"SERVIDOR> Comando dividido: opcode={opcode}, args={args}, perfil={perfil}, utilizador={utilizador}")
            self._validar_permissao(perfil, opcode)
            self.skeleton.obter_loja().verificar_perfil1(perfil, utilizador)
            print("Depois de validar permissao no processar_comando")
            handler = self._obter_handler(opcode)

            # os handlers das ações de gestão de carrinho precisam do id_utilizador
            # o cria_cliente também
            if opcode in  {OpCodes.ADICIONA_PRODUTO_CARRINHO, 
                           OpCodes.REMOVE_PRODUTO_CARRINHO, 
                           OpCodes.CHECKOUT_CARRINHO, 
                           OpCodes.LISTA_CARRINHO,
                           OpCodes.CRIA_CLIENTE}:
                args.append(utilizador)
                args.append(perfil)
            elif opcode in {OpCodes.LISTA_ENCOMENDAS}:
                args.append(utilizador)
        
            self._validar_n_args(args, self.HANDLERS.get(opcode)[2], opcode)

            resultado = handler(args)
            #print(f"SERVIDOR> Resultado do comando: {resultado}")
        except (ExcepcaoSupermercado, ExcepcaoComandoInvalido) as e:
            raise e
        
        if opcode in OPCODES_ESCRITA and self.zk_servidor is not None:
            resposta_sucessor = self.propagar_escrita(comando)
            if resposta_sucessor is not None:
                return resposta_sucessor
       
        return resultado
            
    #------------------------
    # _cmd_ handlers
    #------------------------

    def _cmd_cria_categoria(self, args):
        nome_categoria = normalizar_nome(args[0])
        if nome_categoria in ['', []]:
            raise shared.excepcoes_shared.ExcepcaoNegocio("Nome da categoria vazio após normalização.", 
                                                   OpCodes.CATEGORIA_NAO_EXISTE)
        
        categoria = self.obter_skeleton().obter_loja().criar_categoria(nome_categoria)
        return [OpCodes.OK_CRIA_CATEGORIA, [categoria]]
    
    def _cmd_lista_categorias(self, args):        
        if len(args) != 0:
            raise shared.excepcoes_shared.ValorArgumentoInvalido("Lista de argumentos deve ser vazia.")
        
        categorias, produtos = self.obter_skeleton().obter_loja().lista_categorias()
        return [OpCodes.OK_LISTA_CATEGORIAS, [categorias, produtos]]

    def _cmd_remove_categoria(self, args):
        nome_categoria = normalizar_nome(args[0])
        categoria = self.obter_skeleton().obter_loja().remover_categoria(nome_categoria)
        return [OpCodes.OK_REMOVE_CATEGORIA, [categoria]]

    def _cmd_cria_produto(self, args):
        nome_produto = normalizar_nome(args[0])
        nome_categoria = normalizar_nome(args[1])
        try:
            preco = round(float(args[2]), 2)
        except ValueError:
            raise shared.excepcoes_shared.TipoArgumentoInvalido()
        try:
            quantidade = int(args[3])
        except ValueError:
            raise shared.excepcoes_shared.TipoArgumentoInvalido()

        produto = self.obter_skeleton().obter_loja().criar_produto(nome_produto, nome_categoria, preco, quantidade)    
        return [OpCodes.OK_CRIA_PRODUTO, [produto]]
    
    def _cmd_lista_produtos(self, args):
        if len(args) != 0:
            raise shared.excepcoes_shared.ValorArgumentoInvalido("Lista de argumentos deve ser vazia.")
        
        categorias, produtos = self.obter_skeleton().obter_loja().listar_produtos()
        return [OpCodes.OK_LISTA_PRODUTOS, [categorias, produtos]]

    def _cmd_aumenta_stock_produto(self, args):
        nome_produto = normalizar_nome(args[0])
        try:
            quantidade_delta = int(args[1])
        except ValueError:
            raise shared.excepcoes_shared.TipoArgumentoInvalido()

        produto = self.obter_skeleton().obter_loja().aumentar_stock_produto(nome_produto, quantidade_delta)
        return [OpCodes.OK_AUMENTA_STOCK, [produto]]

    def _cmd_atualiza_preco_produto(self, args):
        nome_produto = normalizar_nome(args[0])
        try:
            novo_preco = float(args[1])
        except ValueError:
            raise shared.excepcoes_shared.PrecoInvalido()
        produto = self.obter_skeleton().obter_loja().atualizar_preco_produto(nome_produto, novo_preco)
        return [OpCodes.OK_ATUALIZA_PRECO, [produto]]

    def _cmd_cria_cliente(self, args):
        nome = normalizar_nome(args[0])
        email = args[1]
        pw = args[2]
        id_cliente = args[3]
        permissao = args[4]

        if permissao != 0:
            raise shared.excepcoes_shared.OperacaoNaoAutorizada()
        
        if '@' not in email:
            raise shared.excepcoes_shared.EmailInvalido()

        cliente = self.obter_skeleton().obter_loja().criar_cliente(nome, email, pw, id_cliente, permissao)
        return [OpCodes.OK_CRIA_CLIENTE, [cliente]] 
    
    def _cmd_lista_clientes(self, args):
        if len(args) != 0:
            raise shared.excepcoes_shared.ValorArgumentoInvalido("Lista de argumentos deve ser vazia.")
        return [OpCodes.OK_LISTA_CLIENTES, [self.obter_skeleton().obter_loja().listar_clientes()]]

    def _cmd_adiciona_produto_carrinho(self, args):
        perfil = args[-1]
        if perfil == 2 or perfil == 3:
            raise shared.excepcoes_shared.OperacaoNaoAutorizada("Funcionários e administradores não podem ter carrinho de compras.")

        try:
            quantidade = int(args[1])
        except ValueError:
            raise shared.excepcoes_shared.QuantidadeInvalida()
        nome_produto = normalizar_nome(args[0])
        id_cliente = int(args[2])
        produto = self.obter_skeleton().obter_loja().adiciona_produto_carrinho(id_cliente, nome_produto, quantidade)
        return [OpCodes.OK_ADICIONA_CARRINHO,[produto]]
    
    def _cmd_remove_produto_carrinho(self, args):
        perfil = args[-1]
        if perfil == 2 or perfil == 3:
            raise shared.excepcoes_shared.OperacaoNaoAutorizada("Funcionários e administradores não podem ter carrinho de compras.")

        nome_produto = normalizar_nome(args[0])
        id_cliente = args[1]
        produto = self.obter_skeleton().obter_loja().remover_produto_carrinho(id_cliente, nome_produto)
        return [OpCodes.OK_REMOVE_CARRINHO, [produto]]
    
    def _cmd_lista_carrinho(self, args):
        perfil = args[-1]
        if perfil == 2 or perfil == 3:
            raise shared.excepcoes_shared.OperacaoNaoAutorizada("Funcionários e administradores não podem ter carrinho de compras.")
        
        id_cliente = args[0]
        categorias, produtos = self.obter_skeleton().obter_loja().lista_carrinho_cliente(id_cliente)
        return [OpCodes.OK_LISTA_CARRINHO, [categorias, produtos]]

    def _cmd_checkout_carrinho(self, args):
        perfil = args[-1]
        if perfil == 2 or perfil == 3:
            raise shared.excepcoes_shared.OperacaoNaoAutorizada("Funcionários e administradores não podem ter carrinho de compras.")
        
        id_cliente = args[0]
        encomenda = self.obter_skeleton().obter_loja().checkout_carrinho(id_cliente)
        return [OpCodes.OK_CHECKOUT, [encomenda]]
    
    def _cmd_lista_encomendas(self, args):
        id_cliente = int(args[0])
        encomendas, produtos_por_encomenda = self.obter_skeleton().obter_loja().lista_encomendas(id_cliente)
        return [OpCodes.OK_LISTA_ENCOMENDAS, [encomendas, produtos_por_encomenda]]
