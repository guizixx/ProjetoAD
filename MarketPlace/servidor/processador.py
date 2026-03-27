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
from shared.utilities import normalizar_nome

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

    def __init__(self):
        self.loja = Loja()
                        # opcode:  [ handler, permissão mínima para poder executar a operação, numero_args a serem passados ]
        self.HANDLERS = {
            OpCodes.CRIA_CATEGORIA: [self._cmd_cria_categoria, 3, 1],
            OpCodes.LISTA_CATEGORIAS: [self._cmd_lista_categorias, 3, 0],
            OpCodes.REMOVE_CATEGORIA: [self._cmd_remove_categoria, 3, 1],
            OpCodes.CRIA_PRODUTO: [self._cmd_cria_produto, 2, 4],
            OpCodes.LISTA_PRODUTOS: [self._cmd_lista_produtos, 0],
            OpCodes.AUMENTA_STOCK: [self._cmd_aumenta_stock_produto, 2, 2],
            OpCodes.ATUALIZA_PRECO: [self._cmd_atualiza_preco_produto, 2, 2],
            OpCodes.CRIA_CLIENTE: [self._cmd_cria_cliente, 0, 3], 
            OpCodes.LISTA_CLIENTES: [self._cmd_lista_clientes, 2, 0],
            OpCodes.ADICIONA_PRODUTO_CARRINHO: [self._cmd_adiciona_produto_carrinho, 1, 2],
            OpCodes.REMOVE_PRODUTO_CARRINHO: [self._cmd_remove_produto_carrinho, 1, 1],
            OpCodes.LISTA_CARRINHO: [self._cmd_lista_carrinho, 1, 0],
            OpCodes.CHECKOUT_CARRINHO: [self._cmd_checkout_carrinho, 1, 0],
            OpCodes.LISTA_ENCOMENDAS: [self._cmd_lista_encomendas, 1, 1]
        }

    def _dividir_comando(self, comando): 
        pass
    ## VERIFICAR OPCODES CORRETOS
    #       IF IN SELF.HANDLERS.KEYS
    # !!!!!!!!!!!!!!!!!!!1
    
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
    
    def processar_comando(self, comando):
        try:            
            opcode, args, perfil, utilizador = self._dividir_comando(comando)
            self._validar_permissao(perfil, utilizador)
            self._validar_utilizador(perfil, utilizador, opcode)
            self._validar_n_args(args, self.HANDLERS.get(opcode)[2])
            handler = self._obter_handler(opcode)

            # os handlers das ações de gestão de carrinho precisam do id_utilizador
            # o cria_cliente também
            if opcode in  {OpCodes.ADICIONA_PRODUTO_CARRINHO, 
                           OpCodes.REMOVE_PRODUTO_CARRINHO, 
                           OpCodes.CHECKOUT_CARRINHO, 
                           OpCodes.LISTA_CARRINHO, 
                           OpCodes.CRIA_CLIENTE}:
                args.append(utilizador)
        
            resultado = handler(args)
        except (ExcepcaoSupermercado, ExcepcaoComandoInvalido) as e:
            raise e
       
        return resultado
            

    #------------------------
    # _cmd_ handlers
    #------------------------

    def _cmd_cria_categoria(self, args):
        nome_categoria = normalizar_nome(args[0])
        if nome_categoria in ['', []]:
            raise shared.excepcoes_shared.ExcepcaoNegocio("Nome da categoria vazio após normalização.", 
                                                   OpCodes.CATEGORIA_NAO_EXISTE)
        
        categoria = self.loja.criar_categoria(nome_categoria)
        return [OpCodes.OK_CRIA_CATEGORIA, [categoria.nome]]
    
    def _cmd_lista_categorias(self):        
        categorias, produtos = self.loja.lista_categorias()
        return [OpCodes.OK_LISTA_PRODUTOS, categorias, produtos]

    def _cmd_remove_categoria(self, args):
        nome_categoria = normalizar_nome(args[0])
        self.loja.remover_categoria(nome_categoria)
        return [OpCodes.OK_REMOVE_CATEGORIA, []]

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

        produto_nome = self.loja.criar_produto(nome_produto, nome_categoria, preco, quantidade)    
        return [OpCodes.OK_CRIA_PRODUTO, [produto_nome]]
    
    def _cmd_lista_produtos(self):
        categorias, produtos = self.loja.listar_produtos()
        return [OpCodes.OK_LISTA_PRODUTOS, categorias, produtos]

    def _cmd_aumenta_stock_produto(self, args):
        nome_produto = normalizar_nome(args[0])
        try:
            quantidade_delta = int(args[1])
        except ValueError:
            raise shared.excepcoes_shared.TipoArgumentoInvalido()

        self.loja.aumentar_stock_produto(nome_produto, quantidade_delta)
        return [OpCodes.OK_AUMENTA_STOCK, [nome_produto]]

    def _cmd_atualiza_preco_produto(self, args):
        nome_produto = normalizar_nome(args[0])
        try:
            novo_preco = float(args[1])
        except ValueError:
            raise shared.excepcoes_shared.PrecoInvalido()
        self.loja.atualizar_preco_produto(nome_produto, novo_preco)
        return [OpCodes.OK_ATUALIZA_PRECO, [nome_produto]]

    def _cmd_cria_cliente(self, args):
        nome = normalizar_nome(args[0])
        email = args[1]
        pw = args[2]
        id_cliente = args[3]
        if '@' not in email:
            raise shared.excepcoes_shared.EmailInvalido()

        self.loja.criar_cliente(nome, email, pw, id_cliente)
        return [OpCodes.OK_CRIA_CLIENTE, [nome]] 
    
    def _cmd_lista_clientes(self):
        return [OpCodes.OK_LISTA_CLIENTES, self.loja.listar_clientes()]

    def _cmd_adiciona_produto_carrinho(self, args):
        try:
            quantidade = int(args[1])
        except ValueError:
            raise shared.excepcoes_shared.QuantidadeInvalida()
        nome_produto = normalizar_nome(args[0])
        id_cliente = int(args[2])
        self.loja.adiciona_produto_carrinho(id_cliente, nome_produto, quantidade)
        return [OpCodes.OK_ADICIONA_CARRINHO,[nome_produto]]
    
    def _cmd_remove_produto_carrinho(self, args):
        nome_produto = normalizar_nome(args[0])
        id_cliente = args[1]
        self.loja.remover_produto_carrinho(id_cliente, nome_produto)
        return [OpCodes.OK_REMOVE_CARRINHO, [nome_produto]]
    
    def _cmd_lista_carrinho(self, args):
        id_cliente = args[0]
        categorias, produtos = self.loja.lista_carrinho_cliente(id_cliente)
        return [OpCodes.OK_LISTA_CARRINHO, categorias, produtos]

    def _cmd_checkout_carrinho(self, args):
        id_cliente = args[0]
        encomenda_id = self.loja.checkout_carrinho(id_cliente)
        return [OpCodes.OK_CHECKOUT, [encomenda_id]]
    
    def _cmd_lista_encomendas(self, args):
        id_cliente = int(args[0])
        encomendas, produtos_por_encomenda = self.loja.lista_encomendas(id_cliente)
        ans = [OpCodes.OK_LISTA_ENCOMENDAS, encomendas]
        for p in produtos_por_encomenda:
            ans.append(p)
        return ans
