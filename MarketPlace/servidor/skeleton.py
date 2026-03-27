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
        self.obter_rede().accept()
        print("SERVIDOR> Servidor ligado a %s no porto %s" % (self.obter_rede().ponto_acesso.endereco_ip, self.obter_rede().ponto_acesso.port))

    def envia(self, msg_str): 
        try:
            size = struct.pack('i', len(msg_str))
            bytes = pickle.dumps(msg_str, protocol=pickle.HIGHEST_PROTOCOL)            
        except excepcoes_shared.ExcecaoSerializacaoInvalida as e:
            raise e
        try:
            self.obter_rede().envia(size, bytes)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        print("Estou a enviar", msg_str)

    def recebe(self): 
        msg_bytes = self.obter_rede().recebe()
        try:
            msg = pickle.loads(msg_bytes)
        except excepcoes_shared.ExcecaoDesserializacaoInvalida as e:
            raise e
        print(f"SERVIDOR> Comando recebido: {msg}")
        return msg

    def close(self): 
        self.obter_rede().close()

    def closeall(self): 
        self.obter_rede().closeall()
