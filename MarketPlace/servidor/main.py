# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Ponto de entrada do servidor - inicializa socket TCP e aguarda clientes

import sys
import select as sel
from servidor.processador import Processador
from shared.excepcoes_shared import ExcepcaoConfiguracaoInvalida, ExcecaoLigacaoInterrompida
import shared.excepcoes_shared
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

    print("SERVIDOR> À espera de ligações. Escreva 'exit' ou 'quit' para terminar.")

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
                    print("SERVIDOR> A encerrar...")
                    break
            
            else: # Se for a socket de um cliente...
                try:
                    pedido = processador.recebe(sckt)
                except ExcecaoLigacaoInterrompida:
                    print(f"SERVIDOR> Cliente {sckt.fileno()} fechou a ligação.")
                    sckt.close()
                    lista_sockets.remove(sckt)
                    continue
                except shared.excepcoes_shared.ExcecaoDesserializacaoInvalida:
                    processador.envia(sckt, [shared.excepcoes_shared.OpCodes.DESSERIALIZACAO_INVALIDA, []])
                    continue

                try:
                    resposta = processador.processar_comando(pedido)
                except shared.excepcoes_shared.OperacaoNaoAutorizada:
                    resposta = [shared.excepcoes_shared.OpCodes.OPERACAO_NAO_AUTORIZADA, []]
                except shared.excepcoes_shared.UtilizadorInvalido:
                    resposta = [shared.excepcoes_shared.OpCodes.ID_UTILIZADOR_INVALIDO, []]
                except shared.excepcoes_shared.PerfilInvalido:
                    resposta = [shared.excepcoes_shared.OpCodes.PERFIL_INVALIDO, []]
                except shared.excepcoes_shared.ExcecaoNumeroCamposInvalido:
                    resposta = [shared.excepcoes_shared.OpCodes.NUMERO_CAMPOS_INVALIDO, []]
                except shared.excepcoes_shared.ExcecaoArgumentoInvalido:
                    resposta = [shared.excepcoes_shared.OpCodes.ARGUMENTOS_NAO_SAO_LISTA, []]
                except shared.excepcoes_shared.ComandoDesconhecido:
                    resposta = [shared.excepcoes_shared.OpCodes.OP_CODE_INVALIDO, []]
                except (shared.excepcoes_shared.ExcepcaoNegocio,
                        shared.excepcoes_shared.ExcepcaoValidacao) as e:
                    resposta = [e.code, [str(e)]]
                except Exception as e:
                    resposta = [shared.excepcoes_shared.OpCodes.ERRO_INTERNO_SERVIDOR, [str(e)]]

                try:
                    print(f"SERVIDOR> Enviando resposta: {resposta}")
                    processador.envia(sckt, resposta)
                except ExcecaoLigacaoInterrompida:
                    print(f"SERVIDOR> Cliente {sckt.fileno()} fechou a ligação ao enviar resposta.")
                    sckt.close()
                    lista_sockets.remove(sckt)
                
    for sckt in lista_sockets:
        if sckt != sys.stdin:
            try:
                sock.close()
            except Exception:
                pass
    print("SERVIDOR> Servidor encerrado.")

if __name__ == "__main__":
    main()