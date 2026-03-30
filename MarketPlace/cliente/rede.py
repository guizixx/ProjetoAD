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

    def ligar(self):
        self.socket_cliente.connect((self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto)))
        print(f"CLIENTE> Ligado ao servidor em {self.ponto_acesso.endereco_ip}:{self.ponto_acesso.porto}")

    def receive_all(self, length):
        dados = b""
        while len(dados) < length:
            parte = self.socket_cliente.recv(length - len(dados))
            if not parte:
                raise excepcoes_shared.ExcecaoLigacaoInterrompida()
            dados += parte
        return dados

    def envia(self, bytes):        
        try:
            tamanho = struct.pack('!I', len(bytes))
            self.socket_cliente.sendall(tamanho)
            self.socket_cliente.sendall(bytes)
        except OSError:
            raise excepcoes_shared.ExcecaoLigacaoInterrompida()

    def recebe(self):
        try:
            tamanho_bytes = self.receive_all(4)
            tamanho = struct.unpack('!I', tamanho_bytes)[0]
            dados = self.receive_all(tamanho)
            return dados
        except excepcoes_shared.ExcecaoLigacaoInterrompida:
            raise
        except OSError:
            raise excepcoes_shared.ExcecaoLigacaoInterrompida()
        

    
    def desligar(self):
        if self.socket_cliente is not None:
            self.socket_cliente.close()
            self.socket_cliente = None
            print("CLIENTE> Ligação encerrada.")