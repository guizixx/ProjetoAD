# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Ponto de entrada do servidor. 
#           Regista o servidor no ZooKeeper, sincroniza o estado com o nó antecessor (se existir)        
#           Gere o ciclo select() com múltiplos
#           clientes simultâneos e ligações persistentes. 
#           Usa o Skeleton para comunicação e o Processador para lógica de dispatch.
#           Propaga operações de escrita ao sucessor de forma atómica.

import sys
import select as sel
from servidor.processador import Processador
from servidor.zookeeper_client import ZooKeeperServidor
from shared.excepcoes_shared import ExcepcaoConfiguracaoInvalida, ExcecaoLigacaoInterrompida
import shared.excepcoes_shared
from shared.socket_utilities import PontoAcesso
from servidor.skeleton import Skeleton

def main():

    # Uso sem SSL: python -m servidor.main <porto> <ip_zk>:<porto_zk>
    # Uso com SSL: python -m servidor.main <porto> <ip_zk>:<porto_zk> <cert_ficheiro> <key_ficheiro> <ca_ficheiro>

    if len(sys.argv) not in (4, 7):
        print("SERVIDOR> Uso: python -m servidor.main <ip> <porto> <ip_zk>:<porto_zk> "
              "[serv_crt serv_key root_pem]")
        sys.exit(1)

    ip_proprio = sys.argv[1]
    porto_proprio = sys.argv[2]
    endereco_zk = sys.argv[3]

    # Certifcados SSL
    cert_ficheiro = sys.argv[4] if len(sys.argv) == 7 else None
    key_ficheiro = sys.argv[5] if len(sys.argv) == 7 else None
    ca_ficheiro = sys.argv[6] if len(sys.argv) == 7 else None

    try:
        ponto_acesso = PontoAcesso(endereco_ip=ip_proprio, porto=porto_proprio)
        processador = Processador(ponto_acesso, cert_ficheiro=cert_ficheiro, key_ficheiro=key_ficheiro, ca_ficheiro=ca_ficheiro)
        skeleton = processador.obter_skeleton()
        rede = skeleton.obter_rede()
        sock_escuta = rede.socket_servidor
        print("SERVIDOR> Configuracao do servidor válida. ")
    except ExcepcaoConfiguracaoInvalida as e:
        print("SERVIDOR>", e)
        sys.exit(1)

    zk_servidor = ZooKeeperServidor(endereco_zk, ip_proprio=ip_proprio, porto_proprio=porto_proprio)

    try:
        zk_servidor.ligar(rede)
        zk_servidor.registar()
        antecessor_endereco, sucessor_endereco = zk_servidor.descobrir_vizinhos()
    except Exception as e:
        print(f"SERVIDOR> Erro ao inicializar ZooKeeper: {e}")
        sys.exit(1)

    processador.definir_zk_servidor(zk_servidor)

    if antecessor_endereco is not None:
        skeleton.pedir_estado(antecessor_endereco)
    
    lista_sockets = [sock_escuta, sys.stdin]
    print("SERVIDOR> À espera de ligações. Escreva 'exit' ou 'quit' para terminar.")

    running = True
    while running:
        R, W, X = sel.select(lista_sockets, [], []) # Espera sockets

        for sckt in R:
            if sckt == sock_escuta: # Se for a socket de escuta...
                try:
                    conn_sock, addr = sock_escuta.accept()
                    try:
                        addr, port = conn_sock.getpeername()
                        print('SERVIDOR> Novo cliente ligado desde %s:%d' % (addr, port))
                        lista_sockets.append(conn_sock) # Adiciona ligação à lista
                    except OSError as e:
                        print(f"SERVIDOR> Erro ao obter peer name: {e}. Socket fechado.")
                        try:
                            conn_sock.close()
                        except:
                            pass
                        continue
                except Exception as e:
                    print(f"SERVIDOR> Erro ao aceitar conexão: {e}")
                    continue
            
            elif sckt == sys.stdin: # Se for a entrada do stdin ...
                command = sys.stdin.readline().strip()
                if command.upper() in ("EXIT","QUIT"):
                    print("SERVIDOR> A encerrar...")
                    sockets_to_close = [s for s in lista_sockets if s != sys.stdin]
                    for sckt in sockets_to_close:
                        try:
                            processador.envia(sckt, "SERVIDOR_ENCERROU")
                        except Exception:
                            pass
                        try:
                            sckt.close()
                        except Exception:
                            pass
                        try:
                            lista_sockets.remove(sckt)
                        except Exception:
                            pass
                    print("SERVIDOR> Servidor encerrado.")
                    running = False
                    break
            
            else: # Se for a socket de um cliente...
                try:
                    pedido = processador.recebe(sckt)
                    print(f"SERVIDOR> Pedido recebido do cliente: {pedido}")
                except ExcecaoLigacaoInterrompida:
                    print(f"SERVIDOR> Cliente {sckt.fileno()} fechou a ligação.")
                    try:
                        sckt.close()
                        lista_sockets.remove(sckt)
                    except Exception:
                        pass
                    continue
                except shared.excepcoes_shared.ExcecaoDesserializacaoInvalida:
                    try:
                        processador.envia(sckt, [shared.excepcoes_shared.OpCodes.DESSERIALIZACAO_INVALIDA, []])
                    except Exception:
                        pass
                    continue
                
                # Pedido de sincronização de estado
                if isinstance(pedido, dict) and pedido.get("tipo") == "OBTER_ESTADO":
                    try:
                        skeleton.receber_estado(sckt)
                    except Exception as e:
                        print(f"SERVIDOR> Erro ao exportar estado: {e}")
                    try:
                        sckt.close()
                        lista_sockets.remove(sckt)
                    except Exception:
                        pass
                    continue

                try:
                    resposta = processador.processar_comando(sckt, pedido)
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
                    try:
                        sckt.close()
                        lista_sockets.remove(sckt)
                    except Exception:
                        pass
                except Exception as e:
                    print(f"SERVIDOR> Erro ao enviar resposta: {e}")
                    try:
                        sckt.close()
                        lista_sockets.remove(sckt)
                    except Exception:
                        pass
                
if __name__ == "__main__":
    main()