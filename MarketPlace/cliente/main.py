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
    print("CLIENTE> Falta implementar:")
    print("CLIENTE>  - Tratamento de exceções de ligação")
    print("CLIENTE>  - Envio de comandos ao servidor")
    print("CLIENTE>  - Receção e processamento de respostas")


if __name__ == "__main__":
    main()