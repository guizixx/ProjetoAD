# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Ponto de entrada do servidor - inicializa socket TCP e aguarda clientes

import sys
import select as sel
import time
from sys import stdin
from servidor.processador import Processador
from shared.excepcoes_shared import ExcepcaoConfiguracaoInvalida
from shared.socket_utilities import PontoAcesso
from servidor.skeleton import Skeleton

def main():

    if len(sys.argv) != 2:
        print("SERVIDOR> Uso: python -m servidor.main <porto>")
        sys.exit(1)

    try:
        ponto_acesso = PontoAcesso(endereco_ip='localhost', porto = sys.argv[1])  
        processador = Processador(ponto_acesso)
        sock_escuta = processador.obter_skeleton().obter_rede().socket_servidor
        print("SERVIDOR> Configuracao do servidor válida. ")

    except ExcepcaoConfiguracaoInvalida as e:
        print("SERVIDOR>", e)
        sys.exit(1)

    lista_sockets = [sock_escuta, sys.stdin]

    while True:
        R, W, X = sel.select(lista_sockets, [], []) # Espera sockets

        for sckt in R:
            if sckt == sock_escuta: # Se for a socket de escuta...
                conn_sock, addr = sock_escuta.accept()
                addr, port = conn_sock.getpeername()
                print('SERVIDOR> Novo cliente ligado desde %s:%d' % (addr, port))
                lista_sockets.append(conn_sock) # Adiciona ligação à lista
            
            elif sckt == sys.stdin: # Se for a entrada do stdin ...
                command = sys.stdin.readline().strip()
                if command.upper() in ("EXIT","QUIT"):
                    sckt.close()
                    lista_sockets.remove(sckt)
                    print(f"SERVIDOR> Cliente {sckt.fileno()} fechou ligação")
            
            else: # Se for a socket de um cliente...
                msg = processador.recebe()
                if msg: # Se recebeu dados
                    try:
                        if msg.upper() in ("EXIT","QUIT"):
                            sckt.close()
                            lista_sockets.remove(sckt)
                            print('SERVIDOR> Cliente fechou ligação')
                            exit(0)
                            break 

                        processador.processar_comando(msg)  

                    except OSError as e:
                        print(f"SERVIDOR> Erro na comunicação com o cliente: {e}")
                    
                else: # Se não recebeu dados
                    sckt.close() # cliente fechou ligação
                    lista_sockets.remove(sckt)
                    print('Cliente fechou ligação')
    sock_escuta.close()

if __name__ == "__main__":
    main()