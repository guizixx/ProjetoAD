import socket
from shared.socket_utilities import PontoAcesso
from servidor.processador import Processador


class TCPSocketServidor:
    """
    Camada Transporte:
    - não interpreta comandos
    - não chama Loja
    - não faz validações de negócio
    - só move strings
    """

    def __init__(self, ponto_acesso):
        self.ponto_acesso = ponto_acesso
        self.socket_servidor = None

    # TODO: A eliminar (código auxiliar)
    def simula_cliente(self):
        return input("SERVIDOR> Escreva mensagem>")

    # TODO: A completar