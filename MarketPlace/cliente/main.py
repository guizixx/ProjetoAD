# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 
# Descrição: Ponto de entrada do cliente - lê comandos do utilizador e comunica com o servidor

from sys import argv
import sys
from  shared.socket_utilities import PontoAcesso
from shared.excepcoes import ExcepcaoConfiguracaoInvalida
from cliente.rede import TCPSocketCliente

def main():
    if len(argv) != 2:
        print("CLIENTE> Uso: python -m cliente.main <porto>")
        sys.exit(1)

    try: 
        # valida endereco_ip e porto (se erro ExcepcaoIPInvalido ou ExcepcaoPortoInvalido)
        ponto_acesso = PontoAcesso(endereco_ip = 'localhost', porto = argv[1])
        print("CLIENTE> Configuracao do servidor válida. ")
        print("CLIENTE> Iniciando aplicação do lado do cliente. ")
    except ExcepcaoConfiguracaoInvalida  as e: 
        print("CLIENTE>", e)
        sys.exit(1) 

    # TODO: chama funcoes no cliente para contactar o servidor e enviar mensagens
    cliente = TCPSocketCliente(ponto_acesso)

    try:
        cliente.ligar()
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

            cliente.enviar_comando(comando)
            resposta = cliente.receber_resposta()
            print(f"SERVIDOR> {resposta}")

            if comando.strip().upper() == "EXIT":
                break

    except OSError as e:
        print(f"CLIENTE> Erro na comunicação: {e}")
    finally:
        cliente.desligar()


if __name__ == "__main__":
    main()