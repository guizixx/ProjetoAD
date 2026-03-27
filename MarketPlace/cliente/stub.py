from cliente.rede import TCPSocketCliente
from shared import excepcoes_shared
import pickle, struct
from shared.excepcoes_shared import OpCodes

# copiado da pl3, adaptar o que for necessario
class Stub:

    def __init__(self, ponto_acesso):
        self.rede = TCPSocketCliente(ponto_acesso)

    def obter_rede(self):
        return self.rede
    
    def ligar(self):
        self.obter_rede().ligar()

    def desligar(self):
        self.obter_rede().desligar()
        
    def envia(self, pedido): 
        try:
            bytes = pickle.dumps(pedido, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            raise excepcoes_shared.ExcecaoSerializacao("Erro ao serializar pedido.")
        try:
            self.obter_rede().envia(bytes)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        print("Estou a enviar", pedido)

    def recebe(self): 
        try:
            bytes = self.obter_rede().recebe()
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        try:
            resposta = pickle.loads(bytes)
        except Exception:
            raise excepcoes_shared.ExcecaoSerializacao("Erro ao desserializar resposta.")
        return resposta

