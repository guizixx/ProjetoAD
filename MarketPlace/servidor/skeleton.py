# Grupo: 47
# Guilherme Pinto - nº 60260
# Tiago Telha - nº 60261
# Descrição: Skeleton - camada de comunicação do servidor.
#            Responsável por receber bytes da rede, desserializar com pickle,
#            e serializar + enviar as respostas. Não interpreta comandos.

from servidor.rede import TCPSocketServidor
import pickle, struct
from shared.socket_utilities import PontoAcesso
from shared import excepcoes_shared
from servidor.loja import Loja

class Skeleton:

    def __init__(self, pontoAcesso):
        self.rede = TCPSocketServidor(pontoAcesso)
        self.loja = Loja()

    def reset(self): 
        self.obter_loja().reset()

    def obter_loja(self):
        return self.loja
    
    def obter_rede(self):
        return self.rede

    def accept(self): 
        conn_sock, addr = self.obter_rede().accept()
        print("SERVIDOR> Servidor ligado a %s no porto %s" % (self.obter_rede().ponto_acesso.endereco_ip, self.obter_rede().ponto_acesso.porto))
        return conn_sock, addr

    def envia(self, conn_sock, msg_str): 
        try:
            bytes = pickle.dumps(msg_str, protocol=pickle.HIGHEST_PROTOCOL)            
            tamanho = struct.pack('!I', len(bytes))
        except Exception:
            raise excepcoes_shared.ExcecaoSerializacaoInvalida()
        try:
            self.obter_rede().envia(conn_sock, tamanho, bytes)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        print("Estou a enviar", msg_str)

    def recebe(self, conn_sock): 
        try:
            msg_bytes = self.obter_rede().recebe(conn_sock)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        try:
            msg = pickle.loads(msg_bytes)
        except Exception:
            raise excepcoes_shared.ExcecaoDesserializacaoInvalida()
        print(f"SERVIDOR> Comando recebido: {msg}")
        return msg

    def close(self): 
        self.obter_rede().close()

    def closeall(self): 
        self.obter_rede().closeall()
