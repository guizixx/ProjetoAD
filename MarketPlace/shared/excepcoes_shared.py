# ---------------------------------------------
# Códigos de Operação (ver excepcoes abaixo)
# ---------------------------------------------

class OpCodes:
    # -------------------------
    # PEDIDOS (1xxxx)
    # -------------------------
    CRIA_CATEGORIA = 10100
    LISTA_CATEGORIAS = 10200
    REMOVE_CATEGORIA = 10300

    CRIA_PRODUTO = 10400
    LISTA_PRODUTOS = 10500
    AUMENTA_STOCK = 10600
    ATUALIZA_PRECO = 10700

    CRIA_CLIENTE = 10800
    LISTA_CLIENTES = 10900

    ADICIONA_PRODUTO_CARRINHO = 11000
    REMOVE_PRODUTO_CARRINHO = 11100
    LISTA_CARRINHO = 11200
    CHECKOUT_CARRINHO = 11300

    LISTA_ENCOMENDAS = 11400

    # -------------------------
    # SUCESSO (2xxxx)
    # -------------------------
    OK_CRIA_CATEGORIA = 20100
    OK_LISTA_CATEGORIAS = 20200
    OK_REMOVE_CATEGORIA = 20300

    OK_CRIA_PRODUTO = 20400
    OK_LISTA_PRODUTOS = 20500
    OK_AUMENTA_STOCK = 20600
    OK_ATUALIZA_PRECO = 20700

    OK_CRIA_CLIENTE = 20800
    OK_LISTA_CLIENTES = 20900

    OK_ADICIONA_CARRINHO = 21000
    OK_REMOVE_CARRINHO = 21100
    OK_LISTA_CARRINHO = 21200
    OK_CHECKOUT = 21300

    OK_LISTA_ENCOMENDAS = 21400

    # -------------------------
    # ERROS GENÉRICOS (39xxx)
    # -------------------------
    ERRO_GENERICO = 39900
    OP_CODE_INVALIDO = 39901
    MENSAGEM_MAL_FORMADA = 39902
    NUMERO_ARGUMENTOS_INVALIDO = 39914
    TIPO_ARGUMENTO_INVALIDO = 39915
    VALOR_ARGUMENTO_INVALIDO = 39916
    ARGUMENTO_VAZIO = 39918
    OPERACAO_NAO_AUTORIZADA = 39920
    UTILIZADOR_NAO_AUTENTICADO = 39921
    ERRO_INTERNO_SERVIDOR = 39928

    # -------------------------
    # ERROS DE NEGÓCIO (3xxxx)
    # -------------------------
    CATEGORIA_JA_EXISTE = 30110
    CATEGORIA_NAO_EXISTE = 30310
    CATEGORIA_COM_PRODUTOS = 30311

    PRODUTO_JA_EXISTE = 30410
    CATEGORIA_NAO_EXISTE_PRODUTO = 30411
    PRECO_INVALIDO = 30412
    QUANTIDADE_INVALIDA = 30413
    NOME_PRODUTO_INVALIDO = 30414

    PRODUTO_NAO_EXISTE = 30610
    INCREMENTO_INVALIDO = 30611

    PRODUTO_NAO_EXISTE_PRECO = 30710
    NOVO_PRECO_INVALIDO = 30711

    EMAIL_JA_EXISTE = 30810
    NOME_CLIENTE_INVALIDO = 30811
    EMAIL_INVALIDO = 30812
    PASSWORD_INVALIDA = 30813

    CLIENTE_NAO_EXISTE = 31010
    PRODUTO_NAO_EXISTE_CARRINHO = 31011
    QUANTIDADE_INVALIDA_CARRINHO = 31012
    STOCK_INSUFICIENTE = 31013

    CLIENTE_NAO_EXISTE_REMOVE = 31110
    PRODUTO_NAO_EXISTE_REMOVE = 31111
    PRODUTO_NAO_NO_CARRINHO = 31112

    CLIENTE_NAO_EXISTE_LISTA = 31210

    CLIENTE_NAO_EXISTE_CHECKOUT = 31310
    CARRINHO_VAZIO = 31311
    FALHA_ENCOMENDA = 31312

    CLIENTE_NAO_EXISTE_ENCOMENDAS = 31410


#--------------------------------------------------
#--------------------------------------------------
# Excepções Específicas (A LANÇAR NUNCA, SO EM ULTIMO CASO)
# APANHAR NO TRY CATCH
# -------------------------------------------------
#--------------------------------------------------

class ExcepcaoBase(Exception):
    def __init__(self, msg, code):
        super().__init__(msg)
        self.msg = msg
        self.code = code


class ExcepcaoComando(ExcepcaoBase):
    pass


class ExcepcaoValidacao(ExcepcaoBase):
    pass


class ExcepcaoNegocio(ExcepcaoBase):
    pass


class ExcepcaoInterna(ExcepcaoBase):
    pass

#--------------------------------------------------
#--------------------------------------------------
# Excepções Específicas (A LANÇAR ESPECIFICAMENTE)
# -------------------------------------------------
#--------------------------------------------------

# ----------------------------------
#   EXCEÇÕES DE COMANDO
# ----------------------------------

class ComandoDesconhecido(ExcepcaoComando):
    def __init__(self, nome):
        super().__init__(
            f"O comando {nome} não é conhecido.",
            OpCodes.OP_CODE_INVALIDO
        )


