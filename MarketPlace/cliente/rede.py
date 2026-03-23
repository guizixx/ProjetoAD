# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Camada de transporte TCP do cliente - conecta ao servidor e move strings

import socket
from shared.socket_utilities import PontoAcesso

class TCPSocketCliente:
    """
    Camada Transporte:
    - move strings 
    - não conhece regras de negócio
    - não interpreta comandos
    """

    def __init__(self, ponto_acesso):
        self.ponto_acesso = ponto_acesso
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_cliente.connect((self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto)))
        print(f"CLIENTE> Ligado ao servidor em {self.ponto_acesso.endereco_ip}:{self.ponto_acesso.porto}")

    def envia(self, bytes):
        self.socket_cliente.sendall(bytes)

    def recebe(self):
        # ver com o gui o recv
        # passar o decode dos dados para o stub
        resposta = b""
        while True:
            parte = self.socket_cliente.recv(4096)
            resposta += parte
            if resposta.endswith(b"\n"):
                break
        return resposta
    
    def desligar(self):
        if self.socket_cliente is not None:
            self.socket_cliente.close()
            self.socket_cliente = None
            print("CLIENTE> Ligação encerrada.")