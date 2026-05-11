# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Ponto de entrada do cliente - lê perfil e id_utilizador no arranque,
#            e delega toda a lógica ao ProcessadorCliente.

import sys
import ast
from  shared.socket_utilities import PontoAcesso
from shared.excepcoes_shared import ExcepcaoConfiguracaoInvalida, ExcecaoLigacaoInterrompida
import shared.excepcoes_shared
from cliente.stub import Stub
from cliente.processador import Processador
import shlex
from cliente.clienteZookeeper import ZooKeeperCliente


# o ip:port passado pelo user passa a ser o ip:port do zookeeper

def main():
    if len(sys.argv) != 4:
        # ver enunciado para alterar
        # em principio só se passa a localizaçao do zookeeper
        print("CLIENTE> Uso: python -m cliente.main <porto> <id_perfil> <id_utilizador>")
        sys.exit(1)

    try:
        perfil = int(sys.argv[2])
        id_utilizador = int(sys.argv[3])
    except ValueError:
        print(f"CLIENTE> id_perfil e id_utilizador devem ser inteiros.")
        sys.exit(1)

    if perfil not in [0, 1, 2, 3]:
        print("CLIENTE> id_perfil inválido. Use 0 para anónimo, 1 para cliente, 2 para funcionário e 3 para administrador.")
        sys.exit(1)

    if id_utilizador < 0:
        print("CLIENTE> id_utilizador deve ser um inteiro não negativo.")
        sys.exit(1)

    # alterar para o argumento passado em caso de nao ser o sys.argv[1]
    cliente_zk = ZooKeeperCliente(sys.argv[1])

    cliente_zk.ligar()
    cliente_zk.obter_head_e_tail()

    # obter localizaçao head
    endereco_head = cliente_zk.obter_head()
    if endereco_head is None:
        print("CLIENTE> Nenhum servidor head disponível.")
        sys.exit(1)
    head_sep_ix = endereco_head.index(":")
    head_ip = endereco_head[:head_sep_ix]
    head_port = endereco_head[head_sep_ix + 1:]

    # obter localizaçao tail
    endereco_tail = cliente_zk.obter_tail()
    if endereco_tail is None:
        print("CLIENTE> Nenhum servidor tail disponível.")
        sys.exit(1)
    tail_sep_ix = endereco_tail.index(":")
    tail_ip = endereco_tail[:tail_sep_ix]
    tail_port = endereco_tail[tail_sep_ix + 1:]
    
    try: 
        # valida endereco_ip e porto (se erro ExcepcaoIPInvalido ou ExcepcaoPortoInvalido)
        ponto_acesso_w = PontoAcesso(endereco_ip = head_ip, porto = head_port)
        ponto_acesso_r = PontoAcesso(endereco_ip = tail_ip, porto = tail_port)
    except ExcepcaoConfiguracaoInvalida  as e: 
        print("CLIENTE>", e)
        sys.exit(1) 

    ca_ficheiro = 'root.pem'

    stub = Stub(ponto_acesso_w, ponto_acesso_r, ca_ficheiro)
    try:
        stub.ligar()
    except OSError as e:
        print(f"CLIENTE> Erro ao ligar ao servidor: {e}")
        sys.exit(1)

    processador = Processador(stub)

    try:
        while True:
            try:
                msg = input("Mensagem: ")
            except EOFError:
                break

            if not msg.strip():
                continue

            if msg.strip().upper() in ("EXIT", "QUIT"):
                break # testar como lida ao terminar com isto

            try:
                lista_comando = shlex.split(msg)
            except ValueError as e:
                raise shared.excepcoes_shared.ComandoMalFormado(msg)
            
            try:
                if len(lista_comando) == 1:
                    comando = lista_comando[0].upper()
                    args = []
                elif len(lista_comando) > 1:
                    comando = lista_comando[0].upper()
                    args = lista_comando[1:]
                else: 
                    raise shared.excepcoes_shared.ComandoVazio()

                opcode, args_normalizados = processador.validar_pedido(comando, args)
                pedido_formatado = [opcode, args_normalizados, perfil, id_utilizador]
            except (SyntaxError, ValueError, shared.excepcoes_shared.ComandoVazio, shared.excepcoes_shared.ComandoMalFormado, shared.excepcoes_shared.NumeroArgumentosInvalido) as e:
                print(f"CLIENTE> {e}")
                continue

            try:
                resultado = processador.processar_pedido(pedido_formatado)
                if resultado == "SERVIDOR_ENCERROU":
                    print("CLIENTE> O servidor encerrou a ligação.")
                    break
                
                if "Cliente criado com sucesso com identificador único" in resultado:
                    perfil = 1 # atualizar perfil para cliente após criação bem-sucedida


                print(resultado)
            except ValueError as e:
                print(f"CLIENTE> {e}")
            except ExcecaoLigacaoInterrompida:
                print("CLIENTE> Ligação ao servidor perdida.")
                break
            except Exception as e:
                print(f"CLIENTE> Erro ao processar pedido: {e}")
                break

    except OSError as e:
        print(f"CLIENTE> Erro na comunicação: {e}")
    finally:
        stub.desligar()


if __name__ == "__main__":
    main()