# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Camada de transporte TCP do servidor - aceita ligações e move bytes.
#            Não interpreta conteúdo - apenas lida com sockets.

import socket
import struct
import ssl
from shared.socket_utilities import PontoAcesso
from shared import excepcoes_shared
import struct

class TCPSocketServidor:

    def __init__(self, ponto_acesso, ca_ficheiro, cert_ficheiro, key_ficheiro):
        """
        ca_ficheiro: caminho para o certificado CA
        cert_ficheiro: caminho para o certificado SSL
        key_ficheiro: caminho para a chave privada SSL
        """
        self.ponto_acesso = ponto_acesso
        self.ca_ficheiro = ca_ficheiro
        self.cert_ficheiro = cert_ficheiro
        self.key_ficheiro = key_ficheiro

        sock_antes_ssl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_antes_ssl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_antes_ssl.bind((self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto)))
        sock_antes_ssl.listen(5)
        
        if self.cert_ficheiro is not None and self.key_ficheiro is not None:
            contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            contexto.verify_mode = ssl.CERT_REQUIRED
            contexto.load_verify_locations(cafile=self.ca_ficheiro)
            contexto.load_cert_chain(certfile=self.cert_ficheiro, keyfile=self.key_ficheiro)
            self.socket_servidor = contexto.wrap_socket(sock_antes_ssl, server_side=True)
            print(f"SERVIDOR> A escutar com SSL em \n {self.ponto_acesso.endereco_ip}:{self.ponto_acesso.porto}")
        else:
            self.socket_servidor = sock_antes_ssl
            print(f"SERVIDOR> A escutar em \n {self.ponto_acesso.endereco_ip}:{self.ponto_acesso.porto}")

    def receive_all(self, conn_sock, length):
        dados = b""
        while len(dados) < length:
            parte = conn_sock.recv(length - len(dados))
            print(f"SERVIDOR> Recebido {len(parte)} bytes, total recebido: {len(dados) + len(parte)}/{length} bytes")
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

    
    def ligar_a_servidor(self, endereco, ca_ficheiro=None):
        """
        Ligação TCP com SSL opcional a outro servidor da cadeia.

        ca_ficheiro: caminho para o certificado CA para verificar o servidor destino.
        """

        try:
            ip, porto = endereco.split(":")
            sock_saida = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if ca_ficheiro is not None:
                contexto = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                contexto.verify_mode = ssl.CERT_REQUIRED
                contexto.check_hostname = True
                contexto.load_verify_locations(cafile=self.ca_ficheiro)
                contexto.load_cert_chain(certfile=self.cert_ficheiro, keyfile=self.key_ficheiro)
                sock = contexto.wrap_socket(sock_saida, server_hostname=ip)
            else:
                sock = sock_saida

            sock.connect((ip, int(porto)))
            print(f"SERVIDOR> Ligado ao servidor {endereco}")
            return sock

        except Exception as e:
            print(f"SERVIDOR> Erro ao ligar ao servidor {endereco}: {e}")
            return None
