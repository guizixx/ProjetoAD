# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Camada de transporte TCP do servidor - aceita ligações e move strings

import socket
from shared.socket_utilities import PontoAcesso
from shared import excepcoes_shared
# ver se a classe continua a ser TCPSocketserver ou Rede
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
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_servidor.bind((self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto)))
        self.socket_servidor.listen(1)
        print(f"SERVIDOR> A escutar em {self.ponto_acesso.endereco_ip}:{self.ponto_acesso.porto}")

    def envia(self, size, bytes): 
        try:
            self.socket_servidor.sendall(size)
            self.socket_servidor.sendall(bytes)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e

    def recebe(self): 
        bytes = self.conn_sock.recv(1024)
        return bytes

    def close(self): 
        self.conn_sock.close()

    def closeall(self): 
        self.conn_sock.close()
        self.socket_servidor.close()

    def accept(self): 
        (conn_sock, addr) = self.socket_servidor.accept()
        self.conn_sock = conn_sock