# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Camada de transporte TCP do servidor - aceita ligações e move strings

import socket
import struct
from shared.socket_utilities import PontoAcesso
from shared import excepcoes_shared
import struct
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
        self.socket_servidor.listen(5)
        print(f"SERVIDOR> A escutar em {self.ponto_acesso.endereco_ip}:{self.ponto_acesso.porto}")

    def receive_all(self, conn_sock, length):
        dados = b""
        while len(dados) < length:
            parte = conn_sock.recv(length - len(dados))
            if not parte:
                raise excepcoes_shared.ExcecaoLigacaoInterrompida()
            dados += parte
        return dados

    def envia(self, conn_sock, tamanho, bytes): 
        try:
            conn_sock.sendall(tamanho)
            conn_sock.sendall(bytes)
        except OSError:
            raise excepcoes_shared.ExcecaoLigacaoInterrompida()

    def recebe(self, conn_sock): 
        try:
            tamanho_bytes = self.receive_all(conn_sock, 4)
            tamanho = struct.unpack('!I', tamanho_bytes)[0]
            dados = self.receive_all(conn_sock, tamanho)
            return dados
        except excepcoes_shared.ExcecaoLigacaoInterrompida:
            raise
        except OSError:
            raise excepcoes_shared.ExcecaoLigacaoInterrompida()

    def close(self): 
        self.conn_sock.close()

    def closeall(self): 
        self.conn_sock.close()
        self.socket_servidor.close()

    def accept(self): 
        conn_sock, addr = self.socket_servidor.accept()
        return conn_sock, addr