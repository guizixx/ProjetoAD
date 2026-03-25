# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 
# Descrição: Ponto de entrada do cliente - lê comandos do utilizador e comunica com o servidor

import sys
from  shared.socket_utilities import PontoAcesso
from shared.excepcoes_shared import ExcepcaoConfiguracaoInvalida, OpCodes
from cliente.rede import TCPSocketCliente
import cliente.stub as Stub

COMANDOS_TEXTO = {
    "CRIA_CATEGORIA": OpCodes.CRIA_CATEGORIA,
    "LISTA_CATEGORIAS": OpCodes.LISTA_CATEGORIAS,
    "REMOVE_CATEGORIA": OpCodes.REMOVE_CATEGORIA,
    "CRIA_PRODUTO": OpCodes.CRIA_PRODUTO,
    "LISTA_PRODUTOS": OpCodes.LISTA_PRODUTOS,
    "AUMENTA_STOCK_PRODUTO": OpCodes.AUMENTA_STOCK,
    "ATUALIZA_PRECO_PRODUTO": OpCodes.ATUALIZA_PRECO,
    "CRIA_CLIENTE": OpCodes.CRIA_CLIENTE,
    "LISTA_CLIENTES": OpCodes.LISTA_CLIENTES,
    "ADICIONA_PRODUTO_CARRINHO": OpCodes.ADICIONA_PRODUTO_CARRINHO,
    "REMOVE_PRODUTO_CARRINHO": OpCodes.REMOVE_PRODUTO_CARRINHO,
    "LISTA_CARRINHO": OpCodes.LISTA_CARRINHO,
    "CHECKOUT_CARRINHO": OpCodes.CHECKOUT_CARRINHO,
    "LISTA_ENCOMENDAS": OpCodes.LISTA_ENCOMENDAS,
}

N_ARGS = {
    OpCodes.CRIA_CATEGORIA: 1,
    OpCodes.LISTA_CATEGORIAS: 0,
    OpCodes.REMOVE_CATEGORIA: 1,
    OpCodes.CRIA_PRODUTO: 4,
    OpCodes.LISTA_PRODUTOS: 0,
    OpCodes.AUMENTA_STOCK: 2,
    OpCodes.ATUALIZA_PRECO: 2,
    OpCodes.CRIA_CLIENTE: 3,
    OpCodes.LISTA_CLIENTES: 0,
    OpCodes.ADICIONA_PRODUTO_CARRINHO: 2,
    OpCodes.REMOVE_PRODUTO_CARRINHO: 1,
    OpCodes.LISTA_CARRINHO: 0,
    OpCodes.CHECKOUT_CARRINHO: 0,
    OpCodes.LISTA_ENCOMENDAS: 1,
}

def main():
    if len(sys.argv) != 2:
        print("CLIENTE> Uso: python -m cliente.main <porto>")
        sys.exit(1)

    try: 
        # valida endereco_ip e porto (se erro ExcepcaoIPInvalido ou ExcepcaoPortoInvalido)
        ponto_acesso = PontoAcesso(endereco_ip = 'localhost', porto = sys.argv[1])
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
                exit()

    except OSError as e:
        print(f"CLIENTE> Erro na comunicação: {e}")
    finally:
        cliente.desligar()


if __name__ == "__main__":
    main()