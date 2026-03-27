# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Ponto de entrada do cliente - lê comandos do utilizador e comunica com o servidor

import sys
from  shared.socket_utilities import PontoAcesso
from shared.excepcoes_shared import ExcepcaoConfiguracaoInvalida, OpCodes
from cliente.rede import TCPSocketCliente
from cliente.processador import Processador

def main():
    if len(sys.argv) != 2:
        print("CLIENTE> Uso: python -m cliente.main <porto>")
        sys.exit(1)

    try: 
        # valida endereco_ip e porto (se erro ExcepcaoIPInvalido ou ExcepcaoPortoInvalido)
        ponto_acesso = PontoAcesso(endereco_ip = 'localhost', porto = sys.argv[1])
        processador = Processador(ponto_acesso)
        print("CLIENTE> Configuracao do servidor válida. ")
        print("CLIENTE> Iniciando aplicação do lado do cliente. ")
    except ExcepcaoConfiguracaoInvalida  as e: 
        print("CLIENTE>", e)
        sys.exit(1) 

    try:
        processador.ligar()
    except OSError as e:
        print(f"CLIENTE> Erro ao ligar ao servidor: {e}")
        sys.exit(1)

    try:
        while True:
            try:
                comando = input("CLIENTE> ")
            except EOFError:
                break

            if not comando.strip():
                continue

            processador.envia(comando)
            resposta = processador.recebe()
            print(f"SERVIDOR> {resposta}")

            if comando.strip().upper() == "EXIT":
                exit()

    except OSError as e:
        print(f"CLIENTE> Erro na comunicação: {e}")
    finally:
        processador.desligar()


if __name__ == "__main__":
    main()