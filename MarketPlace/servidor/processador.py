# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 
# Descrição: 

from servidor.excepcoes import ExcepcaoComandoInvalido
from servidor.excepcoes import ExcepcaoComandoDesconhecido
from servidor.excepcoes import ExcepcaoComandoNumeroArgumentosIncorreto
from servidor.excepcoes import ExcepcaoSupermercado
from servidor.excepcoes import ExcepcaoComandoNaoInterpretavel
from servidor.excepcoes import ExcepcaoComandoVazio
import shlex
from servidor.loja import Loja

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
            "AUMENTA_STOCK_PRODUTO": self._cmd_aumenta_stock,
            "ATUALIZA_PRECO_PRODUTO": self._atualiza_preco,
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

    # _cmd_ handlers

    def _cmd_cria_categoria(self, args):
        self._validar_n_args(args, 1)
        nome_categoria = args[0]
        categoria = self.loja.criar_categoria(nome_categoria)
        return f"Categoria {categoria.nome} criada com sucesso."
    
    def _cmd_lista_categorias(self):
        prints = "OK; \n"
        categorias = self.loja._categorias
        if categorias.__len__() == 0:
            return "OK; Sem Categorias."
        for c in categorias.values():
            prints + f"{c.id} - {c.nome} - {c.nr_produtos_categoria};\n"
        return prints

    def _cmd_remove_categorias(self, args):
        self._validar_n_args(args, 1)
        categoria = self.loja.obter_id_categoria(args[0])
        if categoria is None:
            raise ExcepcaoComandoInvalido("Categoria Inexistente")
        for p in self.loja._produtos.values():
            if (p._categoria == categoria & p._quantidade > 0):
                raise ExcepcaoComandoInvalido("Existem produtos com essa categoria associada")
        
        return f"Categoria {self.loja._categorias.get(categoria)} removida com sucesso."

    def _cmd_cria_produto(self, args):
        self._validar_n_args(args, 4)
        nome_produto = args[0]
        nome_categoria = args[1]
        preco = round(args[2], 2)
        quantidade = args[3]

        for p in self.loja._produtos.values():
            if nome_produto == p.nome():
                raise ExcepcaoComandoInvalido("Nome do produto já existe.")

        if self.loja.obter_id_categoria(nome_categoria) is None:
            raise ExcepcaoComandoInvalido("Categoria não existe.")

        if preco <= 0:
            raise ExcepcaoComandoInvalido("Preço inválido.")

        if quantidade < 0:
            raise ExcepcaoComandoInvalido("Quantidade inválida.")


        return f"Produto {nome_produto} criado com sucesso."
    
    def _cmd_sai_aplicacao(self, args):
        self._validar_n_args(args, 0)
        return "Saindo da aplicação do lado do servidor."
    
    def processar_comando(self, comando):
        try:
            nome_comando, args = self._dividir_comando(comando)
            handler = self._obter_handler(nome_comando)
        
            resultado = handler(args)
            return f"OK; {resultado}"
        except (ExcepcaoSupermercado, ExcepcaoComandoInvalido) as e:
            return f"NOK; {e}"
