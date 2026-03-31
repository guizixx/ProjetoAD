# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Ponto de entrada do cliente - lê comandos do utilizador e comunica com o servidor

import sys
import ast
from  shared.socket_utilities import PontoAcesso
from shared.excepcoes_shared import ExcepcaoConfiguracaoInvalida, ExcecaoLigacaoInterrompida
import shared.excepcoes_shared
from cliente.stub import Stub
from cliente.processador import Processador
import shlex

def main():
    if len(sys.argv) != 4:
        print("CLIENTE> Uso: python -m cliente.main <porto> <id_perfil> <id_utilizador>")
        sys.exit(1)

    try: 
        # valida endereco_ip e porto (se erro ExcepcaoIPInvalido ou ExcepcaoPortoInvalido)
        ponto_acesso = PontoAcesso(endereco_ip = 'localhost', porto = sys.argv[1])
    except ExcepcaoConfiguracaoInvalida  as e: 
        print("CLIENTE>", e)
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

    stub = Stub(ponto_acesso)
    try:
        stub.ligar()
    except OSError as e:
        print(f"CLIENTE> Erro ao ligar ao servidor: {e}")
        sys.exit(1)

    processador = Processador(stub)
    print(f"CLIENTE> Ligado com perfil={perfil}, id_utilizador={id_utilizador}")

    try:
        while True:
            try:
                msg = input("CLIENTE> ")
            except EOFError:
                break

            if not msg.strip():
                continue

            if msg.strip().upper() in ("EXIT", "QUIT"):
                break # testar como lida ao terminar com isto

            try:
                lista_comando = shlex.split(msg)
            except ValueError as e:
                raise shared.excepcoes_shared.ComandoMalFormado()
            
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
                # print(f"CLIENTE> Pedido formatado: {pedido_formatado}")
            except (SyntaxError, ValueError):
                print("CLIENTE> Formato de pedido inválido. Exemplo de formato: [10100, [\"Fruta\"], 3, 1]")
                continue

            try:
                resultado = processador.processar_pedido(pedido_formatado)
                if resultado == "SERVIDOR_ENCERROU":
                    print("CLIENTE> O servidor encerrou a ligação.")
                    break
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