class ComandoMalFormado(ExcepcaoComando):
    def __init__(self, comando):
        super().__init__(
            f"Não foi possível interpretar o comando '{comando}'.",
            OpCodes.MENSAGEM_MAL_FORMADA
        )


class ComandoVazio(ExcepcaoComando):
    def __init__(self):
        super().__init__(
            "Não é possível correr um comando vazio.",
            OpCodes.ARGUMENTO_VAZIO
        )


class NumeroArgumentosInvalido(ExcepcaoComando):
    def __init__(self, esperado, recebido):
        super().__init__(
            f"Número de argumentos inválido. Esperado {esperado}, recebido {recebido}.",
            OpCodes.NUMERO_ARGUMENTOS_INVALIDO
        )


# ----------------------------------
#   EXCEÇÕES DE VALIDAÇÃO
# ----------------------------------

class TipoArgumentoInvalido(ExcepcaoValidacao):
    def __init__(self, nome):
        super().__init__(
            f"O argumento '{nome}' tem tipo inválido.",
            OpCodes.TIPO_ARGUMENTO_INVALIDO
        )


class ValorArgumentoInvalido(ExcepcaoValidacao):
    def __init__(self, msg="Valor inválido."):
        super().__init__(msg, OpCodes.VALOR_ARGUMENTO_INVALIDO)


class PrecoInvalido(ExcepcaoValidacao):
    def __init__(self):
        super().__init__(
            "Preço inválido. Deve ser maior que zero.",
            OpCodes.PRECO_INVALIDO
        )


class QuantidadeInvalida(ExcepcaoValidacao):
    def __init__(self):
        super().__init__(
            "Quantidade inválida.",
            OpCodes.QUANTIDADE_INVALIDA
        )


class QuantidadeCarrinhoInvalida(ExcepcaoValidacao):
    def __init__(self):
        super().__init__(
            "Quantidade inválida no carrinho.",
            OpCodes.QUANTIDADE_INVALIDA_CARRINHO
        )


class EmailInvalido(ExcepcaoValidacao):
    def __init__(self):
        super().__init__(
            "Email inválido.",
            OpCodes.EMAIL_INVALIDO
        )


class PasswordInvalida(ExcepcaoValidacao):
    def __init__(self):
        super().__init__(
            "Password inválida.",
            OpCodes.PASSWORD_INVALIDA
        )


# ----------------------------------
#   EXCEÇÕES DE NEGÓCIO
# ----------------------------------

class CategoriaJaExiste(ExcepcaoNegocio):
    def __init__(self, nome):
        super().__init__(
            f"A categoria {nome} já existe.",
            OpCodes.CATEGORIA_JA_EXISTE
        )


class CategoriaNaoExiste(ExcepcaoNegocio):
    def __init__(self, nome):
        super().__init__(
            f"A categoria {nome} não existe.",
            OpCodes.CATEGORIA_NAO_EXISTE
        )


class CategoriaComProdutos(ExcepcaoNegocio):
    def __init__(self, nome):
        super().__init__(
            f"A categoria {nome} tem produtos associados.",
            OpCodes.CATEGORIA_COM_PRODUTOS
        )


class ProdutoJaExiste(ExcepcaoNegocio):
    def __init__(self, nome):
        super().__init__(
            f"O produto {nome} já existe.",
            OpCodes.PRODUTO_JA_EXISTE
        )


class ProdutoNaoExiste(ExcepcaoNegocio):
    def __init__(self, nome=""):
        super().__init__(
            f"O produto {nome} não existe." if nome else "Produto não existe.",
            OpCodes.PRODUTO_NAO_EXISTE
        )


class ClienteNaoExiste(ExcepcaoNegocio):
    def __init__(self):
        super().__init__(
            "Cliente não existe.",
            OpCodes.CLIENTE_NAO_EXISTE
        )


class EmailJaExiste(ExcepcaoNegocio):
    def __init__(self):
        super().__init__(
            "Email já registado.",
            OpCodes.EMAIL_JA_EXISTE
        )


class StockInsuficiente(ExcepcaoNegocio):
    def __init__(self):
        super().__init__(
            "Stock insuficiente.",
            OpCodes.STOCK_INSUFICIENTE
        )


class ProdutoNaoNoCarrinho(ExcepcaoNegocio):
    def __init__(self):
        super().__init__(
            "Produto não está no carrinho.",
            OpCodes.PRODUTO_NAO_NO_CARRINHO
        )


class CarrinhoVazio(ExcepcaoNegocio):
    def __init__(self):
        super().__init__(
            "Carrinho vazio.",
            OpCodes.CARRINHO_VAZIO
        )


class FalhaEncomenda(ExcepcaoNegocio):
    def __init__(self):
        super().__init__(
            "Falha ao criar encomenda.",
            OpCodes.FALHA_ENCOMENDA
        )


# ----------------------------------
#   EXCEÇÕES INTERNAS
# ----------------------------------

class ErroInterno(ExcepcaoInterna):
    def __init__(self, msg="Erro interno do servidor."):
        super().__init__(msg, OpCodes.ERRO_INTERNO_SERVIDOR)


class OperacaoNaoAutorizada(ExcepcaoInterna):
    def __init__(self):
        super().__init__(
            "Operação não autorizada.",
            OpCodes.OPERACAO_NAO_AUTORIZADA
        )


class UtilizadorNaoAutenticado(ExcepcaoInterna):
    def __init__(self):
        super().__init__(
            "Utilizador não autenticado.",
            OpCodes.UTILIZADOR_NAO_AUTENTICADO
        )