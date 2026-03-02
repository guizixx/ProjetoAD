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
            "EXIT": self._cmd_sai_aplicacao
            #TODO: restantes comandos
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

    def _cmd_cria_categoria(self, args):
        self._validar_n_args(args, 1)
        nome_categoria = args[0]
        categoria = self.loja.criar_categoria(nome_categoria)
        return f"Categoria {categoria.nome} criada com sucesso."

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
