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
    #TODO: chamar funcoes de rede do servidor ...
    #TODO: apagar e substituir código abaixo por código de sockets

    print("SERVIDOR> A aguardar implementação de:")
    print("SERVIDOR>  - Criação do socket")
    print("SERVIDOR>  - Bind ao endereço")
    print("SERVIDOR>  - Colocação em modo listen")
    print("SERVIDOR>  - Aceitação de ligação de cliente")
    print("SERVIDOR>  - Tratamento de exceções")
    print("SERVIDOR>  - A função processar_comando() deve ser desenvolvida.")
    print("SERVIDOR> NÃO remover a chamada a processar_comando() — é obrigatória para a correção automática.")
    print("SERVIDOR> NÃO alterar path para processar_comando() — é obrigatório para a correção automática.")
    
    while True: 
        print("SERVIDOR> Servidor pronto para receber comandos simulado. ")
        comando = servidor.simula_cliente()
        resposta = processador.processar_comando(comando)
        print(resposta)
        if comando == 'EXIT': 
            break

if __name__ == "__main__":
    main()