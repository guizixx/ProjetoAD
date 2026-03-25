from servidor.rede import TCPSocketServidor
import pickle, struct
from shared.socket_utilities import PontoAcesso
from shared import excepcoes_shared

class Skeleton:

    def __init__(self, pontoAcesso):
        self.rede = TCPSocketServidor(pontoAcesso)

    def accept(self): 
        self.rede.accept()
        print("SERVIDOR> Servidor ligado a %s no porto %s" % (self.rede.ponto_acesso.endereco_ip, self.rede.ponto_acesso.port))

    def envia(self, msg_str): 
        try:
            size = struct.pack('i', len(msg_str))
            bytes = pickle.dumps(msg_str, protocol=pickle.HIGHEST_PROTOCOL)            
        except excepcoes_shared.ExcecaoSerializacaoInvalida as e:
            raise e
        try:
            self.rede.envia(size, bytes)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        print("Estou a enviar", msg_str)

    def recebe(self): 
        msg_bytes = self.rede.recebe()
        try:
            msg = pickle.loads(msg_bytes)
        except excepcoes_shared.ExcecaoDesserializacaoInvalida as e:
            raise e
        print(f"SERVIDOR> Comando recebido: {msg}")
        return msg

    def close(self): 
        self.rede.close()

    def closeall(self): 
        self.rede.closeall()
