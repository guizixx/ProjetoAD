# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Camada de transporte TCP do cliente - conecta ao servidor e move strings

import socket
from shared.socket_utilities import PontoAcesso, receive_all
from shared import excepcoes_shared
import struct

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

    def envia(self, size, bytes):        
        try:
            self.socket_cliente.sendall(size)
            self.socket_cliente.sendall(bytes)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e

    def recebe(self):
        try:
            size_bytes = self.socket_cliente.recv(4)
            size = struct.unpack('i', size_bytes)[0]
        except: # acabar aqui
        msg_bytes = receive_all(self.socket_cliente, size)
        return msg_bytes
        

    
    def desligar(self):
        if self.socket_cliente is not None:
            self.socket_cliente.close()
            self.socket_cliente = None
            print("CLIENTE> Ligação encerrada.")