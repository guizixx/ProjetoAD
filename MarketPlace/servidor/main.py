# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Ponto de entrada do servidor - inicializa socket TCP e aguarda clientes

import sys
from servidor.processador import Processador
from servidor.rede import TCPSocketServidor
from shared.excepcoes import ExcepcaoConfiguracaoInvalida
from shared.socket_utilities import PontoAcesso

def main():

    if len(sys.argv) != 2:
        print("SERVIDOR> Uso: python -m servidor.main <porto>")
        sys.exit(1)

    processador = Processador()
    try:
        ponto_acesso = PontoAcesso(endereco_ip='localhost', porto = sys.argv[1])  
        print("SERVIDOR> Configuracao do servidor válida. ")

    except ExcepcaoConfiguracaoInvalida as e:
        print("SERVIDOR>", e)
        sys.exit(1)

    servidor = TCPSocketServidor(ponto_acesso)
    
    servidor.iniciar(processador)

if __name__ == "__main__":
    main()