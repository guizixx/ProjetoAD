# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Camada de transporte TCP do cliente - conecta ao servidor e move bytes.
#            Não interpreta conteúdo - apenas lida com sockets.

import socket
from shared.socket_utilities import PontoAcesso, receive_all
from shared import excepcoes_shared
import struct
import ssl

class TCPSocketCliente:

    def __init__(self, ponto_acesso, ca_ficheiro=None):
        """
        cert_ficheiro: caminho para o certificado SSL
        key_ficheiro: caminho para a chave privada SSL
        ca_ficheiro: caminho para a autoridade certificadora
        """
        self.ponto_acesso = ponto_acesso
        self.ca_ficheiro = ca_ficheiro

        sock_pre_ssl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if ca_ficheiro is not None:
            context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            context.load_verify_locations(cafile= ca_ficheiro)
            self.socket_cliente = context.wrap_socket(sock_pre_ssl, server_hostname= self.ponto_acesso.endereco_ip)
        else:
            self.socket_cliente = sock_pre_ssl

    def ligar(self):
        self.socket_cliente.connect((self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto)))
        print(f"CLIENTE> Ligado ao servidor em {self.ponto_acesso.endereco_ip}:{self.ponto_acesso.porto}")

    def receive_all(self, length):
        dados = b""
        while len(dados) < length:
            parte = self.socket_cliente.recv(length - len(dados))
            print(f"CLIENTE> Recebido {len(parte)} bytes, total recebido: {len(dados) + len(parte)}/{length} bytes")
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
            print(f"CLIENTE> Tamanho dos bytes a receber: {struct.unpack('!I', tamanho_bytes)[0]} bytes")
            tamanho = struct.unpack('!I', tamanho_bytes)[0]
            dados = self.receive_all(tamanho)
            print(f"CLIENTE> Dados recebidos: {dados}")
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