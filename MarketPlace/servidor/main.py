# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Ponto de entrada do servidor - inicializa socket TCP e aguarda clientes

import sys
import select as sel
import time
from processador import Processador
from shared.excepcoes import ExcepcaoConfiguracaoInvalida
from ..shared.socket_utilities import PontoAcesso

def main():

    # !!!! adaptar ao protocolo de mnsgs da fase2
    if len(sys.argv) != 2:
        print("SERVIDOR> Uso: python -m servidor.main <porto>")
        sys.exit(1)

    try:
        ponto_acesso = PontoAcesso(endereco_ip='localhost', porto = sys.argv[1])  
        print("SERVIDOR> Configuracao do servidor válida. ")

    except ExcepcaoConfiguracaoInvalida as e:
        print("SERVIDOR>", e)
        sys.exit(1)

    processador = Processador(ponto_acesso)
    sock_escuta = processador.rede.socket_servidor

    RUNNING = True
    lista_sockets = [sock_escuta]
    while RUNNING:
        R, W, X = sel.select(lista_sockets, [], []) # Espera sockets

        for sckt in R:
            if sckt is sock_escuta: # Se for a socket de escuta...
                conn_sock, addr = sock_escuta.accept()
                addr, port = conn_sock.getpeername()
                print('Novo cliente ligado desde %s:%d' % (addr, port))
                lista_sockets.append(conn_sock) # Adiciona ligação à lista
            else: # Se for a socket de um cliente...
                msg = sckt.recv(1024)
                if msg: # Se recebeu dados
                    try:
                        if msg.decode().upper() in ("EXIT","QUIT"):
                            lista_sockets.remove(sckt)
                            print('SERVIDOR> Cliente fechou ligação')
                            break

                        # adicionar stdin, outras excecoes
                        # ver se o codigo faz sentido assim

                        processador.accept()
                        processador.processar_comando()
                        processador.close()
                        
                    except OSError as e:
                        print(f"SERVIDOR> Erro na comunicação com o cliente: {e}")
                    
                else: # Se não recebeu dados
                    sckt.close() # cliente fechou ligação
                    lista_sockets.remove(sckt)
                    print('Cliente fechou ligação')
    sock_escuta.close()


if __name__ == "__main__":
    main()