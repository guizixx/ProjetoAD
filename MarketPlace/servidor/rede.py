# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 
# Descrição: Camada de transporte TCP do servidor - aceita ligações e move strings

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

    def iniciar(self, processador):
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_servidor.bind((self.ponto_acesso.endereco_ip, int(self.ponto_acesso.porto)))
        self.socket_servidor.listen(1)
        print(f"SERVIDOR> A escutar em {self.ponto_acesso.endereco_ip}:{self.ponto_acesso.porto}")
        
        while True:
            try:
                (conn_sock, (addr, port)) = self.socket_servidor.accept()
                print("SERVIDOR> Servidor ligado a %s no porto %s" % (addr, port))
                self.tratar_cliente(conn_sock, processador)
            except KeyboardInterrupt:
                print("SERVIDOR> Servidor terminado pelo utilizador.")
                break
            except OSError as e:
                print(f"SERVIDOR> Erro ao aceitar ligação: {e}")
                break

        self.socket_servidor.close()

    def tratar_cliente(self, conn_sock, processador):
        try:
            while True:
                dados = conn_sock.recv(4096)
                if not dados:
                    print(f"SERVIDOR> Cliente desligou-se.")
                    break

                comando = dados.decode('utf-8').strip()
                print(f"SERVIDOR> Comando recebido: {comando}")

                resposta = processador.processar_comando(comando)
                print(f"SERVIDOR> Resposta: {resposta}")
                conn_sock.sendall((resposta + "\n").encode('utf-8'))

                if comando.upper() == "EXIT":
                    break
        except KeyboardInterrupt:
            raise
        except OSError as e:
            print(f"SERVIDOR> Erro na comunicação com o cliente: {e}")
        finally:
            conn_sock.close()
            print(f"SERVIDOR> Ligação com o cliente encerrada.")