from rede import TCPSocketCliente
from shared import excepcoes_shared
import pickle, struct

# copiado da pl3, adaptar o que for necessario
class Stub:

    def __init__(self, HOST, PORT):
        self.rede = TCPSocketCliente(HOST, PORT)
        
    def processa(self, msg_str):
        self.envia(msg_str)
        resposta_str = self.recebe()
        print ('Recebi: %s' % resposta_str)

    def envia(self, msg_str): 
        try:
            bytes = pickle.dumps(msg_str, protocol=pickle.HIGHEST_PROTOCOL)
            size = struct.pack('i', len(msg_str))
        except excepcoes_shared.ExcecaoSerializacaoInvalida as e:
            raise e
        try:
            self.rede.envia(size, bytes)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        print("Estou a enviar", msg_str)

    def recebe(self): 
        
        return resposta_str

    def close(self): 
        self.rede.close()